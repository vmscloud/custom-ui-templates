// moz-component 타입 선언 (패키지에 .d.ts가 없는 경우)
declare module "@vmscloud/moz-component" {
  import { DefineComponent } from "vue";

  export const SHARED_STORE_ID: string;
  export const DEFAULT_LOCAL_STORAGE_PATHS: string[];
  export const DEFAULT_SESSION_STORAGE_PATHS: string[];
  export function useProjectInfoComposable(): any;
  export function buildDualStoragePersist(
    localPaths: string[],
    sessionPaths: string[]
  ): any;
  export function createSharedStoresPlugin(options: any): any;

  // Grid 컴포넌트
  export const ExtendFlexGrid: DefineComponent<{
    itemsSource?: any[];
    autoGenerateColumns?: boolean;
    isReadOnly?: boolean;
    alternatingRowStep?: number;
    height?: string;
    name?: string;
    dataKey?: string[];
    selectionMode?: string;
    validateKey?: string;
    loading?: boolean;
    emptyState?: { isLoading?: boolean };
    setContextMenuProps?: any;
    onInitializeRowData?: () => any;
  }>;

  export const ExtendGridFooter: DefineComponent<any>;
  export const FlexColumnSetupModal: DefineComponent<any>;
  export const FlexGridFilter: DefineComponent<any>;
  export const FlexGridSetupModal: DefineComponent<any>;
  export const FlexGridSort: DefineComponent<any>;
  export const FlexGridToolBox: DefineComponent<any>;
  export const GridBulkEditor: DefineComponent<any>;
  export const GridSearchInput: DefineComponent<any>;
}

declare module "@vmscloud/moz-component/style.css";
