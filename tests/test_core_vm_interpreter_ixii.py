"""
    Fx07 - LD Vx, DT - Set Vx = DT
    Fx15 - LD DT, Vx - Set DT = vX
    Fx18 - LD ST, Vx - Set ST = Vx.
"""
import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine

EXECUTION_START = 512
TWO_HUNDREDTH = 1.0 / 200


def prep_and_execute_ixii_instruction(
        vm: Chip8VirtualMachine,
        x_value: int,
        end_value: int,
        type_nibble : int = 0xF0
):
    """
    helper that sets first execution point to an ixii instruction

    :param vm: the vm to set memory on
    :param x_value: the x value that will specify the v-register targeted
    :param end_value: the last two hex digits of the instruction
    :return:
    """
    vm.memory[EXECUTION_START] = end_value
    vm.memory[EXECUTION_START + 1] = type_nibble | x_value
    vm.tick(TWO_HUNDREDTH)


@pytest.mark.parametrize(
    "v_register_index,v_initial_value,delay_timer_value",
    product(range(0, 16), (0, 255), (0, 255))
)
def test_getting_delay_timer_value(
        v_register_index,
        v_initial_value,
        delay_timer_value
    ):

    vm = Chip8VirtualMachine()
    vm._delay_timer.value = delay_timer_value

    prep_and_execute_ixii_instruction(vm, v_register_index, 0x07)

    assert vm.v_registers[v_register_index] == delay_timer_value


class TestSettingTimers:
    @pytest.mark.parametrize(
        "source_register,initial_delay_value,set_value",
        product(
            range(0,16),
            (0, 255),
            (0, 255),
        )
    )
    def test_set_delay_timer(self, source_register, initial_delay_value, set_value):

        vm = Chip8VirtualMachine()

        vm.delay_timer = initial_delay_value
        vm.v_registers[source_register] = set_value

        prep_and_execute_ixii_instruction(vm, source_register, 0x15)

        assert vm.delay_timer == set_value

    @pytest.mark.parametrize(
        "source_register,initial_sound_value,set_value",
        product(
            range(0, 16),
            (0, 255),
            (0, 255),
        )
    )
    def test_set_sound_timer(self, source_register, initial_sound_value, set_value):

        vm = Chip8VirtualMachine()

        vm.sound_timer = initial_sound_value
        vm.v_registers[source_register] = set_value

        prep_and_execute_ixii_instruction(vm, source_register, 0x18)

        assert vm.sound_timer == set_value




