"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Home, Utensils, Dumbbell, TrendingUp, MessageCircle } from "lucide-react";
import { clearToken } from "@/lib/api";

const navItems = [
  { href: "/app", label: "Home", icon: Home },
  { href: "/app/meals", label: "Meals", icon: Utensils },
  { href: "/app/workouts", label: "Workouts", icon: Dumbbell },
  { href: "/app/progress", label: "Progress", icon: TrendingUp },
  { href: "/app/coach", label: "Coach", icon: MessageCircle },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  function signOut() {
    clearToken();
    router.push("/login");
  }

  return (
    <div className="flex h-screen bg-zinc-50">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-52 bg-white border-r border-zinc-100 p-4 shrink-0">
        <div className="mb-8 px-3">
          <h1 className="text-lg font-bold text-zinc-900">BodyOps</h1>
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
                    ? "bg-zinc-900 text-white"
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
      </nav>
    </div>
  );
}
