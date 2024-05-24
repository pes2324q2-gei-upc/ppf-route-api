import heapq


def dijkstra(
    graph: dict[str, dict[str, float]], start: str, end: str, autonomy: float = 2.5
) -> list:
    """
    Returns the shortest path and distance from the start to the end node in the graph.

    Args:
        graph (dict): The graph.
        start (str): The start node.
        end (str): The end node.
        autonomy (float): The autonomy in kilometers.

    Returns:
        list: The shortest path from start to end.
    """

    # Initialize the distance to every node as infinity, except the start node
    distances = {node: float("infinity") for node in graph}
    distances[start] = 0

    queue = [(0.0, start)]
    parents = {node: "" for node in graph}

    while queue:
        # Get the node with the smallest distance
        current_distance, current_node = heapq.heappop(queue)

        # If the current distance is larger than the stored distance, skip this node
        if current_distance > distances[current_node]:
            continue

        # If the current node is the end node, break the loop
        if current_node == end:
            break

        # Update the distances to the neighboring nodes
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor] and weight <= autonomy:
                distances[neighbor] = distance
                parents[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    # Build the path from start to end
    path: list = []
    current_node = end
    while current_node != "":
        path.append(current_node)
        current_node = parents[current_node]
    path.reverse()

    return path
