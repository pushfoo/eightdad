"""

Tests for the innn instructions:

* 1nnn, jump to nnn: set pc to nnn
* 2nnn, call routine at nnn: push current location to stack, jump to nnn
* Annn, set I to nnn
* Bnnn, Jump to nnn + v0: set pc to nnn + v0

"""
from itertools import product

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
    assert vm.stack_size == 0
    assert vm.program_counter == DEFAULT_EXECUTION_START
    load_and_execute_instruction(vm, 0x2000, nnn=memory_location)

    assert vm.program_counter == memory_location
    assert vm.stack_top == DEFAULT_EXECUTION_START
    assert vm.stack_size == 1


@pytest.mark.parametrize("memory_location", VALID_MEMORY_LOCATIONS)
def test_1nnn_jumps_to_address(memory_location):
    """1nnn sets program counter to nnn"""
    vm = VM()

    assert vm.program_counter == DEFAULT_EXECUTION_START
    load_and_execute_instruction(vm, 0x1000, nnn=memory_location)
    assert vm.program_counter == memory_location
    assert vm.stack_size == 0

@pytest.mark.parametrize(
    "memory_location, v0",
    product(
        VALID_MEMORY_LOCATIONS[:-1], # remove #FFF as it's at the end
        (0x00, 0x20, 0xFF)
    )
)
def test_bnnn_jumps_to_address_plus_offset(memory_location, v0):
    """Bnnn sets program counter to nnn + v0"""
    vm = VM()

    assert vm.program_counter == DEFAULT_EXECUTION_START
    assert vm.stack_size == 0

    vm.v_registers[0] = v0
    load_and_execute_instruction(
        vm, 0xB000,
        nnn=memory_location,
    )
    assert vm.program_counter == memory_location + v0
    assert vm.stack_size == 0

