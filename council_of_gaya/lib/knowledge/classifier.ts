import type { PersonaScope, Priority, MemoryType, KnowledgeRecord } from "./types";
import type { CouncilSeatId } from "../council";

const VR_KEYWORDS = [
  "vr", "visual-rhyme", "visualrhyme", "microtronix", "led", "quote", "quote-pqm",
  "dealer", "pixel-quote", "leynna", "reyansh", "cabinet", "module", "warranty",
  "gst", "sqft", "solidtwin", "gopi", "harit", "cantex", "hexa", "panther",
  "raj-appliances", "dd-enterprise", "power-calc", "storm", "laxcon", "ia-dishank",
  "bdm-comp", "bdm", "brochure", "brand-pricing", "lamp", "gkgd", "truehue",
  "curved-led", "led-wall", "led-saas", "pqm", "pi-po", "po-vs-pi",
  "growel", "bella-aroma", "bansal", "green-palazzo", "vr-content", "vr-hiring",
  "arha", "docs-workspace", "quote-generation", "state-cabinet", "true-area",
  "virtual-pixel", "warranty-by-series", "microtronix-gstin", "kathan"
];

const GAYA_AI_KEYWORDS = [
  "gaya-core", "prism-noir", "gaya-empire", "nexur", "nexurscale", "nexurmedia",
  "foxtale", "green-palazzo-cafe"
];

const BOULDER_MARKERS = ["🚨", "BOULDER RULE", "BOULDER", "never guess", "NEVER GUESS"];

/**
 * Guess persona scope from slug + description text.
 * Default = "shared" when nothing matches (workflow rules, GAYA internals, etc.).
 */
export function classifyPersona(slug: string, description: string, body: string): PersonaScope {
  const hay = `${slug} ${description} ${body.slice(0, 400)}`.toLowerCase();
  const hasGaya = GAYA_AI_KEYWORDS.some((k) => hay.includes(k));
  const hasVr = VR_KEYWORDS.some((k) => hay.includes(k));
  if (hasGaya && !hasVr) return "gaya-core";
  if (hasVr && !hasGaya) return "visual-rhyme";
  if (hasVr && hasGaya) return "shared";
  return "shared";
}

export function classifyPriority(slug: string, description: string, body: string): Priority {
  const hay = `${slug} ${description} ${body.slice(0, 500)}`;
  if (BOULDER_MARKERS.some((m) => hay.includes(m))) return "boulder";
  if (/\bnever\b/i.test(hay) && /\brule\b/i.test(hay)) return "high";
  if (hay.startsWith("🚫") || hay.startsWith("🚨")) return "high";
  return "normal";
}

export function classifyType(
  fmType: string | undefined,
  slugPrefix: string
): MemoryType {
  const t = (fmType ?? slugPrefix).toLowerCase();
  if (t.startsWith("user")) return "user";
  if (t.startsWith("feedback")) return "feedback";
  if (t.startsWith("project")) return "project";
  if (t.startsWith("reference")) return "reference";
  if (t.startsWith("decision")) return "decision";
  if (t.startsWith("win")) return "win";
  if (t.startsWith("gotcha")) return "gotcha";
  if (t.startsWith("law")) return "law";
  if (t.startsWith("thread")) return "thread";
  return "unknown";
}

/**
 * Derive tags from slug + type + content signals.
 */
export function extractTags(slug: string, type: MemoryType, body: string): string[] {
  const tags = new Set<string>();
  tags.add(type);

  const bodyLower = body.toLowerCase();

  // domain tags
  if (/\bgstin\b/i.test(body)) tags.add("compliance");
  if (/\bpricing\b|\brate\b|\bmrp\b/i.test(body)) tags.add("pricing");
  if (/\bquote\b|\bpo\b|\bpi\b/i.test(body)) tags.add("quote");
  if (/\bdesign\b|\blogo\b|\bbrand\b/i.test(body)) tags.add("design");
  if (/\bgithub\b|\bvercel\b|\bdeploy\b/i.test(body)) tags.add("infra");
  if (/\bmemory\b|\bcharter\b|\bgaya\b|\bcouncil\b/i.test(bodyLower)) tags.add("gaya");
  if (/led|display|pixel|cabinet/i.test(body)) tags.add("led");
  if (/\bhiring\b|\bbdm\b|\bemployee\b|\bsalary\b/i.test(body)) tags.add("hr");

  // slug-based
  const slugParts = slug.split("-");
  for (const p of slugParts) {
    if (p.length > 4 && !["visual", "rhyme", "project", "feedback"].includes(p)) {
      tags.add(p);
    }
  }

  return [...tags];
}

/**
 * Map a KnowledgeRecord to the council seat most responsible for it.
 * Used to power click-a-seat filtering on the radial graph.
 * Precedence: explicit tag/type match → keyword scan of description+slug → "shared".
 */
export function classifySeat(record: KnowledgeRecord): CouncilSeatId | "shared" {
  const hay = `${record.slug} ${record.description} ${record.tags.join(" ")}`.toLowerCase();
  const type = record.type;

  // LOGOS: laws, decisions, gotchas, QC/planning/security/hard-check gate
  if (type === "law" || type === "decision" || type === "gotcha") return "logos";
  if (/\b(qc|planning|review|risk|security|verify|test|audit|compliance|evals)\b/.test(hay)) return "logos";

  // FREYA: design, brand, content, social, creative, UI/UX, visual truth
  if (/\b(design|brand|logo|content|social|instagram|linkedin|creative|visual|palette|typography|deck|brochure|website|ui|ux)\b/.test(hay)) {
    return "freya";
  }

  // BOB: build, dev, infra, deploy, backend, data, precision builder
  if (/\b(build|dev|frontend|backend|fullstack|deploy|infra|database|api|architecture|refactor|migration|schema|repo|codebase|next\.?js|react|tdd)\b/.test(hay)) {
    return "bob";
  }

  // TVASHTAR: research, tools, specialty (GIS, XR, VisionOS, procedural 3D, toolkeeper)
  if (/\b(tool|research|gis|xr|vision|visionos|specialty|comfyui|hyperframes|image|video|fooocus|higgsfield|scrape|ingest|3d)\b/.test(hay)) {
    return "tvashtar";
  }

  // Wins default to shared
  if (type === "win" || type === "thread") return "shared";

  return "shared";
}

