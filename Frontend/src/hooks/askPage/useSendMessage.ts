import {useState} from "react";
import type {ChatMessage} from "../../types/chat.ts";
import api from "../../api.ts";
import type {CatOption} from "../../types/categories.ts";


// pack json object in form that the BaseModel in router expects (uses axios)
export function useSendMessage(
    userId: string | null,
    selectedCategories: CatOption[],
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>,
    setInput: React.Dispatch<React.SetStateAction<string>>
) {

    const [isLoading, setIsLoading] = useState(false);

    // Helper function to use it in handleClick()
    async function send(input: string) {
        // 1) Prevent empty messages
        if (!input.trim()) return;

        //2) Show user message in UI
        const userMsg: ChatMessage = {role: "user", content: input}; // 1) build temporary user message object
        setMessages((prev) => [...prev, userMsg]); // 2) Add it to messages (function, to avoid batching (e.g. overwrite several newMessages with the latest))
        setInput(""); //3) clear input
        setIsLoading(true); // 4) start loading bar

        //3) Call backend
        const response = await api.post("/ask", {
            query: input,
            categories: selectedCategories.map(c => c.label),
        });


        // 4) Build assistant response object (answer + sources) and append
        console.log(response.data);
        const answer = response.data[0];
        const sources = response.data[1];

        const assistantMsg: ChatMessage = {
            role: "assistant",
            contentA: answer,
            contentB: answer,          // identical
            sourcesA: sources,
            sourcesB: sources,         // identical
        };
        setMessages((prev) => [...prev, assistantMsg]);

        // 5) Stop spinner
        setIsLoading(false);

    }


    return {send, isLoading};

}
