/**
 * Runtime shim for @vmscloud/moz-wijmo-grid 의 Excel 다운로드 유틸리티.
 *
 * 원본 aps monorepo 의 libraries/moz-wijmo-grid/src/store/excelStore.ts 와
 * 동일한 철학:
 *   "백엔드가 xlsx 를 생성해 스트리밍, 프론트는 받아서 saveAs" 만 수행.
 *
 * 원본이 가진 ExcelQueueManager / SSE / S3 / 잠금 / 세션 등 인프라는 custom-ui-templates
 * 범위에서 불필요하므로 생략. 호출부 API 표면(`downloadBigData(param)`,
 * `createColumnMapForExport(grid)`) 은 유지해 추후 공식 인프라가 npm 으로
 * 열리면 이 shim 만 교체하면 된다.
 */
import { saveAs } from "file-saver";
import axios from "axios";

/** 원본 createColumnMapForExport 결과 타입. */
export type ColumnMap = Record<string, string>;

/** 원본 downloadBigData 가 받던 파라미터. */
export interface DownloadBigDataParam {
  /** 생성할 파일명 (확장자 제외). 오늘 날짜가 자동으로 suffix 로 붙는다. */
  file_name: string;
  /** 컬럼 바인딩 → 헤더 라벨 맵. 백엔드가 엑셀 헤더에 사용. */
  column_map?: ColumnMap;
  /** Python 백엔드 xlsx 엔드포인트 (POST, binary 응답). */
  proxy_path?: string;
  /** 전체 URL 직접 지정 (원본 호환용). 현재는 proxy_path 를 권장. */
  data_path?: string;
  /** HTTP method. 기본 POST. */
  data_method?: "GET" | "POST";
  /** 요청 바디. 문자열(JSON) 또는 객체. */
  data_parameter?: string | Record<string, any>;
  /** client 식별자 — 원본과 호환. shim 에선 사용만 하고 따로 의미 부여 안 함. */
  client_id?: string;
  /** 원본 호환 플래그들. shim 에선 무시. */
  is_stream?: boolean;
  data_server?: string;
  project_id?: string;
  api_key?: string;
  file_format?: "excel" | "csv";
}

const todayStamp = () => {
  const d = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
};

/**
 * downloadBigData — 원본 APS queryStore.downloadBigData 와 동일한 시그니처.
 *
 * 흐름 (원본 excelStore.ts:download 와 동일):
 *   1. proxy_path 로 POST(binary) — 바디에는 column_map + data_parameter
 *   2. 백엔드(Python FastAPI) 가 C# APS 호출 → JSON → openpyxl 로 xlsx 생성 → StreamingResponse
 *   3. 프론트는 받은 blob 을 saveAs() 로 브라우저 다운로드
 *
 * 파일명 규칙: "{file_name}_{YYYYMMDD}.xlsx"
 */
export const downloadBigData = async (
  param: DownloadBigDataParam,
): Promise<{ queued: true }> => {
  const url = param.proxy_path ?? param.data_path;
  if (!url) {
    console.error("[downloadBigData] proxy_path 또는 data_path 필수");
    return { queued: true };
  }

  const method = (param.data_method ?? "POST").toUpperCase();

  // data_parameter 는 C# 으로 forward 될 원본 쿼리 파라미터.
  //   column_map 은 백엔드에서 xlsx 헤더/컬럼 순서 결정에 사용.
  const dataParam =
    typeof param.data_parameter === "string" && param.data_parameter.length > 0
      ? JSON.parse(param.data_parameter)
      : param.data_parameter ?? {};

  const body = {
    column_map: param.column_map ?? {},
    data_parameter: dataParam,
    file_name: param.file_name,
  };

  const fileName = `${param.file_name}_${todayStamp()}.xlsx`;

  try {
    const resp = await axios.request<Blob>({
      method,
      url,
      data: method === "GET" ? undefined : body,
      params: method === "GET" ? body : undefined,
      responseType: "blob",
      // 쿠키 기반 인증 (프록시 세션). 프론트와 백엔드 같은 오리진이라 기본 동작.
      withCredentials: true,
    });
    saveAs(resp.data, fileName);
  } catch (e) {
    console.error("[downloadBigData] xlsx 다운로드 실패:", e);
  }

  return { queued: true };
};

/**
 * createColumnMapForExport — wijmo FlexGrid 인스턴스에서 컬럼 바인딩/헤더 맵 생성.
 *   원본 excelStoreSetup().createColumnMapForExport 와 동일한 형태를 반환.
 */
export const createColumnMapForExport = (grid: any): ColumnMap => {
  const map: ColumnMap = {};
  const columns = grid?.columns;
  if (!columns) return map;
  const len = typeof columns.length === "number" ? columns.length : 0;
  for (let i = 0; i < len; i++) {
    const col = columns[i];
    if (!col) continue;
    // visible === false 면 export 제외 (원본 동작과 일치)
    if (col.visible === false) continue;
    const binding: string | undefined = col.binding;
    if (!binding) continue;
    map[binding] = col.header ?? binding;
  }
  return map;
};
