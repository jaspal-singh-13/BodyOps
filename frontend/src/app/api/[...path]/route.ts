import { type NextRequest } from "next/server";

const HF_URL = process.env.HF_API_URL ?? "http://localhost:8000";
const HF_TOKEN = process.env.HF_TOKEN ?? "";

type Context = { params: Promise<{ path: string[] }> };

async function proxy(req: NextRequest, pathSegments: string[]): Promise<Response> {
  const jwt = req.cookies.get("token")?.value ?? "";
  const targetUrl = `${HF_URL}/${pathSegments.join("/")}${req.nextUrl.search}`;

  const headers: Record<string, string> = {};

  const contentType = req.headers.get("content-type");
  if (contentType) headers["Content-Type"] = contentType;

  if (jwt) headers["Authorization"] = `Bearer ${jwt}`;
  if (HF_TOKEN) headers["X-HF-Token"] = HF_TOKEN;

  const hasBody = !["GET", "HEAD"].includes(req.method);

  const upstream = await fetch(targetUrl, {
    method: req.method,
    headers,
    body: hasBody ? await req.arrayBuffer() : undefined,
  });

  const responseHeaders: Record<string, string> = {};
  const upstreamContentType = upstream.headers.get("content-type");
  if (upstreamContentType) responseHeaders["Content-Type"] = upstreamContentType;

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export async function GET(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function POST(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PUT(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function PATCH(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}

export async function DELETE(req: NextRequest, ctx: Context) {
  const { path } = await ctx.params;
  return proxy(req, path);
}
