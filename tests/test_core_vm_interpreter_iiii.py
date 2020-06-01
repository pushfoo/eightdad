"""

Tests for iiii instructions


"""

import pytest

from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START
from tests.util import load_and_execute_instruction


@pytest.mark.parametrize("call_location", (0xF00, 0x500))
def test_00ee_returns_to_last_location(call_location):
    vm = VM()
    vm.stack_call(call_location)

    load_and_execute_instruction(
        vm,
        0x00EE, # return instruction
        load_point=call_location
    )
    assert vm.program_counter == DEFAULT_EXECUTION_START
    assert vm.stack_size == 0

