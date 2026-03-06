import { DirectiveBinding } from 'vue';
import { addTooltipEvent, TooltipTarget, TooltipXPos, TooltipYPos } from './element';

interface TooltipDirectiveValue {
  text: string;
  onlyEllipsis?: boolean;
  handleEllipsis?: boolean | string | HTMLElement;
  position: [TooltipXPos, TooltipYPos, TooltipTarget?];
}

const tooltipDirective = (el: HTMLElement, binding: DirectiveBinding<TooltipDirectiveValue>) => {
  binding.instance?.$nextTick(() => {
    addTooltipEvent(
      el,
      binding.value?.text,
      binding.value?.onlyEllipsis ?? binding.value?.handleEllipsis ?? false,
      binding.value?.position ?? ['center', 'toBottom', 'element'],
    );
  });
};

export default {
  mounted: tooltipDirective,
  updated: tooltipDirective,
};
