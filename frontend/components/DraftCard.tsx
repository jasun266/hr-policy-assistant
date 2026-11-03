import type { LeaveRequest } from "@/lib/api";
import { LEAVE_LABEL, formatRange } from "@/lib/format";
import { useAction } from "@/lib/useAction";
import { Spinner } from "./icons";
import { StatusBadge } from "./StatusBadge";
import { button, errorBox } from "./ui";

const AFTER: Partial<Record<LeaveRequest["status"], string>> = {
  pending: "Submitted. Your manager will review it.",
  approved: "Approved by your manager.",
  rejected: "Rejected by your manager.",
  cancelled: "Draft discarded.",
};

interface Props {
  request: LeaveRequest; // the latest known state of the draft (kept in sync with "My requests")
  onConfirm: (id: number) => Promise<unknown>;
  onDiscard: (id: number) => Promise<unknown>;
}

// The agent can only draft. Submitting happens here, by the employee, with an explicit click.
// Discarding needs no confirm: the assistant can draft it again.
export function DraftCard({ request: r, onConfirm, onDiscard }: Props) {
  const { busy, error, run } = useAction();
  const isDraft = r.status === "draft";

  return (
    <section
      aria-label={`Leave request #${r.id}`}
      aria-busy={busy !== null}
      className={`rounded-panel border bg-surface px-4 py-3 ${isDraft ? "border-draft-border" : "border-border"}`}
    >
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold">
          {isDraft ? "Draft" : "Request"} <span className="tabular-nums">#{r.id}</span> · {LEAVE_LABEL[r.leave_type]}
        </h2>
        <StatusBadge status={r.status} />
      </div>
      <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
        <dt className="text-muted">Dates</dt>
        <dd className="tabular-nums">{formatRange(r.start_date, r.end_date)}</dd>
        <dt className="text-muted">Working days</dt>
        <dd className="tabular-nums">{r.days}</dd>
        <dt className="text-muted">Reason</dt>
        <dd className="min-w-0 break-words">{r.reason || <span className="text-muted">—</span>}</dd>
      </dl>
      {isDraft ? (
        <>
          <p className="mt-2 text-sm text-muted">Not submitted yet. Check the dates, then submit.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              className={button("primary")}
              disabled={busy !== null}
              onClick={() => run("submit", () => onConfirm(r.id))}
            >
              {busy === "submit" ? <><Spinner /> Submitting…</> : "Submit request"}
            </button>
            <button
              type="button"
              className={button("secondary")}
              disabled={busy !== null}
              onClick={() => run("discard", () => onDiscard(r.id))}
            >
              {busy === "discard" ? <><Spinner /> Discarding…</> : "Discard draft"}
            </button>
          </div>
        </>
      ) : (
        <p role="status" className="mt-2 text-sm">
          {AFTER[r.status]}
        </p>
      )}
      {error && (
        <p role="alert" className={`mt-3 ${errorBox}`}>
          {error}
        </p>
      )}
    </section>
  );
}
