/**
 * Authenticated app shell — sidebar (desktop) + bottom nav (mobile) + chat drawer.
 *
 * This is the layout for all `/app/**` routes. It is a `"use client"` component
 * because the chat drawer state (`chatOpen`) must live here so it persists across
 * page navigations without re-mounting.
 *
 * The "Chat to log" button toggles `<ChatDrawer>` as an overlay on top of the
 * current page without navigating away.
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Home, Utensils, Dumbbell, TrendingUp, Scale, MessageCircle,
  CheckSquare, Sparkles, BarChart2, Settings, Footprints, Menu, X,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { ChatDrawer } from "@/components/ChatDrawer";
import { RefreshProvider } from "@/lib/refresh";

const navItems = [
  { href: "/app", label: "Home", icon: Home },
  { href: "/app/weight", label: "Weight", icon: Scale },
  { href: "/app/steps", label: "Steps", icon: Footprints },
  { href: "/app/meals", label: "Meals", icon: Utensils },
  { href: "/app/workouts", label: "Workouts", icon: Dumbbell },
  { href: "/app/missions", label: "Missions", icon: CheckSquare },
];

const navItemsExtra = [
  { href: "/app/coach", label: "Coach", icon: Sparkles },
  { href: "/app/progress", label: "Progress", icon: BarChart2 },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

// Mobile nav: Home · Weight · Meals · Workouts · Steps
const mobileNavItems = [
  { href: "/app", label: "Home", icon: Home },
  { href: "/app/weight", label: "Weight", icon: Scale },
  { href: "/app/meals", label: "Meals", icon: Utensils },
  { href: "/app/workouts", label: "Workouts", icon: Dumbbell },
  { href: "/app/steps", label: "Steps", icon: Footprints },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [chatOpen, setChatOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [userName, setUserName] = useState<string>("");

  useEffect(() => {
    apiFetch<{ name: string }>("/settings")
      .then((s) => setUserName(s.name || ""))
      .catch(() => {});
  }, []);

  const initial = userName ? userName.trim()[0].toUpperCase() : "U";

  return (
    <RefreshProvider>
    <div className="flex flex-col md:flex-row h-screen bg-zinc-50">
      {/* Mobile top bar — hamburger + logo; hidden on desktop */}
      <header className="md:hidden flex items-center gap-3 px-4 h-12 bg-white border-b border-zinc-100 shrink-0">
        <button
          onClick={() => setMenuOpen(true)}
          className="p-1.5 rounded-lg text-zinc-700 hover:bg-zinc-100 active:scale-95 transition-all"
          aria-label="Open menu"
        >
          <Menu className="size-5" />
        </button>
        <span className="text-base font-bold text-zinc-900">BodyOps</span>
      </header>

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
          <div className="my-1 border-t border-zinc-100" />
          {navItemsExtra.map(({ href, label, icon: Icon }) => {
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

        {/* User profile chip */}
        {userName && (
          <div className="px-3 py-2 flex items-center gap-2 mb-1">
            <div className="w-7 h-7 rounded-full bg-zinc-900 flex items-center justify-center shrink-0">
              <span className="text-white text-[11px] font-bold">{initial}</span>
            </div>
            <span className="text-sm font-medium text-zinc-700 truncate">{userName}</span>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto pb-20 md:pb-0">{children}</main>

      {/* Mobile side drawer */}
      {menuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="md:hidden fixed inset-0 bg-black/40 z-50"
            onClick={() => setMenuOpen(false)}
          />
          {/* Drawer panel */}
          <aside className="md:hidden fixed top-0 left-0 h-full w-64 bg-white z-50 flex flex-col p-4 shadow-xl">
            <div className="flex items-center justify-between mb-4 px-1">
              <h1 className="text-lg font-bold text-zinc-900">BodyOps</h1>
              <button
                onClick={() => setMenuOpen(false)}
                className="p-1 rounded-lg text-zinc-500 hover:bg-zinc-100 transition-colors"
                aria-label="Close menu"
              >
                <X className="size-5" />
              </button>
            </div>

            {/* Chat to log button */}
            <div className="mb-4">
              <button
                onClick={() => { setMenuOpen(false); setChatOpen(true); }}
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
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      active ? "bg-zinc-100 text-zinc-900" : "text-zinc-600 hover:bg-zinc-100"
                    }`}
                  >
                    <Icon className="size-4" />
                    {label}
                  </Link>
                );
              })}
              <div className="my-1 border-t border-zinc-100" />
              {navItemsExtra.map(({ href, label, icon: Icon }) => {
                const active = pathname === href;
                return (
                  <Link
                    key={href}
                    href={href}
                    onClick={() => setMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      active ? "bg-zinc-100 text-zinc-900" : "text-zinc-600 hover:bg-zinc-100"
                    }`}
                  >
                    <Icon className="size-4" />
                    {label}
                  </Link>
                );
              })}
            </nav>

            {/* User profile chip */}
            {userName && (
              <div className="px-3 py-2 flex items-center gap-2 mt-1">
                <div className="w-7 h-7 rounded-full bg-zinc-900 flex items-center justify-center shrink-0">
                  <span className="text-white text-[11px] font-bold">{initial}</span>
                </div>
                <span className="text-sm font-medium text-zinc-700 truncate">{userName}</span>
              </div>
            )}
          </aside>
        </>
      )}

      {/* Mobile bottom nav — 5 tabs, no hardcoded Coach chat button */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-zinc-100 flex safe-bottom">
        {mobileNavItems.map(({ href, label, icon: Icon }) => {
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
      </nav>

      {/* Mobile chat FAB — opens ChatDrawer; hidden on desktop (sidebar button handles it) */}
      <button
        onClick={() => setChatOpen(true)}
        className="md:hidden fixed bottom-20 right-4 flex items-center gap-2 px-4 py-2.5 rounded-full bg-zinc-900 text-white text-sm font-bold shadow-lg hover:bg-zinc-700 active:scale-95 transition-all z-40"
        aria-label="Chat to log"
      >
        <MessageCircle className="size-4" />
        Chat
      </button>

      {/* Chat drawer — mounted here so it persists across page navigations */}
      <ChatDrawer open={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
    </RefreshProvider>
  );
}
