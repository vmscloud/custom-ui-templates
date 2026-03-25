<template>
  <div class="simple-grid" ref="gridContainerRef" tabindex="0">
    <table class="grid-table" v-if="itemsSource && itemsSource.length > 0">
      <thead>
        <tr>
          <th
            v-for="(column, columnIndex) in columns"
            :key="column.key"
            class="grid-header"
            :class="{ [`grid-header-index-${columnIndex}`]: true }"
            :ref="(el) => onHeaderRef(el, columnIndex, column.key, column)"
          >
            <div
              :data-key="column.key"
              class="header-content"
              :title="column?.hoverText || column.header || column.key"
            >
              {{ column.header || column.key }}
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(item, rowIndex) in itemsSource"
          :key="rowIndex"
          class="grid-row"
          :class="{ [`grid-row-index-${rowIndex}`]: true }"
        >
          <td
            v-for="(column, columnIndex) in columns"
            v-show="!shouldHideCell(rowIndex, column.key)"
            :key="column.key"
            class="grid-cell"
            :class="{
              [column.type]: true,
              [`grid-cell-index-${columnIndex}`]: true,
              'dragged-border-top': isDraggedBorderTop(rowIndex, column.key),
              'dragged-border-bottom': isDraggedBorderBottom(rowIndex, column.key),
              'dragged-border-left': isDraggedBorderLeft(rowIndex, column.key),
              'dragged-border-right': isDraggedBorderRight(rowIndex, column.key),
              'dragged-corner-top-right': isDraggedCornerTopRight(rowIndex, column.key),
              'dragged-corner-bottom-left': isDraggedCornerBottomLeft(rowIndex, column.key),
              'dragged-corner-bottom-right': isDraggedCornerBottomRight(rowIndex, column.key),
              'single-column-selection': isSingleColumnSelection(),
            }"
            :rowspan="getCellRowspan(rowIndex, column.key)"
            @click="onCellClick($event, rowIndex, column.key, item[column.key], item)"
            @mousedown="onMouseDown($event, rowIndex, column.key, item[column.key], item)"
            @mouseenter="onMouseEnter($event, rowIndex, column.key, item[column.key], item)"
            @contextmenu="onContextMenu($event, rowIndex, column.key, item[column.key], item)"
          >
            <div
              :class="{
                ['cell-wrapper']: true,
                cell: true,
                selectedCell: isSelected(rowIndex, column.key),
                draggedCells: isDragged(rowIndex, column.key),
              }"
              :ref="(el) => onCellRef(el, rowIndex, column.key, item[column.key], item)"
            >
              <div class="cell-value">
                {{ formatCellValue(item[column.key], column.type) }}
              </div>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-state">
      데이터 없음
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';

interface ColumnType {
  key: string;
  header?: string;
  type: string;
  hoverText?: string | null;
}

interface Props {
  itemsSource: any[];
  simpleColumns?: { binding: string; id: number; header: string; type: string; hoverText?: string }[];
  columnHeader?: string[];
  simpleFormatItem?: (element: HTMLElement, rowIndex: number, columnKey: string, value: any, rowData: any) => void;
  simpleFormatHeader?: (element: HTMLElement, columnIndex: number, columnKey: string, column: any) => void;
  enableCellMerge?: boolean;
  mergeColumnIndex?: number;
}

interface SelectedCell {
  rowIndex: number;
  columnKey: string;
  value: any;
  rowData: any;
}

const props = defineProps<Props>();
const selectedCell = ref<SelectedCell | null>(null);

// Cell merge 관련 computed
const mergedCells = computed(() => {
  if (!props.enableCellMerge || !props.itemsSource || props.itemsSource.length === 0) {
    return new Map();
  }

  const mergeInfo = new Map<string, { display: boolean; rowspan: number }>();
  const mergeColumnKey = columns.value[props.mergeColumnIndex as number]?.key as string | undefined;

  if (!mergeColumnKey) return mergeInfo;

  let currentValue: unknown = undefined;
  let currentRowspan = 0;
  let startRowIndex = 0;

  props.itemsSource.forEach((item, index) => {
    const cellValue = item[mergeColumnKey];

    if (cellValue === currentValue) {
      currentRowspan++;
      mergeInfo.set(`${index}-${mergeColumnKey}`, {
        display: false,
        rowspan: 0,
      });
    } else {
      if (currentRowspan > 0) {
        mergeInfo.set(`${startRowIndex}-${mergeColumnKey}`, {
          display: true,
          rowspan: currentRowspan,
        });
      }

      currentValue = cellValue;
      currentRowspan = 1;
      startRowIndex = index;
      mergeInfo.set(`${index}-${mergeColumnKey}`, {
        display: true,
        rowspan: 1,
      });
    }
  });

  if (currentRowspan > 0) {
    mergeInfo.set(`${startRowIndex}-${mergeColumnKey}`, {
      display: true,
      rowspan: currentRowspan,
    });
  }

  return mergeInfo;
});

const shouldHideCell = (rowIndex: number, columnKey: string): boolean => {
  if (!props.enableCellMerge) return false;
  const cellKey = `${rowIndex}-${columnKey}`;
  const mergeInfo = mergedCells.value.get(cellKey);
  return mergeInfo && !mergeInfo.display;
};

const getCellRowspan = (rowIndex: number, columnKey: string): number => {
  if (!props.enableCellMerge) return 1;
  const cellKey = `${rowIndex}-${columnKey}`;
  const mergeInfo = mergedCells.value.get(cellKey);
  return mergeInfo?.rowspan || 1;
};

const gridContainerRef = ref<HTMLDivElement | null>(null);

// 드래그 관련 상태
const isDragging = ref(false);
const draggedCells = ref<Set<string>>(new Set());
const draggedRowData = ref<any[]>([]);
const dragStartCell = ref<{ rowIndex: number; columnKey: string } | null>(null);
const lastClickedCell = ref<{ rowIndex: number; columnKey: string } | null>(null);

const emit = defineEmits<{
  cellSelected: [selectedCell: SelectedCell | null];
  cellsDragged: [rowData: any[]];
}>();

const columns = computed<ColumnType[]>(() => {
  if (!props.itemsSource || props.itemsSource.length === 0) return [];

  if (props.simpleColumns && props.simpleColumns.length > 0) {
    return props.simpleColumns
      .sort((a, b) => a.id - b.id)
      .map((col) => ({
        key: col.binding,
        header: col.header,
        type: col.type,
        hoverText: col.hoverText ?? null,
      }));
  }

  const firstItem = props.itemsSource[0];
  return Object.keys(firstItem).map((key) => ({
    key,
    type: getColumnType(firstItem[key]),
    header: undefined as string | undefined,
    hoverText: null,
  }));
});

const getColumnType = (value: any): string => {
  if (typeof value === 'number') {
    return 'number';
  } else if (typeof value === 'string') {
    return 'string';
  } else if (typeof value === 'boolean') {
    return 'boolean';
  }
  return 'string';
};

const formatCellValue = (value: any, type: string): string => {
  if (value === null || value === undefined) {
    return '';
  }

  if (type === 'number') {
    return Number(value).toLocaleString();
  }

  return String(value);
};

const isSelected = (rowIndex: number, columnKey: string): boolean => {
  if (draggedCells.value.size > 0) return false;
  return selectedCell.value?.rowIndex === rowIndex && selectedCell.value?.columnKey === columnKey;
};

const selectCellRange = (startRow: number, startCol: string, endRow: number, endCol: string) => {
  const minRow = Math.min(startRow, endRow);
  let maxRow = Math.max(startRow, endRow);
  const startColIndex = columns.value.findIndex((col) => col.key === startCol);
  const endColIndex = columns.value.findIndex((col) => col.key === endCol);
  const minColIndex = Math.min(startColIndex, endColIndex);
  const maxColIndex = Math.max(startColIndex, endColIndex);

  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minColIndex; c <= maxColIndex; c++) {
      const colKey = columns.value[c].key;
      const rowspan = getCellRowspan(r, colKey);
      if (rowspan > 1) {
        const cellEndRow = r + rowspan - 1;
        if (cellEndRow > maxRow) {
          maxRow = cellEndRow;
        }
      }
    }
  }

  const cellsToAdd: string[] = [];
  const rowDataToAdd: any[] = [];
  const addedCategories = new Set<any>();

  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minColIndex; c <= maxColIndex; c++) {
      const keyStr = cellKey(r, columns.value[c].key);
      cellsToAdd.push(keyStr);
    }

    const currentRowData = props.itemsSource[r];
    const categoryKey = currentRowData.category;
    if (!addedCategories.has(categoryKey)) {
      addedCategories.add(categoryKey);
      rowDataToAdd.push(currentRowData);
    }
  }

  draggedCells.value.clear();
  cellsToAdd.forEach((key) => draggedCells.value.add(key));
  draggedRowData.value = rowDataToAdd;

  if (rowDataToAdd.length > 0) {
    emit('cellsDragged', [...rowDataToAdd]);
  }
};

const onCellClick = (event: MouseEvent, rowIndex: number, columnKey: string, value: any, rowData: any) => {
  if (event.shiftKey && lastClickedCell.value) {
    selectCellRange(lastClickedCell.value.rowIndex, lastClickedCell.value.columnKey, rowIndex, columnKey);
    return;
  }

  draggedCells.value.clear();
  draggedRowData.value = [];

  const newSelectedCell: SelectedCell = {
    rowIndex,
    columnKey,
    value,
    rowData,
  };

  selectedCell.value = newSelectedCell;
  emit('cellSelected', newSelectedCell);
  lastClickedCell.value = { rowIndex, columnKey };
};

const selectFirstCell = () => {
  if (props.itemsSource && props.itemsSource.length > 0 && columns.value.length > 0) {
    const lastRowIndex = props.itemsSource.length - 1;
    const lastRowData = props.itemsSource[lastRowIndex];
    const firstColumnKey = columns.value[0].key;
    const lastCellValue = lastRowData[firstColumnKey];

    const fakeEvent = { shiftKey: false } as MouseEvent;
    onCellClick(fakeEvent, lastRowIndex, firstColumnKey, lastCellValue, lastRowData);
  }
};

watch(
  () => props.itemsSource,
  () => {
    nextTick(() => {
      selectFirstCell();
    });
  },
  { immediate: true },
);

defineExpose({
  selectedCell,
  clearSelection: () => {
    selectedCell.value = null;
    draggedCells.value.clear();
    draggedRowData.value = [];
    lastClickedCell.value = null;
    emit('cellSelected', null);
  },
  clearDraggedSelection: () => {
    draggedCells.value.clear();
    draggedRowData.value = [];
  },
});

const cellKey = (rowIndex: number, columnKey: string) => `${rowIndex}-${columnKey}`;

const isDragged = (rowIndex: number, columnKey: string): boolean =>
  draggedCells.value.has(cellKey(rowIndex, columnKey));

const isDraggedBorderTop = (rowIndex: number, columnKey: string): boolean => {
  if (!isDragged(rowIndex, columnKey)) return false;
  return !isDragged(rowIndex - 1, columnKey);
};
const isDraggedBorderBottom = (rowIndex: number, columnKey: string): boolean => {
  if (!isDragged(rowIndex, columnKey)) return false;
  const rowspan = getCellRowspan(rowIndex, columnKey);
  const cellEndRow = rowIndex + rowspan - 1;
  return !isDragged(cellEndRow + 1, columnKey);
};
const isDraggedBorderLeft = (rowIndex: number, columnKey: string): boolean => {
  if (!isDragged(rowIndex, columnKey)) return false;
  const colIdx = columns.value.findIndex((col) => col.key === columnKey);
  if (colIdx <= 0) return true;
  const leftCol = columns.value[colIdx - 1];
  if (!leftCol) return true;
  return !isDragged(rowIndex, leftCol.key);
};
const isDraggedBorderRight = (rowIndex: number, columnKey: string): boolean => {
  if (!isDragged(rowIndex, columnKey)) return false;
  const colIdx = columns.value.findIndex((col) => col.key === columnKey);
  if (colIdx === -1 || colIdx === columns.value.length - 1) return true;
  const rightCol = columns.value[colIdx + 1];
  if (!rightCol) return true;
  return !isDragged(rowIndex, rightCol.key);
};

const isDraggedCornerTopRight = (rowIndex: number, columnKey: string): boolean =>
  isDraggedBorderTop(rowIndex, columnKey) && isDraggedBorderRight(rowIndex, columnKey);

const isDraggedCornerBottomLeft = (rowIndex: number, columnKey: string): boolean =>
  isDraggedBorderBottom(rowIndex, columnKey) && isDraggedBorderLeft(rowIndex, columnKey);

const isDraggedCornerBottomRight = (rowIndex: number, columnKey: string): boolean =>
  isDraggedBorderBottom(rowIndex, columnKey) && isDraggedBorderRight(rowIndex, columnKey);

const onMouseDown = (event: MouseEvent, rowIndex: number, columnKey: string, value: any, rowData: any) => {
  if (event.button !== 0) return;

  if (event.shiftKey && lastClickedCell.value) {
    return;
  }

  isDragging.value = false;
  dragStartCell.value = { rowIndex, columnKey };

  selectedCell.value = null;

  const keyStr = cellKey(rowIndex, columnKey);
  draggedCells.value.clear();
  draggedCells.value.add(keyStr);
  draggedRowData.value = [rowData];

  const onMouseMove = () => {
    if (dragStartCell.value) {
      isDragging.value = true;
    }
  };

  const onMouseUp = (_upEvent: MouseEvent) => {
    if (isDragging.value) {
      if (draggedRowData.value.length > 0) {
        emit('cellsDragged', [...draggedRowData.value]);
      }
    } else {
      const clickEvent = { shiftKey: event.shiftKey } as MouseEvent;
      onCellClick(clickEvent, rowIndex, columnKey, value, rowData);
    }

    isDragging.value = false;
    dragStartCell.value = null;

    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  };

  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);
};

const onMouseEnter = (_event: MouseEvent, rowIndex: number, columnKey: string, _value: any, _rowData: any) => {
  if (isDragging.value && dragStartCell.value) {
    const startRow = dragStartCell.value.rowIndex;
    const startCol = dragStartCell.value.columnKey;
    const endRow = rowIndex;
    const endCol = columnKey;

    const minRow = Math.min(startRow, endRow);
    let maxRow = Math.max(startRow, endRow);
    const startColIndex = columns.value.findIndex((col) => col.key === startCol);
    const endColIndex = columns.value.findIndex((col) => col.key === endCol);
    const minColIndex = Math.min(startColIndex, endColIndex);
    const maxColIndex = Math.max(startColIndex, endColIndex);

    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minColIndex; c <= maxColIndex; c++) {
        const colKey = columns.value[c].key;
        const rowspan = getCellRowspan(r, colKey);
        if (rowspan > 1) {
          const cellEndRow = r + rowspan - 1;
          if (cellEndRow > maxRow) {
            maxRow = cellEndRow;
          }
        }
      }
    }

    const cellsToAdd: string[] = [];
    const rowDataToAdd: any[] = [];
    const addedCategories = new Set<any>();

    for (let r = minRow; r <= maxRow; r++) {
      for (let c = minColIndex; c <= maxColIndex; c++) {
        const keyStr = cellKey(r, columns.value[c].key);
        cellsToAdd.push(keyStr);
      }

      const currentRowData = props.itemsSource[r];
      const categoryKey = currentRowData.category;
      if (!addedCategories.has(categoryKey)) {
        addedCategories.add(categoryKey);
        rowDataToAdd.push(currentRowData);
      }
    }

    draggedCells.value.clear();
    cellsToAdd.forEach((key) => draggedCells.value.add(key));
    draggedRowData.value = rowDataToAdd;
  }
};

const isSingleColumnSelection = (): boolean => {
  if (draggedCells.value.size === 0) return false;

  const draggedColsSet = new Set<string>();
  draggedCells.value.forEach((key: string) => {
    const [, col] = key.split('-');
    draggedColsSet.add(col);
  });

  return draggedColsSet.size === 1;
};

const onContextMenu = (event: MouseEvent, _rowIndex: number, _columnKey: string, _value: any, _rowData: any) => {
  event.preventDefault();
  // Context menu simplified - no ContextMenu component dependency
};

const onCellRef = (el: any, rowIndex: number, columnKey: string, value: any, rowData: any) => {
  if (el && props.simpleFormatItem && el instanceof HTMLElement) {
    props.simpleFormatItem(el, rowIndex, columnKey, value, rowData);
  }
};

const onHeaderRef = (el: any, columnIndex: number, columnKey: string, column: any) => {
  if (el && props.simpleFormatHeader && el instanceof HTMLElement) {
    props.simpleFormatHeader(el, columnIndex, columnKey, column);
  }
};

// 클립보드 복사
const copySelectedCellsToClipboard = async () => {
  try {
    let textToCopy = '';

    if (draggedCells.value.size > 0) {
      const cellKeys = Array.from(draggedCells.value);
      const rows = new Set<number>();
      const cols = new Set<string>();

      cellKeys.forEach((key: string) => {
        const [rowIndex, columnKey] = key.split('-');
        rows.add(parseInt(rowIndex));
        cols.add(columnKey);
      });

      const sortedRows = Array.from(rows).sort((a, b) => a - b);
      const sortedColKeys = Array.from(cols).sort((a, b) => {
        const indexA = columns.value.findIndex((col) => col.key === a);
        const indexB = columns.value.findIndex((col) => col.key === b);
        return indexA - indexB;
      });

      const rowsData: string[] = [];
      sortedRows.forEach((rowIndex) => {
        const rowValues: string[] = [];
        sortedColKeys.forEach((columnKey) => {
          const cellKeyStr = cellKey(rowIndex, columnKey);
          if (draggedCells.value.has(cellKeyStr)) {
            const rowData = props.itemsSource[rowIndex];
            const value = rowData?.[columnKey];
            rowValues.push(value !== null && value !== undefined ? String(value) : '');
          }
        });
        rowsData.push(rowValues.join('\t'));
      });
      textToCopy = rowsData.join('\n');
    } else if (selectedCell.value) {
      const value = selectedCell.value.value;
      textToCopy = value !== null && value !== undefined ? String(value) : '';
    }

    if (textToCopy) {
      await navigator.clipboard.writeText(textToCopy);
    }
  } catch (error) {
    console.error('클립보드 복사 실패:', error);
  }
};

const handleKeyDown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
    if (draggedCells.value.size > 0 || selectedCell.value) {
      event.preventDefault();
      copySelectedCellsToClipboard();
    }
  }
};

onMounted(() => {
  if (gridContainerRef.value) {
    gridContainerRef.value.addEventListener('keydown', handleKeyDown);
  }
});

onUnmounted(() => {
  if (gridContainerRef.value) {
    gridContainerRef.value.removeEventListener('keydown', handleKeyDown);
  }
});
</script>

<style lang="scss" scoped>
.simple-grid {
  width: 100%;
  border: 1px solid #b5c3f3;
  border-radius: 4px;
  overflow: auto;
  height: 100%;
  min-height: 0;
  outline: none;

  .custom-border-top {
    border-top: 3px solid red !important;
  }

  .custom-border-right {
    border-right: 1px solid #b5c3f3 !important;
  }

  .custom-total-row {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #28364e !important;
    background-color: #e9f1fd !important;
    border-top: 1px solid #b5c3f3 !important;
  }

  .custom-header-highlight {
    background-color: #f0f8ff !important;
    font-weight: bold !important;
  }

  .custom-header-border {
    border-left: 3px solid #007acc !important;
  }

  .custom-header-text-color {
    color: #007acc !important;
  }

  .custom-header-center {
    text-align: center !important;
  }

  .grid-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    border-radius: 0px;
    overflow: hidden;
    user-select: none;

    .grid-header {
      background-color: #eef1fc;
      font-size: 13px;
      padding: 0 12px;
      height: 32px;
      border-bottom: 1px solid #b5c3f3;
      border-right: 1px solid #ddddec;
      z-index: 1;
      white-space: nowrap;
      position: relative;
      vertical-align: middle;
      text-align: left;
      width: 76px !important;

      .header-content {
        color: #565f6e;
        width: 100%;
        overflow: hidden;
        font-size: 13px;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
        font-weight: 500;
      }
    }

    .grid-cell {
      width: 76px !important;
      min-width: 100px !important;
      height: 32px;
      border-bottom: 1px solid #e1e3f0;
      border-right: 1px solid #e1e3f0;
      font-size: 13px;
      color: #28364e;
      vertical-align: middle;
      cursor: pointer;
      transition: background-color 0.2s ease;

      &:hover {
        background-color: #e2e7fa;
      }

      .cell-wrapper {
        width: 100%;
        height: 100%;
        padding: 0px 0px 0px 12px;
        box-sizing: border-box;

        &.selectedCell {
          background-color: #e2e7fa;
          position: relative;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: calc(100% + 1px);
            height: 100%;
            border: 2px solid #3e5dc9;
            z-index: 3;
            pointer-events: none;
            box-sizing: border-box;
          }
        }

        &.draggedCells {
          background-color: #e2e7fa;
          border: none;
        }
      }

      .cell-value {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
      }

      &.number {
        text-align: right;
        font-variant-numeric: tabular-nums;

        .cell-wrapper {
          padding: 0px 12px;
        }

        .cell-value {
          justify-content: flex-end;
        }
      }

      &.string {
        text-align: left;

        .cell-value {
          justify-content: flex-start;
        }
      }

      &.boolean {
        text-align: center;

        .cell-value {
          justify-content: center;
        }
      }
    }
  }

  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
    color: #6a7184;
    font-size: 0.75rem;
  }
}

.simple-grid .grid-cell {
  &.dragged-border-top,
  &.dragged-border-bottom {
    position: relative;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 3;
      pointer-events: none;

      width: calc(100% + 1px);
    }
  }

  &.dragged-border-left,
  &.dragged-border-right {
    position: relative;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 3;
      pointer-events: none;
      height: calc(100% + 1px);
    }
  }

  &.dragged-border-top::before {
    border-top: 2px solid #3e5dc9 !important;
  }

  &.dragged-border-bottom::before {
    border-bottom: 2px solid #3e5dc9 !important;
  }

  &.dragged-border-left::after {
    border-left: 2px solid #3e5dc9 !important;
    left: 0px !important;
  }

  &.dragged-border-right::after {
    border-right: 2px solid #3e5dc9 !important;
    left: 1px !important;
  }

  &.single-column-selection.dragged-border-left::after {
    left: 0px !important;
  }

  &.single-column-selection.dragged-border-right::after {
    left: 0px !important;
    width: calc(100% + 1px) !important;
  }

  &.dragged-corner-bottom-left::after {
    height: 100% !important;
  }

  &.dragged-corner-bottom-right::after {
    height: 100% !important;
  }
}

.simple-grid .grid-header.grid-header-index-1 {
  width: 60px !important;
  min-width: 60px !important;
  max-width: 60px !important;
}

.simple-grid .grid-cell.grid-cell-index-1 {
  width: 60px !important;
  min-width: 60px !important;
  max-width: 60px !important;
}

.simple-grid {
  .grid-header.grid-header-index-5 {
    border-right: #b5c3f3 solid 1px;
    z-index: 2;
  }
  .grid-cell.grid-cell-index-5 {
    border-right: #b5c3f3 solid 1px;
    z-index: 2;
  }

  .grid-header.grid-header-index-6 {
    border-right: none !important;
  }
  .grid-cell.grid-cell-index-6 {
    border-right: none !important;
  }
}
</style>
