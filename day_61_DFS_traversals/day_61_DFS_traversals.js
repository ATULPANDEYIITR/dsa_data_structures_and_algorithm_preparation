"use strict";

/*
 * Binary-tree DFS traversal laboratory.
 *
 * The three traversal orders are:
 *   Preorder:  Root, Left, Right
 *   Inorder:   Left, Root, Right
 *   Postorder: Left, Right, Root
 *
 * This implementation uses iterative algorithms where an explicit stack
 * avoids JavaScript call-stack limits on highly skewed trees.
 */

class TreeNode {
  constructor(value, left = null, right = null) {
    this.value = value;
    this.left = left;
    this.right = right;
  }
}

class TraversalError extends Error {
  constructor(message) {
    super(message);
    this.name = "TraversalError";
  }
}

function validateTree(root) {
  if (root === null) return;

  const active = new Set();
  const visited = new Set();

  function check(node) {
    if (node === null) return;

    if (active.has(node)) {
      throw new TraversalError("Cycle detected in tree structure");
    }
    if (visited.has(node)) {
      throw new TraversalError(
        "A node has multiple parents; input is not a tree"
      );
    }

    active.add(node);
    check(node.left);
    check(node.right);
    active.delete(node);
    visited.add(node);
  }

  check(root);
}

function preorderRecursive(root) {
  validateTree(root);
  const result = [];

  function visit(node) {
    if (node === null) return;
    result.push(node.value);
    visit(node.left);
    visit(node.right);
  }

  visit(root);
  return result;
}

function inorderRecursive(root) {
  validateTree(root);
  const result = [];

  function visit(node) {
    if (node === null) return;
    visit(node.left);
    result.push(node.value);
    visit(node.right);
  }

  visit(root);
  return result;
}

function postorderRecursive(root) {
  validateTree(root);
  const result = [];

  function visit(node) {
    if (node === null) return;
    visit(node.left);
    visit(node.right);
    result.push(node.value);
  }

  visit(root);
  return result;
}

function preorderIterative(root) {
  validateTree(root);
  if (root === null) return [];

  const result = [];
  const stack = [root];

  while (stack.length > 0) {
    const node = stack.pop();
    result.push(node.value);

    if (node.right !== null) stack.push(node.right);
    if (node.left !== null) stack.push(node.left);
  }

  return result;
}

function inorderIterative(root) {
  validateTree(root);
  const result = [];
  const stack = [];
  let current = root;

  while (current !== null || stack.length > 0) {
    while (current !== null) {
      stack.push(current);
      current = current.left;
    }

    current = stack.pop();
    result.push(current.value);
    current = current.right;
  }

  return result;
}

function postorderIterative(root) {
  validateTree(root);
  if (root === null) return [];

  const first = [root];
  const second = [];

  while (first.length > 0) {
    const node = first.pop();
    second.push(node);

    if (node.left !== null) first.push(node.left);
    if (node.right !== null) first.push(node.right);
  }

  const result = [];
  while (second.length > 0) {
    result.push(second.pop().value);
  }
  return result;
}

function postorderIterativeOneStack(root) {
  validateTree(root);

  const result = [];
  const stack = [];
  let current = root;
  let previous = null;

  while (current !== null || stack.length > 0) {
    if (current !== null) {
      stack.push(current);
      current = current.left;
      continue;
    }

    const node = stack[stack.length - 1];

    if (node.right !== null && previous !== node.right) {
      current = node.right;
    } else {
      result.push(node.value);
      previous = stack.pop();
    }
  }

  return result;
}

function buildSampleTree() {
  return new TreeNode(
    1,
    new TreeNode(2, new TreeNode(4), new TreeNode(5)),
    new TreeNode(3, new TreeNode(6), new TreeNode(7))
  );
}

async function runTraversalDemo() {
  const tree = buildSampleTree();

  const expected = {
    preorder: [1, 2, 4, 5, 3, 6, 7],
    inorder: [4, 2, 5, 1, 6, 3, 7],
    postorder: [4, 5, 2, 6, 7, 3, 1],
  };

  const checks = {
    preorderRecursive: preorderRecursive(tree),
    preorderIterative: preorderIterative(tree),
    inorderRecursive: inorderRecursive(tree),
    inorderIterative: inorderIterative(tree),
    postorderRecursive: postorderRecursive(tree),
    postorderIterative: postorderIterative(tree),
    postorderIterativeOneStack: postorderIterativeOneStack(tree),
  };

  const expectedByName = {
    preorderRecursive: expected.preorder,
    preorderIterative: expected.preorder,
    inorderRecursive: expected.inorder,
    inorderIterative: expected.inorder,
    postorderRecursive: expected.postorder,
    postorderIterative: expected.postorder,
    postorderIterativeOneStack: expected.postorder,
  };

  for (const [name, actual] of Object.entries(checks)) {
    if (JSON.stringify(actual) !== JSON.stringify(expectedByName[name])) {
      throw new Error(`Traversal mismatch for ${name}`);
    }
    console.log(`${name.padEnd(34)} ${JSON.stringify(actual)}`);
  }

  console.assert(JSON.stringify(preorderIterative(null)) === "[]");
  console.assert(JSON.stringify(inorderIterative(null)) === "[]");
  console.assert(JSON.stringify(postorderIterative(null)) === "[]");

  const single = new TreeNode(42);
  console.assert(JSON.stringify(inorderIterative(single)) === "[42]");

  // Iterative traversals handle a 5,000-node skewed tree without recursive
  // call-stack growth.
  const deepRoot = new TreeNode(0);
  let current = deepRoot;

  for (let i = 1; i <= 5000; i++) {
    current.right = new TreeNode(i);
    current = current.right;
  }

  const preorder = preorderIterative(deepRoot);
  const inorder = inorderIterative(deepRoot);
  const postorder = postorderIterative(deepRoot);

  console.assert(preorder.length === 5001);
  console.assert(inorder[0] === 0 && inorder[5000] === 5000);
  console.assert(postorder[0] === 5000 && postorder[5000] === 0);

  const cyclic = new TreeNode("A");
  cyclic.left = cyclic;

  try {
    preorderIterative(cyclic);
    throw new Error("Cycle should have been rejected");
  } catch (error) {
    if (!(error instanceof TraversalError)) throw error;
  }

  // Demonstrate asynchronous event-style consumption of traversal output.
  await new Promise((resolve) => {
    setImmediate(() => {
      console.log("\nAsynchronous traversal event:", preorderIterative(tree));
      resolve();
    });
  });

  console.log("All traversal assertions passed.");
}

runTraversalDemo().catch((error) => {
  console.error("Traversal failure:", error.message);
  process.exitCode = 1;
});
