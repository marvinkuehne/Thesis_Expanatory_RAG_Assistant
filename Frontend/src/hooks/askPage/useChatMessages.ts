import { useEffect, useState } from "react";
import api from "../../api.ts";
import type {ChatMessage} from "../../types/chat.ts";



export function useChatMessages(currentSessionId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    if (!currentSessionId) {
      setMessages([]); // no current session active
      return;
    }

    async function fetchMessages() {
      try {
        const res = await api.get(`/get_session/${currentSessionId}`);
        setMessages(res.data ?? []);
      } catch (err) {
        console.error("Error loading messages for session:", err);
      }
    }

    fetchMessages();
  }, [currentSessionId]);

  return { messages, setMessages };
}