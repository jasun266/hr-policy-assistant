import type { RequestStatus } from "@/lib/api";

// Pale tint + dark label of the same hue; the word itself is the non-colour signal.
const STYLES: Record<RequestStatus, string> = {
  draft: "bg-draft-bg text-draft-ink",
  pending: "bg-pending-bg text-pending-ink",
  approved: "bg-approved-bg text-approved-ink",
  rejected: "bg-rejected-bg text-rejected-ink",
  cancelled: "bg-cancelled-bg text-cancelled-ink",
};

const LABEL: Record<RequestStatus, string> = {
  draft: "Draft",
  pending: "Pending",
  approved: "Approved",
  rejected: "Rejected",
  cancelled: "Cancelled",
};

export function StatusBadge({ status }: { status: RequestStatus }) {
  return (
    <span
      className={`inline-flex h-5 flex-none items-center whitespace-nowrap rounded-tag px-1.5 text-xs font-medium ${STYLES[status]}`}
    >
      {LABEL[status]}
    </span>
  );
}
