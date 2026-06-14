import type { DocumentResponse } from "../types";

interface Props {
  documents: DocumentResponse[];
  value: string;
  onChange: (id: string) => void;
  label?: string;
  placeholder?: string;
}

/** A styled dropdown listing indexed documents. */
export function DocumentSelect({
  documents,
  value,
  onChange,
  label = "Document",
  placeholder = "Select a document…",
}: Props) {
  const indexed = documents.filter((d) => d.status === "indexed");
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-300">
        {label}
      </span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
      >
        <option value="">{placeholder}</option>
        {indexed.map((d) => (
          <option key={d.id} value={d.id}>
            {d.filename}
          </option>
        ))}
      </select>
    </label>
  );
}
