import Select, { type GroupBase, type MultiValue, type StylesConfig} from "react-select";
import type {CatOption} from "../types/categories";
import React from "react";
import {useFakeProgress} from "../hooks/askPage/progressBar.ts";

type Props = {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  onSend: () => void | Promise<void>;
  isLoading: boolean;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  categories: CatOption[];
  selectedCategories: CatOption[];
  setSelectedCategories: React.Dispatch<React.SetStateAction<CatOption[]>>;
  loadCategories: () => void | Promise<void>;
  selectStyles: StylesConfig<CatOption, true, GroupBase<CatOption>>;
};

export function ChatComposer({
  input,
  setInput,
  onSend,
  isLoading,
  textareaRef,
  categories,
  selectedCategories,
  setSelectedCategories,
  loadCategories,
  selectStyles,
}: Props) {

  const progress = useFakeProgress(isLoading);

   return (
    <div className="border-t border-neutral-800 px-3 sm:px-6 py-3 bg-black/20">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          placeholder="Ask something…"
          className="min-h-[44px] max-h-40 w-full resize-none rounded-2xl
                     bg-neutral-800 text-white placeholder:text-neutral-500
                     px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          type="button"
          onClick={onSend}
          disabled={isLoading || !input.trim()}
          className="shrink-0 rounded-2xl bg-blue-600 px-4 py-2 font-medium text-white
                     hover:bg-blue-500 disabled:opacity-50"
        >
          Send
        </button>

        {isLoading && (
          <div className="h-5 w-5 relative" aria-label="Loading">
            {/* optional: progress als kleine bar */}
            <div className="absolute -bottom-2 left-0 h-1 w-20 bg-neutral-700 rounded">
              <div className="h-1 bg-blue-500 rounded" style={{ width: `${progress}%` }} />
            </div>
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-500 border-t-transparent" />
          </div>
        )}
      </div>

      <div className="mt-4">
        <Select
          isMulti
          options={categories}
          value={selectedCategories}
          onChange={(opts: MultiValue<CatOption>) => setSelectedCategories([...opts])}
          onMenuOpen={loadCategories}
          menuPlacement="top"
          menuPosition="fixed"
          menuPortalTarget={document.body}
          styles={selectStyles}
        />
      </div>
    </div>
  );
}