import {useEffect} from "react";
import api from "../../api.ts";
import type {ChatMessage} from "../../types/chat.ts";

export function useChatAutosave(
  userId: string | null,
  currentSessionId: string | null,
  messages: ChatMessage[]
) {
  useEffect(() => {
    if (userId && currentSessionId) {
      // 1) Save locally
      localStorage.setItem(`chat_${userId}_${currentSessionId}`, JSON.stringify(messages));

      // 2) Save on backend
      async function saveChat() {
        try {
          await api.post("/save_session", {
            session_id: currentSessionId,
            messages: messages,
          });
        } catch (error) {
          console.error("Error saving chat:", error);
        }
      }

      saveChat();
    }
  }, [messages, userId, currentSessionId]);
}