<template>
  <div style="display: none" />
</template>
<script setup lang="ts">
import { useMenuStore } from '../adapters/stores';
import { inject, onBeforeMount, toRefs } from 'vue';

interface Props {
  setLocalStorage?: (
    selectedItems: any,
    selectedCell?: any,
  ) => {
    key: string;
    value: any;
  };
  route: (
    selectedItems: any,
    selectedCell?: any,
  ) => {
    path: string;
    query?: { [prop: string]: string };
  };
  label?: string;
  disabled?: (selectedItems: any, selectedCell?: any) => any;
}

const props = withDefaults(defineProps<Props>(), {});
const { setLocalStorage, route, label, disabled } = toRefs(props);

const gridCustomModule = inject('extendGridCustomModule', null) as any;

/** MF 환경에서는 Host의 라우터를 사용할 수 없으므로 window.open으로 대체 */
function openLinkNewTab(routeInfo: { path: string; query?: Record<string, string> }) {
  const queryStr = routeInfo.query
    ? '?' + new URLSearchParams(routeInfo.query).toString()
    : '';
  window.open(routeInfo.path + queryStr, '_blank');
}

const openNewTab = () => {
  if (setLocalStorage.value) {
    const getPropsToLocalStorage = setLocalStorage.value(
      gridCustomModule.selectedCellItem.value,
      gridCustomModule.selectedCell.value,
    );
    localStorage?.setItem(getPropsToLocalStorage.key, getPropsToLocalStorage.value);
  }
  openLinkNewTab(route.value(gridCustomModule.selectedCellItem.value, gridCustomModule.selectedCell.value));
};

const flexGridCustomMenu = [
  {
    header: label.value,
    cmd: label.value,
    clicked: () => {
      openNewTab();
    },
    active: () =>
      (disabled.value &&
        !disabled.value(gridCustomModule.selectedCellItem.value, gridCustomModule.selectedCell.value)) ||
      disabled.value === undefined,
  },
];

const pivotGridCustomMenu = [
  {
    text: label.value,
    function: () => {
      openNewTab();
    },
    disabled: () =>
      disabled?.value && disabled.value(gridCustomModule.selectedCellItem.value, gridCustomModule.selectedCell.value),
  },
];

const menuModule = useMenuStore();
const items = menuModule.getNavis;

onBeforeMount(() => {
  /**
   * 권한 없는 페이지 context 메뉴에서 차단
   */
  // const targetPath = route.value(gridCustomModule.selectedCellItem.value, gridCustomModule.selectedCell.value).path;
  // if (!(items as any).map((elem: any) => elem.path).includes(targetPath)) {
  //   console.warn(
  //     `[components/Grid/ExtendGridContextOpenNewTab] ${targetPath} 은 등록되지 않았거나 권한이 없는 메뉴라 ContextMenu에 추가되지 않습니다.`,
  //   );
  //   return;
  // }

  if (gridCustomModule.type === 'flexGrid') {
    gridCustomModule.addCustomContextMenus(flexGridCustomMenu);
  }
  if (gridCustomModule.type === 'pivotGrid') {
    gridCustomModule.addCustomContextMenus(pivotGridCustomMenu);
  }
});
</script>
