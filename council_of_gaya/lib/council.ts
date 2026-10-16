export type CouncilSeatId = "logos" | "bob" | "freya" | "tvashtar";

export interface CouncilSeat {
  id: CouncilSeatId;
  codename: string;
  role: string;
  angleDeg: number; // position on inner orbit, 0 = 12 o'clock, clockwise
  domain: string[]; // skill category slugs this seat owns
  avatarIcon: string;
}

export const COUNCIL: CouncilSeat[] = [
  {
    id: "logos",
    codename: "LOGOS",
    role: "Mind // Mastermind Planner & Hard-Check Gate",
    angleDeg: 0,
    domain: ["qc", "planning", "review", "testing", "security", "evals"],
    avatarIcon: "🛡️"
  },
  {
    id: "bob",
    codename: "Bob",
    role: "Hands // Precision Builder & Execution Engine",
    angleDeg: 90,
    domain: ["build", "dev", "deploy", "backend", "data", "infra"],
    avatarIcon: "🔨"
  },
  {
    id: "freya",
    codename: "Freya",
    role: "Heart // Polymath Designer & Visual Seer",
    angleDeg: 180,
    domain: ["design", "brand", "content", "social", "creative", "ui-ux"],
    avatarIcon: "✨"
  },
  {
    id: "tvashtar",
    codename: "Tvashtar",
    role: "Craftsman // Systems Architect & Toolkeeper",
    angleDeg: 270,
    domain: ["tools", "gis", "xr", "visionos", "specialty", "mcp"],
    avatarIcon: "⚙️"
  }
];
