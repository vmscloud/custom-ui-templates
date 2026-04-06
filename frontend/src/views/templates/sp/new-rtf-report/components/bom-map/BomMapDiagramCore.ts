// @ts-nocheck — GoJS 3.x type incompatibilities with original 2.x code
import { convertToInternationalization, formatCompactNumber } from '@moz-shared/utils';
import * as go from 'gojs';
import { Diagram } from 'gojs';
import { onBeforeUnmount } from 'vue';
import {
  ALERT_COLOR,
  ALIGN_SPACING,
  LINK_COLOR,
  NODE_HEADER_COLOR,
  NODE_HEADER_ICON,
  NODE_ICON_COLOR,
  SELECTED_COLOR,
} from './common/BomMapConstants';
import { CustomTreeLayout } from './diagram-layout/BomMapDiagramCoreLayout';
// @ts-ignore
import { RealtimeDragSelectingTool } from './diagram-layout/RealtimeDragSelectingTool';

type paramsType = { diagramID: string; overviewID: string; initConfigs: any };

export const initDiagram = async ({ diagramID, overviewID, initConfigs }: paramsType) => {
  const NODE_WIDTH = 180;
  const NODE_HEIGHT = 136;

  /**
   * 노드 관련 이벤트를 저장하는 객체
   */
  let nodeEvents: any = {
    bom: {
      click: () => {},
      contextClick: () => {},
      doubleClick: () => {},
      mouseEnter: () => {},
      mouseLeave: () => {},
    },
    buffer: {
      click: () => {},
      contextClick: () => {},
      doubleClick: () => {},
      mouseEnter: () => {},
      mouseLeave: () => {},
    },
    alert: {
      click: () => {},
      contextClick: () => {},
      doubleClick: () => {},
      mouseEnter: () => {},
      mouseLeave: () => {},
    },
    label: {
      click: () => {},
      contextClick: () => {},
      doubleClick: () => {},
      mouseEnter: () => {},
      mouseLeave: () => {},
    },
  };

  /**
   * 노드 관련 설정을 저장하는 객체
   */
  let configs = initConfigs;
  // let configs = {
  //   bufferNode: {
  //     label1: 'itemName',
  //     label2: '',
  //   },
  //   bomNode: {
  //     headerLabel1: 'hide',
  //   },
  //   qtyUnit: 'planQty',
  //   initialViewPoint: 'fitToScreen',
  // };

  /**
   * 노드 관련 이벤트를 설정하는 Setter
   */
  const setNodeEvents = (value: any) => {
    nodeEvents = { ...nodeEvents, ...value };
  };

  /**
   * 노드 관련 설정을 설정하는 Setter
   */
  const setConfigs = (value: any) => {
    configs = value;
    myDiagram.updateAllTargetBindings();
    myDiagram.redraw();
    // myDiagram.layoutDiagram(true);
  };

  /**
   * 노드 관련 이벤트 객체를 반환하는 함수, Node에서 실제적으로 사용됨
   */
  const nodeEventsHandler = (key: string) => ({
    click: (e: go.InputEvent, obj: go.GraphObject) => {
      if (nodeEvents[key] && nodeEvents[key]?.click) {
        nodeEvents[key].click(e, obj.part);
      }
    },
    // 노드에서 우클릭 이벤트 핸들러 등록
    contextClick: (e: go.InputEvent, obj: go.GraphObject) => {
      if (nodeEvents[key] && nodeEvents[key]?.contextClick) {
        nodeEvents[key].contextClick(e, obj.part);
      }
    },
    doubleClick: (e: go.InputEvent, obj: go.GraphObject) => {
      if (nodeEvents[key] && nodeEvents[key].doubleClick) {
        nodeEvents[key].doubleClick(e, obj.part);
      }
    },
    mouseEnter(e: go.InputEvent, obj: go.GraphObject) {
      if (nodeEvents[key] && nodeEvents[key].mouseEnter) {
        nodeEvents[key].mouseEnter(e, obj.part);
      }
    },
    mouseLeave(e: go.InputEvent, obj: go.GraphObject) {
      if (nodeEvents[key] && nodeEvents[key].mouseLeave) {
        nodeEvents[key].mouseLeave(e, obj.part);
      }
    },
  });

  /**
   * Diagram을 선언, bom-map-canvas 태그에 적용하고 전체적인 Layout을 설정하는 로직
   */
  const $ = go.GraphObject.make;
  let myDiagram: Diagram = $(go.Diagram, diagramID, {
    'toolManager.dragSelectingTool': $(RealtimeDragSelectingTool, { isPartialInclusion: true }),
    initialAutoScale: go.Diagram.Uniform,
    initialContentAlignment: go.Spot.Center,
    initialViewportSpot: go.Spot.Center,
    initialDocumentSpot: go.Spot.Center,
    'contextMenuTool.isEnabled': false, // 기본 컨텍스트 메뉴 비활성화
    ...(configs.layoutMode === 0
      ? {
          layout: $(CustomTreeLayout, {
            // portSpot: go.Spot.Right,
            // childPortSpot: go.Spot.Left,

            setsPortSpot: false, // Link.fromSpot과 Link.toSpot을 자동으로 설정하지 않음
            setsChildPortSpot: false, // Link.fromSpot과 Link.toSpot을 자동으로 설정하지 않음
            isOngoing: false,
            angle: 0,
            alignment: go.TreeLayout.AlignmentStart,
            layerSpacingParentOverlap: 40 / NODE_WIDTH,
            // arrangement: go.TreeLayout.ArrangementVertical
          }),
        }
      : {}),
    ...(configs.layoutMode === 1
      ? {
          layout: $(go.LayeredDigraphLayout, {
            isOngoing: false,
            setsPortSpots: false,
            alignOption: go.LayeredDigraphLayout.AlignAll,
            cycleRemoveOption: go.LayeredDigraphLayout.InitDepthFirstOut,
            columnSpacing: 0, // 노드 간의 세로 간격 조정
          }),
        }
      : {}),
    // 스크롤바 표시 여부 옵션, 이 옵션을 설정하면 undoManager 관련 버그가 생김.
    // hasHorizontalScrollbar: false,
    // hasVerticalScrollbar: false,
    // layout: $(go.LayeredDigraphLayout, {
    //   isOngoing: false,
    //   setsPortSpots: false,
    //   alignOption: go.LayeredDigraphLayout.AlignAll,
    //   cycleRemoveOption: go.LayeredDigraphLayout.InitDepthFirstOut,
    //   columnSpacing: 0 // 노드 간의 세로 간격 조정
    // })
    // layout: $(CustomTreeLayout, {
    //   // portSpot: go.Spot.Right,
    //   // childPortSpot: go.Spot.Left,

    //   setsPortSpot: false, // Link.fromSpot과 Link.toSpot을 자동으로 설정하지 않음
    //   setsChildPortSpot: false, // Link.fromSpot과 Link.toSpot을 자동으로 설정하지 않음
    //   isOngoing: false,
    //   angle: 0,
    //   alignment: go.TreeLayout.AlignmentStart,
    //   layerSpacingParentOverlap: 40 / NODE_WIDTH,
    //   // arrangement: go.TreeLayout.ArrangementVertical
    // }),
  });

  /**
   * Diagram의 Undo/Redo 기능 활성화
   */
  myDiagram.model.undoManager.isEnabled = true;

  /**
   * Diagram의 Scroll 마진 지정
   */
  myDiagram.scrollMargin = ALIGN_SPACING.WHITE_SPACE;

  /**
   * 경고 알림에 대한 Shape를 생성하는 로직
   */
  go.Shape.defineFigureGenerator('AllRoundedRectangle', (shape, w, h) => {
    let p1 = 50; // default corner size
    if (shape !== null) {
      const param1 = shape.parameter1;
      if (!isNaN(param1) && param1 >= 0) p1 = param1;
    }
    p1 = Math.min(p1, w / 2);
    p1 = Math.min(p1, h / 2);
    const geo = new go.Geometry();

    geo.add(
      new go.PathFigure(0, p1)
        .add(new go.PathSegment(go.PathSegment.Arc, 180, 90, p1, p1, p1, p1))
        .add(new go.PathSegment(go.PathSegment.Line, w - p1, 0))
        .add(new go.PathSegment(go.PathSegment.Arc, 270, 90, w - p1, p1, p1, p1))
        .add(new go.PathSegment(go.PathSegment.Line, w, h - p1))
        .add(new go.PathSegment(go.PathSegment.Arc, 0, 90, w - p1, h - p1, p1, p1))
        .add(new go.PathSegment(go.PathSegment.Line, p1, h))
        .add(new go.PathSegment(go.PathSegment.Arc, 90, 90, p1, h - p1, p1, p1).close()),
    );

    geo.spot1 = new go.Spot(0, 0, 0.3, 0.3);
    geo.spot2 = new go.Spot(1, 1, -0.3, -0.3);
    return geo;
  });

  go.Shape.defineFigureGenerator('RoundedTopRectangle', (shape, w, h) => {
    // this figure takes one parameter, the size of the corner
    let p1 = 5; // default corner size
    if (shape !== null) {
      const param1 = shape.parameter1;
      if (!isNaN(param1) && param1 >= 0) p1 = param1; // can't be negative or NaN
    }
    p1 = Math.min(p1, w / 2);
    p1 = Math.min(p1, h / 2); // limit by whole height or by half height?
    const geo = new go.Geometry();
    // a single figure consisting of straight lines and quarter-circle arcs
    geo.add(
      new go.PathFigure(0, p1)
        .add(new go.PathSegment(go.PathSegment.Arc, 180, 90, p1, p1, p1, p1))
        .add(new go.PathSegment(go.PathSegment.Line, w - p1, 0))
        .add(new go.PathSegment(go.PathSegment.Arc, 270, 90, w - p1, p1, p1, p1))
        .add(new go.PathSegment(go.PathSegment.Line, w, h))
        .add(new go.PathSegment(go.PathSegment.Line, 0, h).close()),
    );
    // don't intersect with two top corners when used in an "Auto" Panel
    geo.spot1 = new go.Spot(0, 0, 0.3 * p1, 0.3 * p1);
    geo.spot2 = new go.Spot(1, 1, -0.3 * p1, 0);
    return geo;
  });

  /**
   * Adornment가 노드의 위가 아닌 밑에 뜨게 하기 위한 레이어 생성
   */
  const forelayer = myDiagram.findLayer('Foreground');
  myDiagram.addLayerBefore($(go.Layer, { name: 'BackAdornment', isTemporary: true }), forelayer!);

  /**
   * NodeTemplate 선언부
   */
  const alertNode = () =>
    $(
      go.Panel,
      'Auto',
      {
        margin: new go.Margin(6, 0, 0, 0),
        height: 0,
        cursor: 'pointer',
        ...nodeEventsHandler('alert'),
        visible: false,
      },
      // new go.Binding('visible', 'alerts', v => v.length >= 1).makeTwoWay(),
      new go.Binding('height', 'alerts', (v) => (v.length >= 1 ? 21 : 0)).makeTwoWay(),
      new go.Binding('visible', 'alerts', (v) => !!Array.isArray(v)).makeTwoWay(),
      $(
        go.Shape,
        'AllRoundedRectangle',
        { fill: '#DC5A5A', stroke: '#DC5A5A' },
        new go.Binding('fill', 'alerts', (v) => ALERT_COLOR[v[0].color].FILL).makeTwoWay(),
        new go.Binding('stroke', 'alerts', (v) => ALERT_COLOR[v[0].color].STROKE).makeTwoWay(),
      ),
      // $(go.Picture, {
      //   width: 16,
      //   alignment: go.Spot.Left,
      //   height: 16,
      //   margin: new go.Margin(0, 0, 0, 8),
      //   source: `../assets/icons/IconBomMapAlert.svg`
      // }),

      $(
        go.Panel,
        'Horizontal',
        { padding: new go.Margin(0, 8, 2, 8) },
        $(
          go.Panel,
          'Table',
          { width: 105, height: 21, visible: true },
          $(
            go.TextBlock,
            {
              margin: new go.Margin(3.5, 0, 0, 0),
              stroke: 'white',
              font: "500 16px 'Roboto', 'Noto Sans KR'",
              stretch: go.GraphObject.UniformToFill,
              overflow: go.TextBlock.OverflowEllipsis,
              wrap: go.TextBlock.WrapBreakAll,
            },
            new go.Binding('text', 'alerts', (v) => convertToInternationalization(v[0].label, 'short')).makeTwoWay(),
          ),
        ),
        $(
          go.TextBlock,
          {
            margin: new go.Margin(2.5, 0, 0, 0),
            stroke: 'white',
            font: "500 16px 'Roboto', 'Noto Sans KR'",
            stretch: go.GraphObject.UniformToFill,
            overflow: go.TextBlock.OverflowEllipsis,
          },
          // new go.Binding('margin', 'alerts', v => (v.length > 1 ? new go.Margin(0, 0, 0, 0) : null)).makeTwoWay(),
          new go.Binding('text', 'alerts', (v) => (v.length > 1 ? `(${v.length})` : '')).makeTwoWay(),
        ),

        // $(
        //   go.Picture,
        //   {
        //     margin: new go.Margin(0, 8, 0, 6),
        //     width: 16,
        //     alignment: go.Spot.Left,
        //     height: 16,
        //     source: `../assets/icons/IconBomMapShowFalse.svg`
        //   }
        //   // new go.Binding('source', 'isSelected', v =>
        //   //   v ? `../assets/icons/IconBomMapShowTrue.svg` : `../assets/icons/IconBomMapShowFalse.svg`
        //   // ).ofObject()
        // )
      ),
    );

  const bufferNodeAdornment = () =>
    $(
      go.Adornment,
      'Auto',

      {
        layerName: 'BackAdornment',
        cursor: 'pointer',
        ...nodeEventsHandler('buffer'),
      },
      $(
        go.Panel,
        'Vertical',
        $(
          go.Panel,
          'Position',
          $(go.Shape, 'Triangle', {
            fill: '#4568E0',
            stroke: null,
            opacity: 0.3,
            width: 70,
            height: 64,
            position: new go.Point(0, 41),
          }),
        ),
      ),

      $(go.Placeholder, {}),
    ); // end Adornment
  const bufferNodeHeader = () =>
    $(
      go.Panel,
      'Spot',
      { width: NODE_WIDTH, height: 32 },
      $(
        go.Shape,
        'RoundedTopRectangle',
        {
          alignment: go.Spot.Center, // Panel 내에서의 위치
          parameter1: 0,
          strokeWidth: 0,
          fill: NODE_HEADER_COLOR.GRAY.FILL,
          stretch: go.GraphObject.Fill, // 패널의 전체 영역을 채우도록 설정
        },
        new go.Binding('parameter1', 'isFirstNode', (v) => (v ? 10.5 : 0)),
        new go.Binding('fill', '', (v) => {
          if (v.targetDatetime === null || v.planGap === null || !v[configs.qtyUnit]) {
            return NODE_HEADER_COLOR.GRAY.FILL;
          } else if (v.planGap > 0) {
            return NODE_HEADER_COLOR.ORANGE.FILL;
          } else if (v.planGap <= 0) {
            return NODE_HEADER_COLOR.GREEN.FILL;
          }
          return NODE_HEADER_COLOR.GRAY.FILL;
        }),
      ),
      $(
        go.Panel,
        'Horizontal',
        { visible: true },
        $(
          go.Picture,
          {
            width: 16,
            // alignment: go.Spot.Center,
            height: 16,
            source: NODE_HEADER_ICON.GRAY,
          },
          new go.Binding('source', '', (v) => {
            if (v.planGap === null || !v[configs.qtyUnit]) {
              return NODE_HEADER_ICON.GRAY;
            } else if (v.planGap > 0) {
              return NODE_HEADER_ICON.ORANGE;
            } else if (v.planGap <= 0) {
              return NODE_HEADER_ICON.GREEN;
            }
            return NODE_HEADER_ICON.GRAY;
          }),
        ),
        $(
          go.TextBlock,
          {
            font: "500 16px 'Roboto', 'Noto Sans KR'",
            stroke: '#357E63',
            _isNodeLabel: true,
            // textAlign: 'center',
            margin: new go.Margin(2.5, 0, 0, 4),
            text: 'DelayedTime',
            // maxSize: new go.Size(150, 18),
            // minSize: new go.Size(150, 18),
            // stretch: go.GraphObject.UniformToFill,
            // overflow: go.TextBlock.OverflowEllipsis
          },
          new go.Binding('text', '', (v) => {
            if (v.planGap === null || !v[configs.qtyUnit]) {
              return `- Day`;
            } else if (Number(v.planGap) === 0) {
              return `-${v.planGap} Day`;
            } else if (v.planGap > 0) {
              return `+${v.planGap} Day`;
            } else if (v.planGap < 0) {
              return `${v.planGap} Day`;
            }
            return '- Day';
          }),
          new go.Binding('stroke', '', (v) => {
            if (v.planGap === null || !v[configs.qtyUnit]) {
              return NODE_HEADER_COLOR.GRAY.STROKE;
            } else if (v.planGap > 0) {
              return NODE_HEADER_COLOR.ORANGE.STROKE;
            } else if (v <= 0) {
              return NODE_HEADER_COLOR.GREEN.STROKE;
            }
            return NODE_HEADER_COLOR.GRAY.STROKE;
          }),
        ),
        new go.Binding('opacity', '', (v) => (v.targetDatetime ? 1 : 0)),
      ),
    );

  const bufferNodeAbsoluteElement = () =>
    $(
      go.Panel,
      'Position',
      { margin: new go.Margin(0, 0, -17, 0) },
      $(
        go.TextBlock,
        {
          font: "500 16px 'Roboto', 'Noto Sans KR'",
          stroke: '#96A5BE',
          text: 'Unpeg',
          textAlign: 'right',
          width: NODE_WIDTH - 20,
          // alignment: go.Spot.TopRight,

          position: new go.Point(0, 8),
        },
        new go.Binding('text', 'unpegQty', (v) =>
          v > 0 ? formatCompactNumber(v, { returnWhenInvalid: '', convertUnit: { standard: 1_000_000 } }) : '',
        ),
      ),
    );

  const bufferNodeIcon = () =>
    $(
      go.Panel,
      'Spot',
      {
        ...nodeEventsHandler('buffer'),
        cursor: 'pointer',
      },

      $(
        go.Shape,
        'Triangle',
        {
          width: 70,
          height: 65,
          strokeWidth: 0,
          fill: '#4568E0',
          alignment: new go.Spot(0.5, 0.45),
          // margin: new go.Margin(-10, 0, 0, 0)
        },
        new go.Binding('opacity', 'isHighlighted', (h) => (h ? 0.3 : 0)).ofObject(),
      ),
      $(
        go.Panel,
        'Position',
        $(
          go.Shape,
          'Triangle',
          {
            name: 'ICON',
            width: 55,
            height: 50,
            strokeWidth: 1,
            fill: 'white',
            portId: '',
            // fromSpot: new go.Spot(0.0, 0.5, 0, 2.5),
            // toSpot: new go.Spot(0.0, 0.5, 0, 2.5),
            fromSpot: new go.Spot(0.79, 0.55),
            toSpot: new go.Spot(0.21, 0.55),
            fromEndSegmentLength: 11,
            toEndSegmentLength: 11,
            position: new go.Point(0, 5),
            // alignment: go.Spot.Center
          },
          new go.Binding('fill', 'iconColor', (v) => (v ? NODE_ICON_COLOR[v].FILL : NODE_ICON_COLOR.WHITE.FILL)),
          new go.Binding('stroke', 'iconColor', (v) => (v ? NODE_ICON_COLOR[v].STROKE : NODE_ICON_COLOR.WHITE.STROKE)),
          new go.Binding('strokeWidth', 'iconColor', (v) =>
            v ? NODE_ICON_COLOR[v].STROKE_WIDTH : NODE_ICON_COLOR.WHITE.STROKE_WIDTH,
          ),
        ),
      ),

      $(
        go.Panel,
        { minSize: new go.Size(64, 21), visible: true },
        'Auto',
        $(
          go.Shape,
          'AllRoundedRectangle',
          {
            height: 21,
            strokeWidth: 1,
            fill: '#618FF9',
            stroke: null,
            margin: new go.Margin(10, 0, 0, 0),
            fromSpot: new go.Spot(1, 0.5),
            toSpot: new go.Spot(0, 0.5),
            fromEndSegmentLength: 11,
            toEndSegmentLength: 11,
            portId: 'disabled',
          },
          new go.Binding('portId', 'targetDatetime', (v) => (v ? '' : 'disabled')),
        ),
        $(
          go.TextBlock,
          {
            font: "500 16px 'Roboto', 'Noto Sans KR'",
            stroke: '#FFFFFF',
            text: 'Out AccQty',
            margin: new go.Margin(2, 8, 0, 8),
          },
          // new go.Binding('text', 'targetDatetime')
          new go.Binding('text', '', (v) =>
            Number(v[configs.qtyUnit]) === 0
              ? '-'
              : formatCompactNumber(v[configs.qtyUnit], {
                  returnWhenInvalid: '-',
                  convertUnit: { standard: 1_000_000 },
                }),
          ),
        ),
        new go.Binding('visible', 'targetDatetime', (v) => !!v),
      ),
    );

  const bufferNodeLabel = () =>
    $(
      go.Panel,
      'Vertical',
      {
        ...nodeEventsHandler('label'),
      },
      $(
        go.TextBlock,
        {
          font: "400 16px 'Roboto', 'Noto Sans KR'",
          stroke: '#233253',
          _isNodeLabel: true,
          textAlign: 'center',
          maxSize: new go.Size(170, 16),
          minSize: new go.Size(170, 16),
          stretch: go.GraphObject.UniformToFill,
          overflow: go.TextBlock.OverflowEllipsis,
          wrap: go.TextBlock.WrapBreakAll,
        },
        new go.Binding('text', '', (v) => v[configs.bufferNode.label1]),
      ),
      $(
        go.TextBlock,
        {
          font: "400 16px 'Roboto', 'Noto Sans KR'",
          stroke: '#233253',
          _isNodeLabel: true,
          textAlign: 'center',
          maxSize: new go.Size(170, 16),
          minSize: new go.Size(170, 0),
          stretch: go.GraphObject.UniformToFill,
          overflow: go.TextBlock.OverflowEllipsis,
          wrap: go.TextBlock.WrapBreakAll,
        },
        new go.Binding('text', '', (v) => v[configs.bufferNode.label2] ?? ''),
        new go.Binding('height', '', (v) => (v[configs.bufferNode.label2] ? NaN : 0)),
      ),
    );

  const bufferNodeMargin = () =>
    $(go.Panel, 'Vertical', {
      margin: new go.Margin(0, 0, 7, 0),
    });

  const bomNodeAdornment = () =>
    $(
      go.Adornment,
      'Auto',

      { layerName: 'BackAdornment', cursor: 'pointer', ...nodeEventsHandler('bom') },
      $(
        go.Panel,
        'Vertical',
        $(
          go.Panel,
          'Position',
          $(go.Shape, 'RoundedRectangle', {
            // alignmentFocus: new go.Spot(go.Spot.Bottom.x, go.Spot.Bottom.y, 0, 20),
            fill: '#4568E0',
            strokeWidth: 0,
            opacity: 0.3,
            width: 61,
            height: 60,
            position: new go.Point(0, 45),
          }),
        ),
      ),

      $(go.Placeholder, {
        // padding: 25,
        margin: new go.Margin(-4, 0, 0, 0),
      }),
    );

  const bomNodeHeader = () =>
    $(
      go.TextBlock,
      {
        font: "500 16px 'Roboto', 'Noto Sans KR'",
        stroke: '#233253',
        // _isNodeLabel: true,
        textAlign: 'center',
        text: 'AccTAT',
        // maxSize: new go.Size(150, 14),
        // minSize: new go.Size(150, NaN),
        // stretch: go.GraphObject.UniformToFill,
        // overflow: go.TextBlock.OverflowEllipsis
      },
      new go.Binding('text', '', (v) => v[configs.bomNode.headerLabel1] ?? ''),
      // new go.Binding('height', 'label', l => (l.length === 0 ? 0 : 14))
    );

  const bomNodeIcon = () =>
    $(
      go.Panel,
      {
        ...nodeEventsHandler('bom'),
        cursor: 'pointer',
      },
      'Spot',
      { margin: new go.Margin(4, 0, 0, 0) },
      $(
        go.Shape,
        'RoundedRectangle',
        {
          width: 61,
          height: 60,
          strokeWidth: 0,
          fill: '#4568E0',
          alignment: new go.Spot(0.5, 0.5),
        },
        new go.Binding('opacity', 'isHighlighted', (h) => (h ? 0.3 : 0)).ofObject(),
      ),
      $(
        go.Shape,
        'RoundedRectangle',
        {
          name: 'ICON',
          width: 50,
          height: 50,
          // strokeWidth: 1,
          fill: 'white',
          portId: '',
          fromSpot: new go.Spot(1, 0.5),
          toSpot: new go.Spot(0, 0.5),
          fromEndSegmentLength: 11,
          toEndSegmentLength: 11,
          // margin: new go.Margin(0, 0, 6, 0)
        },
        new go.Binding('fill', 'iconColor', (v) => (v ? NODE_ICON_COLOR[v].FILL : NODE_ICON_COLOR.WHITE.FILL)),
        new go.Binding('stroke', 'iconColor', (v) => (v ? NODE_ICON_COLOR[v].STROKE : NODE_ICON_COLOR.WHITE.STROKE)),
        new go.Binding('strokeWidth', 'iconColor', (v) =>
          v ? NODE_ICON_COLOR[v].STROKE_WIDTH : NODE_ICON_COLOR.WHITE.STROKE_WIDTH,
        ),
      ),
    );

  const bomNodeLabel = () =>
    $(
      go.Panel,
      {
        ...nodeEventsHandler('label'),
      },
      'Vertical',
      $(
        go.TextBlock,
        {
          font: "400 16px 'Roboto', 'Noto Sans KR'",
          stroke: '#233253',
          _isNodeLabel: true,
          textAlign: 'center',
          maxSize: new go.Size(150, 16),
          minSize: new go.Size(150, NaN),
          stretch: go.GraphObject.UniformToFill,
          overflow: go.TextBlock.OverflowEllipsis,
        },
        new go.Binding('text', '', (v) => v[configs.bomNode.label1]),
        new go.Binding('height', '', (v) => (v[configs.bomNode.label1].length === 0 ? 0 : 16)),
      ),
    );

  // Buffer Node
  myDiagram.nodeTemplateMap.add(
    'Buffer', // male
    $(
      go.Node,
      'Vertical',
      {
        minSize: new go.Size(NODE_WIDTH, NODE_HEIGHT),
        selectionChanged: onNodeSelection,
        layerName: 'Foreground',
        selectionAdornmentTemplate: bufferNodeAdornment(),
      },
      bufferNodeHeader(),
      bufferNodeAbsoluteElement(),
      bufferNodeIcon(),
      bufferNodeLabel(),
      alertNode(),
      bufferNodeMargin(),
    ),
  );

  // Bom Node
  myDiagram.nodeTemplateMap.add(
    'Bom',
    $(
      go.Node,
      'Vertical',
      {
        minSize: new go.Size(NODE_WIDTH, NODE_HEIGHT),
        padding: new go.Margin(26.5, 0, 0, 0),
        selectionChanged: onNodeSelection,
        layerName: 'Foreground',
        selectionAdornmentTemplate: bomNodeAdornment(),
      },
      bomNodeHeader(),
      bomNodeIcon(),
      bomNodeLabel(),
      alertNode(),
    ),
  );

  /**
   * GroupTemplate 선언부
   */
  // Buffer Group
  myDiagram.groupTemplateMap.add(
    'Buffer',
    $(go.Group, 'Vertical', {
      locationSpot: go.Spot.Top,
      layout: $(go.GridLayout, { isOngoing: false, cellSize: new go.Size(NODE_WIDTH, NaN), wrappingColumn: 1 }),
      // layout: $(go.LayeredDigraphLayout, { isOngoing: false }),
      minSize: new go.Size(NODE_WIDTH + 10, NaN),
      // maxSize: new go.Size(NODE_WIDTH + 10, NaN),
      selectionAdorned: false,
      layerName: 'Background',
      // selectable: false
    }).add(
      $(
        go.Panel,
        'Spot',
        $(
          go.TextBlock,
          {
            margin: 4,
            font: "700 16pt 'Roboto', 'Noto Sans KR'",
            stroke: '#738099',
          },
          new go.Binding('text', 'label'),
        ),
      ),
      $(
        go.Panel,
        'Auto',
        $(go.Shape, 'RoundedRectangle', {
          fill: '#FFFFFF',
          stroke: '#6A7184',
          parameter1: 10,
          minSize: new go.Size(NaN, NODE_HEIGHT),
          // maxSize: new go.Size(NODE_WIDTH, NaN)
        }),

        // $(go.Shape, 'RoundedRectangle', {
        //   fill: '#FFFFFF',
        //   stroke: '#6A7184',
        //   parameter1: 10
        // }),
        $(go.Placeholder, {
          stretch: go.GraphObject.Fill,
          padding: new go.Margin(-5, -5, 8, -5),
        }),
      ),
    ),
  );

  // Bom Group
  myDiagram.groupTemplateMap.add(
    'Bom',
    $(go.Group, 'Vertical', {
      locationSpot: go.Spot.Top,
      layout: $(go.GridLayout, { isOngoing: false, cellSize: new go.Size(NaN, NODE_HEIGHT), wrappingColumn: 1 }),
      // layout: $(go.LayeredDigraphLayout, { isOngoing: false }),
      minSize: new go.Size(NODE_WIDTH, NaN),
      // maxSize: new go.Size(NODE_WIDTH, NaN),
      selectionAdorned: false,
      layerName: 'Background',
      selectable: false,
    }).add(
      $(
        go.TextBlock,
        {
          margin: 4,
          font: "700 16pt 'Roboto', 'Noto Sans KR'",
          stroke: '#738099',
        },
        new go.Binding('text', 'label'),
      ),
      $(
        go.Panel,
        'Auto',
        $(go.Shape, 'RoundedRectangle', {
          fill: '#E2E7FA',
          stroke: '#E2E7FA',
          parameter1: 10,
          opacity: 0,
          minSize: new go.Size(NODE_WIDTH, NaN),
          // maxSize: new go.Size(NODE_WIDTH, NaN)
        }),
        $(go.Placeholder, { padding: -5 }),
      ),
    ),
  );

  // Sequence Group
  myDiagram.groupTemplateMap.add(
    'Sequence',
    $(go.Group, 'Vertical', {
      locationSpot: go.Spot.Top,
      layout: $(go.GridLayout, {
        isOngoing: false,
        cellSize: new go.Size(NODE_WIDTH, NaN),
        wrappingColumn: 1,
      }),
      // layout: $(go.LayeredDigraphLayout, { isOngoing: false }),
      minSize: new go.Size(NODE_WIDTH, NaN),
      // maxSize: new go.Size(NODE_WIDTH, NaN),
      selectionAdorned: false,
      layerName: 'Background',
      selectable: false,
    }).add(
      $(
        go.TextBlock,
        {
          margin: 4,
          font: "700 16pt 'Roboto', 'Noto Sans KR'",
          stroke: '#738099',
        },
        new go.Binding('text', 'label'),
      ),
      $(
        go.Panel,
        'Auto',
        $(go.Shape, 'RoundedRectangle', {
          fill: '#0030ec',
          stroke: '#738099',
          parameter1: 10,
          opacity: 0,
          minSize: new go.Size(NODE_WIDTH, NaN),
          // maxSize: new go.Size(NODE_WIDTH, NaN)
        }),
        $(go.Placeholder, { padding: -5 }),
      ),
    ),
  );

  /**
   * LinkTemplate 선언부
   */
  myDiagram.linkTemplate = $(
    go.Link,
    {
      layerName: '',
      // routing: go.Link.Orthogonal
    },
    $(
      go.Shape,
      {
        isPanelMain: true,
        strokeWidth: 16,
        stroke: '#4568E0',
        opacity: 0.3,
      },
      new go.Binding('opacity', 'isHighlighted', (h) => (h ? 0.3 : 0)).ofObject(),
    ),
    $(
      go.Shape,
      {
        isPanelMain: true,
      },
      new go.Binding('stroke', 'bomType', (h) => LINK_COLOR[h].STROKE),
      // new go.Binding('strokeWidth', 'bomType', h => LINK_COLOR[h].STROKE_WIDTH),
      new go.Binding('strokeWidth', 'isHighlighted', (h) => (h ? 3 : 1)).ofObject(),
    ),
    $(
      go.Shape,
      {
        fromArrow: 'Circle',
      },
      new go.Binding('stroke', 'bomType', (h) => LINK_COLOR[h].STROKE),
      new go.Binding('fill', 'bomType', (h) => LINK_COLOR[h].FILL),
    ),
    $(
      go.Shape,
      { toArrow: 'Standard', fill: '#6A7184', stroke: '#6A7184' },
      new go.Binding('stroke', 'bomType', (h) => LINK_COLOR[h].STROKE),
      new go.Binding('fill', 'bomType', (h) => LINK_COLOR[h].FILL),
    ),
    $(
      go.TextBlock,
      {
        segmentOffset: new go.Point(0, -10),
        segmentOrientation: go.Link.OrientUpright,
      },
      new go.Binding('text', 'label'),
    ),

    {
      selectionAdornmentTemplate: $(
        go.Adornment,
        { layerName: 'Adornment' },
        $(
          go.Shape,
          {
            isPanelMain: true,
          },
          new go.Binding('stroke', '', () => SELECTED_COLOR.LINK_STROKE),
          new go.Binding('strokeWidth', '', () => SELECTED_COLOR.LINK_STROKE_WIDTH),
          new go.Binding('fill', '', () => SELECTED_COLOR.LINK_FILL),
        ),
        $(
          go.Shape,
          {
            fromArrow: 'Circle',
          },
          new go.Binding('stroke', '', () => SELECTED_COLOR.LINK_STROKE),
          new go.Binding('strokeWidth', '', () => SELECTED_COLOR.LINK_STROKE_WIDTH),
          new go.Binding('fill', '', () => SELECTED_COLOR.LINK_FILL),
        ),
        $(
          go.Shape,
          {
            toArrow: 'Standard',
          },
          new go.Binding('stroke', '', () => SELECTED_COLOR.LINK_STROKE),
          new go.Binding('strokeWidth', '', () => SELECTED_COLOR.LINK_STROKE_WIDTH),
          new go.Binding('fill', '', () => SELECTED_COLOR.LINK_FILL),
        ),
      ), // end Adornment
    },
  );

  /**
   * BomMap 오버뷰를 생성
   */
  /**
   * BomMap 오버뷰를 생성
   */
  function initOverview() {
    const myOverview = new go.Overview(overviewID, {
      observed: myDiagram,
      contentAlignment: go.Spot.Center,
      box: $(go.Part, 'Auto', $(go.Shape, 'Rectangle', { fill: '#4568E017', stroke: '#4568E0', strokeWidth: 10 })),
    });
    myOverview.autoScrollRegion = 0;
    return myOverview;
  }

  /**
   * Node 선택 시, Node의 ICON (go.Shape)를 변경하는 함수
   */
  function onNodeSelection(node: any) {
    const icon = node.findObject('ICON');
    if (icon !== null) {
      const correction = SELECTED_COLOR.NODE_STROKE_WIDTH - NODE_ICON_COLOR[node.data.iconColor].STROKE_WIDTH;
      if (node.isSelected) {
        icon.stroke = SELECTED_COLOR.NODE_STROKE;
        icon.strokeWidth = SELECTED_COLOR.NODE_STROKE_WIDTH;
        icon.fill = SELECTED_COLOR.NODE_FILL || icon.fill;
        icon.height = icon.height - correction;
        icon.width = icon.width - correction;
      } else {
        icon.stroke = NODE_ICON_COLOR[node.data.iconColor].STROKE;
        icon.strokeWidth = NODE_ICON_COLOR[node.data.iconColor].STROKE_WIDTH;
        icon.fill = NODE_ICON_COLOR[node.data.iconColor].FILL;
        icon.height = icon.height + correction;
        icon.width = icon.width + correction;
      }
    }
  }

  // /**
  //  * @Deprecated
  //  * 회전 방향에 따라 다이어그램의 포지션과 스케일을 조정하는 함수
  //  */
  // function setDiagramScale(factor: number, align: 'Horizontal' | 'Vertical' | 'All' | 'None', whole = false) {
  //   myDiagram.scale = factor;
  //
  //   if (align === 'Horizontal') {
  //     myDiagram.position = new go.Point(
  //       -(myDiagram.viewportBounds.width - myDiagram.documentBounds.width) / 2,
  //       -Math.min(myDiagram.documentBounds.width, myDiagram.documentBounds.height) / 10,
  //     );
  //   } else if (align === 'Vertical') {
  //     myDiagram.position = new go.Point(
  //       -Math.min(myDiagram.documentBounds.width, myDiagram.documentBounds.height) / 10,
  //       -(myDiagram.viewportBounds.height - myDiagram.documentBounds.height) / 2,
  //     );
  //   } else if (align === 'All') {
  //     myDiagram.position = new go.Point(
  //       -(myDiagram.viewportBounds.width - myDiagram.documentBounds.width) / 2,
  //       -(myDiagram.viewportBounds.height - myDiagram.documentBounds.height) / 2,
  //     );
  //   } else {
  //     myDiagram.position = new go.Point(-ALIGN_SPACING.INIT_SPACE, -ALIGN_SPACING.INIT_SPACE);
  //   }
  // }

  /**
   * 그룹내 첫번째 노드를 찾고, 첫번째 노드 데이터에 isFirstNode = true를 부여하는 함수
   */
  const findFirstNodeInGroups = () => {
    // 다이어그램의 모든 그룹을 순회
    myDiagram.nodes.each((node) => {
      if (node instanceof go.Group) {
        // 현재 그룹의 모든 멤버(노드) 순회
        let firstNode: any = null;
        node.memberParts.each((member) => {
          if (member instanceof go.Node && !firstNode) {
            member.data.isFirstNode = true;
            firstNode = member;
          }
        });
      }
    });
    myDiagram.updateAllTargetBindings('isFirstNode');
  };

  /**
   * 다이어그램이 초기화되었을 때 실행하는 함수
   */
  const initFunc = () => {
    // GoJS 다이어그램을 초기화할 때 CommandHandler의 메소드를 오버라이드합니다.
    myDiagram.commandHandler.canCopySelection = () => false;
    myDiagram.commandHandler.canCutSelection = () => false;
    myDiagram.commandHandler.canDeleteSelection = () => false;
    myDiagram.commandHandler.canPasteSelection = () => false;

    // Ctrl+드래그로 복사하는 기능 비활성화
    myDiagram.toolManager.draggingTool.isCopyEnabled = false;
    myDiagram.toolManager.draggingTool.copiesEffectiveCollection = false;

    // Ctrl 키를 눌렀을 때도 일반 드래그처럼 동작하도록 오버라이드
    const originalDoActivate = myDiagram.toolManager.draggingTool.doActivate;
    myDiagram.toolManager.draggingTool.doActivate = function doActivate() {
      const e = this.diagram.lastInput;
      // Ctrl 키가 눌렸으면 무시
      if (e.control || e.meta) {
        // 현재 드래그하려는 요소만 선택
        const part = this.diagram.findPartAt(e.documentPoint, false);
        if (part) {
          this.diagram.clearSelection();
          part.isSelected = true;
        }
      }
      originalDoActivate.call(this);
    };

    findFirstNodeInGroups();
    // setDiagramScale(0.6, 'None');
  };

  // myDiagram.toolManager.doMouseWheel = function () {
  //   const step = 100;
  //   let scrollPosX = myDiagram.position.x;
  //   let scrollPosY = myDiagram.position.y;
  //
  //   const e = this.diagram.lastInput;
  //   if (e.control) {
  //     if (e.delta > 0) {
  //       scrollPosY -= step;
  //     } else {
  //       scrollPosY += step;
  //     }
  //     myDiagram.position = new go.Point(scrollPosX, scrollPosY);
  //   } else if (e.shift) {
  //     if (e.delta > 0) {
  //       scrollPosX -= step;
  //     } else {
  //       scrollPosX += step;
  //     }
  //     myDiagram.position = new go.Point(scrollPosX, scrollPosY);
  //   } else {
  //     const mousePt = e.viewPoint;
  //     // zoomPoint를 마우스 포인터의 위치로 설정합니다.
  //     this.diagram.zoomPoint = mousePt;
  //     if (e.delta > 0) {
  //       myDiagram.commandHandler.increaseZoom();
  //     } else {
  //       myDiagram.commandHandler.decreaseZoom();
  //     }
  //     // go.ToolManager.prototype.doMouseWheel.call(this);
  //   }
  // };

  /**
   * Diagram의 Initialize이후, 함수 실행
   */
  myDiagram.addDiagramListener('InitialLayoutCompleted', initFunc);

  onBeforeUnmount(() => {
    myDiagram.removeDiagramListener('InitialLayoutCompleted', initFunc);
  });

  /**
   * Diagram 객체를 반환하는 함수, 해당 객체는 Vue의 ref객체에 담으면 오류가 발생하므로, 컴포넌트 단위에서 getDiagram으로 Diagram 객체를 반환받아 사용한다.
   */
  const getDiagram = () => myDiagram;

  return { setNodeEvents, setConfigs, getDiagram, initOverview };
};
