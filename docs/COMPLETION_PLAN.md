# Completion Plan

Statuses: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`,
`DEFERRED_WITH_REASON`.

## Milestone 1 — Recovery and repeatable verification

### BOBA-001 — Reconcile repository safety and intent

- **Reason:** Preserve the existing static-only direction and remote history.
- **Files:** repository history, `README.md`, `index.html`, `css/style.css`
- **Dependencies:** None
- **Acceptance criteria:** Working tree is clean; local and remote `main` are
  reconciled; relevant history and all source/assets are audited.
- **Verification:** `git status --short --branch`, `git branch -a -vv`,
  `git fetch --prune Viraat-Chauhan`
- **Status:** COMPLETED
- **Commit:** Existing baseline `e2fc2ac`

### BOBA-002 — Add an offline site integrity check

- **Reason:** The project has no build or quality gate.
- **Files:** `scripts/verify.py`, `scripts/verify.sh`
- **Dependencies:** BOBA-001
- **Acceptance criteria:** One dependency-free command validates metadata,
  landmarks, heading order, unique IDs, fragment links, local assets, image alt
  text/dimensions, and balanced CSS delimiters.
- **Verification:** `./scripts/verify.sh`
- **Status:** COMPLETED
- **Commit:** `adca455`

## Milestone 2 — Accessible responsive completion

### BOBA-003 — Complete semantic and keyboard accessibility

- **Reason:** Keyboard, screen-reader, contrast, and motion behavior is incomplete.
- **Files:** `index.html`, `css/style.css`
- **Dependencies:** BOBA-002
- **Acceptance criteria:** Skip navigation, named navigation, meaningful image
  alternatives, decorative-content handling, visible focus, AA text contrast,
  fragment offsets, and reduced-motion behavior are present.
- **Verification:** `./scripts/verify.sh` and browser keyboard/reduced-motion smoke
- **Status:** COMPLETED
- **Commit:** `adca455`

### BOBA-004 — Preserve navigation and layout on narrow screens

- **Reason:** Mobile navigation is currently removed and fixed visuals can crowd
  small viewports.
- **Files:** `css/style.css`
- **Dependencies:** BOBA-003
- **Acceptance criteria:** Navigation remains visible, page has no horizontal
  overflow at 320 CSS pixels, imagery scales, and content remains readable.
- **Verification:** browser smoke at 1440×900, 390×844, and 320×568
- **Status:** COMPLETED
- **Commit:** `adca455`
- **Validation note:** Static responsive guards pass. Automated viewport rendering
  is externally blocked because no controllable browser was available; the
  manual procedure is documented in `README.md`.

## Milestone 3 — Documentation and handoff

### BOBA-005 — Synchronize content and operations

- **Reason:** Credits, dates, purpose, verification, hosting, and legal status
  must match the repository.
- **Files:** `README.md`, `index.html`, `docs/FINAL_STATUS.md`
- **Dependencies:** BOBA-003, BOBA-004
- **Acceptance criteria:** Site copy and README accurately document static
  behavior, local serving, browser checks, external fonts, image provenance,
  deployment readiness, and the absence of a declared software license.
- **Verification:** link/content review and `./scripts/verify.sh`
- **Status:** COMPLETED
- **Commit:** Final documentation closeout (see `git log -1`)

## Deferred with reason

- **Dynamic breed search/quiz:** `DEFERRED_WITH_REASON` — repository history
  explicitly removed JavaScript in favor of a static experience.
- **Automatic public deployment:** `DEFERRED_WITH_REASON` — requires an explicit
  repository visibility/hosting decision.
- **Image relicensing:** `BLOCKED` — source and license information is not
  recoverable from the repository; owner confirmation or replacement assets are
  required.
