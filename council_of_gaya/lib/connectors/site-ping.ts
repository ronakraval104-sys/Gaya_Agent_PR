/**
 * Generic public-site health check — no auth, no secrets.
 * Used for VR site + Gaya OS URLs.
 *
 * Arnie's 36:
 *   1/2/3 → no secrets
 *   5     → URL is pinned by caller (via env-var default or hard-coded)
 *   12    → structured error return, no stack traces leaked
 *   34    → callers pass a validated URL string; no user input flows through
 */

export interface SiteStatus {
  status: "ok" | "warn" | "err" | "off";
  url: string;
  httpCode: number;
  latencyMs: number;
  fetchedAt: number;
  error?: string;
}

export async function pingSite(url: string, timeoutMs = 5000): Promise<SiteStatus> {
  const start = Date.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      method: "GET",
      signal: controller.signal,
      redirect: "follow",
      headers: { "user-agent": "stark-council-dashboard/1.0" }
    });
    clearTimeout(timer);
    const latencyMs = Date.now() - start;
    return {
      status:
        res.ok ? "ok"
        : res.status >= 500 ? "err"
        : "warn",
      url,
      httpCode: res.status,
      latencyMs,
      fetchedAt: Date.now()
    };
  } catch (err) {
    clearTimeout(timer);
    const isAbort = (err as Error).name === "AbortError";
    return {
      status: "err",
      url,
      httpCode: 0,
      latencyMs: Date.now() - start,
      fetchedAt: Date.now(),
      error: isAbort ? `timeout after ${timeoutMs}ms` : (err as Error).message ?? "fetch-failed"
    };
  }
}
