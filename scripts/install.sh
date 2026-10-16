#!/usr/bin/env bash
# Universal Gaya Installer for macOS and Linux (Update 0.5.2610)
# Supports OpenCode, Claude Code, and OpenAI Codex

set -e

echo "=========================================================="
echo "  ⚔ Gaya Universal Installer : Update 0.5.2610"
echo "  The Seat of Awakening: OpenCode | Claude Code | Codex"
echo "=========================================================="

GAYA_DIR="$HOME/.gaya"
PROFILE_PATH="$GAYA_DIR/user_profile.json"
mkdir -p "$GAYA_DIR"

USER_NAME=""
USER_PREFIX=""

# 1. Check existing profile or older installation
if [ -f "$PROFILE_PATH" ]; then
    USER_PREFIX=$(python3 -c "import json; print(json.load(open('$PROFILE_PATH')).get('prefix', ''))" 2>/dev/null || true)
    USER_NAME=$(python3 -c "import json; print(json.load(open('$PROFILE_PATH')).get('name', ''))" 2>/dev/null || true)
    if [ -n "$USER_PREFIX" ]; then
        echo "[Upgrade Detected] Loaded user profile: Prefix='$USER_PREFIX', Name='$USER_NAME'"
    fi
fi

if [ -z "$USER_PREFIX" ]; then
    LEGACY_AGENTS="$HOME/.gemini/config/rules/AGENTS.md"
    if [ -f "$LEGACY_AGENTS" ]; then
        USER_PREFIX=$(grep -oE "Address the user as \*\*[^*]+\*\*" "$LEGACY_AGENTS" | sed -e 's/Address the user as \*\*//' -e 's/\*\*//' | head -n 1 || true)
        if [ -n "$USER_PREFIX" ]; then
            USER_NAME="$USER_PREFIX"
            echo "[Upgrade Detected] Fetched identity from existing rule: Prefix='$USER_PREFIX'"
        fi
    fi
fi

# Fresh install interactive prompt
if [ -z "$USER_PREFIX" ]; then
    echo ""
    echo "[Fresh Install] Personalize how Gaya addresses you:"
    read -p "Enter your name (e.g. Ronak / Alice) [default: Ronak]: " INPUT_NAME
    read -p "Enter address title or prefix (e.g. R0n / Ron / Commander) [default: R0n]: " INPUT_PREFIX
    USER_NAME="${INPUT_NAME:-Ronak}"
    USER_PREFIX="${INPUT_PREFIX:-R0n}"
fi

cat <<EOF > "$PROFILE_PATH"
{
  "name": "$USER_NAME",
  "prefix": "$USER_PREFIX"
}
EOF

echo "Profile saved to ~/.gaya/user_profile.json (Prefix='$USER_PREFIX', Name='$USER_NAME')"

# 2. OpenCode setup
OPENCODE_DIR="$HOME/.config/opencode"
mkdir -p "$OPENCODE_DIR/skills" "$OPENCODE_DIR/agents"
cp -r skills/* "$OPENCODE_DIR/skills/"
cp -r agents/* "$OPENCODE_DIR/agents/"
cp config/opencode.jsonc "$OPENCODE_DIR/opencode.jsonc"

# Update AGENTS.md with user identity
sed "s/- Address the user as \*\*.*\*\*/- Address the user as \*\*$USER_PREFIX\*\* (or $USER_NAME)/g" .opencode/AGENTS.md > "$OPENCODE_DIR/AGENTS.md"

echo ""
echo "=========================================================="
echo "  Gaya successfully installed!"
echo "=========================================================="
echo "To share Gaya, share the GitHub repository directly:"
echo "  https://github.com/ronakraval104-sys/Gaya_Agent_PR"
echo ""
