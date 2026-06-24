# Branching & Merging — the parallel sprint playbook

We're three people sitting together, sprinting fast, each on our own Claude Code,
each owning one MVC layer (see `CLAUDE.md`). This guide keeps our git history clean
and our integration painless. **Read it before your first push.**

The whole strategy in one line: **`main` is always green; everyone works on a short
role branch; integrate small and often.**

---

## The model: trunk + short-lived role branches

- **`main`** is the integration trunk. It must **always run** (tests pass, UI builds).
  Never push half-finished work straight to `main`.
- Each person works on a branch **named for their layer**, so a glance at the branch
  tells everyone which seam it touches:

  | Owner | Layer | Branch prefix | Example |
  |---|---|---|---|
  | Zargham | Model | `m/` | `m/ontology-claims`, `m/flexo-load` |
  | Joshua | View | `v/` | `v/inspector-polish`, `v/edge-labels` |
  | Christine | Controller | `c/` | `c/participation-analysis` |

- Branches are **short-lived** — hours, not days. Branch → small change → merge to
  `main` → branch again. Because our directories are disjoint (see the ownership
  table in `CLAUDE.md`), most branches never touch the same files, so most merges are
  conflict-free.

---

## The loop (do this all day)

```bash
# 1. Start fresh from the latest main
git checkout main
git pull
git checkout -b v/edge-labels          # your prefix + a short topic

# 2. Work in YOUR layer's directories only. Commit small and often.
git add ui/src/graph/style.ts
git commit -m "v: thicker edges, readable rel labels"

# 3. Before you merge, catch up on main (rebase keeps history linear)
git fetch origin
git rebase origin/main                 # replay your commits on top of latest main

# 4. Verify green, then merge to main
uv run pytest -q        # if you touched Python
cd ui && npm run build  # if you touched the UI
git checkout main
git pull
git merge --no-ff v/edge-labels        # --no-ff keeps the branch visible in history
git push
git branch -d v/edge-labels            # tidy up
```

**Rule of thumb:** if you've been on a branch more than ~30 minutes, pull `main` into
it (`git rebase origin/main`) so you don't drift.

---

## Direct-to-main vs. branch — pick fast

We're sitting together, so optimize for speed:

- **Tiny change, entirely inside your own layer, tests green?** Push to `main`
  directly is fine (`git pull --rebase` first). Low conflict risk because layers are
  disjoint.
- **Anything touching a seam, anything big, or anything you want a second pair of eyes
  on?** Use a role branch and merge. Seam = `views/schema.json`, `views/cache/*.json`,
  `fixtures/*.trig`, or any file outside your layer.

We are **not** using PRs/reviews for the in-person sprint — turnaround is a tap on the
shoulder. (If we open the repo to outside contributors later, switch to PRs.)

---

## The seam files — how to not step on each other

Most conflicts will only ever happen on these shared artifacts. Handle them by rule,
not by hand:

### `views/schema.json` — the frozen contract
- **Only Zargham (M) edits it.** Changing a V1–V5 column ripples to Joshua's UI and
  Christine's conformance. **Announce at the table before changing**, then everyone
  `git pull` immediately.
- Changes must be **additive** (new optional field) — never rename/retype an existing
  column. That's what keeps V and C from breaking mid-sprint.

### `views/cache/*.json` — generated, never hand-edited
- This is build output committed for convenience (so Joshua can run without Flexo).
- **On a merge conflict here, do not resolve manually.** Take either side, then
  regenerate and commit:
  ```bash
  git checkout --theirs views/cache/        # or --ours; doesn't matter, we regenerate
  uv run ccp seed-offline                    # rebuild from the current .trig
  git add views/cache/ && git commit
  ```
- Whoever changes the underlying data/ontology regenerates the cache as part of the
  same commit.

### `fixtures/*.trig` — Christine's data, coerced into the ontology
- Co-owned by **C (content) + Z (form)**. Christine produces the analysis + capture
  rows; Zargham lifts them into a conformant `.trig`. Coordinate the hand-off; don't
  both edit the same `.trig` simultaneously.

---

## Conflict triage (when a merge does conflict)

1. **Is it a `views/cache/*.json` conflict?** → regenerate (above). Done.
2. **Is it in a file you don't own?** → stop, grab the owner. It means a seam moved.
3. **Is it in your own layer?** → resolve normally; your change wins for your files.
4. **Still stuck after 2 minutes?** → `git merge --abort`, talk it out at the table,
   re-approach. We have no time for a tangled rebase; a 60-second conversation beats it.

---

## Keeping `main` green

- Don't merge red. Run the relevant gate first: `uv run pytest -q` (Python) and/or
  `cd ui && npm run build` (UI).
- If you push something that breaks `main`, **fixing it is the top priority** — call
  it out so nobody branches off the breakage.
- Commit messages: prefix with your layer (`m:`, `v:`, `c:`) and keep them one line,
  present tense. History should read like a sprint log.

---

## Quick reference

```bash
git checkout main && git pull              # start of every task
git checkout -b <m|v|c>/<topic>            # your branch
# ...work, commit small...
git fetch origin && git rebase origin/main # catch up before merging
git checkout main && git pull
git merge --no-ff <branch> && git push     # integrate
git branch -d <branch>                     # clean up
```

Seam file? → owner edits + announces. Cache conflict? → regenerate. Stuck? → the table.
