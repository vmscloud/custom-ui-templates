/**
 * Runtime shim for @vmscloud/moz-wijmo-grid/store
 */
import { ref } from "vue";

/**
 * useExcelStore — 엑셀 다운로드 상태 스토어
 */
export function useExcelStore() {
  const isDownloading = ref(false);
  const downloadProgress = ref(0);
  return {
    isDownloading,
    downloadProgress,
    startDownload() {
      isDownloading.value = true;
      downloadProgress.value = 0;
    },
    finishDownload() {
      isDownloading.value = false;
      downloadProgress.value = 100;
    },
  };
}

export default useExcelStore;
