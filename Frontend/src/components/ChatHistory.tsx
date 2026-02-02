import type { ChatMessage } from "../types/chat";
import React from "react";

//bundle messages and messageEndRed as Props to give return jsx in AskPage 1 Parameter!
type Props = {
  messages: ChatMessage[];
  messageEndRef: React.RefObject<HTMLDivElement | null>;
};

export function ChatHistory({ messages, messageEndRef }: Props) {
    return (
        <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 space-y-4">
            {messages.map((m, i) => {
                if (m.role === "user") {
                    return (
                        <div key={i} className="flex justify-end">
                            <div
                                className="max-w-[92%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm bg-blue-600 text-white rounded-br-md">
                                <div className="whitespace-pre-wrap">{m.content}</div>
                            </div>
                        </div>
                    );
                }

                return (
                    <div key={i} className="flex justify-start gap-3">
                        {/* Bubble A */}
                        <div
                            className="max-w-[92%] sm:max-w-[40%] rounded-2xl px-4 py-3 shadow-sm bg-neutral-800 text-neutral-100 border border-neutral-700">
                            <div className="text-xs uppercase tracking-wide text-neutral-400 mb-1">
                                Style A
                            </div>
                            <div className="whitespace-pre-wrap">{m.contentA}</div>

                            {m.sourcesA?.length ? (
                                <div className="mt-3 border-t border-neutral-700 pt-2">
                                    <div className="text-xs uppercase tracking-wide text-neutral-400 mb-1">
                                        Sources
                                    </div>
                                    <ul className="list-disc pl-5 text-sm text-neutral-300">
                                        {m.sourcesA.map((src, idx) => (
                                            <li key={idx}>{src}</li>
                                        ))}
                                    </ul>
                                </div>
                            ) : null}
                        </div>

                        {/* Bubble B */}
                        <div
                            className="max-w-[92%] sm:max-w-[40%] rounded-2xl px-4 py-3 shadow-sm bg-neutral-800 text-neutral-100 border border-neutral-700">
                            <div className="text-xs uppercase tracking-wide text-neutral-400 mb-1">
                                Style B
                            </div>
                            <div className="whitespace-pre-wrap">{m.contentB}</div>

                            {m.sourcesB?.length ? (
                                <div className="mt-3 border-t border-neutral-700 pt-2">
                                    <div className="text-xs uppercase tracking-wide text-neutral-400 mb-2">
                                        Sources & Explanation
                                    </div>

                                    <ul className="space-y-3 text-sm text-neutral-300">
                                        {m.sourcesB.map((src, idx) => (
                                            <li key={idx} className="rounded-lg bg-neutral-900/40 p-2">
                                                <div className="font-medium text-neutral-200">{src}</div>
                                                <div className="mt-1 text-xs text-neutral-400 italic">
                                                    This source is relevant because it contains information that is
                                                    important for proposal drafting xxxxx
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            ) : null}
                        </div>
                    </div>
                );
            })}

            <div ref={messageEndRef}></div>
        </div>
    );
}