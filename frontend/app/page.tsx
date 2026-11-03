"use client";

// The whole portal is one client page: it owns the signed-in user, the chat transcript and the
// sidebar data, and passes callbacks down to small presentational components.

import { useEffect, useState } from "react";
import { ApiError, api, type Employee, type Health } from "@/lib/api";
import { plural } from "@/lib/format";
import { FALLBACK_ERROR } from "@/lib/useAction";
import { Chat, type ChatMessage } from "@/components/Chat";
import { Header } from "@/components/Header";
import { Sidebar, type SidebarData } from "@/components/Sidebar";
import { button, card, focus } from "@/components/ui";

const USER_KEY = "acme-hr:user";

async function fetchSidebar(me: Employee): Promise<SidebarData> {
  const [balances, requests, team] = await Promise.all([
    api.balance(me.id),
    api.myRequests(me.id),
    me.role === "manager" ? api.teamRequests(me.id) : null,
  ]);
  return { balances, requests, team };
}

// localStorage can throw (private mode, blocked storage); the demo works fine without it.
function savedUser(): string | null {
  try {
    return localStorage.getItem(USER_KEY);
  } catch {
    return null;
  }
}
function saveUser(id: string) {
  try {
    localStorage.setItem(USER_KEY, id);
  } catch {}
}

const message = (e: unknown) => (e instanceof Error ? e.message : FALLBACK_ERROR);

// Copy = what failed + what to do next.
const chatError = (e: unknown) =>
  e instanceof ApiError && e.status === 0
    ? "Couldn't reach the assistant. Check your connection, then try again."
    : message(e);

export default function Home() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [userId, setUserId] = useState("");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [sidebar, setSidebar] = useState<SidebarData | null>(null); // null = loading, not empty
  const [sidebarError, setSidebarError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string>();
  const [sending, setSending] = useState(false);

  const me = employees.find((e) => e.id === userId);

  // On first load: who can sign in, and which model the backend runs.
  useEffect(() => {
    Promise.all([api.employees(), api.health()])
      .then(([emps, h]) => {
        setEmployees(emps);
        setHealth(h);
        const saved = savedUser();
        setUserId(emps.some((e) => e.id === saved) ? saved! : (emps[0]?.id ?? ""));
      })
      .catch(() => setLoadError("Couldn't reach the HR service. Check that the backend is running, then reload."));
  }, []);

  // Whenever the user changes, load their sidebar. `stale` drops a response that arrives after
  // the user has already switched again.
  useEffect(() => {
    if (!me) return;
    let stale = false;
    fetchSidebar(me)
      .then((data) => !stale && setSidebar(data))
      .catch((e) => !stale && setSidebarError(message(e)));
    return () => {
      stale = true;
    };
  }, [me]);

  const refresh = () =>
    me &&
    fetchSidebar(me)
      .then((data) => {
        setSidebar(data);
        setSidebarError(null);
      })
      .catch((e) => setSidebarError(message(e)));

  function switchUser(id: string) {
    if (id === userId) return;
    saveUser(id);
    setUserId(id);
    setMessages([]);
    setConversationId(undefined);
    setSidebar(null);
    setSidebarError(null);
  }

  // `retry` resends after an error: it replaces the error message instead of adding a new bubble.
  async function send(text: string, retry = false) {
    if (!me || sending) return;
    setMessages((m) => (retry ? m.slice(0, -1) : [...m, { role: "user", text }]));
    setSending(true);
    try {
      const turn = await api.chat(me.id, text, conversationId);
      setConversationId(turn.conversation_id);
      setMessages((m) => [...m, { role: "assistant", turn }]);
      if (turn.drafts.length > 0) await refresh(); // new drafts appear under "My requests"
    } catch (e) {
      setMessages((m) => [...m, { role: "error", text: chatError(e), prompt: text }]);
    } finally {
      setSending(false);
    }
  }

  // Actions throw on failure so the button that triggered them can show the error next to itself.
  const confirm = async (id: number) => {
    await api.confirm(userId, id);
    await refresh();
  };
  const cancel = async (id: number) => {
    await api.cancel(userId, id);
    await refresh();
  };
  const decide = async (id: number, decision: "approve" | "reject") => {
    await api.decide(userId, id, decision);
    await refresh();
  };

  const waiting = sidebar?.team?.length ?? 0;

  return (
    <div className="flex min-h-dvh flex-col lg:h-dvh">
      <Header
        employees={employees}
        userId={userId}
        onUserChange={switchUser}
        demoMode={health?.llm === "FakeLLM"}
        disabled={sending}
      />
      {loadError && (
        <div role="alert" className="border-b border-danger-border bg-danger-bg text-sm text-danger">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-2 lg:px-6">
            <p>{loadError}</p>
            <button type="button" className={button("ghost", "sm")} onClick={() => location.reload()}>
              Reload
            </button>
          </div>
        </div>
      )}
      <main
        className="mx-auto grid w-full max-w-7xl flex-1 grid-cols-1 gap-4 p-4 lg:min-h-0 lg:grid-cols-[minmax(0,1fr)_22rem] lg:gap-6 lg:p-6"
      >
        {/* On a phone the sidebar sits below the chat, so a manager gets a pointer to the approvals. */}
        {waiting > 0 && (
          <a
            href="#team-approvals"
            className={`${card} flex items-center justify-between gap-2 px-4 py-3 text-sm lg:hidden ${focus}`}
          >
            <span className="tabular-nums">{plural(waiting, "request")} waiting for your approval</span>
            <span className="font-medium text-accent-ink underline underline-offset-2">Review</span>
          </a>
        )}
        <Chat
          messages={messages}
          sending={sending}
          onSend={send}
          onRetry={(prompt) => send(prompt, true)}
          requests={sidebar?.requests ?? []}
          onConfirm={confirm}
          onDiscard={cancel}
        />
        <div className="lg:min-h-0 lg:overflow-y-auto">
          <Sidebar
            data={sidebar}
            isManager={me?.role === "manager"}
            error={sidebarError}
            onRetry={refresh}
            onCancel={cancel}
            onDecide={decide}
          />
        </div>
      </main>
    </div>
  );
}
