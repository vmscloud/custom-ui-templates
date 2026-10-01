/**
 * MozGrid 컨텍스트 메뉴 헬퍼
 *
 * MozGrid 의 customMenu 항목은 handler 에 셀 정보를 넘기지 않으므로,
 * contextmenu 이벤트 페이로드(우클릭한 행/셀)를 보관해 두고 handler 에서 읽는다.
 */
import type { IContextMenuItem } from '@vmscloud/moz-ui-grid-vue';
import { shallowRef } from 'vue';
import { openLinkNewTab } from '../adapters/utils';

export interface GridContextTarget {
  /** 우클릭한 행 데이터 */
  item: any;
  /** 우클릭한 셀 (헤더·빈 영역이면 area 로 구분) */
  cell: { area?: string; columnId?: string; value?: unknown; rect?: DOMRect } | null;
}

/**
 * contextmenu 이벤트 페이로드를 보관한다. `@contextmenu="onContextMenu"` 로 연결한다.
 */
export function useGridContextTarget() {
  const target = shallowRef<GridContextTarget>({ item: null, cell: null });

  const onContextMenu = (payload: any) => {
    const cellEl = (payload?.originalEvent?.target as HTMLElement | undefined)?.closest?.('.ps-cell');
    target.value = {
      item: payload?.rowData ?? null,
      cell: {
        area: payload?.area,
        columnId: payload?.columnId,
        value: payload?.value,
        rect: cellEl?.getBoundingClientRect(),
      },
    };
  };

  return { target, onContextMenu };
}

export interface OpenNewTabMenuOptions {
  setLocalStorage?: (selectedItems: any, selectedCell?: any) => { key: string; value: any };
  route: (selectedItems: any, selectedCell?: any) => { path: string; query?: { [prop: string]: string } };
  label: string;
  disabled?: (selectedItems: any, selectedCell?: any) => any;
}

/**
 * 「새 탭으로 열기」 커스텀 메뉴 항목 (옛 ExtendGridContextOpenNewTab 대체)
 *
 * MozGrid 메뉴의 disabled 는 메뉴를 열 때 다시 계산되지 않으므로, disabled 조건은 클릭 시점에 검사해
 * 해당하면 아무 것도 하지 않는다.
 */
export function createOpenNewTabMenu(
  id: string,
  options: OpenNewTabMenuOptions,
  getTarget: () => GridContextTarget,
): IContextMenuItem {
  return {
    id,
    label: options.label,
    handler: () => {
      const { item, cell } = getTarget();
      if (options.disabled && options.disabled(item, cell)) return;

      if (options.setLocalStorage) {
        const { key, value } = options.setLocalStorage(item, cell);
        localStorage?.setItem(key, value);
      }
      openLinkNewTab(options.route(item, cell));
    },
  };
}
