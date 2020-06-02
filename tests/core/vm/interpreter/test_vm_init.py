import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine

@pytest.mark.parametrize(
    "ram_size",
    [
        512,
        1024,
        2048,
        4096,
        8192
    ]
)
def test_ram_size(ram_size):
    vm = Chip8VirtualMachine(memory_size=ram_size)
    print(vm.memory)
    assert len(vm.memory) == ram_size