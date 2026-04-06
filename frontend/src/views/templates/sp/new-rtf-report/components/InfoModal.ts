import { ref } from 'vue';

let storeIdCounter = 0;
export const useInfoModalStore = () => {
  const storeId = ++storeIdCounter; // 고유 ID 생성

  const MODAL_DEFAULT_WIDTH = 1400; // 400으로 유지
  const MODAL_DEFAULT_HEIGHT = 400; // 300으로 유지
  // const MODAL_DEFAULT_LEFT = 100;
  // const MODAL_DEFAULT_TOP = 100;

  const open = ref(false);
  const left = ref(100);
  const top = ref(100);
  const width = ref(MODAL_DEFAULT_WIDTH);
  const height = ref(MODAL_DEFAULT_HEIGHT);
  const opacity = ref(1);

  const browserWidth = ref(window.innerWidth);
  const browserHeight = ref(window.innerHeight);

  const modalClose = () => {
    open.value = false;

    browserWidth.value = window.innerWidth;
    browserHeight.value = window.innerHeight;
  };

  const modalOpen = (leftPoistion?: number, topPosition?: number) => {
    open.value = true;

    width.value = MODAL_DEFAULT_WIDTH;
    height.value = MODAL_DEFAULT_HEIGHT;

    // 화면 안으로 강제 보정
    const maxLeft = window.innerWidth - MODAL_DEFAULT_WIDTH - 20;
    const maxTop = window.innerHeight - MODAL_DEFAULT_HEIGHT - 20;

    let finalLeft = leftPoistion !== undefined ? leftPoistion : 200;
    let finalTop = topPosition !== undefined ? topPosition : 200;

    // 화면 밖으로 나가지 않도록 보정
    finalLeft = Math.max(20, Math.min(finalLeft, maxLeft));
    finalTop = Math.max(20, Math.min(finalTop, maxTop));

    left.value = finalLeft;
    top.value = finalTop;

    browserWidth.value = window.innerWidth;
    browserHeight.value = window.innerHeight;
  };

  const updateBrowserSize = () => {
    browserWidth.value = window.innerWidth;
    browserHeight.value = window.innerHeight;
  };

  return {
    storeId, // 고유 ID 추가
    open,
    left,
    top,
    width,
    height,
    opacity,
    modalClose,
    modalOpen,
    browserWidth,
    browserHeight,
    updateBrowserSize,
  };
};
