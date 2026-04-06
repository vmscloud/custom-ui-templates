/**
 * @moz-shared/utils shim
 *
 * Re-exports available functions from @vmscloud packages,
 * implements missing ones locally.
 */

// ── Re-exports from local shims ──
export {
  showMessage,
  showDialog,
  getValue,
  copyToClipboard,
  dayjs,
  generateUUID,
  addTooltipEvent,
  pxToRem,
} from "../moz-wijmo-grid/utils";

// ── Local implementations of missing functions ──

/**
 * convertToInternationalization — i18n 키 변환 (원본과 동일)
 * 이미 adapters에서도 제공하지만, @moz-shared/utils 경로로 import하는 파일용
 */
export function convertToInternationalization(key: string, _format?: string): string {
  if (!key) return "";
  return key
    .replace(/([A-Z])/g, "_$1")
    .toLowerCase()
    .replace(/^_/, "");
}

/**
 * camelToSnake — 카멜 케이스 객체를 스네이크 케이스 객체로 변환
 */
const toSnakeCase = (str: string): string => {
  str = str.replace(/([A-Z]{2,})$/, (match) => `_${match.toLowerCase()}`);
  str = str.replace(/([A-Z][a-z]*)/g, (match) => `_${match.toLowerCase()}`);
  return str.charAt(0) === "_" ? str.slice(1) : str;
};

export const camelToSnake = (
  obj: Record<string, any>
): Record<string, any> => {
  const newObj: Record<string, any> = {};
  Object.keys(obj).forEach((key) => {
    newObj[toSnakeCase(key)] = obj[key];
  });
  return newObj;
};

/**
 * formatCompactNumber — 숫자 포맷 (K/M/B/T 단위 변환)
 */
export type formatCompactNumberParams = {
  returnWhenInvalid?: string | number;
  fixDecimalPoint?: {
    onlyWhenDecimal: boolean;
    decimalPoint: number;
  };
  convertUnit?: {
    standard: number;
    useMillionToTrillion?: boolean;
  };
};

export function formatCompactNumber(
  number: number,
  options: formatCompactNumberParams
) {
  let parseNum: any = Number(number);
  if (Number.isNaN(parseNum)) {
    return options.returnWhenInvalid ? options.returnWhenInvalid : parseNum;
  }

  const numArr = String(number).split(".");

  if (options.fixDecimalPoint) {
    if (options.fixDecimalPoint.onlyWhenDecimal) {
      if (!Number.isInteger(Number(number))) {
        const decimal = numArr[1].slice(
          0,
          options.fixDecimalPoint.decimalPoint
        );
        const correction = "0".repeat(
          options.fixDecimalPoint.decimalPoint - decimal.length
        );
        parseNum = `${Number(numArr[0]).toLocaleString()}.${decimal}${correction}`;
      }
    } else {
      if (!Number.isInteger(Number(number))) {
        const decimal = numArr[1].slice(
          0,
          options.fixDecimalPoint.decimalPoint
        );
        const correction = "0".repeat(
          options.fixDecimalPoint.decimalPoint - decimal.length
        );
        parseNum = `${Number(numArr[0]).toLocaleString()}.${decimal}${correction}`;
      } else {
        parseNum = `${parseNum.toLocaleString()}.${"0".repeat(options?.fixDecimalPoint.decimalPoint)}`;
      }
    }
  }

  const numberedNumber = Number(number);
  if (options?.convertUnit && numberedNumber >= options?.convertUnit.standard) {
    if (
      Math.round(numberedNumber / 1000) < 1_000 ||
      !options?.convertUnit.useMillionToTrillion
    ) {
      parseNum = `${Math.round(numberedNumber / 1000).toLocaleString()}K`;
    } else if (
      Math.round(numberedNumber / 1_000_000) < 1000 &&
      options?.convertUnit.useMillionToTrillion
    ) {
      parseNum = `${Math.round(numberedNumber / 1_000_000).toLocaleString()}M`;
    } else if (
      Math.round(numberedNumber / 1_000_000_000) < 1000 &&
      options?.convertUnit.useMillionToTrillion
    ) {
      parseNum = `${Math.round(numberedNumber / 1_000_000_000).toLocaleString()}B`;
    } else if (
      Math.round(numberedNumber / 1_000_000_000_000) < 1000 &&
      options?.convertUnit.useMillionToTrillion
    ) {
      parseNum = `${Math.round(numberedNumber / 1_000_000_000_000).toLocaleString()}T`;
    }
  }

  if (Number.isNaN(parseNum)) {
    return parseNum;
  }
  return parseNum.toLocaleString();
}

/**
 * bindDropDownEvents — 마우스/터치 이벤트 바인딩
 */
export const bindDropDownEvents = (
  onMouseUp: Function,
  onMouseMove: Function
) => {
  document.addEventListener("mousemove", onMouseMove as any, {
    passive: false,
  });
  document.addEventListener("mouseup", onMouseUp as any);

  if ("ontouchstart" in window) {
    document.addEventListener("touchmove", onMouseMove as any, {
      passive: false,
    });
    document.addEventListener("touchend", onMouseUp as any);
  }
};

/**
 * unbindDropDownEvents — 마우스/터치 이벤트 해제
 */
export const unbindDropDownEvents = (
  onMouseUp: Function,
  onMouseMove: Function
) => {
  document.removeEventListener("mousemove", onMouseMove as any);
  document.removeEventListener("mouseup", onMouseUp as any);

  if ("ontouchstart" in window) {
    document.removeEventListener("touchmove", onMouseMove as any);
    document.removeEventListener("touchend", onMouseUp as any);
  }
};
