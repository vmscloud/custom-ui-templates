// moz-component 타입 선언 (패키지에 .d.ts가 없는 경우)
declare module "@vmscloud/moz-component" {
  export const SHARED_STORE_ID: string;
  export const DEFAULT_LOCAL_STORAGE_PATHS: string[];
  export const DEFAULT_SESSION_STORAGE_PATHS: string[];
  export function useProjectInfoComposable(): any;
  export function buildDualStoragePersist(
    localPaths: string[],
    sessionPaths: string[]
  ): any;
  export function createSharedStoresPlugin(options: any): any;
}

declare module "@vmscloud/moz-component/style.css";
