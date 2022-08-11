# Helper function for Controller and Fusion API classes.
def find_first_missing(list: list[int]) -> int:
    for index, value in enumerate(sorted(list)):
        if index == value:
            first_missing = value + 1
            continue
        else:
            first_missing = index
            break

    return first_missing


# Helper function for Screen and Grid classes.
def get_coords(item, matrix: list[list]) -> tuple[int, int]:
    for i, v in enumerate(matrix):
        if item in v:
            y = i
            x = v.index(item)
    return x + 1, y + 1


def is_within(coords: tuple[float, float], area: dict[tuple[float, float]]) -> bool:
    x, y = coords[0], coords[1]
    if x <= area["top_left"][0]:
        return False
    if x >= area["top_right"][0]:
        return False
    if y >= area["top_left"][1]:
        return False
    if y <= area["bottom_left"][1]:
        return False
    return True


if __name__ == "__main__":
    pass
