/**
 * GitHub public-repo connector — read-only.
 *
 * Uses the anonymous public API (no auth needed for public repos, 60 req/hr
 * per source IP — plenty for a solo-operator dashboard polling every 60s).
 *
 * Arnie's 36 check:
 *   1/2/3/13 → no secrets used or stored (public API, unauthenticated)
 *   5/34    → server-side fetch; route caller cannot inject repo path
 *             (we pin the repository in the route, not query param)
 *   12      → structured error return, no stack traces to client
 *   27      → no CORS surface (called only from our own /api route)
 */

export interface RepoStatus {
  status: "ok" | "warn" | "err" | "off";
  fullName: string;
  commitCount: number;
  latestSha?: string;
  latestMessage?: string;
  latestAuthor?: string;
  latestAt?: string;             // ISO string
  defaultBranch?: string;
  stars?: number;
  fetchedAt: number;
  error?: string;                // present only when status !== "ok"
}

const CACHE_TTL_MS = 45_000;
const cache = new Map<string, { at: number; value: RepoStatus }>();

export async function getPublicRepoStatus(fullName: string): Promise<RepoStatus> {
  // Serve cached value if fresh — avoids blowing through the 60 req/hr budget
  const hit = cache.get(fullName);
  if (hit && Date.now() - hit.at < CACHE_TTL_MS) return hit.value;

  // Split owner/repo and encode each segment separately — GitHub rejects
  // encoded slashes in the path.
  const [owner, repo] = fullName.split("/");
  if (!owner || !repo) {
    return finalize(fullName, {
      status: "err",
      commitCount: 0,
      error: "bad-repo-slug",
      fullName
    });
  }
  const base = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}`;
  const headers: HeadersInit = {
    accept: "application/vnd.github+json",
    "user-agent": "stark-council-dashboard/1.0"
  };

  try {
    // 1. Repo metadata — default branch + stars
    const metaRes = await fetch(base, { headers, next: { revalidate: 45 } });
    if (metaRes.status === 404) {
      return finalize(fullName, { status: "err", commitCount: 0, error: "repo-not-found", fullName });
    }
    if (!metaRes.ok) {
      return finalize(fullName, {
        status: "warn",
        commitCount: 0,
        error: `meta-http-${metaRes.status}`,
        fullName
      });
    }
    const meta = (await metaRes.json()) as {
      default_branch: string;
      stargazers_count: number;
    };

    // 2. Latest commit on default branch (per_page=1 keeps payload tiny)
    const commitsRes = await fetch(
      `${base}/commits?sha=${encodeURIComponent(meta.default_branch)}&per_page=1`,
      { headers, next: { revalidate: 45 } }
    );
    if (!commitsRes.ok) {
      return finalize(fullName, {
        status: "warn",
        commitCount: 0,
        defaultBranch: meta.default_branch,
        stars: meta.stargazers_count,
        error: `commits-http-${commitsRes.status}`,
        fullName
      });
    }
    const commits = (await commitsRes.json()) as Array<{
      sha: string;
      commit: {
        message: string;
        author: { name: string; date: string };
      };
    }>;

    // Total commit count via Link header on ?per_page=1 pagination trick
    const linkHeader = commitsRes.headers.get("link") ?? "";
    const lastMatch = linkHeader.match(/<[^>]*[?&]page=(\d+)[^>]*>;\s*rel="last"/);
    const totalCommits = lastMatch ? parseInt(lastMatch[1], 10) : commits.length;

    const latest = commits[0];
    return finalize(fullName, {
      status: "ok",
      fullName,
      commitCount: totalCommits,
      latestSha: latest?.sha?.slice(0, 7),
      latestMessage: latest?.commit?.message?.split("\n")[0]?.slice(0, 120),
      latestAuthor: latest?.commit?.author?.name,
      latestAt: latest?.commit?.author?.date,
      defaultBranch: meta.default_branch,
      stars: meta.stargazers_count
    });
  } catch (err) {
    return finalize(fullName, {
      status: "err",
      commitCount: 0,
      error: (err as Error).message ?? "fetch-failed",
      fullName
    });
  }
}

function finalize(key: string, partial: Omit<RepoStatus, "fetchedAt">): RepoStatus {
  const value: RepoStatus = { ...partial, fetchedAt: Date.now() };
  // Only cache successful responses — retry on errors immediately next call
  if (value.status === "ok") cache.set(key, { at: Date.now(), value });
  return value;
}
