import { NextResponse } from "next/server";
import { get } from "@/lib/knowledge/repo";

export async function GET(_req: Request, { params }: { params: { slug: string } }) {
  const r = await get(params.slug);
  if (!r) return NextResponse.json({ ok: false, error: "not_found" }, { status: 404 });
  return NextResponse.json({ ok: true, record: r });
}
