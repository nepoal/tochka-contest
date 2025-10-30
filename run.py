import itertools
import sys
from collections import deque
from heapq import heappop, heappush


MOVE_COSTS = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}


def is_goal(cells):
    for idx in range(1, len(cells)):
        loc = cells[idx]
        if loc[0] == 'H':
            continue
        if loc[3] is None or loc[3] != loc[1]:
            return False
    return True


def deeper_rooms(cells, room_idx, door_idxs):
    room = cells[room_idx]
    if room[0] != 'R':
        return []
    room_owner = room[1]
    room_depth = room[2]
    door_idx = door_idxs[room_owner]
    cur_idx = door_idx + room_depth + 1
    idxs = []
    while cur_idx < len(cells):
        next_cell = cells[cur_idx]
        if next_cell[0] != 'R' or next_cell[1] != room_owner:
            break
        idxs.append(cur_idx)
        cur_idx += 1

    return idxs


def can_move(cells, from_idx, to_idx, door_idxs):
    from_cell = cells[from_idx]
    to_cell = cells[to_idx]
    f_kind, f_owner, f_idx, f_occ = from_cell
    t_kind, t_owner, t_idx, t_occ = to_cell

    if f_occ is None or t_occ is not None:
        return False

    if f_kind == 'H' and t_kind == 'H':
        return False

    if f_kind == 'H' and t_kind == 'R':
        if f_occ != t_owner:
            return False
        for d_idx in deeper_rooms(cells, to_idx, door_idxs):
            d_cell = cells[d_idx]
            if d_cell[3] != d_cell[1]:
                return False
        return True

    if f_kind == 'R' and t_kind == 'H':
        if f_occ != f_owner:
            return True
        for d_idx in deeper_rooms(cells, from_idx, door_idxs):
            d_cell = cells[d_idx]
            if d_cell[3] != d_cell[1]:
                return True
        return False

    if f_kind == 'R' and t_kind == 'R':
        if f_owner == t_owner:
            return False
        if f_occ == f_owner:
            return False
        if f_occ != t_owner:
            return False
        for d_idx in deeper_rooms(cells, to_idx, door_idxs):
            d_cell = cells[d_idx]
            if d_cell[3] != d_cell[1]:
                return False
        return True

    return False


def swap_occupant(cells, idx1, idx2):
    occupant_1 = cells[idx1][3]
    occupant_2 = cells[idx2][3]
    new_cells = list(cells)
    new_cells[idx1] = new_cells[idx1][:3] + (occupant_2, )
    new_cells[idx2] = new_cells[idx2][:3] + (occupant_1, )
    return tuple(new_cells)


def get_possible_moves(idx, cells, neighbors, door_idxs):
    owner = cells[idx][3]
    if owner is None:
        return []

    queue = deque([(0, idx)])
    visited = set()
    moves = []
    doors = set(door_idxs.values())

    while queue:
        cost, cur_idx = queue.popleft()
        if cur_idx in visited:
            continue

        visited.add(cur_idx)
        for neigh in neighbors[cur_idx]:
            if cells[neigh][3] is not None:
                continue
            next_cost = cost + MOVE_COSTS[owner]
            queue.append((next_cost, neigh))

            if neigh in doors:
                continue
            if not can_move(cells, idx, neigh, door_idxs):
                continue

            moves.append((next_cost, neigh))
    return moves


def expand_state(cells, neighbors, door_idxs):
    new_cells = []
    for idx in range(1, len(cells)):
        if cells[idx][3] is None:
            continue
        moves = get_possible_moves(idx, cells, neighbors, door_idxs)
        for move_cost, next_idx in moves:
            next_cells = swap_occupant(cells, idx, next_idx)
            new_cells.append((move_cost, next_cells))
    return new_cells


def bfs(cells, neighbors, door_idxs):
    heap = []
    seen = set()
    counter = itertools.count()

    heappush(heap, (0, next(counter), cells))

    while heap:
        total, _, current = heappop(heap)
        if current in seen:
            continue
        seen.add(current)
        if is_goal(current):
            return total
        for new_cells_cost, next_cells in expand_state(current, neighbors, door_idxs):
            new_total = total + new_cells_cost
            heappush(heap, (new_total, next(counter), next_cells))

    return -1


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """
    room_depth = 2 if len(lines) == 5 else 4
    rooms = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
    }
    for floor in lines[2:-1]:
        floor_letters = [i for i in floor.strip().split("#") if i]

        rooms["A"].append(floor_letters[0])
        rooms["B"].append(floor_letters[1])
        rooms["C"].append(floor_letters[2])
        rooms["D"].append(floor_letters[3])

    cells = [None]  # (cell_kind, room_owner, cell_index, cell_occupant)
    neighbors = [[] for _ in range(12 + 4 * room_depth + 1)]
    cell_idxs = {}
    door_cells_idx = {}
    door_idxs = [3, 5, 7, 9]
    owners = tuple(rooms.keys())

    for i in range(1, 12):
        idx = len(cells)
        cells.append(('H', None, i, None))
        cell_idxs[i] = idx

        if i in door_idxs:
            owner = owners[door_idxs.index(i)]
            prev = idx
            for depth in range(1, room_depth + 1):
                room_idx = len(cells)
                cells.append(('R', owner, depth, None))
                neighbors[prev].append(room_idx)
                neighbors[room_idx].append(prev)
                prev = room_idx

    for i in range(1, 11):
        left = cell_idxs[i]
        right = cell_idxs[i + 1]
        neighbors[left].append(right)
        neighbors[right].append(left)

    for i in range(4):
        room_owner = owners[i]
        door_cells_idx[room_owner] = cell_idxs[door_idxs[i]]

    for owner, occupants in rooms.items():
        door_idx = door_cells_idx[owner]
        cur_idx = door_idx
        for depth, occupant in enumerate(occupants, 1):
            while True:
                cur_idx += 1
                if cur_idx >= len(cells):
                    break

                cell = cells[cur_idx]
                if cell[0] == 'R' and cell[1] == owner and cell[2] == depth:
                    cells[cur_idx] = ("R", owner, depth, occupant)
                    break

    cells = tuple(cells)
    min_cost = bfs(cells, neighbors, door_cells_idx)

    return min_cost


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))
    result = solve(lines)
    sys.stdout.write(str(result))


if __name__ == "__main__":
    main()