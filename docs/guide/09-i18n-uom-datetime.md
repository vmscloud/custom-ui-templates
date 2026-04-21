# 09. i18n · UOM · 날짜

화면을 만들다 보면 반복적으로 부딪히는 세 가지 주제 — **다국어 번역, 수량 단위(UOM), 날짜 처리** — 를 한 곳에 정리합니다.

## i18n

### 설정 위치

- 플러그인: `frontend/src/plugins/i18n.ts` 에서 `i18next` + `I18NextVue` 초기화.
- 리소스: `frontend/src/lang/{ko,en,jp,zh}.json`.

```ts
// src/plugins/i18n.ts 요약
i18next.init({
  fallbackLng: "ko",
  lng: "ko",
  resources: {
    ko: { translation: koData },
    en: { translation: enData },
    zh: { translation: zhData },
    jp: { translation: jpData },
  },
  interpolation: { escapeValue: false },
});
```

### 사용법

```ts
import { useTranslation } from "i18next-vue";
const { t } = useTranslation();
t("text-qty_uom");
```

템플릿에서는 `{{ t('text-my_page_title') }}`. **UI 라벨을 문자열 리터럴로 박지 마세요.**

### 키 네이밍

| 접두어 | 용도 |
|--------|------|
| `text-` | 일반 라벨/헤더/메뉴명 |
| `desc-` | 설명/도움말 텍스트 |
| `msg-` | 사용자에게 보여지는 메시지/알림 |
| `MOZ-` | 공용 상수성 메시지 (`MOZ-DATA_EMPTY` 등) |

새 키는 ko/en/jp/zh 네 파일에 모두 추가해두는 것이 원칙입니다. 당장 번역이 어려우면 한국어/영어만 채우고 나머지는 fallback 되도록 비워두거나 영어 그대로 둡니다.

### 언어 전환

```ts
import { loadLanguage } from "@/plugins/i18n";
await loadLanguage("en");
```

i18next 의 `languageChanged` 이벤트에 훅이 걸린 composable(예: `useQtyUomQuery`)은 자동으로 표시값을 재빌드합니다.

## UOM (수량 단위)

이 저장소 공용 훅: `frontend/src/composables/useQtyUomQuery.ts`.

### 사용법

```ts
import { useQtyUomQuery } from "@/composables/useQtyUomQuery";

const { uomType, qtyUOMSource } = useQtyUomQuery(
  ["DEFAULT", "CONVERSION"],
  "DEFAULT",
  { menuID: "myPageUomType" },
);
```

- `uomType`: `Ref<"DEFAULT" | "CONVERSION">`
- `qtyUOMSource`: `[{ label, value, displayValue }]` 형태. `displayValue` 는 i18n 번역(`text-default_uom`, `text-conversion_uom`)을 사용.

### 값 초기화 순서

1. URL 쿼리 `?qtyUOM=CONVERSION` 이 있으면 그 값.
2. localStorage (`moz.customUi.qtyUOM:<menuID>`) 에 저장된 이전 값.
3. 두 번째 인수 `defaultValue`.

URL 쿼리 우선 규칙 덕분에 Host 가 `?qtyUOM=...` 을 포함해 리모트를 로드하면 자동으로 해당 단위가 선택됩니다.

### Select 바인딩

```vue
<Select
  :label="t('text-qty_uom')"
  v-model="uomType"
  :items-source="qtyUOMSource"
  key-prop="value"
  display-prop="displayValue"
/>
```

### i18n 키 번역값 권장

- `text-default_uom`: 프로젝트 현장에 따라 "EA" 등
- `text-conversion_uom`: 환산 단위 기호 (예: "㎡")

현장 단위를 바꾸고 싶으면 `src/lang/*.json` 의 번역값만 수정. 코드 수정은 필요 없습니다.

## 날짜 (Dayjs)

이 저장소에서 날짜/시간은 기본적으로 **Dayjs** 로 통일합니다.

### 왜 Dayjs인가

- `@vmscloud/moz-ui-components` 의 `DateInput`, `TimePicker` 가 Dayjs 객체를 v-model 로 기대.
- 템플릿 안에서 `.format('YYYY-MM-DD')`, `.add(n, 'day')`, `.startOf('month')` 같은 표현을 쉽게 쓰고 싶음.
- `Date` 객체를 섞어 쓰면 위 호출에서 **런타임 `TypeError`** 가 납니다.

### 초기값 패턴

```ts
import dayjs, { type Dayjs } from "dayjs";

const fromDate = ref<Dayjs>(dayjs().startOf("month"));
const toDate   = ref<Dayjs>(dayjs().endOf("month"));
```

복잡한 state 오브젝트면 타입 명시:

```ts
const reExecuteState = ref<{
  startDate: Dayjs;
  planStartTime: string;
  period: number;
  // ...
}>({
  startDate: dayjs(),
  planStartTime: dayjs().format("HH:mm"),
  period: 7,
});
```

### 서버 전송

서버에는 문자열로 변환해 보냅니다.

```ts
const params = {
  fromDate: fromDate.value.format("YYYY-MM-DD"),
  toDate:   toDate.value.format("YYYY-MM-DD"),
};
```

### 날짜 범위 계산 유틸

월 말까지의 일수 같은 헬퍼는 composable 안에 정의해서 재사용.

```ts
const getDaysUntilEndOfMonth = (today: Date) => {
  const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  return (
    Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)) + 1
  );
};

// watch 로 startDate 변할 때마다 period 재계산
watch(() => state.value.startDate, (newVal) => {
  const dateObj =
    newVal && typeof (newVal as any).toDate === "function"
      ? (newVal as any).toDate()
      : newVal instanceof Date
      ? newVal
      : new Date(newVal as any);
  state.value.period = getDaysUntilEndOfMonth(dateObj);
});
```

## 주·월 포맷

Wijmo 피벗 헤더에는 흔히 `"월:2026-04"`, `"주:2026-14"`, `"날짜:2026-04-20"` 같은 포맷이 쓰입니다. 이 문자열은 백엔드에서 내려주거나 프론트에서 `dayjs(...).format("YYYY-MM")` 으로 생성.

주차는 ISO week 기준 `YYYY-WW` 형식이 일반적입니다.

```ts
const iso = dayjs("2026-04-20").isoWeek();  // dayjs-plugin 필요
const weekStr = `${dayjs("2026-04-20").year()}-${String(iso).padStart(2, "0")}`;
// → "2026-17"
```

프로젝트 정책에 따라 **"W" 접두사 유무** 가 다릅니다. 같은 화면 안에서 두 표기가 섞이지 않도록 한 곳에서 관리하세요.

## 숫자 포맷

- 그리드 컬럼: `dataType="Number" format="n2"` 등.
- `toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })` 같은 표시 변환은 셀 `formatItem` 훅에서 제한적으로 사용.
- **백엔드는 raw `double`** 을 그대로 내려주세요. 서버 `round(x, 2)` 는 누적 오차의 원인입니다.

## 타임존 주의

- 대부분의 화면은 **로컬 시각 표시**를 전제. 서버 UTC 데이터를 쓸 때는 dayjs-plugin-timezone 을 로드하거나 명시적으로 변환.
- `DateInput`/`TimePicker` 출력값을 서버로 보낼 때는 항상 `format("YYYY-MM-DD")` / `format("HH:mm:ss")` 등으로 명시적 문자열화.

다음: [10-debugging](./10-debugging.md) 에서 API 디버깅·데이터 정합성 검증 방법을 다룹니다.
