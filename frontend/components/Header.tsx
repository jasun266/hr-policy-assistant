import type { Employee, Role } from "@/lib/api";
import { Mark } from "./icons";
import { focus } from "./ui";

const ROLE_LABEL: Record<Role, string> = { employee: "Employee", manager: "Manager" };

interface Props {
  employees: Employee[];
  userId: string;
  onUserChange: (id: string) => void;
  demoMode: boolean;
  disabled: boolean;
}

// Below 640px: row 1 = mark, name and switcher; row 2 = the demo notice.
export function Header({ employees, userId, onUserChange, demoMode, disabled }: Props) {
  return (
    <header className="border-b border-border bg-surface">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 lg:px-6">
        <div className="flex items-center gap-2">
          <Mark />
          <h1 translate="no" className="text-base font-semibold">
            Acme HR Assistant
          </h1>
        </div>
        {demoMode && (
          <p className="max-sm:order-last max-sm:basis-full">
            <span
              className="rounded-tag bg-raised px-1.5 py-0.5 text-xs font-medium text-muted"
              title="No API key configured: replies come from a scripted stand-in model that uses the same tools."
            >
              Demo mode: scripted replies
            </span>
            {/* A tooltip alone never reaches touch or screen-reader users. */}
            <span className="sr-only">
              . No API key is configured, so replies come from a scripted stand-in model that uses the same tools.
            </span>
          </p>
        )}
        <div className="flex min-w-0 flex-1 items-center justify-end gap-2">
          <label htmlFor="user-switcher" className="sr-only text-sm text-muted sm:not-sr-only">
            Signed in as
          </label>
          <select
            id="user-switcher"
            value={userId}
            onChange={(e) => onUserChange(e.target.value)}
            disabled={disabled || employees.length === 0}
            title={disabled ? "Wait for the reply to finish" : undefined}
            className={`h-9 min-w-0 flex-1 rounded-control border border-control bg-surface px-2 text-base text-ink pointer-coarse:h-11 disabled:bg-raised disabled:text-muted sm:max-w-64 sm:text-sm ${focus}`}
          >
            {employees.map((e) => (
              <option key={e.id} value={e.id}>
                {e.name} · {ROLE_LABEL[e.role]}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
}
