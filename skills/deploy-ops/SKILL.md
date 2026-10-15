---
name: deploy-ops
description: >
  Deployment and runtime operations — environment hygiene (venv, env vars,
  secrets), dependency management (lockfiles, npm/pip/uv), build and run
  scripts, deploy platforms (Vercel, Netlify, Railway, Cloudflare,
  VPS/Docker), basic CI/CD wiring, and the "works on my machine /
  doesn't work in prod" diagnostic playbook. Lifted from recurring
  deploy friction in the Jarvis voice app build, the Pixel Quote Max
  sprint, and similar. Fires on "deploy this", "set up env",
  "fix the build", "ship to prod", "lockfile broke", "env var missing",
  "secrets management", or any runtime/deployment friction.
---

# Deploy Ops
The boring discipline that decides whether you ship. Most "production bugs" are environment drift, secret leaks, lockfile lies, or a build step nobody documented. This skill closes those gaps.

## 1 · Environment Hygiene
**Local first.** Before any deploy, the project must run cleanly from a fresh clone with documented setup steps. If onboarding a new machine is undocumented, you don't have a deploy — you have a magic spell.

- **Python:** real venv (`python -m venv .venv`) — *not* system pip. Lock with `requirements.txt` (pinned) or `pyproject.toml` + `uv lock`. Document the Python version (`3.12.8` not `3.12`).
- **Node:** lockfile in git (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`). Use `engines` field in `package.json` to pin Node version. `npm ci` for reproducible installs, never `npm install` in CI.
- **Versions matter.** "Works on Node 18" and "works on Node 20" can be different stories. Pin in CI, document in README.

## 2 · Secrets & Env Vars
- **Never commit `.env`.** Always have `.env.example` with placeholder values committed.
- **Three-tier setup:** local `.env` (gitignored) · staging vault · prod vault. Same key names, different values.
- **Rotate when leaked.** A key in a screenshot is a key in the wild. Rotate first, debug what leaked second.
- **Platform secret stores:** Vercel/Netlify/Railway env settings, GitHub Actions secrets, AWS Secrets Manager, doppler.com. Pick one per project; don't sprawl.
- **Validate at boot.** First lines of the app should assert required env vars exist (`assert os.environ['ANTHROPIC_API_KEY']`). Fail fast, fail loud.

## 3 · Dependency Lockfiles
- **Lockfile is law.** If it's not in the lockfile, it doesn't ship.
- **Audit on add.** `npm audit` / `pip-audit` runs before merging a dep PR.
- **Dependabot / Renovate.** Automate the PRs; review them weekly. Stale deps are a security and a "site is suddenly broken" risk.
- **Peer-dependency hell.** When npm warns about peer deps, *read the warning* — don't auto-`--force`. That's how prod silently breaks.

## 4 · Deploy Platforms (when to use which)
| Platform | Sweet spot | Avoid for |
|---|---|---|
| **Vercel** | Next.js, static + serverless, fast iteration, preview branches | Long-running jobs, persistent WebSocket, heavy backend |
| **Netlify** | Static + edge functions, Jamstack | Same as Vercel — serverless-only |
| **Railway** | Full apps with a database, long-running services, simple PaaS | Massive scale, complex networking |
| **Cloudflare Pages + Workers** | Edge-first, global low-latency, KV/D1 | Heavy CPU per request |
| **VPS (DigitalOcean / Hetzner / AWS Lightsail) + Docker** | Full control, complex stacks, custom networking | Trivial deploys (overkill) |
| **GitHub Pages** | Pure static, public repos, $0 cost | Anything dynamic |

Default for Katviz's web work: **Vercel** for static/Next, **Railway** for full apps with DB. Override when there's a reason.

## 5 · Build & Deploy Scripts
- `package.json` scripts: `dev`, `build`, `start`, `test`, `lint` — always these names. Don't make people read your README to know the dev command.
- `.bat` / `.sh` runners on Windows/Mac: always include error visibility (`pause` on Windows so the cmd window doesn't flash-close on error; `set -e` in bash so a step failure stops the chain).
- **Idempotent.** `setup.bat` run twice should be the same as once. Same for deploy scripts.

## 6 · CI/CD Basics
- **GitHub Actions** for most projects. One workflow: lint → typecheck → test → build → (on `main`) deploy.
- **Lockfile freshness check** in CI (`npm ci` will fail if lockfile is stale — let it).
- **No secrets in workflow files.** Use Actions secrets.
- **Status badges in README.** If CI's green status isn't visible, nobody trusts it.

## 7 · Production Debugging — "Works on my machine, breaks in prod"
The diagnostic playbook, in order:

1. **Logs first.** Platform's log stream (Vercel `vercel logs`, Railway dashboard, `journalctl` on VPS). 80% of mysteries die here.
2. **Env var sanity.** Same key names locally and in prod? `console.log(Object.keys(process.env).filter(k => k.startsWith('MYAPP_')))` (once, in a hotfix, then remove).
3. **Build artifact diff.** Did the build succeed? Did it bundle the file you think it did? Inspect `dist/` or platform's build output.
4. **Node/Python version drift.** Local is `node 20`, prod is `node 18` — explains half the cases.
5. **Lockfile drift.** Did `npm install` (no `ci`) modify the lockfile during deploy, pulling a newer minor? Check the deploy log.
6. **External-service health.** API rate-limit, DB connection pool exhausted, third-party SaaS down — `curl` the dependencies.
7. **Permissions/paths.** Container filesystem layout differs from local. Logs sometimes pinpoint a missing dir or read-only volume.
8. **Cache.** Edge cache, browser cache, build cache. Force-purge before declaring the bug fixed.

## 8 · Anti-patterns (the ones we've actually hit)
- **`git add -A` blindly** — sweeps stray files (lesson from the Pixel Quote Max sprint). Use `git add <specific files>` or a tight `.gitignore`.
- **Cross-drive venvs** — venv created against a Python that gets garbage-collected by the package manager (uv) silently breaks the venv (lesson from the Jarvis voice app build). Pin the Python; rebuild the venv if the base Python moves.
- **`.bat` without `pause`** — error windows flash-close and you never see the error.
- **Hard-coding API keys "just for testing"** then accidentally committing. Use `.env` from day one.
- **Skipping `.gitignore` until later.** `.gitignore` is a day-one file, not a day-fifty file.
- **Deploying without a rollback plan.** Tag releases (`git tag v1.2.0`) so revert is one command.

## 9 · Pre-deploy Checklist (run before every prod push)
- [ ] Lockfile committed and matches the build's install
- [ ] `.env.example` up to date; no real `.env` in git
- [ ] CI green on the commit being deployed
- [ ] Build succeeds locally with a fresh `node_modules` / `venv`
- [ ] Smoke test plan: which 3 paths must work after deploy?
- [ ] Rollback plan: what's the command to revert?
- [ ] Logging works: can you `vercel logs --since 5m` after deploy to confirm?

## Hard rules
- **Don't ship to prod on a Friday afternoon.** Niti's *"the wise act at once on what the fool does finally"* applies to timing, not just speed. A Monday morning bug is a Monday morning fix; a Friday evening bug is a weekend.
- **One change at a time on prod.** If both code and infra are changing, separate the deploys.
- **Document what broke and how it got fixed** — append to GOTCHAS in memory. Future-Katviz will thank you.
