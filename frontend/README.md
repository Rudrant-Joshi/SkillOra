# SkillGraph — React + Vite Frontend

Frontend-only conversion of the original `skillgraph.html` single-file demo
into a real React + Vite application with client-side routing. There is
**no backend** — auth, snippets, problem "execution", following, and feed
activity are all mocked and persisted to `localStorage`.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL (typically `http://localhost:5173`).

Build for production with `npm run build`; preview that build with `npm run preview`.

## What's here

- **Routing**: `react-router-dom`, wired in `src/App.jsx`. Every screen has
  a real URL (`/app/dashboard`, `/app/problems/:id`, `/recruiter/candidates`,
  etc.) — no more `document.getElementById`/`style.display` page switching.
- **Auth**: `/login` and `/signup` are real routes. Submitting either
  creates a mock session object in `localStorage` (`AuthContext`) and
  navigates to the role's home route. No password is checked — this is a
  frontend demo only, matching the source HTML's behavior.
- **Persistent demo state**: `DemoStateContext` + `useLocalStorage` hold
  snippets, solved problems, network/following, and the activity feed. All
  of it survives a refresh.
- **Monaco editor**: `src/components/editors/CodeEditor.jsx`, used by the
  snippet editor, the problem solver, and exam coding questions.
- **Mock execution**: `src/components/editors/ExecutionPanel.jsx` +
  `evaluateMockSubmission` in `src/data/code.js` drive the
  QUEUED → RUNNING/CHECKING → COMPLETED → ACCEPTED/WRONG/ERROR pipeline
  with a small deterministic heuristic (no Judge0, no backend).
- **Animation**: Framer Motion powers page transitions (`PageTransition`),
  scroll reveals (`Reveal`, `StaggerContainer`/`StaggerItem`), animated
  numbers/progress bars (`AnimatedNumber`, `ProgressBar`), and modal/drawer/
  toast enter-exit motion. `prefers-reduced-motion` is respected globally
  in `src/styles/globals.css`.
- **Design tokens**: ported 1:1 from the original HTML into
  `tailwind.config.js` and `src/styles/globals.css` (black background,
  neon-green accent, Archivo Black display font, Space Mono body font,
  the offset-panel/card/badge/button system, etc.).

## Known simplifications vs. the original HTML draft

This is a large app (34+ screens across 3 roles). Everything listed below
is a real, routed, interactive React page — but a few of the deeper
recruiter/company screens (question bank, campaigns, candidates, team) use
a shared `DataTable` component rather than the fully bespoke layout the
original prototype implied, to keep the codebase consistent and
maintainable. Swap in richer per-page layouts as needed — the data models
in `src/data/recruiter.js` already support it.

## Resetting demo data

Demo state lives under `localStorage` keys prefixed `skillgraph_`. Call
`resetAllDemoData()` from `src/hooks/useLocalStorage.js` (wire it to a
button in Settings/Profile if you want a UI entry point) to clear it and
return to `/login`.
