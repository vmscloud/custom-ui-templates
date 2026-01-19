import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import federation from "@originjs/vite-plugin-federation";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  // Nginx를 통해 /ext/ 경로로 서빙되므로 base 설정
  base: "/ext/",
  plugins: [
    vue(),
    federation({
      name: "external_app",
      filename: "remoteEntry.js",
      // Host(APS)에서 로드할 수 있도록 노출
      exposes: {
        // 뷰 레지스트리 (동적 로딩용)
        "./expose": "./src/expose.ts",
      },
      // Host(APS)와 공유할 의존성
      // Vue, Pinia, moz-ui-components를 singleton으로 공유
      shared: {
        vue: {
          singleton: true,
          requiredVersion: '^3.4.14',
        },
        pinia: {
          singleton: true,
          requiredVersion: '^2.1.7',
        },
        '@vmscloud/moz-ui-components': {
          singleton: true,
          requiredVersion: '^1.0.10',
        },
      } as any,
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
