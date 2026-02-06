import type { SetStateAction } from "react";
import api from "../../api.ts";
import type {ChatMessage} from "../../types/chat.ts";
import type {Session} from "../../types/sessions.ts";


export function useSessionActions(
    userId: string,
    sessions: any[],
    setSessions: {
        (value: SetStateAction<{ session_id: string; title: string; }[]>): void;
        (arg0: (prev: any) => any[]): void;
    },
    currentSessionId: string | null,
    setCurrentSessionId: { (value: SetStateAction<string | null>): void; (arg0: string | null): void; },
    setMessages: { (value: SetStateAction<ChatMessage[]>): void; (arg0: never[]): void; },
) {

    async function createNewSession() {
        if (!userId) return;

        const res = await api.post<Session>("/create_session", {
            user_id: userId,
            title: `New Chat ${sessions.length + 1}`,
        });

        setSessions((prev) => [res.data, ...prev]);
        setCurrentSessionId(res.data.session_id);
        setMessages([]); // clear chat

    }

    async function deleteCurrentSession() {

        if (!currentSessionId) return;

        try {
            await api.delete(`/delete_session/${currentSessionId}`);

            // Remove session from state
            const remaining = sessions.filter((s: { session_id: never; }) => s.session_id !== currentSessionId);//filter out current session to be deleted
            setSessions(remaining);

            // Choose other session or remove everything
            if (remaining.length > 0) {
                setCurrentSessionId(remaining[0].session_id);
            } else {
                setCurrentSessionId(null);
                setMessages([]);
            }
        } catch (err) {
            console.error("Error deleting session:", err);
        }
    }

    return {createNewSession, deleteCurrentSession};
}