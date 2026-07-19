from collections import deque


class TNode:                                  # 이진트리를 위한 노드 클래스
    def __init__(self, data, left, right):    # 생성자
        self.data = data                      # 노드의 데이터
        self.left = left                      # 왼쪽 자식을 위한 링크
        self.right = right                    # 오른쪽 자식을 위한 링크


def inorder(n):
    if n is not None:
        inorder(n.left)                       # 왼쪽 서브트리 처리
        print(n.data, end=' ')                # 루트노드 처리
        inorder(n.right)                      # 오른쪽 서브트리 처리


def preorder(n):
    if n is not None:
        print(n.data, end=' ')                # 루트노드 처리
        preorder(n.left)                      # 왼쪽 서브트리 처리
        preorder(n.right)                     # 오른쪽 서브트리 처리


def postorder(n):
    if n is not None:
        postorder(n.left)                     # 왼쪽 서브트리 처리
        postorder(n.right)                    # 오른쪽 서브트리 처리
        print(n.data, end=' ')                # 루트노드 처리


def levelorder(root):
    queue = deque()
    queue.append(root)                        # 최초의 큐에는 루트노드만 있음
    while len(queue) > 0:
        n = queue.popleft()                   # 큐에서 맨 앞의 노드 n을 꺼냄
        if n is not None:
            print(n.data, end=' ')            # 노드의 정보 출력
            queue.append(n.left)              # n의 왼쪽 자식 노드를 큐에 삽입
            queue.append(n.right)             # n의 오른쪽 자식 노드를 큐에 삽입


def count_node(n):
    if n is None:
        return 0                              # 공백트리이면 0
    else:                                     # 좌우 서브트리의 노드수의 합 + 1
        return 1 + count_node(n.left) + count_node(n.right)


def calc_height(n):
    if n is None:
        return 0                              # 공백트리이면 0
    hLeft = calc_height(n.left)               # 왼쪽 트리의 높이
    hRight = calc_height(n.right)             # 오른쪽 트리의 높이
    if hLeft > hRight:                        # 더 높은 높이에 1을 더해 반환
        return hLeft + 1
    else:
        return hRight + 1


if __name__ == "__main__":
    #            A
    #          /   \
    #         B     C
    #        / \   / \
    #       D   E F   G
    #      / \
    #     H   I
    H = TNode('H', None, None)
    I = TNode('I', None, None)
    D = TNode('D', H, I)
    E = TNode('E', None, None)
    F = TNode('F', None, None)
    G = TNode('G', None, None)
    B = TNode('B', D, E)
    C = TNode('C', F, G)
    A = TNode('A', B, C)

    print("중위탐색: ", end='')
    inorder(A)
    print()

    print("전위탐색: ", end='')
    preorder(A)
    print()

    print("후위탐색: ", end='')
    postorder(A)
    print()

    print("레벨탐색: ", end='')
    levelorder(A)
    print()

    print(f"노드 수: {count_node(A)}")
    print(f"트리 높이: {calc_height(A)}")
