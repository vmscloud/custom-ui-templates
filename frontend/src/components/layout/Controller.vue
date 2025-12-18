<template>
  <div class="moz-controller-root" :style="containerStyle">
    <div class="moz-controller" :style="headerStyle">
      <BreadCrumb :item-source="navis" :show-favorite="false" />

      <div class="spacer"></div>

      <div class="moz-controller-actions">
        <slot name="beforeFilter"></slot>
        <Toggle
          v-if="showFilterButton && !$slots['custom-filter']"
          v-model="showFilter"
          :label="filterLabel"
        />
        <Toggle
          v-if="showFilterButton && $slots['custom-filter']"
          v-model="customQueryParamsPanel"
          :label="filterLabel"
        />
        <div
          class="spacer between-buttons"
          v-if="showFilterButton"
          style="margin: 0 6px"
        />
        <slot name="action"></slot>
        <div
          class="spacer between-buttons"
          v-if="!!$slots.action && actionButtons.length > 0"
        />
        <Button
          v-for="(action, index) in actionButtons"
          :key="index"
          @click="
            () => {
              if (!action?.click) return;
              action?.click();
            }
          "
          v-bind="action"
          :width="!action.text ? 30 : undefined"
          :style="{ padding: !action.text ? 0 : undefined }"
        >
          <template #icon>
            <IconSave
              v-if="action.icon == 'IconSave'"
              color="currentColor"
              size="14"
            />
            <IconTrash
              v-if="action.icon == 'IconTrash'"
              color="currentColor"
              size="14"
            />
            <IconPlus
              v-if="action.icon == 'IconPlus'"
              color="currentColor"
              size="14"
            />
            <IconSearch
              v-if="action.icon == 'IconSearch'"
              color="currentColor"
              size="14"
            />
            <IconPlay
              v-if="action.icon == 'IconPlay'"
              color="currentColor"
              size="14"
            />
          </template>
        </Button>
      </div>
    </div>
    <transition name="controller-filter">
      <div
        v-if="showFilter && !$slots['custom-filter']"
        class="moz-horizontal-filter moz-controller-filter"
        :style="filterStyle"
        ref="filter"
      >
        <slot name="filter"> </slot>
      </div>
    </transition>

    <Teleport
      to=".moz-contents-container"
      v-if="isContentsWrapperMounted && $slots['custom-filter']"
    >
      <div v-show="customQueryParamsPanel">
        <slot name="custom-filter"></slot>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import {
  BreadCrumb,
  Button,
  Toggle,
  IconPlay,
  IconPlus,
  IconSave,
  IconSearch,
  IconTrash,
} from "@vmscloud/moz-component";
import { useTranslation } from "i18next-vue";
import { computed, ModelRef, onBeforeMount, onMounted, ref, toRefs } from "vue";
import { useRouter } from "vue-router";

/**
 * define CONSTANT
 */
interface Actions {
  action: "Add" | "Remove" | "Edit" | "Save" | "Search" | "Run";
  icon?: string;
  text?: string;
  disabled?: boolean;
  click?: Function;
  loading?: boolean;
}

interface LayoutOption {
  useMakeLink?: boolean;
}

interface Props {
  height?: number;
  setControlHeight?: Function;
  showFilterButton?: boolean;
  actions?: Actions[];
  containerStyle?: Record<string, string>;
  headerStyle?: Record<string, string>;
  filterStyle?: Record<string, string>;
  showFavorite?: boolean;
  showPreset?: boolean;
  queryParams?: any[];
  availableQueryParams?: any[];
  queryParamsPageKey?: string;
  layoutOption?: LayoutOption;
  customNavis?: string[];
}

const customQueryParamsPanel: ModelRef<boolean | undefined> = defineModel(
  "customQueryParamsPanel",
  {
    required: false,
  }
);

const router = useRouter();
const { t } = useTranslation();

const isContentsWrapperMounted = ref(false);

// 번역 키가 없을 경우 기본값 사용
const filterLabel = computed(() => {
  const translated = t("text-search_param");
  return translated === "text-search_param" ? "조회조건" : translated;
});

/**
 * props
 */
const props = withDefaults(defineProps<Props>(), {
  height: 66,
  showFilterButton: false,
  showFavorite: true,
  showPreset: false,
  queryParams: () => [],
  availableQueryParams: () => [],
  queryParamsPageKey: "DEFAULT",
  layoutOption: () => ({
    useMakeLink: true,
  }),
});
const {
  height,
  setControlHeight,
  showFilterButton,
  actions,
  headerStyle,
  filterStyle,
  containerStyle,
} = toRefs(props);
const { customNavis } = toRefs(props);

/**
 * state
 */
const showFilter = ref(showFilterButton.value);
const filter = ref();

/**
 * life hook
 */
onBeforeMount(() => {
  if (setControlHeight?.value) {
    setControlHeight.value(height.value);
  }
});

const loadingAction = computed(() =>
  actions?.value?.find((a) => a.loading === true)
);

const actionButtons = computed(
  () =>
    actions?.value?.map((action) => {
      const btnStyle: any = {
        icon: null,
        ...action,
      };
      switch (action.action) {
        case "Add":
          btnStyle.icon = "IconPlus";
          break;
        case "Remove":
          btnStyle.icon = "IconTrash";
          break;
        case "Save":
          btnStyle.icon = "IconSave";
          break;
        case "Search":
          btnStyle.icon = "IconSearch";
          break;
        case "Run":
          btnStyle.icon = "IconPlay";
          break;
        default:
          break;
      }

      // loading이 true인 action이 있으면, 그 action을 제외한 나머지 버튼은 disabled 처리
      btnStyle.disabled =
        (loadingAction.value && action.action !== loadingAction.value.action) ||
        !!action.disabled;

      return btnStyle;
    }) || []
);

// BreadCrumb용 네비게이션 경로
const navis = computed(() => {
  if (customNavis.value) {
    return customNavis.value;
  }

  const routeNavis = router.currentRoute.value.meta.navis as
    | string[]
    | undefined;
  if (routeNavis) {
    return [...routeNavis].reverse().map((_title: string) => {
      const translated = t(_title);
      // 번역이 없으면 원본 반환
      return translated === _title ? _title : translated;
    });
  }

  return [];
});

onMounted(() => {
  isContentsWrapperMounted.value = !!document.querySelector(
    ".moz-contents-container"
  );
});
</script>
<style lang="scss" scoped>
.moz-left-menu-close {
  display: flex;
  justify-content: center;
  align-items: center;

  height: 24px;
  margin-left: 3px;
  margin-right: 8px;

  cursor: pointer;
}

.moz-controller-root {
  padding: 0px var(--size-content-padding);
  background-color: var(--color-controller-background);

  &.popup-controller {
    padding: 0px;

    .moz-controller-filter {
      margin-bottom: 0px;
    }
  }

  .moz-controller {
    height: var(--layout-control-height);
    display: flex;
    align-items: center;
    justify-content: space-between;

    .moz-controller-actions {
      display: flex;
      align-items: center;
      gap: var(--spacing-4);

      .filter-icon {
        svg {
          min-width: 20px;
        }
      }

      & > :deep(.spacer) {
        width: 1px;
        height: 14px;
        background-color: var(--color-controller-button-spacer-background);
        margin-right: calc(var(--size-padding6) - var(--size-padding2));
        border-radius: 100px;

        &.between-buttons {
          margin-left: var(--spacing-1);
          margin-right: var(--spacing-1);
        }
      }
    }
  }

  .moz-horizontal-filter {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .moz-controller-filter {
    border-radius: var(--border-filter-radius);
    padding: var(--size-filter-padding);
    background-color: var(--color-bg-250);
    border: 1px solid var(--color-border-750);
    gap: var(--size-filter-gap);
    margin-bottom: var(--spacing-6);

    position: relative;

    .accessibility-button {
      position: absolute;
      top: -17px;
      right: 0;
      opacity: 0;
      font-size: var(--text-lg);
      border-radius: var(--rounded-sm);
      color: var(--color-text-100);

      line-height: 19px;
      text-align: left;
      padding: 6px 10px;
      background-color: var(--color-bg-900);
      box-shadow: 2px 2px 7px var(--color-shadow);
      z-index: 999999;
      max-width: 350px;
      overflow: hidden;
      word-break: break-all;
      pointer-events: none;

      &:focus,
      &:focus-within {
        opacity: 1;
        pointer-events: auto;
      }
    }
  }
}

.controller-filter-enter-from,
.controller-filter-leave-to {
  transform: translate(0, -10px);
  opacity: 0;
  transition: opacity 0.15s ease-in, transform 0.15s ease-in;
}
.controller-filter-enter-to,
.controller-filter-leave-from {
  transform: translate(0);
  opacity: 1;
  transition: opacity 0.15s ease-in, transform 0.15s ease-in;
}
</style>
