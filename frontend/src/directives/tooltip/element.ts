export type TooltipXPos =
  | `toLeft`
  | `center`
  | `toRight`
  | `middle`
  | `middleReverse`
  | `toLeft, ${string}`
  | `center, ${string}`
  | `toRight, ${string}`
  | `middle, ${string}`
  | `middleReverse, ${string}`;
export type TooltipYPos =
  | `toTop`
  | `center`
  | `toBottom`
  | `middle`
  | `middleReverse`
  | `toTop, ${string}`
  | `center, ${string}`
  | `toBottom, ${string}`
  | `middle, ${string}`
  | `middleReverse, ${string}`;
export type TooltipTarget = 'element' | 'cursor';

export const getTooltipPosition = (
  tooltipEl: HTMLElement,
  event: MouseEvent,
  position: [TooltipXPos, TooltipYPos, TooltipTarget?] = ['center', 'toBottom', 'element'],
  targetEl?: HTMLElement,
  targetElRectParam?: DOMRect,
): {
  x: number;
  y: number;
} => {
  const { xPosParam, yPosParam, targetParam } = {
    xPosParam: position[0],
    yPosParam: position[1],
    targetParam: position[2] || 'element',
  };
  const CURSOR_SPACE_X = 6;
  const CURSOR_SPACE_Y = 6;
  const ELEMENT_SPACE_X = 2;
  const ELEMENT_SPACE_Y = 2;
  const TOOLTIP_BASE_HEIGHT = 31;

  let x = 0;
  let y = 0;
  let xPos: string = xPosParam;
  let yPos: string = yPosParam;
  let marginX = '0px';
  let marginY = '0px';
  let marginXSign = 1;
  let marginYSign = 1;
  let targetElRect: DOMRect | null | undefined = targetElRectParam;

  if (!targetElRect) {
    if (targetEl) {
      targetElRect = targetEl.getBoundingClientRect();
    } else {
      if (event.target instanceof Element) {
        targetElRect = event.target.getBoundingClientRect();
      }
    }
  }

  if (!targetElRect) return { x, y };

  if (xPosParam.includes(',')) {
    const [pos, margin] = xPosParam.split(',').map((s) => s.trim());
    xPos = pos;
    if (margin.includes('-')) {
      marginXSign = -1;
      marginX = margin.replace('-', '');
    } else {
      marginX = margin;
    }
  }
  if (yPosParam.includes(',')) {
    const [pos, margin] = yPosParam.split(',').map((s) => s.trim());
    yPos = pos;
    if (margin.includes('-')) {
      marginYSign = -1;
      marginY = margin.replace('-', '');
    } else {
      marginY = margin;
    }
  }

  let dummyWrapperEl: HTMLElement | null = null;
  let dummyEl: HTMLElement | null = null;
  if (targetEl || event.target instanceof Element) {
    const ele = targetEl || (event.target as HTMLElement);
    const existingDummyWrapperEl = document.querySelectorAll('.tooltip-dummy-wrapper');
    if (existingDummyWrapperEl && existingDummyWrapperEl.length > 0) {
      existingDummyWrapperEl.forEach((el) => {
        document.body.removeChild(el);
      });
    }
    dummyWrapperEl = document.createElement('div');
    dummyEl = document.createElement('div');
    dummyWrapperEl.appendChild(dummyEl);
    dummyWrapperEl.classList.add('tooltip-dummy-wrapper');
    dummyWrapperEl.setAttribute(
      'style',
      `position: absolute; pointer-events: none; visibility: hidden; width: ${ele.offsetWidth}px; height: ${ele.offsetHeight}px;`,
    );
    dummyEl.setAttribute('style', `width: ${marginX}; height: ${marginY};`);
    document.body.appendChild(dummyWrapperEl);
  }

  const marginXNum = dummyEl ? dummyEl.offsetWidth * marginXSign : 0;
  const marginYNum = dummyEl ? dummyEl.offsetHeight * marginYSign : 0;

  if (targetParam === 'cursor') {
    switch (xPos) {
      case 'toLeft':
        x = event.clientX - tooltipEl.offsetWidth - marginXNum - CURSOR_SPACE_X;
        break;
      case 'toRight':
        x = event.clientX + marginXNum + CURSOR_SPACE_X;
        break;
      default:
        x = event.clientX + marginXNum + CURSOR_SPACE_X;
        break;
    }
    switch (yPos) {
      case 'toTop':
        y = event.clientY - tooltipEl.offsetHeight - marginYNum - CURSOR_SPACE_Y;
        break;
      case 'toBottom':
        y = event.clientY + marginYNum + CURSOR_SPACE_Y;
        break;
      default:
        y = event.clientY + marginYNum + CURSOR_SPACE_Y;
        break;
    }
  } else {
    switch (xPos) {
      case 'toLeft':
        x = targetElRect.left - tooltipEl.offsetWidth - marginXNum - ELEMENT_SPACE_X;
        break;
      case 'toRight':
        x = targetElRect.left + marginXNum + targetElRect.width + ELEMENT_SPACE_X;
        break;
      case 'center':
        x = targetElRect.left + targetElRect.width / 2 - tooltipEl.offsetWidth / 2 + marginXNum;
        break;
      case 'middle':
        x = targetElRect.left + targetElRect.width / 2 + marginXNum;
        break;
      case 'middleReverse':
        x = targetElRect.left + targetElRect.width / 2 - tooltipEl.offsetWidth - marginXNum;
        break;
    }
    switch (yPos) {
      case 'toTop':
        y = targetElRect.top - tooltipEl.offsetHeight - marginYNum - ELEMENT_SPACE_Y;
        break;
      case 'toBottom':
        y = targetElRect.top + targetElRect.height + marginYNum + ELEMENT_SPACE_Y;
        break;
      case 'center':
        y = targetElRect.top + targetElRect.height / 2 - tooltipEl.offsetHeight / 2 + marginYNum;
        break;
      case 'middle':
        y = targetElRect.top + targetElRect.height / 2 - TOOLTIP_BASE_HEIGHT / 2 + marginYNum;
        break;
      case 'middleReverse':
        y =
          targetElRect.top +
          targetElRect.height / 2 -
          TOOLTIP_BASE_HEIGHT / 2 -
          (tooltipEl.offsetHeight - TOOLTIP_BASE_HEIGHT) -
          marginYNum;
        break;
    }
  }

  x = Math.min(x, window.innerWidth - tooltipEl.offsetWidth - 1);
  x = Math.max(x, 0);
  y = Math.min(y, window.innerHeight - tooltipEl.offsetHeight);
  y = Math.max(y, 0);

  return {
    x,
    y,
  };
};

export const removeAllClass = (name?: string) => {
  const className = name || 'tooltip';
  const els = document.getElementsByClassName(className);
  if (els && els.length > 0) {
    for (let i = els.length - 1; i >= 0; i--) {
      document.body.removeChild(els[i]);
    }
  }
};

export const addTooltipEvent = (
  element: HTMLElement | string,
  tooltip: string,
  handleEllipsis: boolean | HTMLElement | string = false,
  position: [TooltipXPos, TooltipYPos, TooltipTarget?] = ['center', 'toBottom', 'element'],
  showImmediate: boolean = false,
): void => {
  const { xPos, yPos, target } = { xPos: position[0], yPos: position[1], target: position[2] || 'element' };

  const TRANSITION_DURATION = 120;
  let removeTimer: ReturnType<typeof setTimeout>;

  let el: HTMLElement | null = null;
  if (typeof element === 'string') {
    el = document.getElementById(element as string);
  } else {
    el = element as HTMLElement;
  }

  if (!el) return;
  if (!tooltip) return;

  el.classList.add('has-tooltip');

  const divEl = document.createElement('div');

  let elRect: DOMRect;

  elRect = el.getBoundingClientRect();

  el.onmouseenter = null;
  el.onmousemove = null;
  el.onmouseleave = null;
  el.onclick = null;
  el.onmousedown = null;
  el.onmouseup = null;
  el.onfocus = null;
  el.onblur = null;

  const tooltipFunction = (evt: MouseEvent) => {
    divEl.classList.remove('tooltip-removing');

    if (handleEllipsis === true) {
      if (el && el.offsetWidth >= el.scrollWidth) {
        return;
      }
    } else if (handleEllipsis instanceof HTMLElement && handleEllipsis?.offsetWidth != undefined) {
      if (handleEllipsis?.offsetWidth >= handleEllipsis?.scrollWidth) {
        return;
      }
    } else if (typeof handleEllipsis === 'string') {
      if (el) {
        const ellipsisEl = el.querySelector(handleEllipsis) as HTMLElement;
        if (ellipsisEl) {
          if (ellipsisEl.offsetWidth >= ellipsisEl.scrollWidth) return;
        } else {
          return;
        }
      }
    } else if (handleEllipsis !== false && !handleEllipsis) {
      return;
    }

    removeAllClass('tooltip-presenting');

    divEl.classList.add('tooltip-presenting');
    divEl.classList.add('tooltip');
    divEl.innerHTML = tooltip;

    divEl.style.opacity = '0%';

    document.body.appendChild(divEl);
    const { x, y } = getTooltipPosition(divEl, evt, position);

    divEl.style.left = `${x}px`;
    divEl.style.top = `${y}px`;

    divEl.style.transitionProperty = 'opacity';
    divEl.style.transitionDuration = `${TRANSITION_DURATION}ms`;
    setTimeout(() => {
      divEl.style.opacity = '1';
    }, 0);
  };

  if (showImmediate && el) {
    (el as HTMLElement).onmousemove = tooltipFunction;
    setTimeout(() => {
      (el as HTMLElement).onmousemove = null;
    });
  }

  el.onmouseenter = tooltipFunction;
  el.onfocus = (e: FocusEvent) => {
    if (!e.relatedTarget) tooltipFunction(e as MouseEvent);
  };

  if (target === 'cursor') {
    el.onmousemove = (evt: MouseEvent) => {
      if (el) {
        const { x, y } = getTooltipPosition(divEl, evt, position, el, elRect);
        divEl.style.left = `${x}px`;
        divEl.style.top = `${y}px`;
      }
    };
  }

  const removeTooltip = () => {
    divEl.classList.remove('tooltip-presenting');
    divEl.classList.add('tooltip-removing');
    divEl.style.opacity = '0';
    removeTimer = setTimeout(() => {
      removeAllClass(`tooltip-removing`);
    }, TRANSITION_DURATION);
  };

  el.onmouseleave = (evt: MouseEvent) => {
    removeTooltip();
  };
  el.onclick = () => {
    removeTooltip();
  };
  el.onmousedown = () => {
    removeTooltip();
  };
  el.onmouseup = () => {
    removeTooltip();
  };
  el.onblur = () => {
    removeTooltip();
  };
};

export const removeTooltipEvent = (element: HTMLElement | string) => {
  let el: HTMLElement | null = null;
  if (typeof element === 'string') {
    el = document.getElementById(element as string);
  } else {
    el = element as HTMLElement;
  }

  if (!el) return;

  el.onmouseenter = null;
  el.onmouseleave = null;
  el.onclick = null;
};
