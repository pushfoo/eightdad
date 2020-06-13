"""
In standard chip-8, this pattern covers DXYN, drawing sprites.

Most of the functionality behind this is in the VideoRam class, but some
is located  in VM.

"""
import pytest
from eightdad.core.vm import Chip8VirtualMachine as VM, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction, other_registers_untouched, fullbits_generator


@pytest.fixture
def vm_will_draw_1_px() -> VM:
    """Set up a VM ready to draw a single pixel"""
    vm = VM()
    vm.memory[0xA00] = 0b10000000  # a 1 byte sprite to draw a single pixel
    vm.i_register = 0xA00
    return vm


class TestDxynVFBehavior:

    def test_dxyn_sets_vf_when_turning_off_pixels(self, vm_will_draw_1_px):
        """Dxyn sets VF to 1 when overwriting a pixel"""

        load_and_execute_instruction(vm_will_draw_1_px, 0xD000, n=1)
        load_and_execute_instruction(
            vm_will_draw_1_px,
            0xD000, n=1,
            load_point=0x200 + INSTRUCTION_LENGTH
        )
        assert vm_will_draw_1_px.v_registers[0xF] == 1

    def test_dxyn_sets_vf_to_zero_when_no_pixels_turned_off(
            self,
            vm_will_draw_1_px
    ):
        """Dxyn sets VF to 0 when no pixels turned off by it"""
        vm_will_draw_1_px.v_registers[0xF] = 1
        load_and_execute_instruction(vm_will_draw_1_px, 0xD000, n=1)
        assert vm_will_draw_1_px.v_registers[0xF] == 0

