/**
 * Next.js middleware for route-based auth protection.
 *
 * Runs on the Edge runtime before a request reaches the page or API route.
 * Enforces two rules:
 *   1. Protected routes (`/app/**`, `/onboarding/**`) redirect to `/login`
 *      when no `token` cookie is present.
 *   2. `/login` redirects to `/app` when the user already has a token
 *      (avoids showing the login form to an authenticated user).
 *
 * The `matcher` config restricts execution to the relevant paths — all
 * other routes (static assets, `/api/**`) bypass this middleware entirely.
 */

import { type NextRequest, NextResponse } from "next/server";

/**
 * Middleware handler invoked by Next.js for matched routes.
 *
 * @param req - Incoming Edge request with cookie and URL access.
 * @returns A `NextResponse.redirect` when auth rules are violated, or
 *          `NextResponse.next()` to continue to the destination.
 */
export function middleware(req: NextRequest) {
  const token = req.cookies.get("token");
  const { pathname } = req.nextUrl;

  const isProtected =
    pathname.startsWith("/app") || pathname.startsWith("/onboarding");

  // Unauthenticated user hitting a protected route → send to login
  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  // Already-authenticated user hitting login → send to dashboard
  if (pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/app", req.url));
  }

  return NextResponse.next();
}

/** Route patterns this middleware applies to. */
export const config = {
  matcher: ["/app/:path*", "/onboarding/:path*", "/login"],
};
