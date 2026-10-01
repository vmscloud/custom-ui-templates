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

### Host 에서 번역되는 방식

APS Host 에 Module Federation 으로 올라가면 화면의 `useTranslation()`·`$t` 는 **Host 의 i18next** 를 씁니다. Host 는 접속할 때 용어관리(DB)의 번역을 불러오므로, 운영에서 보이는 번역은 **용어관리에 등록된 값**입니다. `frontend/src/lang/*.json` 은 dev 단독 실행에서만 쓰이고 Host 에서는 쓰이지 않습니다.

**`import i18next from "i18next"` 로 직접 번역하지 마세요.** 리모트 번들에는 Host 와 분리된 i18next 사본이 따로 들어 있어서, 직접 import 하면 Host 번역이 아니라 이 사본으로 번역됩니다. 이 사본은 화면 갱신과 연결되어 있지 않아 첫 진입 때 번역이 반영되지 않고, 다른 메뉴로 이동했다 돌아와야 바뀝니다.

- 컴포넌트·composable 에서는 setup 안에서 `useTranslation()` 의 `t` 를 씁니다.
- 컬럼 정의처럼 번역값으로 만드는 목록은 `computed` 안에서 `t` 를 호출합니다. 언어가 바뀌거나 번역이 적재되면 다시 계산됩니다.
- setup 밖(모듈 최상단 상수, 일반 `.ts` 함수)에서 번역하지 말고, 번역 키만 두었다가 화면에서 `t(key)` 로 바꿉니다.

```ts
// 잘못된 예 — 리모트 사본으로 번역되어 첫 진입 때 반영되지 않음
import i18next from "i18next";
const columns = [{ header: i18next.t("text-item_id") }];

// 올바른 예 — Host i18next 로 번역되고 언어 전환도 반영됨
import { computed } from "vue";
import { useTranslation } from "i18next-vue";
const { t } = useTranslation();
const columns = computed(() => [{ header: t("text-item_id") }]);
```

### 키 네이밍

| 접두어 | 용도 |
|--------|------|
| `text-` | 일반 라벨/헤더/메뉴명 |
| `desc-` | 설명/도움말 텍스트 |
| `msg-` | 사용자에게 보여지는 메시지/알림 |
| `MOZ-` | 공용 상수성 메시지 (`MOZ-DATA_EMPTY` 등) |

새 키는 **APS 용어관리 화면에 프로젝트 키로 등록**해야 운영에서 번역됩니다. ko/en/zh/jp 언어 탭마다 각각 등록하세요. 프로젝트 키는 시스템 기본값으로 fallback 되지 않아서, 등록하지 않은 언어에서는 키 문자열이 그대로 보입니다. 등록 후에는 브라우저를 새로고침해야 반영됩니다. json 파일에만 추가한 키는 dev 에서만 번역됩니다.

### 언어 전환

```ts
import { loadLanguage } from "@/plugins/i18n";
await loadLanguage("en");
```

`useTranslation()` 의 `t` 를 `computed` 안에서 쓰는 composable(예: `useQtyUomQuery`)은 언어가 바뀌면 자동으로 표시값을 다시 계산합니다. `loadLanguage` 는 dev 단독 실행 전용이며, Host 에서는 사용자 언어 설정을 따릅니다.

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
