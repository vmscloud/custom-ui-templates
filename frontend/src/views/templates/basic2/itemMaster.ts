/**
 * Item Master API 호출 및 데이터 관리
 */
import axios from "axios";
import { ref, type Ref } from "vue";

/**
 * Item Master 데이터 타입
 */
export interface ItemMaster {
  partition_key: string;
  project_id: string;
  plan_ver: string;
  item_id: string;
  item_type: string | null;
  item_name: string | null;
  item_group_id: string | null;
  description: string | null;
  procurement_type: string | null;
  item_spec: string | null;
  create_datetime: string;
  create_user_id: string;
  update_datetime: string;
  update_user_id: string;
  prod_type: string | null;
  item_size_type: string | null;
  item_priority: number | null;
  prop01: string | null;
  prop02: string | null;
  prop03: string | null;
  prop04: string | null;
  prop05: string | null;
  prop06: string | null;
  prop07: string | null;
  prop08: string | null;
  prop09: string | null;
  prop10: string | null;
}

/**
 * API 응답 타입
 */
export interface ItemMasterResponse {
  success: boolean;
  count: number;
  data: ItemMaster[];
  error?: string;
}

/**
 * Item Master 조회 파라미터
 */
export interface ItemMasterParams {
  projectId: string;
  planVer: string;
}

/**
 * Item Master API 호출
 */
export async function fetchItemMaster(
  params: ItemMasterParams
): Promise<ItemMasterResponse> {
  const response = await axios.get<ItemMasterResponse>("/api/item-master", {
    params: {
      project_id: params.projectId,
      plan_ver: params.planVer,
    },
  });
  return response.data;
}

/**
 * Item Master 컴포저블
 */
export function useItemMaster() {
  const data: Ref<ItemMaster[]> = ref([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const count = ref(0);

  /**
   * 데이터 조회
   */
  async function loadData(params: ItemMasterParams) {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetchItemMaster(params);

      if (response.success) {
        data.value = response.data;
        count.value = response.count;
      } else {
        error.value = response.error || "조회 실패";
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : "알 수 없는 오류";
      console.error("Item Master 조회 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  return {
    data,
    loading,
    error,
    count,
    loadData,
  };
}
