MAX_VERTEX = 6
INFINITE = 1000

G = [
    [   0,   50,   10, 1000,   45, 1000],
    [1000,    0,   15, 1000,   10, 1000],
    [  20, 1000,    0,   15, 1000, 1000],
    [1000,   20, 1000,    0,   35, 1000],
    [1000, 1000,   30, 1000,    0, 1000],
    [1000, 1000, 1000,    3, 1000,    0],
]

V = MAX_VERTEX
check = [0] * V      # 최단 경로가 확정되었는지
parent = [-1] * V    # 최단 경로 트리에서의 부모
distance = [0] * V


def name2int(c):
    return ord(c) - ord('0')


def int2name(i):
    return chr(ord('A') + i)


def dijkstra(a, s):
    global check, parent, distance
    check = [0] * V
    parent = [-1] * V

    # 초기화: 출발점 s에서 바로 가는 거리로 채운다
    for x in range(V):
        distance[x] = a[s][x]
        if x != s:
            parent[x] = s

    check[s] = 1
    checked = 1

    while checked < V:
        # 확정 안 된 정점 중 distance가 최소인 x를 고른다
        x = 0
        while check[x]:
            x += 1
        for i in range(x, V):
            if check[i] == 0 and distance[i] < distance[x]:
                x = i

        check[x] = 1
        checked += 1

        # x를 거쳐 가는 길로 나머지 정점의 distance를 갱신
        for y in range(V):
            if x == y or a[x][y] >= INFINITE or check[y]:
                continue
            d = distance[x] + a[x][y]
            if d < distance[y]:
                distance[y] = d
                parent[y] = x


def print_adjmatrix(a):
    print("\n     " + "  ".join(f"{int2name(i)}" for i in range(V)))
    for i in range(V):
        row = " ".join(f"{a[i][j]:4d}" for j in range(V))
        print(f"  {int2name(i)}  {row}")


def print_tree(tree):
    print("son     " + "  ".join(int2name(i) for i in range(V)))
    print("-" * 40)
    parents = "  ".join("^" if tree[i] == -1 else int2name(tree[i]) for i in range(V))
    print(f"parent  {parents}")


def print_cost(d):
    print("vertex  " + "  ".join(int2name(i) for i in range(V)))
    print("-" * 40)
    print("cost    " + "  ".join(f"{d[i]}" for i in range(V)))


if __name__ == "__main__":
    print("Adjacency Matrix representation for weighted graph")
    print_adjmatrix(G)

    dijkstra(G, 0)

    print("\nShortest Path Tree from A")
    print_tree(parent)

    print("\nCost from A in shortest path")
    print_cost(distance)
