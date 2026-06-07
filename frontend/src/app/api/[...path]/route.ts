/**
 * Next.js catch-all API proxy route.
 *
 * All requests to `/api/**` are forwarded transparently to the FastAPI backend
 * running at `HF_API_URL` (defaults to `http://localhost:8000` in dev).
 *
 * The proxy:
 *   - Forwards the JWT from the `token` cookie as a `Authorization: Bearer` header.
 *   - Optionally adds `X-HF-Token` if `HF_TOKEN` is set (used on HF Spaces).
 *   - Streams response bodies directly (no buffering) so SSE works end-to-end.
 *   - Preserves the upstream `Content-Type` in the response.
 *
 * Environment variables:
 *   HF_API_URL — backend base URL (e.g. `https://user-bodyops-api.hf.space`)
 *   HF_TOKEN   — optional Hugging Face token for private Spaces
 */

import { type NextRequest } from "next/server";

const HF_URL = process.env.HF_API_URL ?? "http://localhost:8000";
const HF_TOKEN = process.env.HF_TOKEN ?? "";

type Context = { params: Promise<{ path: string[] }> };

/**
 * Forward a Next.js request to the FastAPI backend and return the response.
 *
 * Attaches the JWT from the `token` cookie as `Authorization: Bearer` and
 * passes the request body through unchanged (using `arrayBuffer` to support
 * both JSON and multipart payloads).
 *
 * @param req - Incoming Next.js request.
 * @param pathSegments - URL path segments after `/api/`, e.g. `["weight", "history"]`.
 * @returns Upstream response with the original body and `Content-Type` header.
 */
async function proxy(req: NextRequest, pathSegments: string[]): Promise<Response> {
  const jwt = req.cookies.get("token")?.value ?? "";
  const targetUrl = `${HF_URL}/${pathSegments.join("/")}${req.nextUrl.search}`;

  const headers: Record<string, string> = {};

  // Forward Content-Type for POST/PUT/PATCH requests (JSON, multipart, etc.)
  const contentType = req.headers.get("content-type");
  if (contentType) headers["Content-Type"] = contentType;

  if (jwt) headers["Authorization"] = `Bearer ${jwt}`;
  if (HF_TOKEN) headers["X-HF-Token"] = HF_TOKEN;

  // Only attach a body for methods that allow one; GET/HEAD have no body
  const hasBody = !["GET", "HEAD"].includes(req.method);

  const upstream = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
  });

  // Preserve only Content-Type from the upstream response; let Next.js handle
  // other headers (e.g. CORS is handled by FastAPI's CORSMiddleware).
  const responseHeaders: Record<string, string> = {};
  const upstreamContentType = upstream.headers.get("content-type");
  if (upstreamContentType) responseHeaders["Content-Type"] = upstreamContentType;

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

/** Proxy GET requests (e.g. `/api/weight/history`). */
export async function GET(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

/** Proxy POST requests (e.g. `/api/weight`, `/api/agent/chat`). */
export async function POST(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

/** Proxy PUT requests. */
export async function PUT(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

/** Proxy PATCH requests. */
export async function PATCH(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

/** Proxy DELETE requests (e.g. `/api/agent/history`). */
export async function DELETE(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}
