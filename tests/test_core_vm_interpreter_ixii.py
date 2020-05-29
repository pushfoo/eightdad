"""
    Fx07 - LD Vx, DT - Set Vx = DT
    Fx15 - LD DT, Vx - Set DT = vX
    Fx18 - LD ST, Vx - Set ST = Vx.
"""
import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine
from eightdad.core.video import DEFAULT_DIGITS

EXECUTION_START = 512
TWO_HUNDREDTH = 1.0 / 200


def prep_and_execute_ixii_instruction(
        vm: Chip8VirtualMachine,
        x_value: int,
        lo_byte: int,
        type_nibble: int = 0xF0
):
    """
    helper that sets first execution point to an ixii instruction

    :param vm: the vm to set memory on
    :param x_value: the x value that will specify the v-register targeted
    :param lo_byte: the last two hex digits of the instruction
    :return:
    """
    vm.memory[EXECUTION_START] = lo_byte
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
            range(0, 16),
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


@pytest.mark.parametrize(
    "source_register,initial_i,value_to_add",
    product(
        range(0, 16),
        (0, 0x400, 0x800),
        (0, 1, 0xFF)
    )
)
def test_adding_to_i_register(
        source_register: int,
        initial_i: int,
        value_to_add: int):
    """
    Ensure that adding to I register works correctly

    :param source_register: which register will be pulled from
    :param initial_i: initial value for i to hold
    :param value_to_add: value that will be added to the I register
    """
    vm = Chip8VirtualMachine()

    vm.i_register = initial_i
    vm.v_registers[source_register] = value_to_add

    prep_and_execute_ixii_instruction(vm, source_register, 0x1E)

    assert vm.i_register == initial_i + value_to_add


@pytest.mark.parametrize(
    "digit_start",
    [
        0,
        0x10,
        0x100
    ]
)
def test_fx29_load_digit_address_to_i(digit_start):
    vm = Chip8VirtualMachine(digit_start=digit_start)

    for source_register in range(0, 16):
        for digit_value in range(0, 16):
            vm.program_counter = EXECUTION_START

            vm.v_registers[source_register] = digit_value
            prep_and_execute_ixii_instruction(vm, source_register, 0x29)
            i = vm.i_register

            assert vm.memory[i:i+vm.digit_length] ==\
                DEFAULT_DIGITS[digit_value]


@pytest.mark.parametrize(
    "x_reg, i_reg_value,value_to_bcd,digits",
    (
        (0, 2048, 0, (0, 0, 0)),
        (8, 2049, 234, (2, 3, 4))
    )
)
def test_fx33_bcd_of_vx_starting_at_i(
        x_reg,
        i_reg_value,
        value_to_bcd,
        digits
):
    """
    BCD of digits to memory works properly.

    :param x_reg: which x register to use
    :param i_reg_value: where in memory to store the bcd
    :param value_to_bcd: what will be converted
    :param digits: the expected digit output
    :return:
    """
    vm = Chip8VirtualMachine()

    vm.i_register = i_reg_value
    vm.v_registers[x_reg] = value_to_bcd

    prep_and_execute_ixii_instruction(
        vm,
        x_reg, 0x33
    )

    for index, digit in enumerate(digits):
        assert vm.memory[i_reg_value + index] == digit


