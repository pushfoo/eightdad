"""

Tests the iiii instructions:
* EE00 - return to last location on the stack
* 00E0 - clear the screen

"""
from unittest.mock import Mock

import pytest

from eightdad.core import Chip8VirtualMachine as VM, VideoRam
from eightdad.core.vm import DEFAULT_EXECUTION_START
from tests.util import load_and_execute_instruction


@pytest.mark.parametrize("call_location", (0xF00, 0x500))
def test_00ee_returns_to_last_location_plus_two(call_location):
    """Return instruction returns to last location on the stack"""
    vm = VM()
    vm.stack_call(call_location)

    load_and_execute_instruction(
        vm,
        0x00EE, # return instruction
        load_point=call_location
    )
    assert vm.program_counter == DEFAULT_EXECUTION_START + 2


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


def test_00e0_calls_vram_clear_screen():
    """00E0 causes VM to call screen clear on video ram"""
    vm = VM()
    vm.video_ram = Mock(VideoRam)

    load_and_execute_instruction(vm, 0x00E0)
    assert vm.video_ram.clear_screen.called_once()

