"""LlamaIndex integration: indexing, persistence, and RAG querying.

Uses LlamaIndex's built-in ``SimpleVectorStore`` persisted to disk under
``data/index_storage`` (no native build toolchain required). Each indexed chunk
carries ``document_id`` and ``filename`` metadata so answers can be returned with
source citations and retrieval can be filtered per document.
"""

from __future__ import annotations

import threading

from app.config import settings
from app.schemas.chat_schema import SourceNode
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LlamaIndexNotConfiguredError(RuntimeError):
    """Raised when LlamaIndex is used without an OpenAI API key configured."""


class LlamaIndexService:
    """Lazily initialized wrapper around a persistent LlamaIndex vector index."""

    def __init__(self) -> None:
        self._index = None
        self._llm = None
        self._initialized = False
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Initialization
    # ------------------------------------------------------------------ #
    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            if not settings.openai_api_key:
                raise LlamaIndexNotConfiguredError(
                    "OPENAI_API_KEY is not configured. Set it in your environment or .env file."
                )

            # Imported lazily so the app (and tests) can import without the heavy
            # LlamaIndex stack being needed until indexing actually runs.
            from llama_index.core import (
                Settings,
                StorageContext,
                VectorStoreIndex,
                load_index_from_storage,
            )
            from llama_index.core.node_parser import SentenceSplitter
            from llama_index.embeddings.openai import OpenAIEmbedding
            from llama_index.llms.openai import OpenAI

            settings.ensure_dirs()

            self._llm = OpenAI(
                model=settings.openai_model,
                api_key=settings.openai_api_key,
                temperature=0,
            )
            Settings.llm = self._llm
            Settings.embed_model = OpenAIEmbedding(
                model=settings.openai_embedding_model,
                api_key=settings.openai_api_key,
            )
            Settings.node_parser = SentenceSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )

            persist_dir = settings.index_storage_dir
            if (persist_dir / "docstore.json").exists():
                storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
                self._index = load_index_from_storage(storage_context)
                logger.info("Loaded existing index from %s", persist_dir)
            else:
                self._index = VectorStoreIndex.from_documents([])
                self._index.storage_context.persist(persist_dir=str(persist_dir))
                logger.info("Created new empty index at %s", persist_dir)

            self._initialized = True
            logger.info(
                "LlamaIndex initialized (model=%s, embed=%s)",
                settings.openai_model,
                settings.openai_embedding_model,
            )

    def get_llm(self):
        """Return the shared LlamaIndex LLM instance (initializing if needed)."""
        self._ensure_initialized()
        return self._llm

    # ------------------------------------------------------------------ #
    # Indexing
    # ------------------------------------------------------------------ #
    def add_document(
        self, document_id: str, filename: str, text: str, owner_id: str
    ) -> int:
        """Chunk, embed, and persist a document. Returns the number of chunks."""
        self._ensure_initialized()
        from llama_index.core import Document as LIDocument
        from llama_index.core import Settings

        if not text.strip():
            logger.warning("Skipping indexing for empty document %s", filename)
            return 0

        li_doc = LIDocument(
            text=text,
            metadata={
                "document_id": str(document_id),
                "filename": filename,
                "owner_id": owner_id,
            },
        )
        nodes = Settings.node_parser.get_nodes_from_documents([li_doc])
        if not nodes:
            return 0
        self._index.insert_nodes(nodes)
        # Persist to disk so the index survives restarts.
        self._index.storage_context.persist(persist_dir=str(settings.index_storage_dir))
        logger.info("Indexed %d chunk(s) for document %s", len(nodes), document_id)
        return len(nodes)

    # ------------------------------------------------------------------ #
    # Querying (RAG)
    # ------------------------------------------------------------------ #
    def query(
        self,
        question: str,
        owner_id: str,
        document_ids: list[str] | None = None,
        top_k: int | None = None,
    ) -> tuple[str, list[SourceNode]]:
        """Answer a question from the owner's documents, with sources.

        Retrieval is always scoped to ``owner_id``. When ``document_ids`` is
        given (already validated as owned by the caller), retrieval is further
        narrowed to those documents.
        """
        self._ensure_initialized()
        from llama_index.core.vector_stores import (
            FilterCondition,
            FilterOperator,
            MetadataFilter,
            MetadataFilters,
        )

        if document_ids:
            # The caller has already validated that these ids belong to the
            # owner, so filtering by them alone preserves isolation.
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="document_id", value=str(doc_id), operator=FilterOperator.EQ
                    )
                    for doc_id in document_ids
                ],
                condition=FilterCondition.OR,
            )
        else:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="owner_id", value=owner_id, operator=FilterOperator.EQ
                    )
                ],
                condition=FilterCondition.AND,
            )

        query_engine = self._index.as_query_engine(
            similarity_top_k=top_k or settings.similarity_top_k,
            filters=filters,
        )
        response = query_engine.query(question)

        sources: list[SourceNode] = []
        for node in getattr(response, "source_nodes", []) or []:
            metadata = node.node.metadata or {}
            snippet = node.node.get_content().strip()
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."
            sources.append(
                SourceNode(
                    document_id=metadata.get("document_id"),
                    filename=metadata.get("filename"),
                    snippet=snippet,
                    score=getattr(node, "score", None),
                )
            )

        answer = str(response).strip() or "No answer could be generated from the indexed documents."
        return answer, sources


# Module-level singleton used across routes and services.
llamaindex_service = LlamaIndexService()
