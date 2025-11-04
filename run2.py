import sys
from collections import defaultdict, deque
from copy import deepcopy


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
    states = {}
    result = sort_states(states, graph, gateways, virus)

    return result


def sort_states(states: dict[str, frozenset[tuple[str, str]]: list[str]],
                graph: dict[str: list[str]],
                gateways: list[str],
                virus: str) -> list[str] | None:
    nodes = set()
    for gateway in gateways:
        for node in graph.get(gateway, []):
            nodes.add((gateway, node))

    nodes = frozenset(nodes)
    state = virus, nodes

    if state in states:
        return states[state]

    nearest_gateway = get_nearest_gateway(graph, gateways, virus)
    if not all(nearest_gateway):
        states[state] = []
        return []

    possible_nodes = []
    for gateway in sorted(gateways):
        for node in sorted(graph.get(gateway, [])):
            possible_nodes.append((gateway, node))

    for gateway, node in sorted(possible_nodes):
        new_graph = deepcopy(graph)
        new_graph[gateway].remove(node)
        new_graph[node].remove(gateway)

        new_gateway, new_node, new_dist = get_nearest_gateway(new_graph, gateways, virus)
        if new_gateway is None:
            states[state] = [f"{gateway}-{node}"]
            return [f"{gateway}-{node}"]

        if new_dist == 1:
            continue

        next_virus = move_virus(new_graph, virus, new_gateway)
        if next_virus is None or next_virus.isupper():
            continue

        new_state = sort_states(states, new_graph, gateways, next_virus)
        if new_state is not None:
            states[state] = [f"{gateway}-{node}"] + new_state
            return states[state]

    states[state] = None
    return None


def get_nearest_gateway(graph: dict[str: list[str]],
                         gateways: list[str],
                         virus: str) -> tuple[str|None, str|None, int|None]:
    queue = deque()
    distances = {}
    path_from = {}

    queue.append(virus)
    distances[virus] = 0

    min_dist = None
    best_gateway = None
    best_node = None

    while queue:
        current = queue.popleft()
        current_dist = distances[current]

        for neighbor in sorted(graph[current]):
            if neighbor not in distances:
                queue.append(neighbor)
                distances[neighbor] = current_dist + 1
                path_from[neighbor] = current
            if neighbor in gateways:
                node = current
                dist = distances[current] + 1
                if best_gateway is None \
                        or dist < min_dist or \
                        (dist == min_dist and neighbor < best_gateway) or \
                        (dist == min_dist and neighbor == best_gateway and current < best_node):
                    min_dist = dist
                    best_gateway = neighbor
                    best_node = current

    return best_gateway, best_node, min_dist


def move_virus(graph: dict[str: list[str]],
               virus: str,
               gateway: str) -> str | None:
    if gateway is None:
        return None
    queue = deque()
    path_from = {}

    queue.append(virus)
    path_from[virus] = None

    while queue:
        current = queue.popleft()

        for neighbor in sorted(graph[current]):
            if neighbor not in path_from:
                queue.append(neighbor)
                path_from[neighbor] = current
            if neighbor == gateway:
                path = [gateway]
                while path_from[path[-1]] is not None:
                    path.append(path_from[path[-1]])
                return path[-2] if len(path) >= 2 else None

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