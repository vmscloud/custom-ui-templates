import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import federation from "@originjs/vite-plugin-federation";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: "external_app",
      filename: "remoteEntry.js",
      // Host(APS)에서 로드할 수 있도록 노출
      exposes: {
        // 개별 뷰 컴포넌트
        "./CustomMenu1": "./src/views/CustomMenu1/CustomMenu1.vue",
        "./CustomMenu2": "./src/views/CustomMenu2/CustomMenu2.vue",
        // 뷰 레지스트리 (동적 로딩용)
        "./expose": "./src/expose.ts",
      },
      // Host와 공유할 의존성
      shared: ["vue", "pinia", "vue-router", "@tanstack/vue-query", "dayjs"],
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
  build: {
    target: "esnext",
    minify: false, // Module Federation은 minify 비활성화 권장
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        // Module Federation을 위한 청크 설정
        minifyInternalExports: false,
      },
    },
  },
  server: {
    port: 5300,
    strictPort: true,
    cors: true,
    // Host(APS)에서 접근할 수 있도록 CORS 허용
    headers: {
      "Access-Control-Allow-Origin": "*",
    },
    // API 프록시 설정
    proxy: {
      "/api": {
        target: "http://localhost:8099",
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
