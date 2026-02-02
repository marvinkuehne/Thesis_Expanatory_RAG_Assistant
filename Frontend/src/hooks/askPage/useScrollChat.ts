// Change in the messages array triggers useEffect --> scrolls down

import {useEffect, useRef} from "react";
import type {Session} from "../../types/sessions.ts";
import type {ChatMessage} from "../../types/chat.ts";

export function  useScrollChat(messages: ChatMessage[], currentSessionId: string | null, sessions: Session[], input: string)
{
    const messageEndRef = useRef<HTMLDivElement | null>(null);
    useEffect(() => {
        messageEndRef.current?.scrollIntoView({behavior: "smooth"});

    }, [messages]);

    // Dynamically update browser tab title based on current chat
    useEffect(() => {
        document.title = currentSessionId
            ? sessions.find((s) => s.session_id === currentSessionId)?.title || "Chat"
            : "New Chat";
    }, [currentSessionId, sessions]);

    //Auto Resize Input field when typing
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        const el = textareaRef.current;
        if (!el) return;
        el.style.height = "0px";
        el.style.height = Math.min(el.scrollHeight, 160) + "px";
    }, [input]);

    return {messageEndRef, textareaRef};
}