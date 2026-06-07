/**
 * Shared UI utility functions.
 *
 * Currently exports only `cn`, a Tailwind class merger. Add other
 * framework-agnostic helpers here as the project grows.
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind CSS class names, resolving conflicts in favour of the last value.
 *
 * Combines `clsx` (handles arrays, objects, conditional strings) with
 * `tailwind-merge` (deduplicates conflicting Tailwind utilities, e.g.
 * `p-2` + `p-4` → `p-4`).
 *
 * @param inputs - Any mix of strings, arrays, or objects accepted by `clsx`.
 * @returns A single merged class string safe to pass to `className`.
 *
 * @example
 * cn("px-2 py-1", isActive && "bg-zinc-900", "px-4")
 * // → "py-1 bg-zinc-900 px-4"
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
