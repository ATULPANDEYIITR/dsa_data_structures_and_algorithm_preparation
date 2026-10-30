'use strict';

/**
 * Manual binary-tree construction and event-driven structural analysis.
 *
 * Conventions:
 * - Height: number of edges on the longest downward path.
 * - Depth: number of edges from the root.
 * - Level: depth + 1.
 * - A leaf has height 0.
 */

const { EventEmitter } = require('node:events');

class TreeError extends Error {
    constructor(message) {
        super(message);
        this.name = 'TreeError';
    }
}

class TreeNode {
    constructor(id, value) {
        if (typeof id !== 'string' || id.trim().length === 0) {
            throw new TreeError('Node ID must be a non-empty string.');
        }
        if (typeof value !== 'string' || value.trim().length === 0) {
            throw new TreeError('Node value must be a non-empty string.');
        }

        this.id = id;
        this.value = value;
        this.left = null;
        this.right = null;
        this.parent = null;
    }

    get isLeaf() {
        return this.left === null && this.right === null;
    }
}

class BinaryTree extends EventEmitter {
    constructor(root) {
        super();

        if (!(root instanceof TreeNode)) {
            throw new TreeError('A tree requires a valid root node.');
        }
        if (root.parent !== null) {
            throw new TreeError('The root cannot have a parent.');
        }

        this.root = root;
        this.knownNodes = new Set([root]);
        this.nodesById = new Map([[root.id, root]]);

        this._collectSubtree(root);
    }

    createNode(id, value) {
        if (this.nodesById.has(id)) {
            throw new TreeError(`Node ID ${id} is already registered.`);
        }

        const node = new TreeNode(id, value);
        this.knownNodes.add(node);
        this.nodesById.set(id, node);
        return node;
    }

    _collectSubtree(start) {
        const result = [];
        const visited = new Set();
        const stack = [{ node: start, expectedParent: null }];

        while (stack.length > 0) {
            const { node, expectedParent } = stack.pop();

            if (visited.has(node)) {
                throw new TreeError(
                    `Cycle or shared child detected at node ${node.id}.`
                );
            }

            if (node.parent !== expectedParent) {
                throw new TreeError(
                    `Invalid parent reference at node ${node.id}.`
                );
            }

            visited.add(node);
            result.push(node);

            if (node.right !== null) {
                stack.push({ node: node.right, expectedParent: node });
            }
            if (node.left !== null) {
                stack.push({ node: node.left, expectedParent: node });
            }
        }

        return result;
    }

    _reachableNodes() {
        return new Set(this._collectSubtree(this.root));
    }

    attach(parent, child, side) {
        const reachable = this._reachableNodes();

        if (!reachable.has(parent)) {
            throw new TreeError('Parent must belong to the current tree.');
        }
        if (!(child instanceof TreeNode) || !this.knownNodes.has(child)) {
            throw new TreeError('Child must be a node created by this tree.');
        }
        if (reachable.has(child)) {
            throw new TreeError('Child already belongs to the current tree.');
        }
        if (child.parent !== null) {
            throw new TreeError('Incoming subtree root must be detached.');
        }
        if (side !== 'left' && side !== 'right') {
            throw new TreeError("Side must be 'left' or 'right'.");
        }

        const incoming = this._collectSubtree(child);

        if (incoming.some(node => reachable.has(node))) {
            throw new TreeError('Incoming subtree overlaps the current tree.');
        }

        if (parent[side] !== null) {
            throw new TreeError(`${parent.id} already has a ${side} child.`);
        }

        parent[side] = child;
        child.parent = parent;

        this.emit('nodeAttached', {
            parentId: parent.id,
            childId: child.id,
            side
        });
    }

    depth(node) {
        if (!this._reachableNodes().has(node)) {
            throw new TreeError('Node does not belong to this tree.');
        }

        let current = node;
        let depth = 0;
        const visited = new Set();

        while (current.parent !== null) {
            if (visited.has(current)) {
                throw new TreeError('Cycle detected in parent references.');
            }

            visited.add(current);
            current = current.parent;
            depth += 1;
        }

        if (current !== this.root) {
            throw new TreeError('Node is disconnected from the root.');
        }

        return depth;
    }

    level(node) {
        return this.depth(node) + 1;
    }

    height(node = this.root) {
        if (!this._reachableNodes().has(node)) {
            throw new TreeError('Node does not belong to this tree.');
        }

        const heights = new Map();
        const stack = [{ node, expanded: false }];

        // Iterative postorder computes child heights before parent heights.
        while (stack.length > 0) {
            const entry = stack.pop();
            const current = entry.node;

            if (!entry.expanded) {
                stack.push({ node: current, expanded: true });

                if (current.right !== null) {
                    stack.push({ node: current.right, expanded: false });
                }
                if (current.left !== null) {
                    stack.push({ node: current.left, expanded: false });
                }
            } else {
                const leftHeight = current.left === null
                    ? -1
                    : heights.get(current.left);

                const rightHeight = current.right === null
                    ? -1
                    : heights.get(current.right);

                heights.set(current, 1 + Math.max(leftHeight, rightHeight));
            }
        }

        return heights.get(node);
    }

    subtreeSize(node) {
        if (!this._reachableNodes().has(node)) {
            throw new TreeError('Node does not belong to this tree.');
        }
        return this._collectSubtree(node).length;
    }

    levels() {
        const result = [];
        let queue = [this.root];

        while (queue.length > 0) {
            result.push(queue.map(node => node.id));

            const nextLevel = [];
            for (const node of queue) {
                if (node.left !== null) nextLevel.push(node.left);
                if (node.right !== null) nextLevel.push(node.right);
            }
            queue = nextLevel;
        }

        return result;
    }

    *preorder() {
        const stack = [this.root];

        while (stack.length > 0) {
            const node = stack.pop();
            yield node.id;

            if (node.right !== null) stack.push(node.right);
            if (node.left !== null) stack.push(node.left);
        }
    }

    *inorder() {
        const stack = [];
        let current = this.root;

        while (current !== null || stack.length > 0) {
            while (current !== null) {
                stack.push(current);
                current = current.left;
            }

            current = stack.pop();
            yield current.id;
            current = current.right;
        }
    }

    *postorder() {
        const stack = [{ node: this.root, expanded: false }];

        while (stack.length > 0) {
            const entry = stack.pop();
            const node = entry.node;

            if (entry.expanded) {
                yield node.id;
                continue;
            }

            stack.push({ node, expanded: true });
            if (node.right !== null) {
                stack.push({ node: node.right, expanded: false });
            }
            if (node.left !== null) {
                stack.push({ node: node.left, expanded: false });
            }
        }
    }

    analyze() {
        const nodes = this._collectSubtree(this.root);
        const heightByNode = new Map();
        const depthByNode = new Map([[this.root, 0]]);

        const heightStack = [{ node: this.root, expanded: false }];

        while (heightStack.length > 0) {
            const { node, expanded } = heightStack.pop();

            if (!expanded) {
                heightStack.push({ node, expanded: true });
                if (node.right !== null) {
                    heightStack.push({ node: node.right, expanded: false });
                }
                if (node.left !== null) {
                    heightStack.push({ node: node.left, expanded: false });
                }
            } else {
                const leftHeight = node.left === null
                    ? -1
                    : heightByNode.get(node.left);
                const rightHeight = node.right === null
                    ? -1
                    : heightByNode.get(node.right);

                heightByNode.set(node, 1 + Math.max(leftHeight, rightHeight));
            }
        }

        const queue = [this.root];

        for (let index = 0; index < queue.length; index += 1) {
            const parent = queue[index];
            const childDepth = depthByNode.get(parent) + 1;

            for (const child of [parent.left, parent.right]) {
                if (child !== null) {
                    depthByNode.set(child, childDepth);
                    queue.push(child);
                }
            }
        }

        return nodes.map(node => ({
            id: node.id,
            value: node.value,
            parent: node.parent?.id ?? null,
            left: node.left?.id ?? null,
            right: node.right?.id ?? null,
            depth: depthByNode.get(node),
            level: depthByNode.get(node) + 1,
            height: heightByNode.get(node),
            isLeaf: node.isLeaf,
            subtreeSize: this._collectSubtree(node).length
        }));
    }

    validate() {
        const reachable = this._reachableNodes();

        if (reachable.size !== this.knownNodes.size) {
            throw new TreeError(
                'Some registered nodes are not connected to the root.'
            );
        }

        return true;
    }
}

function buildExampleTree() {
    const tree = new BinaryTree(new TreeNode('A', 'Root'));
    const nodes = new Map([['A', tree.root]]);

    for (const [id, value] of [
        ['B', 'Left child of A'],
        ['C', 'Right child of A'],
        ['D', 'Left child of B'],
        ['E', 'Right child of B'],
        ['F', 'Right child of C'],
        ['G', 'Left child of E']
    ]) {
        nodes.set(id, tree.createNode(id, value));
    }

    // Each attachment is explicit. No automatic insertion or balancing occurs.
    tree.attach(nodes.get('A'), nodes.get('B'), 'left');
    tree.attach(nodes.get('A'), nodes.get('C'), 'right');
    tree.attach(nodes.get('B'), nodes.get('D'), 'left');
    tree.attach(nodes.get('B'), nodes.get('E'), 'right');
    tree.attach(nodes.get('C'), nodes.get('F'), 'right');
    tree.attach(nodes.get('E'), nodes.get('G'), 'left');

    return { tree, nodes };
}

function main() {
    const { tree, nodes } = buildExampleTree();

    tree.on('nodeAttached', event => {
        console.log(
            `Attached ${event.childId} as ${event.side} child of ${event.parentId}`
        );
    });

    // The tree is already built. This listener demonstrates event-based observation.
    tree.validate();

    console.log('\nTREE REPORT');
    console.log(JSON.stringify({
        nodeCount: tree.analyze().length,
        height: tree.height(),
        levels: tree.levels(),
        preorder: [...tree.preorder()],
        inorder: [...tree.inorder()],
        postorder: [...tree.postorder()],
        nodes: tree.analyze()
    }, null, 2));

    console.log('\nSELECTED NODE METRICS');
    for (const id of ['A', 'B', 'D', 'G', 'F']) {
        const node = nodes.get(id);
        console.log(
            `${id}: parent=${node.parent?.id ?? 'none'}, ` +
            `depth=${tree.depth(node)}, level=${tree.level(node)}, ` +
            `height=${tree.height(node)}, leaf=${node.isLeaf}`
        );
    }

    console.log('\nSUBTREE ROOTED AT B');
    console.log({
        height: tree.height(nodes.get('B')),
        size: tree.subtreeSize(nodes.get('B'))
    });

    console.log('\nINVALID ATTACHMENT TEST');

    try {
        tree.attach(nodes.get('G'), nodes.get('A'), 'left');
    } catch (error) {
        if (!(error instanceof TreeError)) throw error;
        console.log(`Rejected: ${error.message}`);
    }

    try {
        tree.attach(
            nodes.get('A'),
            tree.createNode('X', 'Invalid duplicate slot'),
            'left'
        );
    } catch (error) {
        if (!(error instanceof TreeError)) throw error;
        console.log(`Rejected: ${error.message}`);
    }

    if (tree.height() !== 3 || tree.depth(nodes.get('G')) !== 3) {
        throw new Error('Tree metric assertion failed.');
    }

    if (tree.subtreeSize(nodes.get('B')) !== 4) {
        throw new Error('Subtree-size assertion failed.');
    }

    console.log('\nAll structural checks passed.');
}

if (require.main === module) {
    main();
}

module.exports = { TreeNode, BinaryTree, TreeError, buildExampleTree };
