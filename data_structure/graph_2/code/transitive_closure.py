def transitive_closure(graph, num_vertices):
    # closure 행렬을 인접 행렬로 초기화
    closure = [[graph[i][j] for j in range(num_vertices)]
               for i in range(num_vertices)]

    # 중간 정점 k를 거쳐 가는 경로를 누적
    for k in range(num_vertices):
        for i in range(num_vertices):
            for j in range(num_vertices):
                closure[i][j] = closure[i][j] or (closure[i][k] and closure[k][j])

    # 결과 출력
    print("Transitive Closure:")
    for i in range(num_vertices):
        row = " ".join(str(int(closure[i][j])) for j in range(num_vertices))
        print(row)

    return closure


if __name__ == "__main__":
    graph = [
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [1, 0, 1, 0],
    ]
    num_vertices = 4
    transitive_closure(graph, num_vertices)
