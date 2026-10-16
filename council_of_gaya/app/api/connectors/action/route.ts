import { NextResponse } from "next/server";
import { sendMiniGayaNotification, setMiniGayaScale, setMiniGayaVolume } from "@/lib/connectors/mini-gaya";
import { getAllConnectors } from "@/lib/connectors/all";
import fs from "fs";
import path from "path";

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const action = body.action || "ping_gaya";

    if (action === "ping_gaya") {
      const msg = body.message || "Council of Gaya handshake received. Luminous & online, R0n!";
      const res = await sendMiniGayaNotification(msg);
      return NextResponse.json({ ok: res.ok, action, error: res.error });
    }

    if (action === "refresh") {
      const connectors = await getAllConnectors();
      return NextResponse.json({ ok: true, action, connectors });
    }

    if (action === "set_scale") {
      const scale = Math.max(0.5, Math.min(2.0, parseFloat(body.scale) || 1.0));
      const res = await setMiniGayaScale(scale);
      return NextResponse.json({ ok: res.ok, action, scale: res.scale ?? scale, error: res.error });
    }

    if (action === "set_volume") {
      const volume = Math.max(0, Math.min(100, parseInt(body.volume, 10) || 100));
      const res = await setMiniGayaVolume(volume);
      return NextResponse.json({ ok: res.ok, action, volume: res.volume ?? volume, error: res.error });
    }

    if (action === "set_voice") {
      const voiceName = body.voiceName || "Piper Neural (Amy - Ultra Natural)";
      const home = process.env.USERPROFILE || process.env.HOME || "";
      const voiceConfigPath = path.join(home, ".gaya", "voice", "voice_config.json");
      fs.mkdirSync(path.dirname(voiceConfigPath), { recursive: true });
      let currentCfg: any = { voice_name: voiceName, rate: 0, volume: 100 };
      if (fs.existsSync(voiceConfigPath)) {
        try { currentCfg = JSON.parse(fs.readFileSync(voiceConfigPath, "utf-8")); } catch {}
      }
      currentCfg.voice_name = voiceName;
      fs.writeFileSync(voiceConfigPath, JSON.stringify(currentCfg, null, 2), "utf-8");
      // Notify Mini Gaya of voice update
      await sendMiniGayaNotification(`Divine voice updated to ${voiceName}`);
      return NextResponse.json({ ok: true, action, voiceName });
    }

    return NextResponse.json({ ok: false, error: `Unknown action: ${action}` }, { status: 400 });
  } catch (err: any) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 500 });
  }
}
