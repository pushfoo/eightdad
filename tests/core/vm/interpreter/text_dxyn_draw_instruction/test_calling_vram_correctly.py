import pytest
from unittest.mock import Mock

from eightdad.core import VideoRam
from eightdad.core.vm import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction

def test_dxyn_calls_videoram_draw_correctly():
    """DXYN args are correctly passed to VideoRam draw call"""
    vm = VM()
    vm.video_ram = Mock(VideoRam)
    vm.video_ram.draw_sprite.return_value = 1

    vm.v_registers[1] = 1
    vm.v_registers[2] = 2

    vm.i_register = 0xA00
    load_and_execute_instruction(
        vm, 0xD123
    )
    assert vm.video_ram.draw_sprite.called_with(
        1, 2, vm.memory, num_bytes=3, offset=0xA00
    )

