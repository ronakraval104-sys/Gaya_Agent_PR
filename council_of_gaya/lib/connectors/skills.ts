import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";

export interface SkillItem {
  id: string;
  name: string;
  description: string;
  isBuiltin: boolean;
  category: string;
}

export interface SkillsStatus {
  status: "ok" | "err" | "off";
  totalSkills: number;
  configSkills: number;
  builtinSkills: number;
  categories: Record<string, number>;
  skills: SkillItem[];
  fetchedAt: number;
  error?: string;
}

const CONFIG_SKILLS_DIR = path.join(os.homedir(), ".gemini", "config", "skills");
const BUILTIN_SKILLS_DIR = path.join(os.homedir(), ".gemini", "antigravity", "builtin", "skills");
const CACHE_TTL_MS = 20_000;

let cachedSkills: { at: number; value: SkillsStatus } | null = null;

function inferCategory(id: string, desc: string): string {
  const hay = `${id} ${desc}`.toLowerCase();
  if (hay.includes("3d") || hay.includes("unreal") || hay.includes("gis") || hay.includes("spatial") || hay.includes("visionos") || hay.includes("xr") || hay.includes("mesh")) {
    return "3D & Spatial";
  }
  if (hay.includes("agent") || hay.includes("subagent") || hay.includes("plan") || hay.includes("omni") || hay.includes("edidth") || hay.includes("veronica") || hay.includes("gaya")) {
    return "Agentic Core";
  }
  if (hay.includes("design") || hay.includes("ui") || hay.includes("ux") || hay.includes("frontend") || hay.includes("brand") || hay.includes("video") || hay.includes("friday")) {
    return "Creative & Design";
  }
  if (hay.includes("security") || hay.includes("hack") || hay.includes("test") || hay.includes("audit") || hay.includes("deploy") || hay.includes("codebase")) {
    return "DevOps & Security";
  }
  return "General Specialist";
}

async function scanDirectory(dir: string, isBuiltin: boolean): Promise<SkillItem[]> {
  const items: SkillItem[] = [];
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillMd = path.join(dir, entry.name, "SKILL.md");
      let desc = "";
      try {
        const content = await fs.readFile(skillMd, "utf-8");
        const lines = content.split("\n");
        for (const line of lines) {
          if (line.toLowerCase().startsWith("description:")) {
            desc = line.replace(/description:\s*/i, "").trim().replace(/^["']|["']$/g, "");
            break;
          }
        }
      } catch {}
      items.push({
        id: entry.name,
        name: entry.name.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        description: desc,
        isBuiltin,
        category: inferCategory(entry.name, desc)
      });
    }
  } catch {}
  return items;
}

export async function getSkillsStatus(): Promise<SkillsStatus> {
  if (cachedSkills && Date.now() - cachedSkills.at < CACHE_TTL_MS) {
    return cachedSkills.value;
  }

  try {
    const [configItems, builtinItems] = await Promise.all([
      scanDirectory(CONFIG_SKILLS_DIR, false),
      scanDirectory(BUILTIN_SKILLS_DIR, true)
    ]);

    const all = [...configItems, ...builtinItems];
    const categories: Record<string, number> = {};
    for (const item of all) {
      categories[item.category] = (categories[item.category] || 0) + 1;
    }

    const result: SkillsStatus = {
      status: "ok",
      totalSkills: all.length,
      configSkills: configItems.length,
      builtinSkills: builtinItems.length,
      categories,
      skills: all,
      fetchedAt: Date.now()
    };

    cachedSkills = { at: Date.now(), value: result };
    return result;
  } catch (err: any) {
    return {
      status: "err",
      totalSkills: 0,
      configSkills: 0,
      builtinSkills: 0,
      categories: {},
      skills: [],
      fetchedAt: Date.now(),
      error: err.message
    };
  }
}
