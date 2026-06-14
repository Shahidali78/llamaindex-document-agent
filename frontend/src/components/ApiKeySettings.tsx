import { useState } from "react";
import { getApiKey, setApiKey } from "../api/client";

interface Props {
  /** Called after the key is saved/cleared so the app can refetch. */
  onChange: () => void;
}

/** Sidebar control for entering and storing the API key (localStorage). */
export function ApiKeySettings({ onChange }: Props) {
  const [value, setValue] = useState(getApiKey());
  const [editing, setEditing] = useState(getApiKey() === "");
  const [saved, setSaved] = useState(false);

  function save() {
    setApiKey(value.trim());
    setEditing(false);
    setSaved(true);
    onChange();
    setTimeout(() => setSaved(false), 1500);
  }

  function clear() {
    setApiKey("");
    setValue("");
    setEditing(true);
    onChange();
  }

  const masked =
    value.length > 8 ? `${value.slice(0, 6)}…${value.slice(-2)}` : value;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-800/40 p-3 text-xs">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-medium text-slate-300">API key</span>
        {!editing && value && (
          <span className="rounded bg-emerald-500/15 px-1.5 py-0.5 text-emerald-300">
            set
          </span>
        )}
      </div>

      {editing ? (
        <div className="space-y-2">
          <input
            type="password"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && save()}
            placeholder="X-API-Key…"
            className="w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-slate-100 placeholder:text-slate-600 focus:border-indigo-500 focus:outline-none"
          />
          <button
            onClick={save}
            disabled={!value.trim()}
            className="w-full rounded bg-indigo-600 px-2 py-1 font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            Save key
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-2">
          <code className="truncate text-slate-400">{masked}</code>
          <div className="flex gap-2">
            <button
              onClick={() => setEditing(true)}
              className="text-indigo-300 hover:text-indigo-200"
            >
              edit
            </button>
            <button onClick={clear} className="text-rose-300 hover:text-rose-200">
              clear
            </button>
          </div>
        </div>
      )}
      {saved && <p className="mt-1 text-emerald-300">Saved.</p>}
    </div>
  );
}
