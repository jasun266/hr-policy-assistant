import type { Citation, LeaveRequest, ToolStep } from "@/lib/api";
import { plural } from "@/lib/format";
import { DraftCard } from "./DraftCard";
import { Chevron } from "./icons";
import { focus } from "./ui";

interface Props {
  text: string;
  citations: Citation[];
  steps: ToolStep[];
  drafts: LeaveRequest[];
  onConfirm: (id: number) => Promise<unknown>;
  onDiscard: (id: number) => Promise<unknown>;
}

// No bubble: a policy answer reads like a document. Then its sources, any draft, and the trace.
export function AssistantMessage({ text, citations, steps, drafts, onConfirm, onDiscard }: Props) {
  return (
    <div className="flex max-w-[68ch] flex-col gap-2">
      <p className="whitespace-pre-wrap break-words text-pretty text-base leading-relaxed">
        <span className="sr-only">Assistant: </span>
        {text}
      </p>

      {/* Static references, not buttons: there is no policy document to open yet. */}
      {citations.length > 0 && (
        <ul aria-label="Sources" className="flex flex-wrap gap-1.5">
          {citations.map((c) => (
            <li
              key={`${c.document}/${c.section}`}
              className="whitespace-nowrap rounded-tag bg-accent-subtle px-2 py-0.5 text-xs font-medium text-accent-ink"
            >
              {c.document} › {c.section}
            </li>
          ))}
        </ul>
      )}

      {drafts.map((d) => (
        <DraftCard key={d.id} request={d} onConfirm={onConfirm} onDiscard={onDiscard} />
      ))}

      {steps.length > 0 && <StepsTrace steps={steps} />}
    </div>
  );
}

// "How I got this": every tool call the agent made this turn, with its input and (truncated) result.
function StepsTrace({ steps }: { steps: ToolStep[] }) {
  return (
    <details className="group text-xs">
      <summary
        className={`inline-flex cursor-pointer select-none list-none items-center gap-1 rounded-tag py-1 font-medium text-muted transition-colors hover:text-ink [&::-webkit-details-marker]:hidden ${focus}`}
      >
        <Chevron />
        How I got this · {plural(steps.length, "tool call")}
      </summary>
      <ol className="mt-2 space-y-2 border-l border-border pl-3">
        {steps.map((s, i) => (
          <li key={i} className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span className="tabular-nums text-muted">{i + 1}.</span>
              <code translate="no" className="font-mono text-ink">
                {s.tool}
              </code>
              <span
                className={`rounded-tag px-1.5 font-medium ${s.is_error ? "bg-rejected-bg text-rejected-ink" : "bg-cancelled-bg text-cancelled-ink"}`}
              >
                {s.is_error ? "error" : "ok"}
              </span>
            </div>
            <span className="sr-only">Input</span>
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-all rounded-tag bg-raised p-2 font-mono text-ink">
              {JSON.stringify(s.input, null, 2)}
            </pre>
            <span className="sr-only">Result</span>
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-words rounded-tag bg-raised p-2 font-mono text-muted">
              {s.output}
            </pre>
          </li>
        ))}
      </ol>
    </details>
  );
}
