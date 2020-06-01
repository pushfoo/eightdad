"""

Tests for the innn instructions:

* 1nnn, jump to nnn: set pc to nnn
* 2nn, call routine at nnn: push current location to stack, jump to nnn
* Annn, set I to nnn
* Bnnn, Jump to nnn + v0: set pc to nnn + v0

"""
import pytest

from eightdad.core import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction

VALID_MEMORY_LOCATIONS = (
    0x0,
    0x1,
    0x200,
    0xAAA,
    0xFFF
)


@pytest.mark.parametrize( "memory_location", VALID_MEMORY_LOCATIONS)
def test_annn_sets_i_register(memory_location):
    """Annn instructions set the I register"""
    vm = VM()
    assert vm.i_register == 0
    load_and_execute_instruction(vm, 0xA000, nnn=memory_location)
    assert vm.i_register == memory_location

