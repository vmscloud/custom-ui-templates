/**
 * 상품 그리드 데이터 관리
 */
import { ref, type Ref } from "vue";

/**
 * 상품 데이터 타입
 */
export interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  stock: number;
  manufacturer: string;
  releaseDate: Date;
  isActive: boolean;
}

/**
 * 샘플 상품 데이터 생성
 */
const generateSampleData = (count: number = 30): Product[] => {
  const categories = ["전자제품", "가구", "의류", "식품", "도서"];
  const manufacturers = ["제조사A", "제조사B", "제조사C", "제조사D", "제조사E"];
  const productNames = [
    "스마트폰",
    "노트북",
    "태블릿",
    "의자",
    "책상",
    "티셔츠",
    "청바지",
    "과자",
    "음료",
    "소설책",
  ];

  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    name: `${productNames[i % productNames.length]} ${Math.floor(i / productNames.length) + 1}`,
    category: categories[i % categories.length],
    price: Math.floor(Math.random() * 500000) + 10000,
    stock: Math.floor(Math.random() * 100),
    manufacturer: manufacturers[i % manufacturers.length],
    releaseDate: new Date(
      2020 + Math.floor(Math.random() * 5),
      Math.floor(Math.random() * 12),
      Math.floor(Math.random() * 28) + 1
    ),
    isActive: Math.random() > 0.2,
  }));
};

/**
 * 상품 그리드 컴포저블
 */
export function useProductGrid() {
  const data: Ref<Product[]> = ref([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const count = ref(0);

  /**
   * 데이터 로드
   */
  function loadData() {
    loading.value = true;
    error.value = null;

    try {
      // 실제로는 API 호출을 하지만, 여기서는 샘플 데이터 사용
      const products = generateSampleData(30);
      data.value = products;
      count.value = products.length;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "데이터 로드 실패";
      console.error("Product data 로드 오류:", e);
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
