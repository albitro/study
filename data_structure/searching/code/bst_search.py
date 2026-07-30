class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def search_recursive(node, key):
    if node is None:
        return None
    if key == node.key:
        return node
    elif key < node.key:
        return search_recursive(node.left, key)
    else:
        return search_recursive(node.right, key)


def search_iterative(node, key):
    while node is not None:
        if key == node.key:
            return node
        elif key < node.key:
            node = node.left
        else:
            node = node.right
    return None  # 탐색에 실패했을 경우 None 반환


if __name__ == "__main__":
    root = TreeNode(18)
    root.left = TreeNode(7)
    root.right = TreeNode(26)
    root.left.left = TreeNode(3)
    root.left.right = TreeNode(12)
    root.right.right = TreeNode(31)
    root.right.right.left = TreeNode(27)

    for target in (12, 9):
        r1 = search_recursive(root, target)
        r2 = search_iterative(root, target)
        found1 = r1.key if r1 else None
        found2 = r2.key if r2 else None
        print(f"{target} 탐색 -> 순환: {found1}, 반복: {found2}")
