/**
 * 월별 매출 차트 데이터 관리
 */
import { ref, type Ref } from "vue";

/**
 * 월별 매출 데이터 타입
 */
export interface SalesData {
  month: string;
  sales: number;
  profit: number;
  cost: number;
}

/**
 * 샘플 월별 매출 데이터 생성
 */
const generateSampleData = (): SalesData[] => {
  return [
    { month: "Jan", sales: 120, profit: 50, cost: 70 },
    { month: "Feb", sales: 200, profit: 80, cost: 120 },
    { month: "Mar", sales: 150, profit: 60, cost: 90 },
    { month: "Apr", sales: 180, profit: 75, cost: 105 },
    { month: "May", sales: 220, profit: 95, cost: 125 },
    { month: "Jun", sales: 240, profit: 110, cost: 130 },
    { month: "Jul", sales: 260, profit: 120, cost: 140 },
    { month: "Aug", sales: 230, profit: 100, cost: 130 },
    { month: "Sep", sales: 210, profit: 90, cost: 120 },
    { month: "Oct", sales: 250, profit: 115, cost: 135 },
    { month: "Nov", sales: 280, profit: 130, cost: 150 },
    { month: "Dec", sales: 300, profit: 140, cost: 160 },
  ];
};

/**
 * 월별 매출 차트 컴포저블
 */
export function useSalesChart() {
  const data: Ref<SalesData[]> = ref([]);
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
      console.error("Sales data 로드 오류:", e);
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
