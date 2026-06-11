/**
 * Authenticated app shell — sidebar (desktop) + bottom nav (mobile) + chat drawer.
 *
 * This is the layout for all `/app/**` routes. It is a `"use client"` component
 * because the chat drawer state (`chatOpen`) must live here so it persists across
 * page navigations without re-mounting.
 *
 * The "Chat to log" button and the mobile Coach tab both toggle the same
 * `chatOpen` state, which mounts `<ChatDrawer>` as an overlay on top of the
 * current page without navigating away.
 */

"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Home, Utensils, Dumbbell, TrendingUp, Scale, MessageCircle, CheckSquare } from "lucide-react";
import { clearToken } from "@/lib/api";
import { ChatDrawer } from "@/components/ChatDrawer";
import { RefreshProvider } from "@/lib/refresh";

const navItems = [
  { href: "/app", label: "Home", icon: Home },
  { href: "/app/weight", label: "Weight", icon: Scale },
  { href: "/app/meals", label: "Meals", icon: Utensils },
  { href: "/app/workouts", label: "Workouts", icon: Dumbbell },
  { href: "/app/missions", label: "Missions", icon: CheckSquare },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [chatOpen, setChatOpen] = useState(false);

  function signOut() {
    clearToken();
    router.push("/login");
  }

  return (
    <RefreshProvider>
    <div className="flex h-screen bg-zinc-50">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-52 bg-white border-r border-zinc-100 p-4 shrink-0">
        <div className="mb-4 px-3">
          <h1 className="text-lg font-bold text-zinc-900">BodyOps</h1>
        </div>

        {/* Chat to log button — primary entry point for the AI coach */}
        <div className="px-0 mb-4">
          <button
            onClick={() => setChatOpen(true)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-900 text-white text-sm font-bold hover:bg-zinc-700 transition-colors"
          >
            <MessageCircle className="size-4" />
            Chat to log
          </button>
        </div>

        <nav className="flex flex-col gap-1 flex-1">
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? "bg-zinc-100 text-zinc-900"
                    : "text-zinc-600 hover:bg-zinc-100"
                }`}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <button
          onClick={signOut}
          className="text-sm text-zinc-400 hover:text-zinc-600 text-left px-3 py-2 transition-colors"
        >
          Sign out
        </button>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto pb-20 md:pb-0">{children}</main>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-zinc-100 flex safe-bottom">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors ${
                active ? "text-zinc-900" : "text-zinc-400"
              }`}
            >
              <Icon className={`size-5 ${active ? "stroke-2" : "stroke-[1.5]"}`} />
              {label}
            </Link>
          );
        })}
        {/* Mobile coach tab — opens the same drawer as the desktop "Chat to log" button */}
        <button
          onClick={() => setChatOpen(true)}
          className="flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium text-zinc-400"
        >
          <MessageCircle className="size-5 stroke-[1.5]" />
          Coach
        </button>
      </nav>

      {/* Chat drawer — mounted here so it persists across page navigations */}
      <ChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
    </RefreshProvider>
  );
}
