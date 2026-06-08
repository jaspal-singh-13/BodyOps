/**
 * Typed HTTP client for the BodyOps FastAPI backend.
 *
 * All data fetching goes through `apiFetch`. The JWT is stored in a cookie
 * and attached to every request via the Next.js proxy route (`/api/[...path]`),
 * which reads the cookie server-side and forwards `Authorization: Bearer`.
 *
 * Auth flow:
 *   setToken(token) → stores JWT in a 7-day SameSite cookie
 *   apiFetch(...)   → all requests routed through /api/* proxy
 *   on 401          → clears token and redirects to /login
 *   clearToken()    → removes the cookie (sign-out)
 *
 * Agent streaming:
 *   streamChat(message, sessionId) → async generator yielding `ChatEvent` objects
 */

/** Read the raw JWT string from the `token` cookie, or `""` if absent. */
export function getToken(): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|; )token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

/** Read the JWT from the `token` cookie; returns `true` if present. */
export function isLoggedIn(): boolean {
  return getToken() !== "";
}

/**
 * Persist a JWT in a browser cookie valid for 7 days.
 *
 * Uses `SameSite=Strict` to prevent CSRF. The cookie is readable by the
 * Next.js proxy middleware but NOT accessible to client-side JS in `HttpOnly`
 * mode — here it is readable so `isLoggedIn()` can check it.
 *
 * @param token - Raw JWT string returned by `POST /auth/login`.
 */
export function setToken(token: string): void {
  document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

/**
 * Remove the JWT cookie, effectively signing the user out.
 *
 * Sets `max-age=0` which instructs the browser to delete the cookie immediately.
 */
export function clearToken(): void {
  document.cookie = "token=; path=/; max-age=0";
}

/** Error thrown by `apiFetch` when the upstream returns a non-2xx status. */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

/**
 * Typed fetch wrapper for all BodyOps API calls.
 *
 * Routes all requests through the Next.js `/api/*` proxy, which forwards the
 * JWT cookie as a bearer token to FastAPI. Handles 401 globally by clearing
 * the token and redirecting to `/login`.
 *
 * @param path - API path without the `/api` prefix (e.g. `"/weight/history"`).
 * @param options - Standard `RequestInit` options (method, body, headers, etc.).
 * @returns Parsed JSON response typed as `T`.
 *
 * @throws `ApiError` for any non-2xx response (excluding 401 which redirects).
 *
 * @example
 * const history = await apiFetch<WeightHistoryItem[]>("/weight/history");
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, { ...options, headers });

  if (res.status === 401) {
    // Token expired or invalid — clear it and force re-login
    clearToken();
    window.location.href = "/login";
    throw new ApiError(401, "Unauthorized");
  }

  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(res.status, body);
  }

  return res.json() as Promise<T>;
}

// ── Agent streaming ──────────────────────────────────────────────────────────

/**
 * Discriminated union of all SSE event types emitted by `POST /agent/chat`.
 *
 * Events arrive in this order for a typical tool-calling turn:
 *   1. `tool_call`   — agent is about to call a tool
 *   2. `tool_result` — tool finished, result available
 *   3. `text`        — streaming text chunks (multiple events)
 *   4. `done`        — stream is complete
 *
 * An `error` event may appear at any point if the agent or a tool throws.
 */
export type ChatEvent =
  | { type: "text"; content: string }
  | { type: "tool_call"; tool: string; args: Record<string, unknown> }
  | { type: "tool_result"; tool: string; result: unknown }
  | { type: "done" }
  | { type: "error"; message: string };

/**
 * Async generator that streams chat events from the SSE endpoint.
 *
 * Opens a `POST /api/agent/chat` request and reads the response body as a
 * stream, parsing each `data: {...}` line into a typed `ChatEvent`. The
 * generator completes when the stream closes or a `done` event is parsed.
 *
 * Usage:
 * ```ts
 * for await (const event of streamChat(message, sessionId)) {
 *   if (event.type === "text") appendText(event.content);
 * }
 * ```
 *
 * @param message - The user's message text.
 * @param sessionId - Client-generated UUID for multi-turn session continuity.
 * @yields Typed `ChatEvent` objects as they arrive from the server.
 *
 * @throws `ApiError` for non-2xx, non-401 HTTP errors.
 */
export async function* streamChat(
  message: string,
  sessionId: string
): AsyncGenerator<ChatEvent> {
  const token = getToken();
  const res = await fetch("/api/agent/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (res.status === 401) {
    clearToken();
    window.location.href = "/login";
    return;
  }
  if (!res.ok) throw new ApiError(res.status, await res.text());
  if (!res.body) return;

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  // Buffer accumulates partial lines between `read()` calls
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    // Split on newlines; keep the last (potentially incomplete) line in buffer
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6)) as ChatEvent;
        } catch {
          // Skip malformed SSE lines (e.g. empty data lines, comments)
        }
      }
    }
  }
}
