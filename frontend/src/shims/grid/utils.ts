/**
 * 그리드·화면 공용 유틸
 *
 * 레거시 패키지 내부에만 있던 함수들을 로컬로 구현한다.
 */
import djs from "dayjs";
import duration from "dayjs/plugin/duration";

djs.extend(duration);

export const dayjs = djs;

/** 레거시 moz-ui-components 의 generateUUID 와 같은 구현 */
export function generateUUID(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/** 레거시 moz-ui-components 의 pxToRem 과 같은 구현 */
export function pxToRem(px: number, base = 16): number {
  return px / base;
}

/**
 * showMessage — 토스트 알림 (원본: message + isSuccess)
 */
export function showMessage(message: string, isSuccess?: boolean): void {
  // 간단한 콘솔 기반 구현 — Host 환경에서는 Host의 showMessage 사용
  if (isSuccess === false) {
    console.error("[showMessage]", message);
  } else {
    console.log("[showMessage]", message);
  }
}

/**
 * showDialog — 확인 다이얼로그
 */
export function showDialog(options: any): Promise<any> {
  const confirmed = window.confirm(
    options?.message || options?.title || "Confirm?"
  );
  return Promise.resolve(confirmed);
}

/**
 * copyToClipboard — 클립보드 복사
 */
export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text);
  }
  // fallback
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.left = "-9999px";
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
  return Promise.resolve();
}

/**
 * addTooltipEvent — 엘리먼트에 툴팁 이벤트 추가
 */
export function addTooltipEvent(
  el: HTMLElement,
  text: string,
  _options?: any
): void {
  el.title = text;
}

/**
 * removeTooltipEvent — 툴팁 이벤트 제거
 */
export function removeTooltipEvent(el: HTMLElement): void {
  el.title = "";
}

/**
 * getValue — 값이 있으면 리턴하고 없으면 placeholder를 리턴
 * 원본: @moz-shared/utils/data/validation.ts
 */
export const getValue = (value: any, placeholder: any) => {
  if (value === null || value === undefined || value === '' || Number.isNaN(value)) return placeholder;
  return value;
};


/**
 * getWidthByKey — 컬럼 키 기반 너비 조회 (기본값 반환)
 */
export function getWidthByKey(_key: string): number {
  return 120;
}
