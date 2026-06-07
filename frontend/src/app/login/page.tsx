/**
 * Login page — authenticates the user against `POST /auth/login`.
 *
 * On success the JWT is stored in a browser cookie via `setToken`, then the
 * user is redirected to `/app`. The middleware in `proxy.ts` will redirect
 * back here automatically if the cookie is missing on a protected route.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // Bypass apiFetch — login has no auth cookie yet, so the proxy would
      // forward an empty bearer token; call the proxy route directly instead.
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        setError("Invalid email or password");
        return;
      }
      const data = await res.json();
      if (!data?.access_token) {
        setError("Login failed: no token received. Please try again.");
        return;
      }
      setToken(data.access_token);
      router.push("/app");
    } catch {
      setError("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50">
      <div className="w-full max-w-sm p-8 bg-white rounded-2xl shadow-sm border border-zinc-100">
        <h1 className="text-2xl font-bold text-zinc-900 mb-1">BodyOps</h1>
        <p className="text-zinc-500 text-sm mb-8">Your AI fat-loss OS</p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="border border-zinc-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-zinc-400"
              required
              autoComplete="email"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border border-zinc-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-zinc-400"
              required
              autoComplete="current-password"
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="mt-2 bg-zinc-900 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-zinc-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
