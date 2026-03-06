/**
 * Type declarations for @vmscloud/moz-wijmo-grid subpath imports
 * that don't ship their own .d.ts
 */

declare module "@vmscloud/moz-wijmo-grid/utils" {
  export function showMessage(...args: any[]): any;
  export function showDialog(...args: any[]): Promise<any>;
  export function getValue(obj: any, path: string, defaultValue?: any): any;
  export function copyToClipboard(text: string): Promise<void>;
  export function addTooltipEvent(...args: any[]): void;
  export function removeTooltipEvent(el: HTMLElement): void;
  export function generateUUID(): string;
  export function isDataCell(...args: any[]): boolean;
  export function getWidthByKey(key: string): number;
  export const dayjs: any;
}

declare module "@vmscloud/moz-wijmo-grid/store" {
  export const useGridControlStore: any;
  export const useExcelStore: any;
  export default useGridControlStore;
}

declare module "@vmscloud/moz-wijmo-grid/wijmo.vue2.grid.multirow" {
  import { Component } from "vue";
  export const WjMultiRow: Component;
  export const WjMultiRowCell: Component;
  export const WjMultiRowCellGroup: Component;
  export const WjMultiRowCellTemplate: Component;
  export default WjMultiRow;
}
