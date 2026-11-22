import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, loadEnv } from "vite";

declare const process: { env: Record<string, string | undefined> };

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".");
  const backendTarget = env.VITE_BACKEND_URL || `http://localhost:${env.API_PORT || process?.env?.API_PORT || "8001"}`;

  return {
    plugins: [react(), tailwindcss()],
    // The main file is mostly React and the EN/हिं/Hinglish text (about 170 kB gzipped); pages load on demand.
    build: { chunkSizeWarningLimit: 600 },
    server: {
      port: 5173,
      proxy: {
        // API_PORT lets a second copy run beside this one (default 8000)
        "/api": backendTarget,
      },
    },
  };
});
