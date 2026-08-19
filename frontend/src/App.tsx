/**
 * App.tsx
 * -------
 * Defines all routes and wraps them in the shared Layout (sidebar nav).
 */

import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { ClassifyEmail } from "./pages/ClassifyEmail";
import { History } from "./pages/History";
import { Statistics } from "./pages/Statistics";
import { About } from "./pages/About";

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/classify" element={<ClassifyEmail />} />
        <Route path="/history" element={<History />} />
        <Route path="/statistics" element={<Statistics />} />
        <Route path="/about" element={<About />} />
      </Route>
    </Routes>
  );
}
