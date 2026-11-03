import { useState } from "react";

export const FALLBACK_ERROR = "Something went wrong on our side. Try again in a moment.";

// Tracks the async buttons of one card or row: which action is running (so that button can show
// its "…ing" label while all of them are disabled) and the last error message.
export function useAction() {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(name: string, action: () => Promise<unknown>) {
    setBusy(name);
    setError(null);
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : FALLBACK_ERROR);
    } finally {
      setBusy(null);
    }
  }

  return { busy, error, run };
}
