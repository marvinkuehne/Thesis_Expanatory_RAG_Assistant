import {useEffect, useState} from "react";
import api from "../../api.ts";


export function useSessions(userId: string | null) {

    const [sessions, setSessions] = useState<{ session_id: string; title: string }[]>([]); //List of sessions
    const [currentSessionId, setCurrentSessionId] = useState<string | null>(null); //active session

    useEffect(() => {
        if (!userId) return;

        async function fetchSessions() {
            try {
                const res = await api.get(`/get_sessions/${userId}`);
                const allSessions = res.data || [];
                setSessions(allSessions);

                // No user session? --> create session
                if (allSessions.length === 0) {
                    const newSession = await api.post("/create_session", {
                        user_id: userId,
                        title: "New Chat",
                    });
                    setCurrentSessionId(newSession.data.session_id);
                } else {
                    // Nimm die neueste Session als aktive
                    setCurrentSessionId(allSessions[0].session_id);
                }
            } catch (err) {
                console.error("Error loading sessions:", err);
            }
        }

        fetchSessions();
    }, [userId]);

    return {sessions, setSessions, currentSessionId, setCurrentSessionId};
}