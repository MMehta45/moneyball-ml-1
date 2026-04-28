# UTD Degree Planner — UI Scaffold

Built with React + TypeScript + Tailwind + React Flow + Dagre.

## Setup & Run

```bash
npm install
npm run dev
```

Open http://localhost:5173

## Structure

```
src/
  WelcomeScreen.tsx   ← User input screen (hours + start button)
  ScheduleGraph.tsx   ← React Flow + Dagre graph view  
  mockSchedule.ts     ← Mock data structured like DEAP output
  App.tsx             ← Root — switches between screens
  index.css           ← Tailwind + custom styles
```

## Connecting DEAP (Tuesday)
Replace `generateMockSchedule()` in `mockSchedule.ts` with a real API call.
The `DEAPScheduleOutput` interface is already shaped to match DEAP's output.

## Tech Stack
- React 18 + TypeScript (Vite)
- Tailwind CSS v3
- @xyflow/react (React Flow v12)
- @dagrejs/dagre (layout engine)
