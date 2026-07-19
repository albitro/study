N = 10

# 인접 행렬: matrix[i][j] == 1 이면 간선 (i, j) 존재
matrix = [
    [0, 1, 1, 0, 1, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
]

graph = [[] for _ in range(N)]   # 인접 리스트
visited = [False] * N


def create():
    for i in range(N):
        for j in range(N):
            if matrix[i][j] != 0:
                graph[i].append(j)


def dfs(v):
    visited[v] = True                # 1. 방문 표시
    print(f"{v:5d}", end="")
    for w in graph[v]:               # 2. 인접 리스트 탐색
        if not visited[w]:
            dfs(w)


if __name__ == "__main__":
    create()

    print(" ** Print the graph with linked list.")
    for i in range(N):
        line = " ".join(str(v) for v in graph[i])
        print(f" * {i}th node =  {line}")

    print("\n * DFS Traversal is =")
    dfs(0)
    print("\n end of  DFS Traversal")
