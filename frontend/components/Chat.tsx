"use client";

import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import type { ChatResponse, LeaveRequest } from "@/lib/api";
import { AssistantMessage } from "./AssistantMessage";
import { button, card, errorBox, focus } from "./ui";

export type ChatMessage =
  | { role: "user"; text: string }
  | { role: "assistant"; turn: ChatResponse }
  | { role: "error"; text: string; prompt: string }; // `prompt` is what "Try again" resends

// ISO dates on purpose: the scripted demo model only recognises YYYY-MM-DD.
const SUGGESTIONS = [
  "How many annual leave days can I carry forward?",
  "What's my leave balance?",
  "Apply annual leave from 2026-11-15 to 2026-11-17 for a family trip",
  "Can I work remotely on Wednesday?",
];

interface Props {
  messages: ChatMessage[];
  sending: boolean;
  onSend: (text: string) => Promise<void>;
  onRetry: (prompt: string) => Promise<void>;
  requests: LeaveRequest[]; // used to show each draft's latest status
  onConfirm: (id: number) => Promise<unknown>;
  onDiscard: (id: number) => Promise<unknown>;
}

export function Chat({ messages, sending, onSend, onRetry, requests, onConfirm, onDiscard }: Props) {
  const [input, setInput] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const lastRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const lastRole = messages.at(-1)?.role;

  // Follow the conversation: while waiting, show the bottom (your message + "Thinking…"); when an
  // answer arrives, scroll to its start so a long reply reads from the top.
  useEffect(() => {
    const list = listRef.current;
    const last = lastRef.current;
    if (!list) return;
    const behavior = matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    const answered = !sending && lastRole !== "user" && last;
    list.scrollTo({ top: answered ? last.offsetTop - 16 : list.scrollHeight, behavior }); // 16 = list padding
  }, [messages.length, lastRole, sending]);

  // After a reply, put the cursor back in the composer, unless the user moved focus elsewhere
  // meanwhile (a clicked Send or suggestion button leaves focus on <body>).
  async function sendAndRefocus(send: () => Promise<void>) {
    await send();
    if (document.activeElement === document.body) inputRef.current?.focus();
  }

  function submit(e?: FormEvent) {
    e?.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    sendAndRefocus(() => onSend(text));
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends, Shift+Enter adds a newline; ignore Enter while an IME is composing.
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) submit(e);
  }

  const latest = (d: LeaveRequest) => requests.find((r) => r.id === d.id) ?? d;

  return (
    <section aria-label="Chat with the HR assistant" className={`${card} flex h-[70dvh] min-h-0 flex-col lg:h-auto`}>
      <div
        ref={listRef}
        role="log"
        aria-live="polite"
        className="relative flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto p-4"
      >
        {messages.length === 0 && !sending ? (
          <EmptyState onPick={(text) => sendAndRefocus(() => onSend(text))} />
        ) : (
          messages.map((m, i) => (
            <div key={i} ref={i === messages.length - 1 ? lastRef : undefined} className="flex flex-col">
              {m.role === "user" ? (
                <p className="max-w-[85%] self-end whitespace-pre-wrap break-words text-pretty rounded-panel bg-raised px-3.5 py-2.5 text-base leading-relaxed">
                  <span className="sr-only">You said: </span>
                  {m.text}
                </p>
              ) : m.role === "error" ? (
                <div role="alert" className={`flex max-w-[68ch] flex-wrap items-center justify-between gap-2 ${errorBox}`}>
                  <p>{m.text}</p>
                  {i === messages.length - 1 && (
                    <button
                      type="button"
                      className={button("ghost", "sm")}
                      disabled={sending}
                      onClick={() => sendAndRefocus(() => onRetry(m.prompt))}
                    >
                      Try again
                    </button>
                  )}
                </div>
              ) : (
                <AssistantMessage
                  text={m.turn.reply}
                  citations={m.turn.citations}
                  steps={m.turn.steps}
                  drafts={m.turn.drafts.map(latest)}
                  onConfirm={onConfirm}
                  onDiscard={onDiscard}
                />
              )}
            </div>
          ))
        )}
        {sending && (
          <p role="status" className="flex items-center gap-2 text-sm text-muted">
            <span aria-hidden className="flex gap-1">
              <span className="size-1.5 rounded-full bg-muted motion-safe:animate-think" />
              <span className="size-1.5 rounded-full bg-muted motion-safe:animate-think motion-safe:[animation-delay:150ms]" />
              <span className="size-1.5 rounded-full bg-muted motion-safe:animate-think motion-safe:[animation-delay:300ms]" />
            </span>
            Thinking…
          </p>
        )}
      </div>

      <form onSubmit={submit} className="border-t border-border p-3">
        <div className="flex items-end gap-2">
          <label htmlFor="chat-input" className="sr-only">
            Message the HR assistant
          </label>
          {/* Read-only (not disabled) while sending, so keyboard focus stays here during the wait. */}
          <textarea
            ref={inputRef}
            id="chat-input"
            name="message"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            readOnly={sending}
            aria-busy={sending}
            aria-describedby="chat-hint"
            autoComplete="off"
            maxLength={2000}
            placeholder="Ask about a policy or request leave…"
            className={`max-h-40 min-h-11 min-w-0 flex-1 resize-none rounded-control border border-control bg-surface px-3 py-2 text-base leading-relaxed text-ink field-sizing-content placeholder:text-muted ${focus}`}
          />
          <button
            type="submit"
            className={button("primary", "lg")}
            disabled={sending || !input.trim()}
            title={sending ? "Wait for the reply…" : undefined}
          >
            Send
          </button>
        </div>
        <p id="chat-hint" className="mt-2 hidden text-xs text-muted sm:block">
          Enter to send · Shift+Enter for a new line
        </p>
      </form>
    </section>
  );
}

function EmptyState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="my-auto flex max-w-[60ch] flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h2 className="text-balance text-xl font-semibold tracking-tight">Ask about HR policy or your leave</h2>
        <p className="text-base leading-relaxed">
          Answers come from Acme&apos;s HR policies with sources. I can draft a leave request, but only you can submit
          it.
        </p>
      </div>
      <ul className="grid gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map((s) => (
          <li key={s} className="flex">
            <button
              type="button"
              onClick={() => onPick(s)}
              className={`min-h-11 flex-1 rounded-control border border-border bg-surface px-3 py-2.5 text-left text-sm text-ink transition-colors duration-150 hover:bg-raised ${focus}`}
            >
              {s}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
