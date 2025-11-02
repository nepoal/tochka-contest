import sys
from collections import defaultdict, deque


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """

    graph = defaultdict(list)
    for node_1, node_2 in edges:
        graph[node_1].append(node_2)
        graph[node_2].append(node_1)

    gateways = sorted({node for node in graph if node.isupper()})
    virus = 'a'
    result = []

    while gateways and virus:
        nearest_gateways = get_nearest_gateways(graph, gateways, virus)
        target, dist = nearest_gateways[0]
        gateway, node = target

        result.append(f"{gateway}-{node}")
        graph[node].remove(gateway)
        graph[gateway].remove(node)
        if not graph[gateway]:
            graph.pop(gateway)
            gateways.remove(gateway)

        if len(nearest_gateways) > 1:
            gateway = nearest_gateways[1][0][0]

        virus_next = move_virus(graph, virus, gateway)
        if not virus_next:
            break
        virus = virus_next

    return result


def get_nearest_gateways(graph: dict[str: list[str]],
                         gateways: list[str],
                         virus: str) -> list[tuple[tuple[str, str], int]]:
    queue = deque()
    distances = {}
    result = {}

    queue.append(virus)
    distances[virus] = 0

    while queue:
        current = queue.popleft()
        current_dist = distances[current]

        for neighbor in graph[current]:
            if neighbor not in distances:
                queue.append(neighbor)
                distances[neighbor] = current_dist + 1
            if neighbor in gateways:
                for node in graph[neighbor]:
                    if node not in gateways:
                        result[(neighbor, node)] = distances[neighbor]

    result = sorted(result.items(), key=lambda x: (x[1], x[0][0], x[0][1]))
    return result


def move_virus(graph: dict[str: list[str]],
               virus: str,
               gateway: str) -> str | None:
    queue = deque()
    path_from = {}

    queue.append(virus)
    path_from[virus] = None

    while queue:
        current = queue.popleft()

        for neighbor in graph[current]:
            if neighbor not in path_from:
                queue.append(neighbor)
                path_from[neighbor] = current
            if neighbor == gateway:
                path = [neighbor]
                prev = path_from[neighbor]
                while prev != virus:
                    path.append(prev)
                    prev = path_from[prev]
                return path[-1]

    return None


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()