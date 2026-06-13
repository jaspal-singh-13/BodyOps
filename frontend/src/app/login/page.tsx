/**
 * Login page — authenticates the user against `POST /auth/login`.
 *
 * Desktop: split left brand panel (dark bg, logo, tagline) + right card form.
 * Mobile: centred card form with logo mark on top.
 *
 * On success the JWT is stored in a browser cookie via `setToken`, then the
 * user is redirected to `/app`. The middleware in `proxy.ts` will redirect
 * back here automatically if the cookie is missing on a protected route.
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/api";

function BodyOpsLogo({ size = 40 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0"
    >
      <rect width="40" height="40" rx="10" fill="#1d1c1a" />
      {/* Lightning bolt */}
      <path
        d="M23 7L13 22h8l-4 11 14-15h-8L23 7z"
        fill="white"
      />
    </svg>
  );
}

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
    <div className="min-h-screen flex">
      {/* Brand panel — hidden on mobile, shown on md+ */}
      <div className="hidden md:flex flex-col justify-between w-[420px] bg-zinc-900 p-10 shrink-0">
        <div className="flex items-center gap-3">
          <BodyOpsLogo size={40} />
          <span className="text-white text-xl font-extrabold tracking-tight">BodyOps</span>
        </div>

        <div>
          <p className="text-[32px] font-extrabold text-white leading-tight tracking-tight">
            Your AI fat-loss<br />operating system.
          </p>
          <p className="mt-4 text-zinc-400 text-[15px] leading-relaxed">
            Log meals with a photo. Track weight trends. Complete daily missions.
            Let AI coach you to your goal.
          </p>
        </div>

        <p className="font-mono text-[11px] text-zinc-600">bodyops.ai</p>
      </div>

      {/* Login form */}
      <div className="flex-1 flex items-center justify-center bg-zinc-50 p-6">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 mb-8 md:hidden">
            <BodyOpsLogo size={36} />
            <span className="text-zinc-900 text-lg font-extrabold tracking-tight">BodyOps</span>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-zinc-100 p-8">
            <h1 className="text-xl font-bold text-zinc-900 mb-0.5">Sign in</h1>
            <p className="text-zinc-500 text-sm mb-7">Welcome back. Let&apos;s crush today.</p>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-zinc-700">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="border border-zinc-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-zinc-400 transition-colors"
                  required
                  autoComplete="email"
                  placeholder="you@example.com"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-sm font-medium text-zinc-700">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="border border-zinc-200 rounded-lg px-3 py-2.5 text-sm outline-none focus:border-zinc-400 transition-colors"
                  required
                  autoComplete="current-password"
                  placeholder="••••••••"
                />
              </div>
              {error && <p className="text-sm text-red-500">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="mt-2 bg-zinc-900 text-white rounded-xl py-3 text-sm font-semibold hover:bg-zinc-700 disabled:opacity-50 transition-colors"
              >
                {loading ? "Signing in…" : "Sign in"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
