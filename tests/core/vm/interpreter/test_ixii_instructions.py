"""

Tests for the following ixii instructions:

* Fx07 - LD Vx, DT - Set Vx = DT
* Fx15 - LD DT, Vx - Set DT = vX
* Fx18 - LD ST, Vx - Set ST = Vx.
* Fx29 - LD F,  Vx - Set I = location of sprite for digit Vx.
* Fx33 - LD B,  Vx - Store BCD of Vx at I, I + 1, I + 2

"""
import pytest
from itertools import product, chain
from eightdad.core import Chip8VirtualMachine
from eightdad.core.video import DEFAULT_DIGITS
from eightdad.core.vm import DIGIT_HEIGHT

load_and_execute_instruction = pytest.helpers.load_and_execute_instruction


EXECUTION_START = 512
TWO_HUNDREDTH = 1.0 / 200


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

    load_and_execute_instruction(vm, 0xF007, x=v_register_index)

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
        load_and_execute_instruction(vm, 0xF015, x=source_register)

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

        load_and_execute_instruction(vm, 0xF018, x=source_register)

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

    load_and_execute_instruction(vm, 0xF01E, x=source_register)

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
        load_and_execute_instruction(vm, 0xF029, x=source_register)
        i = vm.i_register

        assert vm.memory[i:i+DIGIT_HEIGHT] ==\
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

    load_and_execute_instruction(vm, 0xF033, x=v_register_index)

    for index, digit in enumerate(expected_result_digits):
        assert vm.memory[i_reg_value + index] == digit


class TestFx55StoresRegistersToRam:

    def _write_values_to_memory(
            self,
            vm: Chip8VirtualMachine,
            max_register: int,
            write_dest: int = 0xA00,
            value_start: int = 128
    ) -> None:
        """

        Helper function that executes a bulk register save operation.

        Will write value_start +0, ... value_start + max_register to
        the first max_register registers.

        Then runs FX55, with max_register as X.

        :param vm: vm object to write to
        :param max_register: the highest register that will be saved
        :param value_start: what the start of the written values will be
        :return:
        """

        # set up the registers with unique values that can be checked
        # for correct write order in memory.
        for index in range(0, max_register + 1):
            vm.v_registers[index] = value_start + index

        # set up where the registers will be stored to
        vm.i_register = write_dest

        load_and_execute_instruction(
            vm, 0xF055, x=max_register
        )

    @pytest.mark.parametrize("max_register", tuple(range(0, 16)))
    def test_fx55_writes_registers_to_ram(self, max_register):
        """Fx55 writes register contents to RAM correctly"""
        vm = Chip8VirtualMachine()

        self._write_values_to_memory(
            vm, max_register, 0xA00, 128
        )

        for index in range(0, max_register+1):
            assert vm.memory[0xA00 + index] == 128 + index

    @pytest.mark.parametrize("write_location", (0xA00, 0x400))
    def test_fx55_does_not_touch_other_memory(self, write_location):
        """Fx55 doesn't touch RAM outside the range it's supposed to"""
        vm = Chip8VirtualMachine()

        self._write_values_to_memory(
            vm, 0xF, write_location, 128
        )

        # memory outside of the write area isn't touched, excludes
        # the load point of the fx55 instruction
        for memory_index in chain(
                range(0x202, write_location),
                range(write_location + 18, len(vm.memory))
        ):
            assert vm.memory[memory_index] == 0


class TestFx65LoadsRamToRegisters:

    def _load_from_memory(
            self,
            vm: Chip8VirtualMachine,
            max_register: int,
            read_src: int = 0xA00,
            value_start: int = 128
    ) -> None:
        """

        Helper function that executes a bulk register save operation.

        Will write value_start +0, ... value_start + max_register to
        the first max_register registers.

        Then runs FX55, with max_register as X.

        :param vm: vm object to write to
        :param max_register: the highest register that will be saved
        :param value_start: what the start of the written values will be
        :return:
        """

        # set up the memory with values to read into registers
        for register_index in range(0, max_register + 1):
            vm.memory[read_src + register_index] = 128 + register_index

        # set up where the registers will be stored to
        vm.i_register = read_src

        load_and_execute_instruction(
            vm, 0xF065, x=max_register
        )

    @pytest.mark.parametrize("max_register", range(0, 16))
    def test_fx65_loads_ram_to_registers(self, max_register):
        """Fx65 reads ram contents to registers correctly"""
        vm = Chip8VirtualMachine()

        self._load_from_memory(
            vm, max_register, 0xA00, 128
        )

        for register_index in range(0, max_register+1):
            assert vm.v_registers[register_index] == 128 + register_index

    @pytest.mark.parametrize("max_register", range(0,0xF))
    def test_fx65_does_not_touch_other_registers(self, max_register):
        """Fx65 doesn't touch registers past x"""
        vm = Chip8VirtualMachine()

        self._load_from_memory(
            vm, max_register, 0xA00, 128
        )

        # memory outside of the write area isn't touched, excludes
        # the load point of the fx55 instruction
        for register_index in range(max_register + 1, 16):
            assert vm.v_registers[register_index] == 0
