import {useState} from "react";
import './AskPage.css';
import {getSelectStyles} from "../ui/selectStyles";
import {useUserId} from "../components/useUserID.ts";
import {useSessions} from "../hooks/askPage/useSessions.ts";
import {useChatMessages} from "../hooks/askPage/useChatMessages.ts";
import {useChatAutosave} from "../hooks/askPage/saveChat.ts";
import {useScrollChat} from "../hooks/askPage/useScrollChat.ts";
import {useSendMessage} from "../hooks/askPage/useSendMessage.ts";
import {useCategories} from "../hooks/askPage/useCategories.ts";
import {useSessionActions} from "../hooks/askPage/useSessionActions.ts";
import {ChatHistory} from "../components/ChatHistory";
import {ChatComposer} from "../components/ChatComposer";
import {SessionControls} from "../components/SessionControls";


export default function AskPage() {
    const [input, setInput] = useState("");


    // Hooks that run sequentially when UI renders
    const userId = useUserId() // 1) fetch/create userId
    const {categories, selectedCategories, setSelectedCategories, loadCategories,} = useCategories(userId);
    const {sessions, setSessions, currentSessionId, setCurrentSessionId} = useSessions(userId) //2) Fetch/create sessions available for userId and set newest session
    const {messages, setMessages} = useChatMessages(currentSessionId) // 3) fetch messages for active session
    useChatAutosave(userId, currentSessionId, messages)    //4) Save user sessions incl. messages
    const {send, isLoading} = useSendMessage(userId, selectedCategories, setMessages, setInput);
    const {createNewSession, deleteCurrentSession} = useSessionActions(userId, sessions, setSessions, currentSessionId, setCurrentSessionId, setMessages);
    const {messageEndRef, textareaRef} = useScrollChat(messages, currentSessionId, sessions, input);

    async function handleClick() {
        await send(input)
    }


    return (
        <div className="flex flex-col h-full bg-neutral-900 text-white">
            {/* Session Controls */}
            <SessionControls
                sessions={sessions}
                currentSessionId={currentSessionId}
                setCurrentSessionId={setCurrentSessionId}
                onCreateNew={createNewSession}
                onDeleteCurrent={deleteCurrentSession}
            />

            {/* Chat-History */}

            <ChatHistory messages={messages} messageEndRef={messageEndRef}/>


            {/* Composer */}
            <ChatComposer
                input={input}
                setInput={setInput}
                onSend={handleClick}
                isLoading={isLoading}
                textareaRef={textareaRef}
                categories={categories}
                selectedCategories={selectedCategories}
                setSelectedCategories={setSelectedCategories}
                loadCategories={loadCategories}
                selectStyles={getSelectStyles(selectedCategories.length === 0)}
            />
        </div>
    );
}
