/**
 * Minimal YAML frontmatter parser for Gaya's memory format.
 * Handles: name, description (quoted or bare), metadata.{type, node_type, originSessionId}.
 * NOT a general YAML parser — hand-tuned for these files, zero deps.
 */
export function parseFrontmatter(content: string): { data: Record<string, any>; body: string } {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: content };
  const yamlText = match[1];
  const body = match[2] ?? "";

  const data: Record<string, any> = {};
  const stack: Array<Record<string, any>> = [data];
  const indentStack: number[] = [-1];

  for (const rawLine of yamlText.split(/\r?\n/)) {
    if (!rawLine.trim() || rawLine.trim().startsWith("#")) continue;
    const indent = rawLine.length - rawLine.trimStart().length;
    const stripped = rawLine.trim();
    const colonIdx = stripped.indexOf(":");
    if (colonIdx === -1) continue;
    const key = stripped.slice(0, colonIdx).trim();
    let value = stripped.slice(colonIdx + 1).trim();

    // pop stack when outdenting
    while (indentStack.length > 1 && indent <= indentStack[indentStack.length - 1]) {
      stack.pop();
      indentStack.pop();
    }
    const cur = stack[stack.length - 1];

    if (value === "") {
      const nested: Record<string, any> = {};
      cur[key] = nested;
      stack.push(nested);
      indentStack.push(indent);
    } else {
      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }
      cur[key] = value;
    }
  }
  return { data, body: body.replace(/^\r?\n/, "") };
}

/**
 * Extract [[wiki-links]] targets. Handles [[slug]] and [[slug|display]].
 */
export function extractWikiLinks(md: string): string[] {
  const links = new Set<string>();
  const re = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(md)) !== null) {
    links.add(m[1].trim().toLowerCase().replace(/_/g, "-"));
  }
  return [...links];
}

/**
 * Extract standard-markdown links to peer memory files: [text](file.md) or [text](./file.md).
 */
export function extractMdLinks(md: string): string[] {
  const links = new Set<string>();
  const re = /\[[^\]]+\]\(\.?\/?([a-z0-9_-]+)\.md\)/gi;
  let m: RegExpExecArray | null;
  while ((m = re.exec(md)) !== null) {
    links.add(m[1].toLowerCase().replace(/_/g, "-"));
  }
  return [...links];
}

/**
 * Pull a human title from the frontmatter name or first H1 in body.
 */
export function titleFrom(name: string | undefined, body: string): string {
  if (name && name.trim()) {
    return name
      .split(/[-_]/)
      .map((s) => (s.length <= 3 ? s.toUpperCase() : s[0].toUpperCase() + s.slice(1)))
      .join(" ");
  }
  const h1 = body.match(/^#\s+(.+)$/m);
  if (h1) return h1[1].trim();
  return "Untitled";
}
