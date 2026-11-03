import type { LeaveType } from "./api";

export const LEAVE_LABEL: Record<LeaveType, string> = {
  annual: "Annual leave",
  sick: "Sick leave",
  casual: "Casual leave",
};

// Dates from the API are plain calendar days, so format them in UTC to avoid timezone shifts.
const dateFmt = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });

// "15–17 Nov 2026", "30 Nov – 2 Dec 2026", or one date when start === end.
export const formatRange = (start: string, end: string) => dateFmt.formatRange(new Date(start), new Date(end));

export const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
