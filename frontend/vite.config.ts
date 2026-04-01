import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import { federation } from "@module-federation/vite";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const DEV_PORT = Number(env.VITE_DEV_PORT || 5300);
  const API_TARGET = env.VITE_API_TARGET || "http://localhost:8000";

  return {
  base: "/ext/",
  plugins: [
    vue(),
    federation({
      name: "external_app",
      filename: "remoteEntry.js",
      exposes: {
        "./expose": "./src/expose.ts",
      },
      shared: {
        vue: { singleton: true, requiredVersion: "^3.4.14" },
        pinia: { singleton: true, requiredVersion: "^2.1.7" },
      },
      dts: false,
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: "modern-compiler",
      },
    },
  },
  optimizeDeps: {
    include: [
      "@vmscloud/moz-ui-chart/echarts",
      "@vmscloud/moz-ui-chart/echarts/core",
      "@vmscloud/moz-ui-chart/echarts/charts",
      "@vmscloud/moz-ui-chart/echarts/components",
      "@vmscloud/moz-ui-chart/echarts/renderers",
      "@vmscloud/moz-ui-chart/echarts-stat",
      "vue-echarts",
    ],
  },
  build: {
    target: "esnext",
    minify: false,
    cssCodeSplit: true,
    modulePreload: false,
    rollupOptions: {
      output: {
        minifyInternalExports: false,
      },
    },
  },
  server: {
    port: DEV_PORT,
    strictPort: true,
    cors: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    port: DEV_PORT,
    strictPort: true,
    cors: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  },
};
});
