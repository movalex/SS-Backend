def find_first_missing(list: list[int]) -> int:
    for index, value in enumerate(sorted(list)):
        if index == value:
            first_missing = value + 1
            continue
        else:
            first_missing = index
            break

    return first_missing


def append_first_missing(list: list[int]) -> None:
    missing = find_first_missing(list)
    list.append(missing)


if __name__ == "__main__":
    test = [0, 1, 2, 3, 5, 4, 7, 8]
    print(find_first_missing(test))  # Should print 6.

    append_first_missing(test)

    print(find_first_missing(test))  # Should print 9.
