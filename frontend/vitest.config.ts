/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
    coverage: {
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/",
        "src/test/",
        "**/*.d.ts",
        "cypress/",
        "dist/",
        "packages/*/test{,s}/**",
        "**/*.config.{js,ts}",
        "**/.{eslint,prettier}rc.{js,cjs}",
        "src/main.tsx",
        "src/vite-env.d.ts",
      ],
    },
  },
});
