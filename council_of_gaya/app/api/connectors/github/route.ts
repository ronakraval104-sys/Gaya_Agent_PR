import { NextResponse } from "next/server";
import { getPublicRepoStatus } from "@/lib/connectors/github";

/**
 * Gaya OS GitHub repository status connector.
 * Public API only, cached with TTL.
 */
const GAYA_AGENT_REPO = "ronakraval104-sys/Gaya_Agent_PR";

export async function GET() {
  const status = await getPublicRepoStatus(GAYA_AGENT_REPO);
  return NextResponse.json({ ok: true, repo: status });
}
