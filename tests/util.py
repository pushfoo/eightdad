from typing import List, Tuple, Any, Mapping, Iterable, Hashable, Union

ValidPairSource = Union[
    Iterable[Tuple[Any, Any]],
    Mapping[Hashable, Any]
]


def src_to_pairs(pairsrc: ValidPairSource) -> List[Tuple[Any, Any]]:
    """

    Turn sources into (k, v) pair legible arguments to parametrized tests

    If the argument is a mapping, then the key is combined with every
    entry in the


    :param pairsrc: what to take the pairs from
    :return:
    """

    out = []

    it_src = pairsrc
    if isinstance(pairsrc, Mapping):
        it_src = pairsrc.items()

    for key, value in it_src:
        if isinstance(value, Iterable):
            for item in value:
                out.append((key, item))
        else:
            out.append((key, value))

    return out