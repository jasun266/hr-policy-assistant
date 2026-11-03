// The app's only icons, drawn by hand (no icon library). All are decorative: the text next to
// them carries the meaning, so they are aria-hidden.

// Product mark: an "A" in the accent square. Same artwork as app/icon.svg, but token-coloured so
// it follows dark mode.
export function Mark() {
  return (
    <svg aria-hidden viewBox="0 0 32 32" className="size-6 flex-none">
      <rect width="32" height="32" rx="6" className="fill-accent" />
      <path
        d="M9.5 24 16 8l6.5 16M12 18h8"
        fill="none"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="stroke-on-accent"
      />
    </svg>
  );
}

// 12px disclosure chevron; rotates when its <details> is open.
export function Chevron() {
  return (
    <svg
      aria-hidden
      viewBox="0 0 12 12"
      className="size-3 flex-none group-open:rotate-90 motion-safe:transition-transform motion-safe:duration-150 motion-safe:ease-[cubic-bezier(.22,1,.36,1)]"
    >
      <path d="m4.5 2.5 3.5 3.5-3.5 3.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

// 14px busy spinner. It stops under reduced motion; the "…ing" label still says what's happening.
export function Spinner() {
  return (
    <svg aria-hidden viewBox="0 0 14 14" className="size-3.5 flex-none motion-safe:animate-spin">
      <circle cx="7" cy="7" r="6" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.25" />
      <path d="M7 1a6 6 0 0 1 6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
