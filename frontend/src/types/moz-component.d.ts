// moz-component 타입 선언 (패키지에 .d.ts가 없는 경우)
declare module "@vmscloud/moz-component" {
  import { DefineComponent, Ref } from "vue";
  import { Router } from "vue-router";

  export const SHARED_STORE_ID: string;
  export const DEFAULT_LOCAL_STORAGE_PATHS: string[];
  export const DEFAULT_SESSION_STORAGE_PATHS: string[];
  export function useProjectInfoComposable(): any;
  export function buildDualStoragePersist(
    localPaths: string[],
    sessionPaths: string[]
  ): any;
  export function createSharedStoresPlugin(options: any): any;

  // ===== UI Components =====
  export const BreadCrumb: DefineComponent<{
    itemSource: string[];
    showFavorite?: boolean;
  }>;

  export const Button: DefineComponent<{
    text?: string;
    icon?: string;
    disabled?: boolean;
    loading?: boolean;
    width?: number;
    onClick?: () => void;
  }>;

  export const Toggle: DefineComponent<{
    modelValue?: boolean;
    label?: string;
  }>;

  // ===== Icons =====
  export const IconPlay: DefineComponent<{ color?: string; size?: string | number }>;
  export const IconPlus: DefineComponent<{ color?: string; size?: string | number }>;
  export const IconSave: DefineComponent<{ color?: string; size?: string | number }>;
  export const IconSearch: DefineComponent<{ color?: string; size?: string | number }>;
  export const IconTrash: DefineComponent<{ color?: string; size?: string | number }>;

  // ===== View Manager - Query Params Module =====
  export function useQueryParamsModuleStore(): any;
  export function createQueryParamsModule(
    projectId: Ref<string>,
    menuId: Ref<string>,
    userId: Ref<string>,
    router: Router
  ): any;
  export function useQueryParamsModule(): {
    urlQueryParamsTimestamp: Ref<number>;
    renewUrlQueryParams: () => void;
    registerToUserLayout: (instance: any) => void;
    router: Ref<Router | null>;
    onRouteChanges: Ref<Function[]>;
  };
  export type IQueryParamsModule = ReturnType<typeof useQueryParamsModule>;

  // ===== View Manager - User Layout Module =====
  export interface LayoutOption {
    useMakeLink?: boolean;
  }

  export function createUserLayoutModule(
    projectId: Ref<string>,
    menuId: Ref<string>,
    userId: Ref<string>,
    router: Router
  ): any;
  export function useUserLayoutModule(): {
    register: () => void;
    currentPreset: Ref<any>;
  };

  // ===== View Manager - Constants =====
  export const USER_LAYOUT_PROVIDER_KEY: string;
  export const DEFAULT_PRESET_KEY: string;
  export const RECENT_PRESET_KEY: string;
  export const QUERY_PARAM_KEY: string;
  export const RECENT_LAYOUT_FIXED_STORAGE_KEY: string;
  export const RECENT_LAYOUT_STORAGE_KEY: string;

  // ===== View Manager - Components =====
  export const UserLayoutContext: DefineComponent<{
    layoutOption?: LayoutOption;
  }>;

  export const ViewManagerProvider: DefineComponent<any>;

  // ===== Stores =====
  export function useQueryParamPanelStore(): any;

  // ===== Types =====
  export interface PropsParam {
    type: string;
    label?: string;
    value?: any;
    [key: string]: any;
  }

  // ===== Grid 컴포넌트 =====
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
