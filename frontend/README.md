# SmartMail Frontend

React + TypeScript + Vite dashboard for the SmartMail email classifier.

## Setup

```bash
cd frontend
cp .env.example .env   # points to the backend at http://localhost:8000
npm install
npm run dev
```

Open `http://localhost:5173`. Make sure the Day 2 backend is running at
`http://localhost:8000` first (`uvicorn app.main:app --reload --port 8000`
from `backend/`), otherwise API calls will show the "unable to connect"
error state.

## Scripts

```bash
npm run dev       # start the dev server
npm run build     # type-check + production build
npm run test       # run the test suite once
npm run test:watch # run tests in watch mode
```

## Pages

- **Dashboard** (`/`) — summary stat cards + recent predictions.
- **Classify Email** (`/classify`) — paste an email, get category, confidence, explanation, timing.
- **History** (`/history`) — search, filter by category, sort, delete.
- **Statistics** (`/statistics`) — category breakdown chart + summary numbers.
- **About** (`/about`) — what SmartMail is, how the ML works, limitations, privacy.

## Design system

All design tokens (colors, type, spacing) live in `src/styles/tokens.css`.
The signature visual element is the postage-stamp-styled `CategoryBadge`
component (`src/components/CategoryBadge.tsx`), used everywhere a
category appears.

## A note on verification

This was built in a sandboxed environment with no internet access, so
`npm install` could not be run there to produce a live build or test run.
Every file was written carefully, cross-checked for matching
imports/exports, and the `lucide-react` icon names used were verified
against the real library. You should run `npm install && npm run test`
and `npm run dev` locally to confirm everything works before considering
Day 3 done — see the checklist in the root README.
