// @ts-nocheck — GoJS 3.x type incompatibilities
import * as go from 'gojs';
import { inject } from 'vue';
import { IBomMapIntefaceQuery } from '../BomMapInterface';
import { ALIGN_SPACING } from '../common/BomMapConstants';

export class CustomTreeLayout extends go.TreeLayout {
  public startBufferKey = null;
  public demandNodeKey = null;

  public data = inject('useBomMapInterface') as IBomMapIntefaceQuery;

  /* eslint-disable no-useless-constructor */
  constructor() {
    super();
  }
  /* eslint-enable no-useless-constructor */

  alignByGroup(node: go.Node, depth = 0) {
    const fromLinks = node.findLinksInto().filter((nextLink) => nextLink.fromNode!.data.key !== node.data.key);

    fromLinks.each((link) => {
      const nextGroup = link.fromNode!.containingGroup!;
      const groupData: { key: string; y: number }[] = [];

      if (nextGroup.data.key !== this.data.startBufferKey.value) {
        let firstNodeY = 0;
        let nodeIdx = 0;
        nextGroup.memberParts.each((nextNode) => {
          groupData.push({ key: nextNode.data.key, y: nextNode.position.y });
        });

        groupData.sort((a, b) => {
          if (a.y > b.y) return 1;
          else if (a.y === b.y) return 0;
          else if (a.y < b.y) return -1;
          return 0;
        });

        groupData.forEach((data) => {
          const nextNode = this.diagram?.findNodeForKey(data.key)!;
          if (!nextGroup.data.isAligned) {
            if (nodeIdx === 0) {
              firstNodeY = nextNode.position.y;
            }
            if (
              !nextNode.findNodesInto().first() ||
              (nextNode.findNodesInto().first() &&
                nextNode.findNodesInto().first()!.position.y < nextNode.position.y &&
                nextNode.findNodesInto().first()!.position.y <= firstNodeY + nodeIdx * ALIGN_SPACING.HORIZONTAL)
            ) {
              nextNode.position = new go.Point(nextNode.position.x, firstNodeY + nodeIdx * ALIGN_SPACING.HORIZONTAL);
            }

            nodeIdx += 1;
          }
          if (!nextGroup.data.isAligned && nextNode instanceof go.Node) {
            this.alignByGroup(nextNode, depth + 1);
          }
        });
        nextGroup.data.isAligned = true;
      }
    });
  }

  alignBackwards(node: go.Node, prevDepth: number, isTo = false) {
    node.data.visited = true;
    let fromDepthWeight = 0;
    // const toDepthWeight = 0;
    let nextDepth: number = prevDepth;

    if (!isTo) {
      const fromLinks = node.findLinksInto().filter((nextLink) => nextLink.fromNode!.data.key !== node.data.key);

      fromLinks.each((link) => {
        if (!link.fromNode!.data.visited) {
          nextDepth = Math.max(nextDepth, this.alignBackwards(link.fromNode!, nextDepth + fromDepthWeight));
          fromDepthWeight = 1;
        }
      });
    }

    if (!node.data.isAligned) {
      node.position = new go.Point(node.position.x, prevDepth * ALIGN_SPACING.HORIZONTAL);
    }

    node.data.isAligned = true;
    return nextDepth;
  }

  initAlign() {
    const node = this.diagram?.findNodeForKey(this.data.demandNodeKey.value)!;
    if (node) {
      this.alignBackwards(node!, 0);
      this.alignByGroup(node!);
    }
  }

  protected commitLayout() {
    super.commitLayout();
    this.initAlign();
  }
}
