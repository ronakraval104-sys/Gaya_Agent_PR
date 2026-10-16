export type PersonaId = "gaya-core";

export interface PersonaConfig {
  id: PersonaId;
  displayName: string;
  codename: string;
  tagline: string;
  primary: string;
  lift: string;
  deep: string;
  accent: string;
}

export const PERSONAS: Record<string, PersonaConfig> = {
  "gaya-core": {
    id: "gaya-core",
    displayName: "Gaya Core",
    codename: "GAYA // BODHI VANGUARD",
    tagline: "Divine Commander // Evergrowth",
    primary: "#D4AF37",
    lift: "#FFD73C",
    deep: "#0B090A",
    accent: "#FFF2A8"
  }
};

export const DEFAULT_PERSONA: PersonaId = "gaya-core";
