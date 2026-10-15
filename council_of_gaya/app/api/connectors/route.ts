import { NextResponse } from "next/server";
import { getAllConnectors } from "@/lib/connectors/all";

/**
 * Unified connector status endpoint. One round-trip returns the whole grid.
 * Callers poll this on a 60s cadence.
 */
export async function GET() {
  const connectors = await getAllConnectors();
  return NextResponse.json({ ok: true, connectors });
}
