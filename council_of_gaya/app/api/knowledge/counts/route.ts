import { NextResponse } from "next/server";
import { counts } from "@/lib/knowledge/repo";

export async function GET() {
  const c = await counts();
  return NextResponse.json({ ok: true, ...c });
}
