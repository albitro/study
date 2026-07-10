from collections import deque

N = 10

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

graph = [[] for _ in range(N)]
visited = [False] * N


def create():
    for i in range(N):
        for j in range(N):
            if matrix[i][j] != 0:
                graph[i].append(j)


def bfs(v):
    q = deque()
    print(f"{v:5d}", end="")
    visited[v] = True                # 1. 방문 기록
    q.append(v)
    while q:                         # 2. 방문지가 있는 동안 반복
        v = q.popleft()
        for w in graph[v]:
            if not visited[w]:
                print(f"{w:5d}", end="")
                q.append(w)
                visited[w] = True


if __name__ == "__main__":
    create()

    print(" ** Print the graph with linked list.")
    for i in range(N):
        line = " ".join(str(v) for v in graph[i])
        print(f" * {i}th node =  {line}")

    print("\n * BFS Traversal is =")
    bfs(0)
    print("\n end of  BFS Traversal")
