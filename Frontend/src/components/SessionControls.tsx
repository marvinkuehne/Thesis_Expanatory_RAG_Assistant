import React from "react";
import type {Session} from "../types/sessions.ts";

//bundle messages and messageEndRed as Props to give return jsx in AskPage 1 Parameter!
type Props = {
    sessions: Session[],
    currentSessionId: string | null,
    setCurrentSessionId: (arg0: string) => void,
    onCreateNew: () => void,
    onDeleteCurrent: () => void,
}


export function SessionControls(
    {
        sessions,
        currentSessionId,
        setCurrentSessionId,
        onCreateNew,
        onDeleteCurrent,
    }: Props
) {
    return (
        <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
                <select
                    value={currentSessionId ?? ""}
                    onChange={(e) => setCurrentSessionId(e.target.value)}
                    className="bg-neutral-800 text-white border border-neutral-700 rounded-lg px-3 py-2"
                >
                    {sessions.map((s) => (
                        <option key={s.session_id} value={s.session_id}>
                            {s.title || "Untitled Chat"}
                        </option>
                    ))}
                </select>

                <button
                    onClick={onCreateNew}
                    className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-500"
                >
                    + New
                </button>
            </div>

            <button
                onClick={onDeleteCurrent}
                className="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-500"
            >
                🗑 Delete
            </button>
        </div>
    );
}