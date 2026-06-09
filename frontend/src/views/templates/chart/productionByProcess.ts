/**
 * 공정별 생산량 차트 데이터 관리
 */
import { ref, type Ref } from "vue";

/**
 * 공정별 생산량 데이터 타입
 */
export interface ProductionData {
  process: string;
  planQty: number;
  actualQty: number;
}

/**
 * 샘플 공정별 생산량 데이터 생성
 */
const generateSampleData = (): ProductionData[] => {
  return [
    { process: "절삭", planQty: 1200, actualQty: 1150 },
    { process: "용접", planQty: 980, actualQty: 1020 },
    { process: "조립", planQty: 1500, actualQty: 1410 },
    { process: "도장", planQty: 760, actualQty: 730 },
    { process: "검사", planQty: 1340, actualQty: 1360 },
    { process: "포장", planQty: 1100, actualQty: 1080 },
  ];
};

/**
 * 공정별 생산량 차트 컴포저블
 */
export function useProductionByProcess() {
  const data: Ref<ProductionData[]> = ref([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * 데이터 로드
   */
  function loadData() {
    loading.value = true;
    error.value = null;

    try {
      // 실제로는 API 호출을 하지만, 여기서는 샘플 데이터 사용
      data.value = generateSampleData();
    } catch (e) {
      error.value = e instanceof Error ? e.message : "데이터 로드 실패";
      console.error("Production data 로드 오류:", e);
    } finally {
      loading.value = false;
    }
  }

  return {
    data,
    loading,
    error,
    loadData,
  };
}
