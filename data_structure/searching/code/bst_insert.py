class TreeNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def insert_node(root, key):
    p = None      # 부모 노드
    t = root      # 현재 노드
    while t is not None:          # 탐색을 먼저 수행
        if key == t.key:
            return root           # 이미 존재 -> 삽입하지 않음
        p = t
        if key < t.key:
            t = t.left
        else:
            t = t.right

    n = TreeNode(key)             # key가 트리에 없으므로 삽입 가능
    if p is not None:             # 부모 노드와 링크 연결
        if key < p.key:
            p.left = n
        else:
            p.right = n
        return root
    else:
        return n                  # 트리가 비어 있었음 -> 새 노드가 루트


def inorder(node, acc):
    if node is not None:
        inorder(node.left, acc)
        acc.append(node.key)
        inorder(node.right, acc)


if __name__ == "__main__":
    root = None
    for k in (18, 7, 26, 3, 12, 31, 27):
        root = insert_node(root, k)

    print("9 삽입 전 중위순회:", end=" ")
    acc = []
    inorder(root, acc)
    print(acc)

    root = insert_node(root, 9)

    print("9 삽입 후 중위순회:", end=" ")
    acc = []
    inorder(root, acc)
    print(acc)
