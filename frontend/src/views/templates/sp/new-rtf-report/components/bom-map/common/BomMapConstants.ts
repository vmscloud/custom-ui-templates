import IconBomMapClockGray from '../assets/IconBomMapClockGray.svg';
import IconBomMapClockGreen from '../assets/IconBomMapClockGreen.svg';
import IconBomMapClockOrange from '../assets/IconBomMapClockOrange.svg';

export const ALIGN_SPACING: {
  VERTICAL: number;
  HORIZONTAL: number;
  WHITE_SPACE: number;
  INIT_SPACE: number;
} = {
  INIT_SPACE: 100,
  WHITE_SPACE: 200,
  VERTICAL: 180,
  HORIZONTAL: 220,
};

export const ALERT_COLOR: { [prop: string]: { FILL: string; STROKE: string } } = {
  SHORT: {
    FILL: '#DC5A5A',
    STROKE: '#DC5A5A',
  },
  LATE: {
    FILL: '#FA9E23',
    STROKE: '#FA9E23',
  },
  REMAIN: {
    FILL: '#DC5A5A',
    STROKE: '#DC5A5A',
  },
};

export const NODE_ICON_COLOR: {
  [prop: string]: { FILL: string; STROKE: string; STROKE_WIDTH: number };
} = {
  WHITE: {
    FILL: 'white',
    STROKE: '#6A7184',
    STROKE_WIDTH: 1,
  },
  GREEN: {
    FILL: '#26C4B0',
    STROKE: '#6A7184',
    STROKE_WIDTH: 1,
  },
  ORANGE: {
    FILL: '#FA9E23',
    STROKE: '#E68600',
    STROKE_WIDTH: 1,
  },
  RED: {
    FILL: '#DC5A5A',
    STROKE: '#993D48',
    STROKE_WIDTH: 1,
  },
  GRAY: {
    FILL: '#BAC6D4',
    STROKE: '#6A7184',
    STROKE_WIDTH: 1,
  },
  LIGHT_GRAY: {
    FILL: '#DDDDEC',
    STROKE: '#6A7184',
    STROKE_WIDTH: 1,
  },
};

export const NODE_HEADER_COLOR: {
  [prop: string]: { FILL: string; STROKE: string; STROKE_WIDTH: number };
} = {
  GREEN: {
    FILL: '#45E0C026',
    STROKE: '#357E63',
    STROKE_WIDTH: 1,
  },
  ORANGE: {
    FILL: '#FA9E2321',
    STROKE: '#F28270',
    STROKE_WIDTH: 1,
  },
  GRAY: {
    FILL: '#21408F10',
    STROKE: '#8998B5',
    STROKE_WIDTH: 1,
  },
};

export const NODE_HEADER_ICON: { [prop: string]: string } = {
  GREEN: IconBomMapClockGreen,
  ORANGE: IconBomMapClockOrange,
  GRAY: IconBomMapClockGray,
};

export const LINK_COLOR: {
  [prop: string]: { FILL: string; STROKE: string };
} = {
  NORMAL: {
    FILL: '#6A7184',
    STROKE: '#6A7184',
  },
  ASSEMBLY: {
    FILL: '#F28270',
    STROKE: '#F28270',
  },
  SPLITCO: {
    FILL: '#A768D6',
    STROKE: '#A768D6',
  },
  SPLITBY: {
    FILL: '#A768D6',
    STROKE: '#A768D6',
  },
};

export const SELECTED_COLOR: {
  LINK_FILL: string;
  LINK_STROKE: string;
  LINK_STROKE_WIDTH: number;
  NODE_FILL: string | null;
  NODE_STROKE: string;
  NODE_STROKE_WIDTH: number;
} = {
  LINK_FILL: '#4568E0',
  LINK_STROKE: '#4568E0',
  LINK_STROKE_WIDTH: 3,
  NODE_FILL: null,
  NODE_STROKE: '#4568E0',
  NODE_STROKE_WIDTH: 3,
};
