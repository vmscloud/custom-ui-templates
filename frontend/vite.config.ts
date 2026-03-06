import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { federation } from "@module-federation/vite";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
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
      "@moz-shared/icons": path.resolve(__dirname, "src/shims/moz-shared/icons"),
      "@moz-shared/utils": path.resolve(__dirname, "src/shims/moz-shared/utils"),
      "@moz-shared/types": path.resolve(__dirname, "src/shims/moz-shared/types"),
      "@vmscloud/moz-wijmo-grid/utils": path.resolve(__dirname, "src/shims/moz-wijmo-grid/utils"),
      "@vmscloud/moz-wijmo-grid/store": path.resolve(__dirname, "src/shims/moz-wijmo-grid/store"),
      "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid.multirow": "@grapecity/wijmo.vue2.grid.multirow",
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
    host: "0.0.0.0",
    port: 5300,
    strictPort: true,
    cors: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    proxy: {
      "/api/aps/": {
        target: "https://dev.mozart-cloud.com",
        changeOrigin: true,
        secure: false,
      },
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  preview: {
    port: 5300,
    strictPort: true,
    cors: true,
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
  },
});
