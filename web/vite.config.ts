import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Dev: Vite serves the app and proxies /api to FastAPI (port 8000).
// Prod: `npm run build` writes web/dist, which FastAPI serves at / (one process).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, proxy: { "/api": "http://localhost:8000" } },
  build: { outDir: "dist", emptyOutDir: true },
});
