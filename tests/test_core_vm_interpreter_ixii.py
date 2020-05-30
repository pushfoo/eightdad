"""

Tests for the following ixii instructions:

* Fx07 - LD Vx, DT - Set Vx = DT
* Fx15 - LD DT, Vx - Set DT = vX
* Fx18 - LD ST, Vx - Set ST = Vx.
* Fx29 - LD F,  Vx - Set I = location of sprite for digit Vx.
* Fx33 - LD B,  Vx - Store BCD of Vx at I, I + 1, I + 2

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
        type_nibble: int = 0xF0,
        load_point=EXECUTION_START
):
    """
    Set a memory location to an ixii instruction & execute it

    This helper is useful for testing.

    :param vm: the vm to set memory on
    :param x_value: the x value that will specify the v-register targeted
    :param lo_byte: the last two hex digits of the instruction
    :param type_nibble: sets the type for this var
    :param load_point: where the instruction will be loaded into memory
    :return:
    """
    if load_point != EXECUTION_START:
        vm.program_counter = load_point

    vm.memory[load_point + 1] = lo_byte
    vm.memory[load_point] = type_nibble | x_value
    vm.tick(TWO_HUNDREDTH)


@pytest.mark.parametrize(
    "v_register_index,v_initial_value,delay_timer_value",
    product(range(0, 16), (0, 255), (0, 255))
)
def test_fx07_set_vx_to_delay_timer_value(
        v_register_index,
        v_initial_value,
        delay_timer_value
):
    vm = Chip8VirtualMachine()
    vm.delay_timer = delay_timer_value

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
    def test_fx15_sets_delay_timer_from_vx(
            self,
            source_register,
            initial_delay_value,
            set_value
    ):
        """
        FX15 sets delay timer to value in VX

        :param source_register: which VX register to set DT from
        :param initial_delay_value: the value DT will initially hold
        :param set_value: the value DT will have after setting
        :return:
        """
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
    def test_fx18_sets_sound_timer_from_vx(
            self,
            source_register,
            initial_sound_value,
            set_value
    ):
        """
        FX15 sets sound timer to value in VX

        :param source_register: which VX register to set DT from
        :param initial_sound_value: the value DT will initially hold
        :param set_value: the value DT will have after setting
        :return:
        """
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
def test_fx1e_adds_vx_to_i_register(
        source_register: int,
        initial_i: int,
        value_to_add: int):
    """
    FX1E Adds VX and I, storing the result in I

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
    "digit_to_sprite,digit_storage_start",
    product(
        range(0, 16),  # which digit to sprite
        (0, 0x10, 0x100)  # where we store the digit in RAM
    )
)
def test_fx29_load_address_for_digit_sprite_to_i(
        digit_to_sprite,
        digit_storage_start
):
    """
    FX29 Loads address for the sprite of the digit in VX to I register

    :param digit_to_sprite: digit to load sprite for, 0-16
    :param digit_storage_start: where digits will be stored in RAM
    :return:
    """
    vm = Chip8VirtualMachine(digit_start=digit_storage_start)

    for source_register in range(0, 16):
        vm.program_counter = EXECUTION_START

        vm.v_registers[source_register] = digit_to_sprite
        prep_and_execute_ixii_instruction(vm, source_register, 0x29)
        i = vm.i_register

        assert vm.memory[i:i+vm.digit_length] ==\
            DEFAULT_DIGITS[digit_to_sprite]


@pytest.mark.parametrize(
    "v_register_index, i_reg_value,value_to_bcd,expected_result_digits",
    (
        (0, 2048, 0, (0, 0, 0)),
        (8, 2049, 234, (2, 3, 4))
    )
)
def test_fx33_store_bcd_of_vx_starting_at_i(
        v_register_index,
        i_reg_value,
        value_to_bcd,
        expected_result_digits
):
    """
    FX33 Stores BCD of the value in VX starting at location in I register

    :param v_register_index: which x register to use
    :param i_reg_value: where in memory to store the bcd
    :param value_to_bcd: what will be converted
    :param expected_result_digits: the expected digit output
    :return:
    """
    vm = Chip8VirtualMachine()

    vm.i_register = i_reg_value
    vm.v_registers[v_register_index] = value_to_bcd

    prep_and_execute_ixii_instruction(
        vm,
        v_register_index, 0x33
    )

    for index, digit in enumerate(expected_result_digits):
        assert vm.memory[i_reg_value + index] == digit


