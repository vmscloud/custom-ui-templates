import { ref } from "vue";
import type { Rule } from "@vmscloud/moz-ui-components";

// Select & MultiSelect용 옵션 데이터
export interface SelectOption {
  label: string;
  value: string | number;
}

// TreeSelect용 데이터 (itemsSource 형식)
export interface TreeSelectItem {
  code: string;
  name: string;
  categoryLv1ID: string;
  categoryLv1Label?: string;
  categoryLv2ID: string;
  categoryLv2Label?: string;
}

/**
 * UI Components Showcase를 위한 샘플 데이터 및 상태 관리
 */
export function useComponentsShowcase() {
  // Form Controls 상태
  const buttonClickCount = ref(0);
  const toggleValue = ref(false);
  const inputValue = ref("");
  const checkboxValue = ref(false);
  const radioValue = ref("option1");
  const numberValue = ref(0);
  const passwordValue = ref("");
  const sliderValue = ref(50);
  const textareaValue = ref("");

  // Selection Controls 상태
  const selectValue = ref<string | number | object | null>(null);
  const multiSelectValue = ref<string[]>([]);
  const treeSelectValue = ref<string[]>([]);

  // Date/Time 상태
  const calendarValue = ref<Date>(new Date());
  const dateInputValue = ref<Date | null>(null);

  // Layout & Navigation 상태
  const activeTabId = ref("tab1");
  const popupVisible = ref(false);

  // SearchBox 상태
  const searchBoxModel = ref<Record<string, unknown> | null>(null);
  const searchBoxInput = ref("");

  // Validator 상태
  const validatorInput = ref("");

  // Select 옵션 데이터 (itemsSource 형식)
  const selectOptions: Record<string, unknown>[] = [
    { label: "옵션 1", value: "option1" },
    { label: "옵션 2", value: "option2" },
    { label: "옵션 3", value: "option3" },
    { label: "옵션 4", value: "option4" },
  ];

  // MultiSelect 옵션 데이터 (itemsSource 형식)
  const multiSelectOptions: Record<string, unknown>[] = [
    { label: "서울", value: "seoul" },
    { label: "부산", value: "busan" },
    { label: "대구", value: "daegu" },
    { label: "인천", value: "incheon" },
    { label: "광주", value: "gwangju" },
    { label: "대전", value: "daejeon" },
  ];

  // TreeSelect 데이터 (itemsSource 형식 - 3레벨 구조)
  const treeSelectData: TreeSelectItem[] = [
    // Level 1: 회사
    {
      code: "company",
      name: "회사",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "",
    },
    // Level 2: 개발팀
    {
      code: "dev",
      name: "개발팀",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "dev",
      categoryLv2Label: "개발팀",
    },
    // Level 3: 개발팀 하위
    {
      code: "frontend",
      name: "프론트엔드",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "dev",
      categoryLv2Label: "개발팀",
    },
    {
      code: "backend",
      name: "백엔드",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "dev",
      categoryLv2Label: "개발팀",
    },
    // Level 2: 디자인팀
    {
      code: "design",
      name: "디자인팀",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "design",
      categoryLv2Label: "디자인팀",
    },
    // Level 3: 디자인팀 하위
    {
      code: "uiux",
      name: "UI/UX",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "design",
      categoryLv2Label: "디자인팀",
    },
    {
      code: "graphic",
      name: "그래픽",
      categoryLv1ID: "company",
      categoryLv1Label: "회사",
      categoryLv2ID: "design",
      categoryLv2Label: "디자인팀",
    },
    // Level 1: 외부
    {
      code: "external",
      name: "외부",
      categoryLv1ID: "external",
      categoryLv1Label: "외부",
      categoryLv2ID: "",
    },
    // Level 2: 외부 하위
    {
      code: "partner",
      name: "파트너",
      categoryLv1ID: "external",
      categoryLv1Label: "외부",
      categoryLv2ID: "partner",
      categoryLv2Label: "파트너",
    },
    {
      code: "customer",
      name: "고객",
      categoryLv1ID: "external",
      categoryLv1Label: "외부",
      categoryLv2ID: "customer",
      categoryLv2Label: "고객",
    },
  ];

  // Tab 데이터 (itemSource 형식 - id와 text 속성 필요)
  const tabItems = [
    { id: "tab1", text: "첫 번째 탭" },
    { id: "tab2", text: "두 번째 탭" },
    { id: "tab3", text: "세 번째 탭" },
  ];

  // BreadCrumb 데이터 (itemSource는 string[] 형식)
  const breadcrumbItems = [
    "홈",
    "템플릿",
    "기본 컴포넌트",
    "컴포넌트 쇼케이스",
  ];

  // Validator 규칙
  const validatorRules: Rule[] = [
    {
      message: "필수 입력 항목입니다",
      type: "blur",
      validator: (value: string | string[]) => !!value,
    },
    {
      message: "최소 3자 이상 입력해주세요",
      type: "blur",
      validator: (value: string | string[]) => typeof value === "string" && value.length >= 3,
    },
  ];

  // 버튼 클릭 핸들러
  const handleButtonClick = () => {
    buttonClickCount.value++;
  };

  // 팝업 토글
  const togglePopup = () => {
    popupVisible.value = !popupVisible.value;
  };

  return {
    // Form Controls 상태
    buttonClickCount,
    toggleValue,
    inputValue,
    checkboxValue,
    radioValue,
    numberValue,
    passwordValue,
    sliderValue,
    textareaValue,

    // Selection Controls 상태
    selectValue,
    multiSelectValue,
    treeSelectValue,

    // Date/Time 상태
    calendarValue,
    dateInputValue,

    // Layout & Navigation 상태
    activeTabId,
    popupVisible,

    // SearchBox 상태
    searchBoxModel,
    searchBoxInput,

    // Validator 상태
    validatorInput,

    // 옵션 데이터
    selectOptions,
    multiSelectOptions,
    treeSelectData,
    tabItems,
    breadcrumbItems,
    validatorRules,

    // 핸들러
    handleButtonClick,
    togglePopup,
  };
}
