from itertools import product
from typing import Tuple, Any, Iterable, Dict, Generator


def dict_to_argtuples(
    src: Dict[Tuple,Iterable[Any]]
) -> Generator[Tuple]:
    """

    Turn structured parameter dicts into legible test case parameters.

    The generator yields one set of testcase parameters per tuple. This
    ensures the user can tell what specific data caused a test case to
    fail while still allowing compact expression of test parameters.

    """
    out_raw = []

    for prefix, suffixes in src.items():
        out_raw.extend(product((prefix,), suffixes))

    return (prefix + (suffix, ) for prefix, suffix  in out_raw)

