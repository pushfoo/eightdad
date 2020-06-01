"""

Tests the iiii instructions:
* EE00 - return to last location on the stack

"""

import pytest

from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START
from tests.util import load_and_execute_instruction


@pytest.mark.parametrize("call_location", (0xF00, 0x500))
def test_00ee_returns_to_last_location(call_location):
    """Return instruction returns to last location on the stack"""
    vm = VM()
    vm.stack_call(call_location)

    load_and_execute_instruction(
        vm,
        0x00EE, # return instruction
        load_point=call_location
    )
    assert vm.program_counter == DEFAULT_EXECUTION_START


@pytest.mark.parametrize("call_location", (0xF00, 0x500))
def test_00ee_decrements_stack_size(call_location):
    """Return instruction decrements stack size"""
    vm = VM()
    vm.stack_call(call_location)

    load_and_execute_instruction(
        vm,
        0x00EE, # return instruction
        load_point=call_location
    )
    assert vm.stack_size == 0
