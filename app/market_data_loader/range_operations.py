import dataclasses


@dataclasses.dataclass(frozen=True)
class Range[T]:
    left: T
    right: T


def rangemerge(ranges: list[Range]) -> list[Range]:
    ranges.sort(key=lambda x: x.left)
    prev = None
    updated_ranges: list[Range] = []
    for rng in ranges:
        if prev is None:
            updated_ranges += [rng]
            prev = rng
            continue
        if rng.left <= prev.right + 1:
            updated_ranges[-1] = Range(
                left=updated_ranges[-1].left,
                right=max(updated_ranges[-1].right, rng.right),
            )
            prev = updated_ranges[-1]
            continue
        updated_ranges += [rng]
        prev = rng
    return updated_ranges


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
