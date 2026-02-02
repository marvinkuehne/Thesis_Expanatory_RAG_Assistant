export type ChatMessage =
  | { role: "user"; content: string }
  | {
      role: "assistant";
      contentA: string;
      contentB: string;
      sourcesA?: string[];
      sourcesB?: string[];
    };