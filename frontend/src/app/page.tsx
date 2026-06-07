/**
 * Root index route — immediately redirects to `/login`.
 *
 * The middleware in `proxy.ts` handles auth-aware redirects for `/app/**`
 * and `/login`, but the bare `/` route is not covered by that matcher.
 * This component fills the gap so users are never left on a blank page.
 */

import { redirect } from "next/navigation";

/** Redirect the root path to the login page unconditionally. */
export default function Home() {
  redirect("/login");
}
