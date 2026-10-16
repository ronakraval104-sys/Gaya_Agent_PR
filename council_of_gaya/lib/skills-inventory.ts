import type { CouncilSeatId } from "./council";

export interface SkillDef {
  slug: string;
  label: string;
  domain: string;
  ownerSeat: CouncilSeatId;
  tier: "always-on" | "tvashtar-pool";
}

/**
 * Seed of skills mapped to Gaya's 4 specialist council seats.
 */
export const SKILLS: SkillDef[] = [
  // ─── DESIGN & AESTHETICS (FREYA) ───
  { slug: "brand-identity",           label: "Brand Identity",           domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "logo-design",              label: "Logo Design",              domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "friday-designer",          label: "Designer Voice",           domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "frontend-design",          label: "Frontend Design",          domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "content-creator",          label: "Content Creator",          domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "social-media-strategist",  label: "Social Strategist",        domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "linkedin-content-creator", label: "LinkedIn Content",         domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "instagram-curator",        label: "Instagram Curator",        domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "technical-writer",         label: "Technical Writer",         domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "prompt-engineer",          label: "Prompt Engineer",          domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "hyperframes-video",        label: "HyperFrames Video",        domain: "design",   ownerSeat: "freya",    tier: "always-on" },
  { slug: "curved-led-wall",          label: "Curved LED Wall",          domain: "design",   ownerSeat: "freya",    tier: "always-on" },

  // ─── BUILD & PRECISION EXECUTION (BOB) ───
  { slug: "veronica-builder",         label: "Builder Voice",            domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "deploy-ops",               label: "Deploy Ops",               domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "agent-engineering",        label: "Agent Engineering",        domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "building-ui-bundle-frontend", label: "UI Bundle Frontend",    domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "improve-codebase-architecture", label: "Architecture Refactor", domain: "build", ownerSeat: "bob",      tier: "always-on" },
  { slug: "test-driven-development",  label: "TDD Engine",               domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "systematic-debugging",     label: "Systematic Debugging",     domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "subagent-driven-development", label: "Subagent Development",  domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "executing-plans",          label: "Plan Execution",           domain: "build",    ownerSeat: "bob",      tier: "always-on" },
  { slug: "using-git-worktrees",      label: "Git Worktrees",            domain: "build",    ownerSeat: "bob",      tier: "always-on" },

  // ─── HARD-CHECK QC & PLANNING (LOGOS) ───
  { slug: "edidth-planner-qc",        label: "Planner & QC Gate",        domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "grill-me",                 label: "Decision Griller",         domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "writing-plans",            label: "Plan Architect",           domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "requesting-code-review",   label: "Code Review Gate",         domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "receiving-code-review",    label: "Review Verification",      domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "verification-before-completion", label: "Pre-Completion Audit", domain: "qc",    ownerSeat: "logos",    tier: "always-on" },
  { slug: "ethical-hacking",          label: "Ethical Hacking Audit",    domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "testing-reality-checker",  label: "Reality Checker",          domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "testing-evidence-collector",label:"Evidence Collector",       domain: "qc",       ownerSeat: "logos",    tier: "always-on" },
  { slug: "project-manager-senior",   label: "Senior PM",                domain: "qc",       ownerSeat: "logos",    tier: "always-on" },

  // ─── SYSTEMS & TOOLKEEPER POOL (TVASHTAR) ───
  { slug: "dum-e-toolkeeper",         label: "Toolkeeper Arsenal",       domain: "tools",    ownerSeat: "tvashtar", tier: "always-on" },
  { slug: "3d-visualizer",            label: "3D Visualizer",            domain: "tools",    ownerSeat: "tvashtar", tier: "always-on" },
  { slug: "comfyui-workflow-builder", label: "ComfyUI Workflow",         domain: "tools",    ownerSeat: "tvashtar", tier: "always-on" },
  { slug: "digital-twin-generation",  label: "Digital Twin Clone",       domain: "tools",    ownerSeat: "tvashtar", tier: "always-on" },
  { slug: "visual-scripting-wizardry",label: "Visual Scripting / n8n",   domain: "tools",    ownerSeat: "tvashtar", tier: "always-on" },
  { slug: "gis-bim-specialist",       label: "GIS/BIM Integration",      domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "gis-3d-scene-developer",   label: "GIS 3D Scene Dev",         domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "gis-cartography-designer", label: "Cartography Design",       domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "security-appsec-engineer", label: "AppSec Engineer",          domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "security-cloud-security-architect", label: "Cloud Security Arch", domain: "specialty", ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "security-incident-responder", label: "Incident Responder",    domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "visionos-spatial-engineer",label: "visionOS Spatial Dev",     domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "xr-immersive-developer",   label: "XR Immersive Dev",         domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "testing-tool-evaluator",   label: "Tool Evaluator",           domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" },
  { slug: "procedural-3d-modeling",   label: "Procedural 3D Modeling",   domain: "specialty",ownerSeat: "tvashtar", tier: "tvashtar-pool" }
];

export const ALWAYS_ON = SKILLS.filter(s => s.tier === "always-on");
export const TVASHTAR_POOL = SKILLS.filter(s => s.tier === "tvashtar-pool");
export const DUM_E_POOL = TVASHTAR_POOL; // compatibility alias
