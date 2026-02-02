import api from "../../api.ts";
import type {Session} from "../../types/sessions.ts";
import type {ChatMessage} from "../../types/chat.ts";




export function useSessionActions(
  userId,
  sessions,
  setSessions,
  currentSessionId,
  setCurrentSessionId,
  setMessages,
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
            const remaining = sessions.filter(s => s.session_id !== currentSessionId);//filter out current session to be deleted
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