/**
 * AI coach chat drawer — right-side overlay panel for logging and coaching.
 *
 * Mounted once in `app/app/layout.tsx` so the session and message history
 * persist across page navigations. The drawer is toggled via the `open` prop.
 *
 * Session continuity:
 *   A stable `sessionId` (UUID) is generated on first render via `useRef`.
 *   It is sent with every message so the backend can maintain multi-turn
 *   conversation history for the same browser session.
 *
 * Streaming protocol (SSE events from `POST /agent/chat`):
 *   tool_call   → appends a pending tool row to the message's `toolEvents`
 *   tool_result → upgrades the matching pending tool_call row to tool_result
 *   text        → appends a text chunk to the message content
 *   done        → marks `isStreaming: false`, hides the cursor
 *   error       → shows the error as the message content
 *
 * Tool result matching:
 *   `tool_result` events are matched to the most recent `tool_call` with the
 *   same tool name using a reverse-scan. This handles back-to-back calls of
 *   the same tool correctly (e.g. two `log_weight` calls in one turn).
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { Send, X } from "lucide-react";
import { type ChatEvent, streamChat } from "@/lib/api";

interface ToolEvent {
  type: "tool_call" | "tool_result";
  tool: string;
  args?: unknown;
  result?: unknown;
}

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolEvents: ToolEvent[];
  isStreaming: boolean;
}

const SUGGESTIONS = [
  "I just weighed 85.5 kg",
  "Had chicken, rice & broccoli for lunch",
  "Finished push day — bench pressed 65 kg × 7",
  "Is my protein too low?",
];

const QUICK_CHIPS = ["Log a meal", "Log my weight", "Log workout", "Coach advice"];

/**
 * Three staggered bouncing dots shown while the assistant hasn't produced any
 * text yet (i.e. waiting for the first token or tool result).
 */
function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 py-0.5">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="size-1.5 rounded-full bg-zinc-400 animate-bounce"
          // Stagger each dot by 150 ms to create a wave effect
          style={{ animationDelay: `${i * 150}ms` }}
        />
      ))}
    </div>
  );
}

/**
 * Single row inside `ToolsExpander`.
 *
 * Shows a spinning border while the tool is pending (type === "tool_call")
 * and a green checkmark once the result arrives (type === "tool_result").
 * The detail string (args or result) is truncated at 90 characters.
 */
function ToolEventRow({ event }: { event: ToolEvent }) {
  const isPending = event.type === "tool_call";
  const detail = isPending
    ? JSON.stringify(event.args ?? {})
    : JSON.stringify(event.result ?? "");
  const truncated = detail.length > 90 ? detail.slice(0, 90) + "…" : detail;

  return (
    <div className="flex items-start gap-2">
      {isPending ? (
        <span className="mt-px size-3 shrink-0 rounded-full border-2 border-zinc-400 border-t-transparent animate-spin" />
      ) : (
        <span className="shrink-0 text-green-600 leading-none">✓</span>
      )}
      <div className="font-mono text-zinc-600 min-w-0">
        <span className="font-semibold">{event.tool}</span>{" "}
        <span className="text-zinc-400 break-all">{truncated}</span>
      </div>
    </div>
  );
}

/**
 * Collapsible section above the assistant text bubble showing tool calls.
 *
 * Auto-opens on the first event so the user sees activity immediately.
 * The user can manually collapse it; it won't re-open on subsequent events
 * because the `useEffect` only fires when `events.length` increases from 0.
 */
function ToolsExpander({ events }: { events: ToolEvent[] }) {
  const [open, setOpen] = useState(false);

  // Auto-open when the first tool event arrives
  useEffect(() => {
    if (events.length > 0) setOpen(true);
  }, [events.length]);

  if (events.length === 0) return null;

  // At least one pending tool_call means the spinner is still running
  const hasPending = events.some((e) => e.type === "tool_call");
  const label = hasPending
    ? "Running tools…"
    : `${events.length} tool${events.length !== 1 ? "s" : ""} used`;

  return (
    <div className="text-xs rounded-lg border border-zinc-200 bg-zinc-50 overflow-hidden self-start w-full max-w-[90%]">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-1.5 px-3 py-2 text-zinc-500 hover:bg-zinc-100 transition-colors text-left"
      >
        {/* Chevron rotates 90° when open */}
        <span
          className="text-zinc-400 inline-block transition-transform duration-150 leading-none"
          style={{ transform: open ? "rotate(90deg)" : "rotate(0deg)" }}
        >
          ▶
        </span>
        <span className="font-mono font-medium flex-1">{label}</span>
        {hasPending && (
          <span className="size-3 shrink-0 rounded-full border-2 border-zinc-400 border-t-transparent animate-spin" />
        )}
      </button>
      {open && (
        <div className="border-t border-zinc-100 px-3 py-2.5 flex flex-col gap-2">
          {events.map((ev, i) => (
            <ToolEventRow key={i} event={ev} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Renders a single chat message.
 *
 * User messages are right-aligned with a dark bubble. Assistant messages are
 * left-aligned, preceded by the `ToolsExpander` (if any tool calls exist),
 * and show a `TypingIndicator` until the first text token arrives.
 */
function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[82%] bg-zinc-900 text-white rounded-tl-2xl rounded-tr-sm rounded-bl-2xl rounded-br-2xl px-4 py-2.5 text-sm leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  // Show typing dots while streaming AND no text has arrived yet (tools may still be running)
  const showTyping = message.isStreaming && message.content === "";

  return (
    <div className="flex flex-col gap-1.5 items-start">
      <ToolsExpander events={message.toolEvents} />
      <div className="max-w-[90%] bg-white border border-zinc-100 rounded-tl-sm rounded-tr-2xl rounded-bl-2xl rounded-br-2xl px-4 py-2.5 text-sm leading-relaxed">
        {showTyping ? (
          <TypingIndicator />
        ) : (
          <>
            {message.content}
            {/* Blinking cursor while text is streaming in */}
            {message.isStreaming && (
              <span className="inline-block w-0.5 h-3.5 bg-zinc-400 ml-0.5 animate-pulse align-middle" />
            )}
          </>
        )}
      </div>
    </div>
  );
}

interface ChatDrawerProps {
  /** Whether the drawer is visible. */
  open: boolean;
  /** Called when the user closes the drawer (backdrop click or × button). */
  onClose: () => void;
}

export function ChatDrawer({ open, onClose }: ChatDrawerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);

  // Stable session ID — same UUID for the lifetime of this component instance.
  // Falls back to Math.random for environments without crypto.randomUUID.
  const sessionId = useRef(
    typeof crypto !== "undefined" ? crypto.randomUUID() : Math.random().toString(36).slice(2)
  );
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to the latest message whenever messages change or streaming starts
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, streaming]);

  async function sendMessage(text: string) {
    if (!text.trim() || streaming) return;
    setInput("");
    setStreaming(true);

    const assistantId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: "user", content: text, toolEvents: [], isStreaming: false },
      { id: assistantId, role: "assistant", content: "", toolEvents: [], isStreaming: true },
    ]);

    // Helper to mutate only the assistant message being streamed into
    const update = (fn: (m: ChatMessage) => ChatMessage) =>
      setMessages((prev) => prev.map((m) => (m.id === assistantId ? fn(m) : m)));

    try {
      for await (const event of streamChat(text, sessionId.current)) {
        if (event.type === "text") {
          update((m) => ({ ...m, content: m.content + event.content }));
        } else if (event.type === "tool_call") {
          update((m) => ({
            ...m,
            toolEvents: [...m.toolEvents, { type: "tool_call", tool: event.tool, args: event.args }],
          }));
        } else if (event.type === "tool_result") {
          update((m) => {
            const evts = [...m.toolEvents];
            // Reverse-scan to find the most recent pending call for this tool
            const idx = [...evts].reverse().findIndex((e) => e.type === "tool_call" && e.tool === event.tool);
            if (idx !== -1) {
              const real = evts.length - 1 - idx;
              evts[real] = { ...evts[real], type: "tool_result", result: event.result };
            } else {
              // No matching call — append the result as a standalone row
              evts.push({ type: "tool_result", tool: event.tool, result: event.result });
            }
            return { ...m, toolEvents: evts };
          });
        } else if (event.type === "done") {
          update((m) => ({ ...m, isStreaming: false }));
        } else if (event.type === "error") {
          update((m) => ({ ...m, content: `Error: ${event.message}`, isStreaming: false }));
        }
      }
    } catch (err) {
      update((m) => ({ ...m, content: `Error: ${String(err)}`, isStreaming: false }));
    } finally {
      setStreaming(false);
    }
  }

  if (!open) return null;

  return (
    <>
      {/* Backdrop — clicking outside closes the drawer */}
      <div className="fixed inset-0 bg-black/20 z-40" onClick={onClose} />

      {/* Drawer panel */}
      <div className="fixed top-0 right-0 bottom-0 w-[440px] bg-white z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-100 shrink-0">
          <div>
            <p className="font-bold text-base text-zinc-900">Chat with Coach</p>
            <p className="text-xs font-mono text-zinc-400">Log anything · ask anything</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-xs font-mono font-semibold text-green-600">
              <span className="size-1.5 rounded-full bg-green-500" />
              ONLINE
            </span>
            <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600">
              <X className="size-4" />
            </button>
          </div>
        </div>

        {/* Quick chips — shorthand phrases that populate the input field */}
        <div className="flex gap-2 overflow-x-auto px-4 py-2 border-b border-zinc-100 shrink-0">
          {QUICK_CHIPS.map((chip) => (
            <button
              key={chip}
              onClick={() => setInput(chip)}
              className="shrink-0 px-2.5 py-1 rounded-full text-xs font-mono border border-zinc-200 text-zinc-500 hover:bg-zinc-50 whitespace-nowrap"
            >
              {chip}
            </button>
          ))}
        </div>

        {/* Message list — scrollable, grows to fill available height */}
        <div className="flex-1 overflow-y-auto flex flex-col gap-3 p-4">
          {messages.length === 0 && (
            <p className="text-xs font-mono text-zinc-400 text-center pt-12">
              Ask me anything or log something
            </p>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Suggestion chips + input bar — pinned to the bottom */}
        <div className="shrink-0 border-t border-zinc-100 p-3">
          {/* One-tap suggestion chips that send immediately (not just fill the input) */}
          <div className="flex gap-1.5 overflow-x-auto mb-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="shrink-0 text-xs px-2.5 py-1 rounded-full border border-zinc-200 text-zinc-500 hover:bg-zinc-50 whitespace-nowrap"
              >
                {s}
              </button>
            ))}
          </div>
          <div className="flex gap-2 items-center">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(input);
                }
              }}
              placeholder="Log something or ask your coach…"
              className="flex-1 rounded-full border border-zinc-200 px-4 py-2.5 text-sm outline-none focus:border-zinc-400 min-h-[44px] bg-white"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={streaming || !input.trim()}
              className="size-[46px] rounded-full bg-zinc-900 flex items-center justify-center shrink-0 disabled:opacity-40 hover:bg-zinc-700 transition-colors"
            >
              <Send className="size-4 text-white" />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
