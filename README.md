# NeonPurr 🐾

NeonPurr is a single-page, neon-themed cat breed showcase created for Hack Club
Boba Drops. It is intentionally built with semantic HTML and responsive CSS
only: no JavaScript, build step, package manager, backend, accounts, or stored
user data.

**Status:** Recovered and verified for its static scope. Local links and assets,
HTML landmarks and heading order, image metadata, CSS integrity, and real HTTP
responses are covered by the canonical check.

## Features

- A hero with original CSS/SVG cat artwork
- A featured Siamese profile
- Local photographs and summaries for four additional breeds
- Three concise feline facts
- A CSS-animated neon mascot
- Persistent fragment navigation from desktop through narrow mobile layouts
- Keyboard skip navigation, visible focus, descriptive image alternatives, and
  reduced-motion support

## Architecture

```text
.
├── index.html                 # Content, landmarks, and fragment navigation
├── css/style.css              # Theme, layout, responsive rules, and animation
├── images/                    # Five local JPEG breed photographs
├── scripts/
│   ├── verify.py              # HTML, link, asset, image, and CSS checks
│   ├── smoke_server.py        # Ephemeral HTTP server and response checks
│   └── verify.sh              # Canonical verification command
└── docs/                      # Audit, completion plan, and final status
```

Google Fonts is the only runtime network dependency. System font fallbacks keep
the content usable when those requests are blocked or unavailable.

## Run locally

There are no dependencies to install for the site itself.

```bash
git clone https://github.com/ViraatC22/Boba-Drops-Hack-Club.git
cd Boba-Drops-Hack-Club
python3 -m http.server 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Opening `index.html`
directly also works, but a local HTTP server more closely matches deployment.

## Verification

The verification scripts require Python 3.10 or newer and otherwise use only the
standard library:

```bash
./scripts/verify.sh
```

The command checks:

- HTML5 metadata and `lang`
- one `nav`, `main`, and `footer` landmark
- one `h1`, valid heading progression, and unique IDs
- skip navigation and every local fragment target
- exact local stylesheet/image paths
- non-empty image alternatives and intrinsic JPEG dimensions
- balanced CSS braces and parentheses
- focus, fragment-offset, reduced-motion, and persistent navigation rules
- HTTP 200 responses and expected content types for all seven local resources
- an HTTP 404 response for a missing page
- whitespace errors in the Git diff

### Manual browser smoke

Before publishing a visual change:

1. Test at 1440×900, 390×844, and 320×568 CSS pixels.
2. Confirm all five navigation links remain visible and the page has no
   horizontal overflow.
3. Press <kbd>Tab</kbd>; confirm the skip link appears, focus remains visible,
   and each fragment link lands below the sticky navigation.
4. Enable reduced motion at the operating-system/browser level and confirm the
   floating cat, mascot, ripple, and smooth scrolling stop.
5. Block Google Fonts and confirm the system-font fallback remains readable.

## Accessibility and responsive behavior

The page uses semantic landmarks, one logical heading hierarchy, a named primary
navigation, decorative-content hiding, descriptive image alternatives, visible
focus rings, a keyboard skip link, fragment offsets, and a
`prefers-reduced-motion` fallback. At 768px and below the navigation wraps rather
than disappearing; at 480px and below grids and large decorative elements
constrain to the viewport.

These measures improve accessibility but are not a certification. See the final
status for the remaining browser/manual validation boundary.

## Deployment

The repository root is deployment-ready for any static host:

- **Build command:** none
- **Publish directory:** repository root (`.`)
- **Entry point:** `index.html`

No automatic public deployment is configured. Enabling GitHub Pages or another
host is an explicit visibility decision and should happen only after confirming
the local image rights described below.

## Assets, privacy, and licensing

- The five breed photos are local repository assets. Their original sources and
  redistribution licenses are not recorded in Git history. Confirm or replace
  them before commercial reuse or a new public deployment.
- Google Fonts requests send normal connection/request metadata to Google. The
  project has no analytics, forms, cookies, storage, or user-submitted data.
- This repository does not contain a `LICENSE` file. Do not assume permission to
  redistribute the code or images beyond rights granted by their respective
  owners.

## Documentation

- [`docs/PROJECT_AUDIT.md`](docs/PROJECT_AUDIT.md)
- [`docs/COMPLETION_PLAN.md`](docs/COMPLETION_PLAN.md)
- [`docs/FINAL_STATUS.md`](docs/FINAL_STATUS.md)

## Repository

[ViraatC22/Boba-Drops-Hack-Club](https://github.com/ViraatC22/Boba-Drops-Hack-Club)
