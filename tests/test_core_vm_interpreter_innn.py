"""

Tests for the innn instructions:

* 1nnn, jump to nnn: set pc to nnn
* 2nnn, call routine at nnn: push current location to stack, jump to nnn
* Annn, set I to nnn
* Bnnn, Jump to nnn + v0: set pc to nnn + v0

"""
import pytest

from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START
from tests.util import load_and_execute_instruction

VALID_MEMORY_LOCATIONS = (
    0x200,
    0xAAA,
    0xFFF
)

@pytest.mark.parametrize(
    "memory_location",
    (0x0, 0x1) + VALID_MEMORY_LOCATIONS
)
def test_annn_sets_i_register(memory_location):
    """Annn instructions set the I register"""
    vm = VM()
    assert vm.i_register == 0
    load_and_execute_instruction(vm, 0xA000, nnn=memory_location)
    assert vm.i_register == memory_location


@pytest.mark.parametrize("memory_location", VALID_MEMORY_LOCATIONS)
def test_2nnn_sets_program_counter_and_pushes_stack(memory_location):
    """2nnn instruction jumps to location and increments stack"""
    vm = VM()

    assert vm.program_counter == DEFAULT_EXECUTION_START
    load_and_execute_instruction(vm, 0x2000, nnn=memory_location)
    assert vm.program_counter == memory_location
    assert vm.call_stack[-1] == DEFAULT_EXECUTION_START


