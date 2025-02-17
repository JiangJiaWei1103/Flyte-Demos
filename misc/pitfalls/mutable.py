from typing import List, Tuple


def mutable(a: List[int] = []) -> List[int]:
    a.append(1)

    return a


def immutable(a: Tuple[int, ...] = ()) -> List[int]:
    if a == ():
        a = []
    a.append(1)

    return a


if __name__ == "__main__":
    n = 3

    print(">>> MUTABLE <<<")
    for _ in range(n):
        print(mutable())

    print(">>> IMMUTABLE <<<")
    for _ in range(n):
        print(immutable())
