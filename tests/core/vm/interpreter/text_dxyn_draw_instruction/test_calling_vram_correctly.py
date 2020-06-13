import pytest
from unittest.mock import Mock

from eightdad.core import VideoRam
from eightdad.core.vm import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction


@pytest.mark.parametrize(
    "x,y,n,i",
    (
        (1, 2, 1, 0xA00),
        (0, 1, 2, 0xB00)
    )
)
def test_dxyn_calls_videoram_draw_correctly(x,y,n,i):
    """DXYN args are correctly passed to VideoRam draw call

    I'm not actually sure that this is a great idea. Need a more
    experienced developer to give feedback on it.
    """
    vm = VM()
    vm.video_ram = Mock(VideoRam)
    vm.video_ram.draw_sprite.return_value = 1

    vm.v_registers[x] = x
    vm.v_registers[y] = y

    vm.i_register = i
    load_and_execute_instruction(
        vm, 0xD000, x=x, y=y, n=n
    )
    assert vm.video_ram.draw_sprite.called_once_with(
        x, y, vm.memory, num_bytes=n, offset=i
    )

