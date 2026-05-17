def get_column_heights(board_grid):
    if not board_grid:
        return []

    height = len(board_grid)
    width = len(board_grid[0])
    heights = []

    for x in range(width):
        column_height = 0

        for y in range(height):
            if board_grid[y][x] != 0:
                column_height = height - y
                break

        heights.append(column_height)

    return heights


def count_holes(board_grid):
    if not board_grid:
        return 0

    height = len(board_grid)
    width = len(board_grid[0])
    holes = 0

    for x in range(width):
        found_block = False

        for y in range(height):
            if board_grid[y][x] != 0:
                found_block = True
            elif found_block:
                holes += 1

    return holes


def calculate_bumpiness(heights):
    bumpiness = 0

    for i in range(len(heights) - 1):
        bumpiness += abs(heights[i] - heights[i + 1])

    return bumpiness


def calculate_well_sums(heights):
    well_sums = 0
    width = len(heights)

    for x in range(width):
        left_height = heights[x - 1] if x > 0 else float("inf")
        right_height = heights[x + 1] if x < width - 1 else float("inf")

        if heights[x] < left_height and heights[x] < right_height:
            well_depth = min(left_height, right_height) - heights[x]
            well_sums += well_depth

    return well_sums


def calculate_row_transitions(board_grid):
    transitions = 0

    for row in board_grid:
        previous_filled = True

        for cell in row:
            current_filled = cell != 0

            if current_filled != previous_filled:
                transitions += 1

            previous_filled = current_filled

        if previous_filled is False:
            transitions += 1

    return transitions


def calculate_column_transitions(board_grid):
    if not board_grid:
        return 0

    height = len(board_grid)
    width = len(board_grid[0])
    transitions = 0

    for x in range(width):
        previous_filled = True

        for y in range(height):
            current_filled = board_grid[y][x] != 0

            if current_filled != previous_filled:
                transitions += 1

            previous_filled = current_filled

        if previous_filled is False:
            transitions += 1

    return transitions


def extract_features(board_grid, lines_cleared=0):
    heights = get_column_heights(board_grid)

    aggregate_height = sum(heights)
    max_height = max(heights) if heights else 0
    holes = count_holes(board_grid)
    bumpiness = calculate_bumpiness(heights)
    well_sums = calculate_well_sums(heights)
    row_transitions = calculate_row_transitions(board_grid)
    column_transitions = calculate_column_transitions(board_grid)

    return {
        "holes": holes,
        "aggregate_height": aggregate_height,
        "max_height": max_height,
        "bumpiness": bumpiness,
        "lines_cleared": lines_cleared,
        "well_sums": well_sums,
        "row_transitions": row_transitions,
        "column_transitions": column_transitions,
    }