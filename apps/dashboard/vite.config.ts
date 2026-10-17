import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// `base: "./"` ensures assets and `./data/projects.json` work under any GitHub Pages sub-path.
export default defineConfig({
  base: "./",
  plugins: [react(), tailwindcss()],
  build: {
    outDir: "dist",
    chunkSizeWarningLimit: 900,
  },
});

