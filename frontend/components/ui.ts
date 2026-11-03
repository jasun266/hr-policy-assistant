// Shared Tailwind class strings so buttons and panels look the same everywhere (see DESIGN.md).
// Sizes live outside the base string because two conflicting utilities (h-8 and h-9) on one
// element don't resolve by class order in Tailwind.
export const focus = "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";

export const card = "rounded-panel border border-border bg-surface";

// Disabled states use tokens, never opacity, so the label stays readable (>= 4.5:1).
const VARIANT = {
  primary: "bg-accent text-on-accent enabled:hover:bg-accent-hover disabled:bg-raised disabled:text-muted",
  secondary: "border border-control bg-surface text-ink enabled:hover:bg-raised disabled:border-border disabled:text-muted",
  destructive:
    "border border-danger-border bg-surface text-danger enabled:hover:bg-danger-bg disabled:border-border disabled:text-muted",
  ghost: "text-muted enabled:hover:bg-raised enabled:hover:text-ink",
};

const SIZE = {
  md: "h-9 px-3",
  sm: "h-8 px-2.5",
  lg: "h-11 px-4", // the composer's Send, level with the 44px textarea
};

export function button(variant: keyof typeof VARIANT, size: keyof typeof SIZE = "md") {
  return `inline-flex flex-none items-center justify-center gap-1.5 whitespace-nowrap rounded-control text-sm font-medium transition-colors duration-150 pointer-coarse:h-11 disabled:cursor-not-allowed ${focus} ${VARIANT[variant]} ${SIZE[size]}`;
}

// Inline error box (chat log, draft card, sidebar panel). Rows use plain `text-xs text-danger`.
export const errorBox = "rounded-panel border border-danger-border bg-danger-bg px-3 py-2 text-sm text-danger";
