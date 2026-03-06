import { dayjs } from '@moz-shared/utils';
import { cloneDeep } from 'es-toolkit';
import * as go from 'gojs';
import { onBeforeUnmount, onMounted, Ref, ref, toRaw, watch } from 'vue';

export type BomMapDataSource = {
  bom_id: string;
  bom_type: string;
  from_item_id: string;
  from_site_id: string;
  from_buffer_id: string;
  from_item_type: string;
  from_qty: number;
  to_item_id: string;
  to_site_id: string;
  to_buffer_id: string;
  to_item_type: string;
  to_qty: number;
  from_buffer_seq: number;
  to_buffer_seq: number;
  path_yn: boolean;
  to_path_yn: boolean;
  res_yn: boolean;
  res_list: string;
  from_item_name: string;
  from_site_name: string;
  to_item_name: string;
  to_site_name: string;
  from_unpeg_qty: number;
  to_unpeg_qty: number;
  from_peg_qty: number;
  to_peg_qty: number;
  from_plan_qty: number;
  to_plan_qty: number;
  from_plan_unit_qty: number;
  to_plan_unit_qty: number;
  from_plan_gap_sec: number;
  to_plan_gap_sec: number;
  routing_tat: number;
  to_min_cum_tat: number;
  to_max_cum_tat: number;
  from_plan_datetime: string;
  to_plan_datetime: string;
  from_target_datetime: string;
  from_extd_target_datetime: string;
  to_target_datetime: string;
  to_extd_target_datetime: string;
  qty_on_left: boolean;
}[];

export type ShortLogDataSource = {
  project_id: string;
  plan_ver: string;
  ref_plan_ver: string;
  stage_id: string;
  module_id: string;
  demand_id: string;
  demand_item_id: string;
  due_date: string;
  demand_qty: number;
  short_type: string;
  short_category: string;
  short_reason: string;
  short_detail_info: string;
  short_qty: number;
  isb_id: string;
  bom_id: string;
  routing_id: string;
  oper_id: string;
  res_id: string;
  from_late_datetime: string;
  to_late_datetime: string;
  short_cnt: number;
  phase_no: number;
  retry_cnt: number;
}[];

export interface BomMapPlanCycleData {
  planVer: string;
  planCycleID: string;
  fromDate: string;
  toDate: string;
  projectID: any;
  demandID: any;
}

export interface BomMapUserAction {
  click: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
  doubleClick: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
  hover: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
  clickAlert: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
  hoverAlert: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
  hoverLabel: {
    current: {
      node: null | go.Node;
    };
    prev: {
      node: null | go.Node;
    };
  };
}

export const useBomMapInterfaceQuery = ({
  bomNetworkInfos,
  shortLogs,
  planCycleData,
  initKey,
  userID,
}: {
  bomNetworkInfos: Ref<BomMapDataSource>;
  shortLogs: Ref<ShortLogDataSource>;
  planCycleData: Ref<BomMapPlanCycleData>;
  initKey: Ref<any>;
  userID: Ref<string>;
}) => {
  const modelData = ref<{ nodeDataArray: any; linkDataArray: any }>({
    nodeDataArray: [],
    linkDataArray: [],
  });

  const userAction = ref<BomMapUserAction>({
    click: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
    doubleClick: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
    hover: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
    clickAlert: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
    hoverAlert: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
    hoverLabel: {
      current: {
        node: null,
      },
      prev: {
        node: null,
      },
    },
  });

  const currentConfigsVersion = '0.1.1';

  const diagramConfigs = ref({
    bufferNode: {
      label1: 'itemID',
      label2: 'siteID',
    },
    bomNode: {
      headerLabel1: 'hide',
      label1: 'bomID',
    },
    qtyUnit: 'planQty',
    layoutMode: 0,
    initialViewPoint: 'fitToBom',
    configsVersion: '0.1.1',
  });
  const diagramConfigsOri = cloneDeep(toRaw(diagramConfigs.value));

  const interfaceConfigs = ref({
    window: {
      demandInfo: {
        opacity: 100,
        isShown: true,
      },
      nodeInfo: {
        opacity: 100,
        isShown: true,
      },
      config: {
        opacity: 100,
        isShown: false,
      },
      overview: {
        opacity: 100,
        isShown: false,
      },
    },
    isToolbarExpanded: true,
    configsVersion: '0.1.1',
  });
  const interfaceConfigsOri = cloneDeep(toRaw(interfaceConfigs.value));

  const isShiftPressing = ref(false);
  const isInitialized = ref(false);
  const contextRef = ref();
  const nodeFloatingRef = ref();
  const alertInfoFloatingRef = ref();
  const labelFloatingRef = ref();
  const alertLabelFloatingRef = ref();
  const alignOrientation = ref<'Vertical' | 'Horizontal'>('Horizontal');
  const isHighlighted = ref(false);
  const demandNodeKey = ref();
  const startBufferKey = ref();
  const isDragMode = ref(false);
  const currentScale = ref(0);

  /**
   * API를 요청하여 받아온 데이터를 GoJS에 맞게 가공하는 함수 실행
   */
  onMounted(() => {
    dataModeler();
  });

  watch([bomNetworkInfos], () => {
    dataModeler();
  });

  /**
   * API를 요청하여 받아온 데이터를 GoJS에 맞게 가공하는 함수
   */
  const dataModeler = () => {
    const nodeMap = new Map();
    const linkMap = new Map();

    bomNetworkInfos.value?.forEach((data, idx) => {
      if (idx === 0) {
        demandNodeKey.value = data.to_item_id + data.to_site_id + data.to_buffer_id;
      }
      if (idx === bomNetworkInfos.value.length - 1) {
        startBufferKey.value = `${data.from_buffer_id}BufGroup`;
      }

      // Sequence Group
      nodeMap.set(`${data.from_buffer_seq}SeqGroup`, {
        key: `${data.from_buffer_seq}SeqGroup`,
        isGroup: true,
        category: 'Sequence',
      });
      nodeMap.set(`${data.to_buffer_seq}SeqGroup`, {
        key: `${data.to_buffer_seq}SeqGroup`,
        isGroup: true,
        category: 'Sequence',
      });
      nodeMap.set(`${data.from_buffer_seq}∥${data.to_buffer_seq}SeqGroup`, {
        key: `${data.from_buffer_seq}∥${data.to_buffer_seq}SeqGroup`,
        isGroup: true,
        category: 'Sequence',
      });

      // Buffer Group
      nodeMap.set(`${data.from_buffer_id}BufGroup`, {
        key: `${data.from_buffer_id}BufGroup`,
        isGroup: true,
        label: data.from_buffer_id,
        category: 'Buffer',
        group: `${data.from_buffer_seq}SeqGroup`,
      });
      nodeMap.set(`${data.to_buffer_id}BufGroup`, {
        key: `${data.to_buffer_id}BufGroup`,
        isGroup: true,
        label: data.to_buffer_id,
        category: 'Buffer',
        group: `${data.to_buffer_seq}SeqGroup`,
      });

      // Bom Group
      nodeMap.set(`${data.to_buffer_id + data.from_buffer_id}BomGroup`, {
        key: `${data.to_buffer_id + data.from_buffer_id}BomGroup`,
        isGroup: true,
        label: '',
        category: 'Bom',
        group: `${data.from_buffer_seq}∥${data.to_buffer_seq}SeqGroup`,
      });

      // Buffer Node
      nodeMap.set(`${data.from_item_id}∥${data.from_site_id}∥${data.from_buffer_id}`, {
        type: 'buffer',
        key: data.from_item_id + data.from_site_id + data.from_buffer_id,
        category: 'Buffer',
        group: `${data.from_buffer_id}BufGroup`,
        iconColor: data.from_item_type === 'Material' ? 'GRAY' : 'WHITE',
        isDemandNode: idx === 0,

        bufferID: data.from_buffer_id,
        itemID: data.from_item_id,
        itemName: data.from_item_name || data.from_item_id,
        siteID: data.from_site_id,
        siteName: data.from_site_name || data.from_site_id,
        unpegQty: data.from_unpeg_qty ? data.from_unpeg_qty : null,
        pegQty: data.from_peg_qty,
        planQty: data.from_plan_qty,
        planUnitQty: data.from_plan_unit_qty,
        planGap:
          typeof data.from_plan_gap_sec === 'number'
            ? (Math.ceil(dayjs.unix(data.from_plan_gap_sec).diff(dayjs.unix(0), 'days', true) * 10) / 10).toFixed(1)
            : null,
        minCumTat: '0 Day 00:00',
        maxCumTat: '0 Day 00:00',
        planDatetime:
          dayjs(data.from_plan_datetime).unix() >= 0 ? dayjs(data.from_plan_datetime).format('YYYY-MM-DD HH:mm') : '',
        targetDatetime: data.from_target_datetime ? dayjs(data.from_target_datetime).format('YYYY-MM-DD HH:mm') : '',
        extdTargetDatetime: data.from_extd_target_datetime
          ? dayjs(data.from_extd_target_datetime).format('YYYY-MM-DD HH:mm')
          : '',
      });
      nodeMap.set(`${data.to_item_id}∥${data.to_site_id}∥${data.to_buffer_id}`, {
        type: 'buffer',
        key: data.to_item_id + data.to_site_id + data.to_buffer_id,
        category: 'Buffer',
        group: `${data.to_buffer_id}BufGroup`,
        iconColor: data.to_item_type === 'Material' ? 'GRAY' : 'WHITE',
        isDemandNode: idx === 0,

        bufferID: data.to_buffer_id,
        itemID: data.to_item_id,
        itemName: data.to_item_name || data.to_item_id,
        siteID: data.to_site_id,
        siteName: data.to_site_name || data.to_site_id,
        unpegQty: data.to_unpeg_qty ? data.to_unpeg_qty : null,
        pegQty: data.to_peg_qty,
        planQty: data.to_plan_qty,
        planUnitQty: data.to_plan_unit_qty,
        planGap:
          typeof data.to_plan_gap_sec === 'number'
            ? (Math.ceil(dayjs.unix(data.to_plan_gap_sec).diff(dayjs.unix(0), 'days', true) * 10) / 10).toFixed(1)
            : null,
        minCumTat:
          typeof data.to_min_cum_tat === 'number'
            ? Math.floor(data.to_min_cum_tat / (60 * 60 * 24)) +
              dayjs
                .duration(Math.floor(Math.abs(data.to_min_cum_tat) % (60 * 60 * 24)), 'seconds')
                .format(' [Day] HH:mm')
            : '',
        maxCumTat:
          typeof data.to_max_cum_tat === 'number'
            ? Math.floor(data.to_max_cum_tat / (60 * 60 * 24)) +
              dayjs
                .duration(Math.floor(Math.abs(data.to_max_cum_tat) % (60 * 60 * 24)), 'seconds')
                .format(' [Day] HH:mm')
            : '',
        planDatetime:
          dayjs(data.to_plan_datetime).unix() >= 0 ? dayjs(data.to_plan_datetime).format('YYYY-MM-DD HH:mm') : '',
        targetDatetime: data.to_target_datetime ? dayjs(data.to_target_datetime).format('YYYY-MM-DD HH:mm') : '',
        extdTargetDatetime: data.to_extd_target_datetime
          ? dayjs(data.to_extd_target_datetime).format('YYYY-MM-DD HH:mm')
          : '',
      });

      // Bom Node
      nodeMap.set(data.bom_id, {
        type: 'bom',
        key: data.bom_id,
        bomID: data.bom_id,
        // label: data.bom_id,
        label: '',
        category: 'Bom',
        group: `${data.to_buffer_id + data.from_buffer_id}BomGroup`,
        iconColor: data.res_yn ? 'LIGHT_GRAY' : 'WHITE',
        resYn: data.res_yn,
        routingTat:
          typeof data.routing_tat === 'number'
            ? Math.floor(data.routing_tat / (60 * 60 * 24)) +
              dayjs.duration(Math.floor(Math.abs(data.routing_tat) % (60 * 60 * 24)), 'seconds').format(' [Day] HH:mm')
            : '',
      });

      // Link : FromISB -> Bom
      linkMap.set(data.from_item_id + data.from_site_id + data.from_buffer_id + data.bom_id, {
        from: data.from_item_id + data.from_site_id + data.from_buffer_id,
        to: data.bom_id,
        label: data.from_qty !== data.to_qty && data.qty_on_left ? `${data.from_qty} : ${data.to_qty}` : '',
        isTargetPath: data.path_yn,
        isForcePath: false,
        bomType: data.bom_type?.toUpperCase(),
      });

      // Link : Bom -> ToISB
      linkMap.set(data.bom_id + data.to_item_id + data.to_site_id + data.to_buffer_id, {
        from: data.bom_id,
        to: data.to_item_id + data.to_site_id + data.to_buffer_id,
        label: data.from_qty !== data.to_qty && !data.qty_on_left ? `${data.from_qty} : ${data.to_qty}` : '',
        isTargetPath: data.path_yn,
        isForcePath: data.to_path_yn,
        bomType: data.bom_type?.toUpperCase(),
      });
    });

    shortLogs.value?.forEach((shortLog) => {
      let temp: any;
      // 경고 알림의 위치 지정: FromISB || Bom
      if (shortLog.routing_id) {
        temp = nodeMap.get(shortLog.bom_id);
      } else {
        temp = nodeMap.get(shortLog.isb_id);
      }

      /**
       * @todo 나중에 정합성을 반드시 보장받을 수 있으면 아래 예외처리는 제거해야 함.
       * - 원래 정합성이 맞는 데이터를 보내주기로 했었는데 깨진 경우 예외처리함.
       * - 현재는 정합성이 안 맞으면 short이 있지만 표현이 안될 것임.
       *
       * 참고. short이 없었으면 shortLogs를 받았을 때부터 빈 배열로 받아야 함. 키가 안 맞는 것으로 short이 없음을 표현하는 것이 부자연스러움.
       */
      if (!temp) {
        console.error(
          'shortLog의 bom_id, isb_id 데이터의 정합성이 안 맞습니다. 올바르게 맵핑되도록 백엔드 혹은 엔진에게 요청하십시오.',
        );
        return;
      }

      // 경고 알림에 대한 데이터를 nodeMap에 추가
      if (temp.hasOwnProperty('alerts')) {
        temp.alerts.push({
          label: shortLog.short_reason,
          color: shortLog.short_type?.toUpperCase(),
          shortType: shortLog.short_type,
          ...shortLog,
        });
      } else {
        temp.alerts = [
          {
            label: shortLog.short_reason,
            color: shortLog.short_type?.toUpperCase(),
            shortType: shortLog.short_type,
            ...shortLog,
          },
        ];
      }
    });

    const sortOrder = ['Short', 'Remain', 'Late'];
    // 경고를 Short를 우선적으로 보여주도록 정렬
    nodeMap.forEach((value) => {
      if (!value.isGroup && value.alerts?.length) {
        value.alerts = value.alerts.sort(
          (a: any, b: any) => sortOrder.indexOf(a.shortType) - sortOrder.indexOf(b.shortType),
        );
      }
    });

    // 가공한 데이터를 Map에서 배열로 변환
    const nodeDataArray = Array.from(nodeMap.values());
    const linkDataArray = Array.from(linkMap.values());

    // 가공한 데이터를 저장
    modelData.value = { nodeDataArray, linkDataArray };
  };

  /**
   * 다이어그램 관련 설정과 인터페이스 관련 설정을 가져오는 코드
   */
  onMounted(() => {
    const getDiagramConfigs = window.localStorage.getItem(
      `bom-map-diagram-configs-${planCycleData.value?.projectID || 'unknown'}-${userID.value || 'unknown'}`,
    );
    if (getDiagramConfigs) {
      diagramConfigs.value = JSON.parse(getDiagramConfigs);
    }

    const getInterfaceConfigs = window.localStorage.getItem(
      `bom-map-interface-configs-${planCycleData.value?.projectID || 'unknown'}-${userID.value || 'unknown'}`,
    );
    if (getInterfaceConfigs) {
      interfaceConfigs.value = JSON.parse(getInterfaceConfigs);
    }

    // 설정 버전이 다르면 설정을 초기화
    if (
      !diagramConfigs.value?.hasOwnProperty('configsVersion') ||
      diagramConfigs.value?.configsVersion !== currentConfigsVersion
    ) {
      diagramConfigs.value = diagramConfigsOri;
    }
    if (
      !interfaceConfigs.value?.hasOwnProperty('configsVersion') ||
      interfaceConfigs.value?.configsVersion !== currentConfigsVersion
    ) {
      interfaceConfigs.value = interfaceConfigsOri;
    }
  });

  /**
   * 다른 페이지 이동 시, 혹은 브라우저를 끌 때 설정값을 저장하는 코드
   */
  const beforeUnload = () => {
    window.localStorage.setItem(
      `bom-map-diagram-configs-${planCycleData.value?.projectID || 'unknown'}-${userID.value || 'unknown'}`,
      JSON.stringify(diagramConfigs.value),
    );
    window.localStorage.setItem(
      `bom-map-interface-configs-${planCycleData.value?.projectID || 'unknown'}-${userID.value || 'unknown'}`,
      JSON.stringify(interfaceConfigs.value),
    );

    isInitialized.value = false;
  };

  onMounted(() => {
    window.addEventListener('unload', () => {
      beforeUnload();
    });
  });

  onBeforeUnmount(() => {
    beforeUnload();
  });

  /**
   * 글로벌 변수의 Setter 함수
   */
  const setData = (callback: Function) => {
    // 변수 조작을 추적하는 개발용 코드
    // const code = callback.toString().split(/\r?\n/);
    //   code
    //     .slice(1, code.length - 1)
    //     .toString()
    //     .trim()
    // );

    callback();
  };
  return {
    planCycleData,
    isShiftPressing,
    modelData,
    isInitialized,
    contextRef,
    nodeFloatingRef,
    alertInfoFloatingRef,
    labelFloatingRef,
    alertLabelFloatingRef,
    userAction,
    alignOrientation,
    isHighlighted,
    demandNodeKey,
    startBufferKey,
    isDragMode,
    interfaceConfigs,
    currentScale,
    diagramConfigs,
    userID,
    initKey,
    diagramConfigsOri,
    setData,
  };
};

export type IBomMapIntefaceQuery = ReturnType<typeof useBomMapInterfaceQuery>;
