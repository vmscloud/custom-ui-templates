import { createVNode, DirectiveBinding, ref, render } from 'vue';
import LoadElement from './LoadElement.vue';
import { generateGUID } from './generator';

let loadStorage: any = {};

/**
 * v-loading 디렉티브
 *
 * 원본 useRenderLoad에서 router.beforeEach로 loadStorage를 초기화했으나,
 * Module Federation remote에서는 라우트 변경 시 컴포넌트가 언마운트되므로
 * unmounted 훅에서 개별 키를 정리합니다.
 */
const loadingDirective = {
  mounted(el: HTMLElement | any, binding: DirectiveBinding) {
    const key = generateGUID();

    if (binding.value instanceof Object) {
      loadStorage[key] = ref(binding.value.isLoading);
    } else {
      loadStorage[key] = ref(binding.value);
    }

    el._loadingKey = key;

    const childInstance = createVNode(LoadElement, { isLoading: loadStorage[key], parentEl: el });

    const childElement = document.createElement('div');
    render(childInstance, childElement);

    el.insertBefore(childElement.firstChild!, el.firstChild);
  },

  updated(el: HTMLElement | any, binding: DirectiveBinding) {
    const key = el._loadingKey;

    if (binding.value instanceof Object) {
      loadStorage[key].value = binding.value.isLoading;
    } else {
      if (typeof loadStorage[key]?.value === 'boolean') loadStorage[key].value = binding.value;
    }
  },

  unmounted(el: HTMLElement | any) {
    const key = el._loadingKey;
    if (key && loadStorage[key]) {
      delete loadStorage[key];
    }
  },
};

export default loadingDirective;
