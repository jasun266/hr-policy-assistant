import type { Metadata, Viewport } from "next";
import { focus } from "@/components/ui";
import "./globals.css";

export const metadata: Metadata = {
  title: "Acme HR Assistant",
  description:
    "Internal HR portal for Acme Corp: ask policy questions with cited answers, check leave balances, and confirm leave requests drafted by an AI agent.",
};

// Browser chrome matches the page canvas in each theme.
export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f6f7f5" },
    { media: "(prefers-color-scheme: dark)", color: "#0f1312" },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body className="bg-canvas font-sans text-ink antialiased">
        <a
          href="#chat-input"
          className={`sr-only rounded-control border border-control bg-surface px-3 py-2 text-sm font-medium focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-10 ${focus}`}
        >
          Skip to chat
        </a>
        {children}
      </body>
    </html>
  );
}
