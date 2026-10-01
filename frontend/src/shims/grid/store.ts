/**
 * 그리드 엑셀 다운로드 상태
 *
 * 원본 레거시 그리드 패키지의 Pinia 기반 useExcelStore 를
 * 간략화해 호출부가 참고하는 표면만 맞춘다.
 *
 *   - excelFileMap, exportFormat: downloadBigData wrapper 에서 참조
 *   - createColumnMapForExport: 그리드 필드 → 컬럼 id/header 맵 추출
 *   - isDownloading / downloadProgress: 호출부의 진행률 뱃지용
 */
import { ref } from "vue";
import { createColumnMapForExport as _createColumnMapForExport } from "./excel";

// 모듈 단위 싱글턴 상태. Pinia 로 옮기지 않아도 문제 없다.
const isDownloading = ref(false);
const downloadProgress = ref(0);
const excelFileMap = new Map<string, string>();
const exportFormat = ref<"excel" | "csv">("excel");

export function useExcelStore() {
  return {
    isDownloading,
    downloadProgress,
    excelFileMap,
    exportFormat,
    createColumnMapForExport: _createColumnMapForExport,
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
