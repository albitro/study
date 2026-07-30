TWO_NODE = 2
THREE_NODE = 3


class Tree23Node:
    def __init__(self, key1, key2=None, node_type=TWO_NODE):
        self.key1 = key1
        self.key2 = key2
        self.type = node_type
        self.left = None
        self.middle = None
        self.right = None


def tree23_search(root, key):
    if root is None:              # 트리가 비어 있으면
        return False
    elif key == root.key1:        # 루트의 키 == 탐색 키
        return True
    elif root.type == TWO_NODE:                 # 2-노드
        if key < root.key1:
            return tree23_search(root.left, key)
        else:
            return tree23_search(root.right, key)
    else:                                       # 3-노드
        if key == root.key2:
            return True
        if key < root.key1:
            return tree23_search(root.left, key)
        elif key > root.key2:
            return tree23_search(root.right, key)
        else:
            return tree23_search(root.middle, key)


if __name__ == "__main__":
    # 강의 예시 트리(p.51) 구성
    root = Tree23Node(50)
    root.left = Tree23Node(10, 35, THREE_NODE)
    root.right = Tree23Node(70)
    root.left.left = Tree23Node(5)
    root.left.middle = Tree23Node(20, 30, THREE_NODE)
    root.left.right = Tree23Node(40)
    root.right.left = Tree23Node(60)
    root.right.right = Tree23Node(90)

    for target in (30, 40, 55):
        print(f"{target} 탐색 -> {tree23_search(root, target)}")
