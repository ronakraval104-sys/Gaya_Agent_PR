import type { Config } from "tailwindcss";

/**
 * MONOLITH SIGNAL tokens — mirrored from CSS vars in globals.css.
 * Change one, change both.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      screens: {
        wide: "1800px",
        ultra: "2200px"
      },
      colors: {
        os: {
          bg: "var(--bg)",
          bg2: "var(--bg-2)",
          surface: "var(--surface)",
          surface2: "var(--surface-2)",
          surface3: "var(--surface-3)",
          border: "var(--border)",
          "border-strong": "var(--border-strong)",
          hairline: "var(--hairline)",
          text: "var(--text)",
          muted: "var(--text-2)",
          dim: "var(--text-3)",
          accent: "var(--accent)",
          accent2: "var(--accent-2)",
          ink: "var(--accent-ink)",
          ok: "var(--ok)",
          warn: "var(--warn)",
          err: "var(--err)"
        },
        // Legacy tokens kept for un-migrated components — resolve to Monolith values
        void: { 0: "#0a0a0a", 100: "#141414", 200: "#1c1c1c" },
        arc: { teal: "#f2f2f2", "teal-glow": "#f2f2f2" },
        stark: { orange: "#ff2d3f", "orange-hot": "#ffb000" },
        vr: { primary: "#f2f2f2", lift: "#f2f2f2", deep: "#0a0a0a", metal: "#9c9c9c" },
        kv: { magenta: "#ff2d3f", violet: "#f2f2f2", cyan: "#f2f2f2", yellow: "#ffb000" }
      },
      fontFamily: {
        // Monolith: mono everywhere
        sans: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
        // Inter kept as escape hatch for record body copy
        body: ["'Inter'", "system-ui", "sans-serif"],
        // legacy tokens map to mono
        display: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        watermark: ["'JetBrains Mono'", "ui-monospace", "monospace"]
      },
      fontSize: {
        "hud-xs": ["10px", { lineHeight: "14px", letterSpacing: "0.14em" }],
        "hud-sm": ["11px", { lineHeight: "16px", letterSpacing: "0.14em" }]
      },
      borderRadius: {
        none: "0",
        DEFAULT: "0",
        sm: "0",
        md: "0",
        lg: "0",
        xl: "0",
        full: "9999px"
      },
      animation: {
        "led-blink": "led-blink 2.6s steps(1) infinite"
      },
      keyframes: {
        "led-blink": {
          "0%,70%,100%": { opacity: "1" },
          "85%": { opacity: "0.25" }
        }
      }
    }
  },
  plugins: []
};

export default config;
