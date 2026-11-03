import { useRef, useState, type ReactNode } from "react";
import { flushSync } from "react-dom";
import type { Balance, LeaveRequest, TeamRequest } from "@/lib/api";
import { LEAVE_LABEL, formatRange, plural } from "@/lib/format";
import { useAction } from "@/lib/useAction";
import { Spinner } from "./icons";
import { StatusBadge } from "./StatusBadge";
import { button, card, errorBox } from "./ui";

export interface SidebarData {
  balances: Balance[];
  requests: LeaveRequest[];
  team: TeamRequest[] | null; // null for non-managers
}

type Decide = (id: number, decision: "approve" | "reject") => Promise<unknown>;

interface Props {
  data: SidebarData | null; // null while the first fetch for this user runs
  isManager: boolean;
  error: string | null;
  onRetry: () => void;
  onCancel: (id: number) => Promise<unknown>;
  onDecide: Decide;
}

export function Sidebar({ data, isManager, error, onRetry, onCancel, onDecide }: Props) {
  return (
    <aside aria-label="Leave overview" className="flex flex-col gap-4 lg:gap-6">
      {error && (
        <div role="alert" className={`flex items-center justify-between gap-2 ${errorBox}`}>
          <p>{error}</p>
          <button type="button" className={button("ghost", "sm")} onClick={onRetry}>
            Try again
          </button>
        </div>
      )}

      {isManager && (
        <Panel id="team-approvals" title="Team approvals" count={data?.team?.length}>
          {!data?.team ? (
            <RowsLoading />
          ) : data.team.length === 0 ? (
            <Empty>Nothing waiting for your approval.</Empty>
          ) : (
            <ul className="divide-y divide-border">
              {data.team.map((r) => (
                <TeamRow key={r.id} request={r} onDecide={onDecide} />
              ))}
            </ul>
          )}
        </Panel>
      )}

      <Panel title="Leave balance">
        <ul className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          {data
            ? data.balances.map((b) => <BalanceMeter key={b.leave_type} balance={b} />)
            : [1, 2, 3].map((i) => <BalanceLoading key={i} />)}
        </ul>
      </Panel>

      <Panel title="My requests" count={data?.requests.length}>
        {!data ? (
          <RowsLoading />
        ) : data.requests.length === 0 ? (
          <Empty>No requests yet. Ask the assistant to draft one.</Empty>
        ) : (
          <ul className="divide-y divide-border">
            {data.requests.map((r) => (
              <RequestRow key={r.id} request={r} onCancel={onCancel} />
            ))}
          </ul>
        )}
      </Panel>
    </aside>
  );
}

// `count` is undefined while loading, so the tag only appears once there is a real number.
function Panel({ id, title, count, children }: { id?: string; title: string; count?: number; children: ReactNode }) {
  return (
    <section id={id} aria-labelledby={id && `${id}-title`} className={`${card} scroll-mt-4 p-4`}>
      <h2 id={id && `${id}-title`} className="mb-3 flex items-center gap-2 text-sm font-semibold">
        {title}
        {count !== undefined && (
          <span className="rounded-tag bg-raised px-1.5 text-xs font-medium tabular-nums text-muted">{count}</span>
        )}
      </h2>
      {children}
    </section>
  );
}

const Empty = ({ children }: { children: ReactNode }) => <p className="text-sm text-muted">{children}</p>;

// Placeholders at the real rows' size, no shimmer. Loading is not the same as empty.
const Bar = ({ className }: { className: string }) => <span className={`block rounded-tag bg-raised ${className}`} />;

function RowsLoading() {
  return (
    <div aria-hidden className="divide-y divide-border">
      {[1, 2].map((i) => (
        <div key={i} className="flex flex-col gap-2 py-3 first:pt-0 last:pb-0">
          <div className="flex justify-between">
            <Bar className="h-5 w-32" />
            <Bar className="h-5 w-16" />
          </div>
          <Bar className="h-4 w-40" />
        </div>
      ))}
    </div>
  );
}

function BalanceLoading() {
  return (
    <li aria-hidden className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Bar className="h-4 w-24" />
        <Bar className="h-7 w-16" />
      </div>
      <Bar className="h-2 rounded-full" />
      <Bar className="h-4 w-32" />
    </li>
  );
}

// One meter per leave type: used (accent), pending, and what's left, split by 2px surface gaps.
function BalanceMeter({ balance: b }: { balance: Balance }) {
  const segments = [
    { days: b.used, className: "bg-accent" },
    { days: b.pending, className: "bg-pending-solid" },
    { days: b.remaining, className: "bg-track" },
  ].filter((s) => s.days > 0);

  return (
    <li className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm">{LEAVE_LABEL[b.leave_type]}</span>
        <span className="text-sm text-muted">
          <span className="text-xl font-semibold tracking-tight tabular-nums text-ink">{b.remaining}</span> left
        </span>
      </div>
      <div
        role="img"
        aria-label={`${b.used} used, ${b.pending} pending, ${b.remaining} left of ${b.entitled}`}
        className="flex h-2 gap-0.5 overflow-hidden rounded-full bg-surface"
      >
        {segments.map((s) => (
          <span key={s.className} className={s.className} style={{ flexGrow: s.days }} />
        ))}
      </div>
      <p className="text-xs text-muted tabular-nums">
        {b.used} used
        {b.pending > 0 && (
          <>
            {" · "}
            <span className="text-pending-ink">{b.pending} pending</span>
          </>
        )}
        {` · ${b.entitled} a year`}
      </p>
    </li>
  );
}

// A destructive row action guarded by an inline confirm (no modal): the trigger swaps for a
// question + confirm + "Keep", and the row's other actions (children) hide meanwhile. Focus moves
// to "Keep" and back to the trigger, so keyboard users never land on <body>. flushSync renders
// the swap first so the button to focus exists.
function ConfirmAction(props: {
  label: string;
  ariaLabel: string;
  question: string;
  confirmLabel: string;
  busyLabel: string;
  busy: boolean;
  disabled: boolean;
  onConfirm: () => void;
  children?: ReactNode;
}) {
  const [asking, setAsking] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const keepRef = useRef<HTMLButtonElement>(null);

  function toggle(next: boolean) {
    flushSync(() => setAsking(next));
    (next ? keepRef : triggerRef).current?.focus();
  }

  if (!asking && !props.busy)
    return (
      <>
        {props.children}
        <button
          ref={triggerRef}
          type="button"
          className={button("destructive", "sm")}
          disabled={props.disabled}
          aria-label={props.ariaLabel}
          onClick={() => toggle(true)}
        >
          {props.label}
        </button>
      </>
    );

  return (
    <div role="group" aria-label={props.question} className="flex basis-full flex-wrap items-center gap-2">
      <p className="basis-full text-sm text-ink">{props.question}</p>
      <button type="button" className={button("destructive", "sm")} disabled={props.busy} onClick={props.onConfirm}>
        {props.busy ? <><Spinner /> {props.busyLabel}</> : props.confirmLabel}
      </button>
      <button ref={keepRef} type="button" className={button("ghost", "sm")} disabled={props.busy} onClick={() => toggle(false)}>
        Keep
      </button>
    </div>
  );
}

function RequestRow({ request: r, onCancel }: { request: LeaveRequest; onCancel: (id: number) => Promise<unknown> }) {
  const { busy, error, run } = useAction();
  const cancel = () => run("cancel", () => onCancel(r.id));
  return (
    <li className="flex flex-col gap-1 py-3 first:pt-0 last:pb-0">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium">
          <span className="tabular-nums">#{r.id}</span> {LEAVE_LABEL[r.leave_type]}
        </span>
        <StatusBadge status={r.status} />
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs text-muted tabular-nums">
          {formatRange(r.start_date, r.end_date)} · {plural(r.days, "day")}
        </span>
        {/* A draft is one click to discard (the assistant can draft it again); a submitted request asks first. */}
        {r.status === "draft" && (
          <button
            type="button"
            className={button("secondary", "sm")}
            disabled={busy !== null}
            onClick={cancel}
            aria-label={`Discard draft #${r.id}`}
          >
            {busy ? <><Spinner /> Discarding…</> : "Discard"}
          </button>
        )}
        {r.status === "pending" && (
          <ConfirmAction
            label="Cancel"
            ariaLabel={`Cancel request #${r.id}`}
            question={`Cancel request #${r.id}?`}
            confirmLabel="Cancel request"
            busyLabel="Cancelling…"
            busy={busy !== null}
            disabled={busy !== null}
            onConfirm={cancel}
          />
        )}
      </div>
      {error && (
        <p role="alert" className="text-xs text-danger">
          {error}
        </p>
      )}
    </li>
  );
}

function TeamRow({ request: r, onDecide }: { request: TeamRequest; onDecide: Decide }) {
  const { busy, error, run } = useAction();
  const firstName = r.employee_name.split(" ")[0];
  return (
    <li className="flex flex-col gap-1 py-3 first:pt-0 last:pb-0">
      <div className="flex items-center justify-between gap-2">
        <span className="min-w-0 break-words text-sm font-medium">{r.employee_name}</span>
        <span className="text-xs text-muted tabular-nums">#{r.id}</span>
      </div>
      <p className="text-xs text-muted tabular-nums">
        {LEAVE_LABEL[r.leave_type]} · {formatRange(r.start_date, r.end_date)} · {plural(r.days, "day")}
      </p>
      {r.reason && <p className="break-words text-xs text-ink">“{r.reason}”</p>}
      {/* Approve is secondary, not filled: a list of filled buttons would be louder than the data. */}
      <div className="mt-1 flex flex-wrap items-center gap-2">
        <ConfirmAction
          label="Reject"
          ariaLabel={`Reject ${r.employee_name}'s request #${r.id}`}
          question={`Reject ${firstName}'s request?`}
          confirmLabel="Reject request"
          busyLabel="Rejecting…"
          busy={busy === "reject"}
          disabled={busy !== null}
          onConfirm={() => run("reject", () => onDecide(r.id, "reject"))}
        >
          <button
            type="button"
            className={button("secondary", "sm")}
            disabled={busy !== null}
            onClick={() => run("approve", () => onDecide(r.id, "approve"))}
            aria-label={`Approve ${r.employee_name}'s request #${r.id}`}
          >
            {busy === "approve" ? <><Spinner /> Approving…</> : "Approve"}
          </button>
        </ConfirmAction>
      </div>
      {error && (
        <p role="alert" className="text-xs text-danger">
          {error}
        </p>
      )}
    </li>
  );
}
