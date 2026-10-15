import { NextResponse } from "next/server";
import { getPublicRepoStatus } from "@/lib/connectors/github";

/**
 * KV-persona connector: Katviz Empire GH repo status.
 *
 * Repo is pinned server-side (no user input flows through) — Arnie 34.
 * Public API only, no secrets, no auth surface — Arnie 1/2/3/5/13.
 * Cache TTL in connector (45s) rides on top of Next revalidate.
 */
const KATVIZ_EMPIRE_REPO = "katviZ/katviz-empire";

export async function GET() {
  const status = await getPublicRepoStatus(KATVIZ_EMPIRE_REPO);
  return NextResponse.json({ ok: true, repo: status });
}
