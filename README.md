# Skillora

A unified developer platform where your coding activity — code you push, problems you solve, and contributions you make — automatically builds your public developer profile. No separate "write your bio" step: the profile is *earned*, not authored.

---

## Project Structure

- **Frontend Application** ([`frontend/`](frontend/)): React + Vite single-page application with client-side routing (`react-router-dom`), Monaco editor integration, high-intensity cyber neon motion design system, Framer Motion animations, and persistent state.
- **ML / AI Intelligence Layer** ([`ml/`](ml/)): Owns models, pipelines, inference, RAG, evaluation, recommendations, the skill engine, feed ranking, difficulty estimation, learning paths, and reputation scoring.

---

## Frontend Quick Start (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Then open the printed local URL (typically `http://localhost:5173`).

Build for production:
```bash
cd frontend
npm run build
```

### Frontend Features
- **High-Intensity Visual Design**: Dynamic cyber grid background with cursor proximity webbing, glowing ambient aurora orbs, and neon green accents.
- **Client-Side Routing**: Full route coverage for Developer, Recruiter, and Admin flows.
- **Persistent Demo State**: Local storage sync for snippets, solved problems, and user stats.
- **Interactive Code Editor & Problem Solver**: Monaco editor integration with execution simulator.

---

## ML Layer Quick Start

```bash
cd ml
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn gateway.main:app --reload --port 8000
```

### Tests
```bash
pytest ml/tests/ -v
```

See [`ml/README.md`](ml/README.md) for ML architecture details and [`ml/docs/API.md`](ml/docs/API.md) for the full endpoint contract.
