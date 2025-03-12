import dataclasses


@dataclasses.dataclass(frozen=True)
class Range:
    left: int
    right: int


def rangediff(remove_what: list[Range], remove_from: Range) -> list[Range]:

    remove_what.sort(key=lambda x: x.left)

    if len(remove_what) == 0:
        return [remove_from]

    if remove_from.right < remove_what[0].left:
        return [remove_from]

    if remove_what[-1].right < remove_from.left:
        return [remove_from]

    out: list[Range] = []
    for r in remove_what:

        if r.right < remove_from.left:
            continue

        if r.left > remove_from.right:
            continue

        if r.left <= remove_from.left and r.right < remove_from.right:
            remove_from = Range(r.right + 1, remove_from.right)
            continue

        if remove_from.left < r.left and remove_from.right <= r.right:
            remove_from = Range(remove_from.left, r.left - 1)
            continue

        if r.left <= remove_from.left and remove_from.right <= r.right:
            return list()

        if remove_from.left < r.left and r.right < remove_from.right:
            out += [Range(remove_from.left, r.left - 1)]
            remove_from = Range(r.right + 1, remove_from.right)

    out += [remove_from]
    return out
