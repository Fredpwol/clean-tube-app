def depth_first_search(map, key, visited):
    if key == None: return None
    key = key.lower() if key.lower() in map else key.upper()
    if map[key] == None: return False
    for point in map[key]:
        if point.lower() in visited:
            return True
        visited.add(key.lower())
        if depth_first_search(map, point, visited):
            return True
        visited = set()
    return False


def find_cycle(map):
    if map == None: return False
    for point in map:
        if depth_first_search(map, point, set()):
            return True
    return False

print(find_cycle({"A": ["b", "c"], "B":["a"], "C":None}))
