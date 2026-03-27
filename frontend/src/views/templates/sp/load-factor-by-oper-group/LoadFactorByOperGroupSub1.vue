<template>
  <div ref="chartContainerRef" style="width: 100%; height: 100%">
    <v-chart
      v-if="!loading && mainDataSource.length"
      class="chart"
      :option="chartOption"
      autoresize
      ref="chartRef"
      @zr:click="onZrClick"
      @click="onSeriesClick"
    />
    <!--
        Echart props인 :is-fetching 만으로 처리하면 깜박임 이슈가 있어서
        v-loading을 별도로 활용해야 함
      -->
    <div v-else class="grid-empty load_factor_by_oper_group-loading">
      <EmptyState :is-read-only="true" />
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
import { EmptyState } from '@vmscloud/moz-ui-components';
import { useTranslation } from 'i18next-vue';
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue';

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
  mainDataSource: any[];
  loading: boolean;
  clickedSeriesData: string;
  detailChartSelectSource: { oper_group_id: string }[];
}>();

const emit = defineEmits<{
  (e: 'update:clickedSeriesData', val: string): void;
  (e: 'update:detailChartSelectSource', val: { oper_group_id: string }[]): void;
}>();

const { t } = useTranslation(); // 다국어

// ✅ 차트 컨테이너 ref와 동적 visible count
const chartContainerRef = ref<HTMLElement | null>(null);
const chartContainerWidth = ref(1200); // 기본값
const chartRef = ref<any>(null);

// ✅ 차트 너비에 따른 visible bar count 계산
const calculateVisibleBarCount = () => {
  if (!chartContainerRef.value) return 10;

  const containerWidth = chartContainerRef.value.offsetWidth;
  chartContainerWidth.value = containerWidth;

  // bar width (80px) + gap (40px) = 120px per bar
  // grid left (60px) + right (40px) = 100px 여백
  const availableWidth = containerWidth - 100;
  const barWidth = 120; // 80px bar + 40px gap

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

// ✅ rnum으로 정렬된 고유 axis 값들
const sortedData = computed(() => [
  ...new Set(
    [...props.mainDataSource]
      .sort((a: any, b: any) => {
        if (a.rnum === null) return 1;
        if (b.rnum === null) return -1;
        return a.rnum - b.rnum;
      })
      .map((d: any) => d.oper_group_id),
  ),
]);

const chartOption = computed(() => {
  const data = sortedData.value;
  if (!data.length) return {};

  // 부하율 데이터 맵
  const strRateMap: Record<string, number> = {};
  props.mainDataSource.forEach((item: any) => {
    strRateMap[item.oper_group_id] = item.str_rate;
  });

  const barData = data.map((operGroupId) => strRateMap[operGroupId] ?? 0);

  // ✅ 동적으로 계산된 visible bar count 사용
  const uniqueAxisCount = data.length;
  const initialVisibleCount = dynamicVisibleCount.value;
  const initialZoomEnd = uniqueAxisCount > 0 ? (initialVisibleCount / uniqueAxisCount) * 100 : 100;

  return {
    title: {
      text: t('text-isu_entire_oper_group_avg_load_factor'), // ✅ 제목 텍스트
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
        // ✅ "Base Line" 시리즈 제거
        const filteredParams = params.filter((item: any) => item.seriesName !== 'Base Line');

        if (filteredParams.length === 0) return '';

        const axisValue = filteredParams[0].axisValue;
        let result = `${axisValue}<br/>`;

        filteredParams.forEach((item: any) => {
          const strRate = typeof item.value === 'number' ? item.value.toFixed(2) : item.value;

          // ✅ mainDataSource에서 해당 막대의 원본 데이터 찾기
          const findData = props.mainDataSource.find(
            (d: any) => d.oper_group_id === axisValue && d.legend === item.seriesName,
          );

          if (findData) {
            const capa =
              typeof findData.capa === 'number' ? Number(findData.capa.toFixed(2)).toLocaleString() : findData.capa;
            const planQty =
              typeof findData.plan_qty === 'number'
                ? Number(findData.plan_qty.toFixed(2)).toLocaleString()
                : findData.plan_qty;

            result += `${item.marker} CAPA: ${capa}<br/>`;
            result += `&nbsp;&nbsp;&nbsp;&nbsp;${t('text-plan_qty')}: ${planQty}<br/>`;
            result += `&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${item.seriesName}: ${strRate}%<br/>`;
          } else {
            result += `${item.marker} ${item.seriesName}: ${strRate}%<br/>`;
          }
        });

        return result;
      },
    },
    legend: {
      show: false, // ✅ 범례 숨김
    },
    xAxis: [
      {
        type: 'category',
        data: data,
        splitLine: {
          show: false, // ✅ x축 격자선(세로선) 제거
        },
        axisLabel: {
          interval: 0, // ✅ 모든 라벨 표시
          rotate: 0,
          overflow: 'truncate',
          color: '#96A5BE', // ✅ x축 글자색
          formatter: (value: string) => {
            // ✅ "001. 자재출고" → "   001.\n자재출고" 형태로 변환
            if (value && value.includes('.')) {
              const parts = value.split('.');
              const number = parts[0].trim();
              const text = parts.slice(1).join('.').trim();
              // 번호를 가운데 정렬하기 위해 공백 추가
              return `   ${number}.\n${text}`;
            }
            return value;
          },
          align: 'center', // ✅ 가운데 정렬
          verticalAlign: 'top',
          lineHeight: 16, // ✅ 줄 간격
        },
      },
    ],
    yAxis: [
      {
        type: 'value',
        name: t('text-isu_load_factor_include_percent'),
        position: 'left',
        min: 0,
        axisLabel: {
          // ✅ Y축 라벨 커스터마이징
          formatter: (value: number) => value.toString(),
          // ✅ 값이 100일 때만 파란색 스타일 적용 (나머지는 기본 스타일 유지)
          color: (value: string) => (value === '100' ? '#4568E0' : '#96A5BE'),
        },
      },
    ],
    series: [
      {
        name: t('부하율'),
        type: 'bar',
        data: barData,
        barWidth: 80,
        label: {
          // ✅ bar 상단에 라벨 표시
          show: true,
          position: 'top',
          formatter: (params: any) => {
            const value = params.value;
            if (value < 0) return '';

            // ✅ 100 이상이면 파란색, 미만이면 회색
            const styleName = value >= 100 ? 'over100' : 'under100';
            return `{${styleName}|${value.toFixed(1)}%}`;
          },
          fontSize: 11,
          rich: {
            over100: {
              color: '#4568E0',
              fontSize: 11,
              fontWeight: 'bold',
            },
            under100: {
              color: '#858e9e',
              fontSize: 11,
            },
          },
        },
        emphasis: {
          // ✅ hover 시에도 label 그대로 표시
          label: {
            show: true,
            position: 'top',
            formatter: (params: any) => {
              const value = params.value;
              if (value < 0) return '';

              const styleName = value >= 100 ? 'over100' : 'under100';
              return `{${styleName}|${value.toFixed(1)}%}`;
            },
            fontSize: 11,
            rich: {
              over100: {
                color: '#4568E0',
                fontSize: 11,
                fontWeight: 'bold',
              },
              under100: {
                color: '#858e9e',
                fontSize: 11,
              },
            },
          },
        },
        itemStyle: {
          color: '#618FF97A',
          borderRadius: [6, 6, 0, 0], // ✅ 모든 bar 상단 둥글게
        },
      },
      // ✅ base_line 선 차트 추가
      {
        name: 'Base Line',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: data.map(() => 100),
        smooth: false,
        showSymbol: false,
        symbol: 'none',
        lineStyle: {
          width: 1,
          color: '#4568E0',
          type: 'solid',
        },
        z: 100,
        animation: false,
      },
    ],
    grid: {
      top: 60, // ✅ 제목 공간 확보
      bottom: 65, // ✅ x축 label(2줄) + dataZoom slider를 위한 공간 확보
      left: 60,
      right: 40,
    },
    barCategoryGap: '40px', // ✅ bar와 bar 사이의 고정 간격
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: Math.min(initialZoomEnd, 100), // ✅ 초기에는 일정 개수만 표시
        bottom: 10, // ✅ 하단에서 10px 위치
        height: 10, // ✅ 스크롤러 높이 감소
        showDetail: false, // 양 끝 핸들 숨김
        brushSelect: false, // ✅ 브러시 선택(드래그 영역 확장) 완전 비활성화
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 0,
        end: Math.min(initialZoomEnd, 100), // ✅ 초기에는 일정 개수만 표시
        zoomOnMouseWheel: false,
        moveOnMouseWheel: true,
        moveOnMouseMove: true,
      },
    ],
  };
});

// ✅ 차트 클릭 핸들러 - grid 영역 클릭
const onZrClick = (params: any) => {
  const chart = chartRef.value?.chart;
  if (!chart) return;

  const pointInPixel = [params.offsetX, params.offsetY];

  if (chart.containPixel('grid', pointInPixel)) {
    const pointInGrid = chart.convertFromPixel({ seriesIndex: 0 }, pointInPixel);
    const option = chart.getOption() as any;

    const xAxisIndex = Math.round(pointInGrid[0]);
    const xAxisData = option.xAxis[0].data;
    const clickedXAxisValue = xAxisData[xAxisIndex];

    const originalData = props.mainDataSource.find((item: any) => item.oper_group_id === clickedXAxisValue);

    if (originalData && originalData.oper_group_id) {
      const currentSource = [...props.detailChartSelectSource];
      const index = currentSource.findIndex(
        (item: { oper_group_id: string }) => item.oper_group_id === originalData.oper_group_id,
      );
      if (index === -1) {
        currentSource.push({
          oper_group_id: originalData.oper_group_id,
        });
        emit('update:detailChartSelectSource', currentSource);
      }

      nextTick(() => {
        emit('update:clickedSeriesData', originalData.oper_group_id);
      });
    }
  }
};

// ✅ stackbar 클릭 이벤트
const onSeriesClick = (params: any) => {
  if (params.componentType === 'series') {
    const clickedAxisValue = params.name;

    const originalData = props.mainDataSource.find((item: any) => item.oper_group_id === clickedAxisValue);

    if (originalData && originalData.oper_group_id) {
      const currentSource = [...props.detailChartSelectSource];
      const index = currentSource.findIndex(
        (item: { oper_group_id: string }) => item.oper_group_id === originalData.oper_group_id,
      );
      if (index === -1) {
        currentSource.push({
          oper_group_id: originalData.oper_group_id,
        });
        emit('update:detailChartSelectSource', currentSource);
      }

      nextTick(() => {
        emit('update:clickedSeriesData', originalData.oper_group_id);
      });
    }
  }
};
</script>
<style lang="scss" scoped>
.chart {
  width: 100%;
  height: 100%;
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
