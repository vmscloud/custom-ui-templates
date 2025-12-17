/**
 * 외주 앱용 ProjectInfo 스토어
 * 독립 실행 시 사용됩니다.
 * APS에서 로드될 때는 Host의 스토어가 inject됩니다.
 */
import { defineStore } from "pinia";
import {
  useProjectInfoComposable,
  SHARED_STORE_ID,
  DEFAULT_LOCAL_STORAGE_PATHS,
  DEFAULT_SESSION_STORAGE_PATHS,
  buildDualStoragePersist,
} from "@vmscloud/moz-component";

export { SHARED_STORE_ID };

/**
 * ProjectInfo 스토어
 * moz-component의 useProjectInfoComposable을 기반으로 구현
 */
export const useProjectInfoStore = defineStore(
  SHARED_STORE_ID,
  () => {
    const core = useProjectInfoComposable();

    return {
      ...core,
    };
  },
  {
    persist: buildDualStoragePersist(
      [...DEFAULT_LOCAL_STORAGE_PATHS],
      [...DEFAULT_SESSION_STORAGE_PATHS]
    ),
  }
);
