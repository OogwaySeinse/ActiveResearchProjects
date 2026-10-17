import { useCallback, useEffect, useState } from "react";
import type { DatasetPayload } from "../types";

export type DatasetState =
  | { status: "loading" }
  | { status: "ready"; data: DatasetPayload }
  | { status: "error"; error: string };

const BOOKMARKS_KEY = "wunderscholar.bookmarks.v1";

export function useDataset(): { state: DatasetState; reload: () => void } {
  const [state, setState] = useState<DatasetState>({ status: "loading" });
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => {
    setState({ status: "loading" });
    setNonce((n) => n + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch(`./data/projects.json?t=${Date.now()}`, { cache: "no-cache" })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<DatasetPayload>;
      })
      .then((data) => {
        if (!cancelled) setState({ status: "ready", data });
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setState({ status: "error", error: e instanceof Error ? e.message : String(e) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [nonce]);

  return { state, reload };
}

export function useNow(intervalMs = 60_000): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return now;
}

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState<Set<string>>(() => {
    try {
      const raw = localStorage.getItem(BOOKMARKS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) return new Set(parsed);
      }
    } catch {
      // ignore
    }
    return new Set();
  });

  const toggleBookmark = useCallback((id: string) => {
    setBookmarks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      try {
        localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(Array.from(next)));
      } catch {
        // ignore
      }
      return next;
    });
  }, []);

  return { bookmarks, toggleBookmark };
}

