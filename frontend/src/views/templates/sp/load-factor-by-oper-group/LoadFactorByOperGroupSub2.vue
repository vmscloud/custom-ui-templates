<template>
  <div class="chart-container" ref="chartContainerRef">
    <div
      v-if="
        detailChartDataSource.length &&
        !loading &&
        clickedSeriesData &&
        detailChartSelectSource.length
      "
      class="chart-wrapper"
    >
      <v-chart
        class="chart"
        :option="chartOption"
        autoresize
        ref="chartRef"
      />
      <!-- ✅ 차트 우측 상단에 Select 오버레이 -->
      <div class="chart-date-input">
        <Select
          v-model="localClickedSeriesData"
          :items-source="detailChartSelectSource"
          :display-prop="'oper_group_id'"
          :key-prop="'oper_group_id'"
          @change="onSelectChange"
        />
      </div>
    </div>
    <div v-else class="grid-empty load_factor_by_oper_group-loading">
      <EmptyState
        :headerMsg="t('msg-empty_state-data_empty_header')"
        :contentMsg="t('msg-select_oper_group')"
        :is-read-only="true"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
import VChart from 'vue-echarts';
import { use } from '@vmscloud/moz-ui-chart/echarts/core';
import { CanvasRenderer } from '@vmscloud/moz-ui-chart/echarts/renderers';
import { BarChart, LineChart } from '@vmscloud/moz-ui-chart/echarts/charts';
import {
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
} from '@vmscloud/moz-ui-chart/echarts/components';
import { EmptyState, Select } from '@vmscloud/moz-ui-components';
import { useTranslation } from 'i18next-vue';
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
]);

// ===== Props & Emits =====
const props = defineProps<{
  detailChartDataSource: any[];
  originDetailChartDataSource: any[];
  loading: boolean;
  groupLoading: boolean;
  clickedSeriesData: string;
  detailChartSelectSource: { oper_group_id: string }[];
}>();

const emit = defineEmits<{
  (e: 'update:clickedSeriesData', val: string): void;
}>();

const { t } = useTranslation(); // 다국어

// ===== Local State =====
const localClickedSeriesData = ref(props.clickedSeriesData);
const chartRef = ref<any>(null);

watch(() => props.clickedSeriesData, (val) => {
  localClickedSeriesData.value = val;
});

const onSelectChange = () => {
  if (localClickedSeriesData.value) {
    emit('update:clickedSeriesData', localClickedSeriesData.value);
  }
};

// ✅ 차트 컨테이너 ref와 동적 visible count
const chartContainerRef = ref<HTMLElement | null>(null);
const chartContainerWidth = ref(1200); // 기본값

// ✅ 차트 너비에 따른 visible bar count 계산
const calculateVisibleBarCount = () => {
  if (!chartContainerRef.value) return 10;

  const containerWidth = chartContainerRef.value.offsetWidth;
  chartContainerWidth.value = containerWidth;

  // bar width (80px) + gap (40px) = 120px per bar
  // grid left (60px) + right (40px) = 100px 여백
  const availableWidth = containerWidth - 100;
  const barWidth = 55; // 80px bar + 40px gap

  const count = Math.floor(availableWidth / barWidth);
  return Math.max(count, 5); // 최소 5개는 보이도록
};

const dynamicVisibleCount = ref(calculateVisibleBarCount());

// ✅ Resize Observer 설정
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  dynamicVisibleCount.value = calculateVisibleBarCount();

  if (chartContainerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      dynamicVisibleCount.value = calculateVisibleBarCount();
    });
    resizeObserver.observe(chartContainerRef.value);
  }
});

onUnmounted(() => {
  if (resizeObserver && chartContainerRef.value) {
    resizeObserver.unobserve(chartContainerRef.value);
    resizeObserver.disconnect();
  }
});

// ✅ 색상 팔레트 정의
const colorPalette = ['#3A71F099', '#4AB6C4A3', '#A5D75BA3', '#FEB34EA3', '#DC5A5AA3'];

// ✅ 시리즈명에서 숫자 추출 함수 (범례 정렬과 동일)
const getSeriesNumber = (str: string) => {
  const match = str.match(/^(\d+)\./);
  return match ? parseInt(match[1], 10) : Infinity;
};

const chartOption = computed(() => {
  if (!props.detailChartDataSource.length) return {};

  // 날짜별로 정렬
  const sortedDates = [
    ...new Set(
      props.detailChartDataSource
        .filter((d: any) => d.date) // date가 있는 항목만
        .map((d: any) => d.date)
        .sort(),
    ),
  ];

  // item_group_id별 고유 목록 (숫자 순 정렬)
  const itemGroups = [
    ...new Set(props.detailChartDataSource.map((d: any) => d.item_group_id)),
  ]
    .filter((id) => id !== 'TOTAL' && id !== t('text-chart-unclassified') && id !== t('text-not_set') && id !== '')
    .sort((a, b) => getSeriesNumber(a) - getSeriesNumber(b));

  // 시리즈 데이터 구성
  const barSeries = itemGroups.map((itemGroup, seriesIndex) => {
    const data = sortedDates.map((date, _dataIndex) => {
      const row = props.detailChartDataSource.find(
        (d: any) => d.date === date && d.item_group_id === itemGroup,
      );
      const value = row ? row.plan_qty : 0;

      // 현재 데이터 포인트의 모든 시리즈 값 확인 (역순으로 확인) - borderRadius 계산
      let isTopOfStack = false;
      for (let i = itemGroups.length - 1; i >= 0; i--) {
        const checkRow = props.detailChartDataSource.find(
          (d: any) => d.date === date && d.item_group_id === itemGroups[i],
        );
        const checkValue = checkRow ? checkRow.plan_qty : 0;
        if (checkValue != null && checkValue > 0) {
          isTopOfStack = i === seriesIndex;
          break;
        }
      }

      return {
        value,
        itemStyle: {
          color: colorPalette[seriesIndex % colorPalette.length],
          borderRadius: isTopOfStack ? [6, 6, 0, 0] : [0, 0, 0, 0],
        },
      };
    });

    return {
      name: itemGroup,
      type: 'bar' as const,
      stack: 'total',
      barWidth: 38,
      data,
    };
  });

  // ✅ base_line 선 차트 추가
  const allSeries: any[] = [
    ...barSeries,
    {
      name: 'Base Line',
      type: 'line',
      xAxisIndex: 0,
      yAxisIndex: 1, // ✅ 우측 Y축(부하율) 사용
      data: sortedDates.map(() => 100), // ✅ 모든 날짜에 100% 표시
      smooth: false,
      showSymbol: false,
      symbol: 'none',
      lineStyle: {
        width: 1,
        color: '#4568E0',
        type: 'solid',
      },
      // ✅ hover 시에도 항상 보이도록 설정
      emphasis: {
        lineStyle: {
          width: 1,
          color: '#4568E0',
          type: 'solid',
          opacity: 1,
        },
      },
      blur: {
        lineStyle: {
          width: 1,
          color: '#4568E0',
          type: 'solid',
          opacity: 1,
        },
      },
      z: 100,
      animation: false,
    },
  ];

  // ✅ str_rate의 최댓값 기준으로 max 설정
  const maxRate = Math.max(...props.detailChartDataSource.map((d: any) => d.str_rate || 0));
  const yAxisMax = Math.ceil(maxRate / 10) * 10;

  // 고유한 날짜 개수 계산
  const uniqueDateCount = sortedDates.length;

  // ✅ 동적으로 계산된 visible bar count 사용
  const visibleBarCount = dynamicVisibleCount.value;

  // dataZoom 시작/끝 비율 계산
  const zoomEnd = uniqueDateCount > 0 ? (visibleBarCount / uniqueDateCount) * 100 : 100;

  // ✅ 범례 정렬
  const legendData = itemGroups.map((elem, index) => ({
    name: elem,
    itemStyle: {
      color: colorPalette[index % colorPalette.length],
    },
  }));

  return {
    title: {
      text: t('text-isu_qty_by_oper_group_str_rate'), // ✅ 제목 텍스트
      left: 'left', // 왼쪽 정렬
      top: 0, // 상단 여백
      textStyle: {
        fontSize: 13,
        fontWeight: '500',
        color: '#565F6E',
      },
    },
    tooltip: {
      trigger: 'axis',
      confine: true,
      appendToBody: true,
      z: 99999,
      axisPointer: {
        label: {
          show: false, // ✅ hover 시 x축 하단 라벨 숨김
        },
      },
      formatter: (params: any) => {
        // ✅ "미지정" 시리즈 제거
        const filteredParams = params.filter((item: any) => {
          const seriesName = item.seriesName;
          return (
            seriesName !== t('text-chart-unclassified') &&
            seriesName !== t('text-not_set') &&
            seriesName !== 'Base Line' &&
            seriesName !== ''
          );
        });

        if (filteredParams.length === 0) return '';

        const axisValue = filteredParams[0].axisValue;

        // TOTAL 항목 찾아 필요한 값 축출
        const firstFindData = props.originDetailChartDataSource.find(
          (d: any) => d.date === axisValue && d.item_group_id === 'TOTAL',
        );

        const { capa, plan_qty: planQty, oper_group_id: operGroupId } = firstFindData || {};

        let result = '';

        if (!!firstFindData) {
          result = `${!!operGroupId ? operGroupId : '-'} (${axisValue})<br/>`;
          result += `CAPA: ${!!capa ? capa.toLocaleString() : '0'}<br/>`;
          result += `${t('text-isu_str_qty')}: ${!!planQty ? planQty.toLocaleString() : '0'}<br/>`;
        } else {
          result = `${'-'} (${axisValue})<br/>`;
          result += `CAPA: ${'0'}<br/>`;
          result += `${t('text-isu_str_qty')}: ${'0'}<br/>`;
        }

        // 데이터 기반 툴팁 내용 구성
        filteredParams.forEach((item: any) => {
          const planQtyValue =
            typeof item.value === 'number' ? Number(item.value.toFixed(2)).toLocaleString() : item.value;

          if (item.seriesName !== 'TOTAL') {
            result += `${item.marker} ${item.seriesName}: ${planQtyValue ?? '-'}<br/>`;
          }
        });

        return result;
      },
    },
    series: allSeries,
    xAxis: [
      {
        type: 'category',
        data: sortedDates,
        splitLine: {
          show: false, // ✅ x축 격자선(세로선) 제거
        },
        axisLabel: {
          interval: 0,
          rotate: 0, // ✅ 회전 제거 (평평하게)
          color: '#96A5BE',
          formatter: (value: string) => {
            // ✅ "2025-11-02" → "11-02"로 변환 (월-일만 표시)
            if (value && value.includes('-')) {
              const parts = value.split('-');
              if (parts.length === 3) {
                return `${parts[1]}-${parts[2]}`; // 월-일
              }
            }
            return value;
          },
        },
      },
    ],
    legend: {
      show: true,
      top: 16, // ✅ 범례를 아래로 이동 (제목 + DateInput 아래)
      data: legendData,
    },
    yAxis: [
      {
        type: 'value',
        name: t('text-qty'),
        position: 'left',
        min: 0,
        axisLabel: {
          formatter: (value: number) => value.toString(),
          color: '#96A5BE',
        },
      },
      {
        type: 'value',
        name: t('text-isu_load_factor_include_percent'), // ✅ 우측 Y축 (참고용)
        position: 'right',
        min: 0,
        max: yAxisMax,
        axisLabel: {
          formatter: (value: number) => `${value}`,
          color: (value: string) => (value === '100' ? '#4568E0' : '#96A5BE'),
        },
      },
    ],
    grid: {
      top: 70, // ✅ 상단 여백 감소 (범례와 차트 간격 줄임)
      bottom: 45, // ✅ x축 label + dataZoom slider를 위한 공간
      left: 60,
      right: 40,
    },
    barCategoryGap: '40px', // ✅ bar와 bar 사이의 고정 간격 (40px)
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: Math.min(zoomEnd, 100),
        bottom: 10, // ✅ 하단에서 10px 위치
        height: 10, // ✅ 스크롤러 높이 감소
        showDetail: false, // 양 끝 핸들 숨김
        brushSelect: false, // ✅ 브러시 선택(드래그 영역 확장) 완전 비활성화
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 0,
        end: Math.min(zoomEnd, 100),
        zoomOnMouseWheel: false, // ✅ 마우스 휠 줌 비활성화
        moveOnMouseWheel: true,
        moveOnMouseMove: true,
      },
    ],
  };
});
</script>
<style lang="scss" scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart {
  width: 100%;
  height: 100%;
}

// ✅ 차트 우측 상단에 DateInput 배치
.chart-date-input {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 100;
}

.grid-empty.load_factor_by_oper_group-loading {
  position: relative;
  width: 100%;
  height: 100%;
  :deep(.load-element-outer-wrapper) {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>
