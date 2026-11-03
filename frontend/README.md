# Acme HR Assistant — frontend

Next.js (App Router) + Tailwind client for the FastAPI backend in `../backend`.

```bash
npm install
npm run dev            # http://localhost:3000
```

The API base URL comes from `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`). It is inlined at build time, so set it before `npm run build`.

| File | Role |
| --- | --- |
| `lib/api.ts` | Typed fetch wrapper and response types for every backend endpoint |
| `app/page.tsx` | The single client page: signed-in user, chat transcript, sidebar data |
| `components/Chat.tsx` | Message list, composer, suggested prompts |
| `components/AssistantMessage.tsx` | Reply with citation chips, draft cards and the "How I got this" tool trace |
| `components/DraftCard.tsx` | Confirm / discard a leave request the agent drafted |
| `components/Sidebar.tsx` | Leave balances, my requests, team approvals (managers) |
