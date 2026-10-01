/**
 * 수량 단위(UOM) 공용 컴포저블
 *
 * 원본: packages/aps/src/api/query/getUomType.ts 의 useQtyUomQuery 포팅.
 * 원본은 URL 파라미터 qtyUOM → 서버 GetUomType/{userID}/{menuID} → defaultValue 순.
 * 커스텀 UI는 서버 UOM 저장소(C# APS) 접근이 제한적이므로 URL → localStorage → defaultValue.
 * Host에 module federation으로 로드되면 window.location은 호스트 페이지 URL이라
 * 원본과 동일하게 URL의 qtyUOM 파라미터가 전달됩니다.
 */
import { computed, ref, watch } from "vue";
import { useTranslation } from "i18next-vue";

export type QtyUOMType = "DEFAULT" | "CONVERSION";
export type QtyUOMSourceType = {
  label: string;
  value: QtyUOMType;
  displayValue: string;
};

export interface UseQtyUomOptions {
  menuID?: string;
}

const STORAGE_PREFIX = "moz.customUi.qtyUOM:";

function readFromUrl(): QtyUOMType | null {
  try {
    const params = new URLSearchParams(window.location.search);
    const v = params.get("qtyUOM");
    if (v === "DEFAULT" || v === "CONVERSION") return v;
  } catch {
    // no-op
  }
  return null;
}

function readFromStorage(menuID: string): QtyUOMType | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_PREFIX + menuID);
    if (raw === "DEFAULT" || raw === "CONVERSION") return raw;
  } catch {
    // no-op
  }
  return null;
}

function writeToStorage(menuID: string, value: QtyUOMType): void {
  try {
    window.localStorage.setItem(STORAGE_PREFIX + menuID, value);
  } catch {
    // no-op
  }
}

export function useQtyUomQuery(
  source: QtyUOMType[],
  defaultValue: QtyUOMType,
  option?: UseQtyUomOptions,
) {
  const menuID = option?.menuID || "default";

  const urlVal = readFromUrl();
  const cachedVal = readFromStorage(menuID);
  const initial: QtyUOMType =
    (urlVal && source.includes(urlVal) ? urlVal : null) ||
    (cachedVal && source.includes(cachedVal) ? cachedVal : null) ||
    defaultValue;

  const uomType = ref<QtyUOMType>(initial);

  // Host 에 로드되면 useTranslation() 은 Host 의 i18next 를 쓴다.
  // computed 로 두면 언어 전환·번역 적재 시 i18next-vue 가 다시 계산한다.
  const { t } = useTranslation();

  const qtyUOMSource = computed<QtyUOMSourceType[]>(() =>
    source.map((v) => {
      const display =
        v === "DEFAULT" ? t("text-default_uom") : t("text-conversion_uom");
      // label/displayValue 둘 다 번역값으로 채워서 display-prop 명칭이 달라도 동작.
      return { label: display, value: v, displayValue: display };
    }),
  );

  // URL에 없었던 경우에는 첫 초기화도 캐시로 저장해 두면 새 탭에서도 유지됨
  if (!urlVal) {
    writeToStorage(menuID, initial);
  }

  watch(uomType, (newVal) => {
    writeToStorage(menuID, newVal);
  });

  return { uomType, qtyUOMSource };
}
