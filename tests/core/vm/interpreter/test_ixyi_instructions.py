from itertools import product

import pytest
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction, other_registers_untouched, fullbits_generator


class Test5XY0SkipsIfVxEqualsVy:

    @pytest.mark.parametrize(
        "x,y",
        (
            filter(
                lambda x: x[0] != x[1],
                product(
                    range(0, 16),
                    range(0, 16),
                )
            )
        )
    )
    def test_5xy0_doesnt_skip_next_if_vx_not_equal_vy(self, x, y):
        vm = VM()
        vm.v_registers[x] = 0
        vm.v_registers[y] = 1

        load_and_execute_instruction(
            vm,
            0x5000,
            x=x, y=y
        )

        assert vm.program_counter ==\
               DEFAULT_EXECUTION_START + INSTRUCTION_LENGTH

    @pytest.mark.parametrize(
        "x,y,equal_val",
        (
            product(
                range(0, 16),
                range(0, 16),
                (0, 1, 2, 3)
            )
        )
    )
    def test_5xy0_skips_next_if_vx_equal_vy(self, x, y, equal_val):

        vm = VM()
        vm.v_registers[x] = equal_val
        vm.v_registers[y] = equal_val

        load_and_execute_instruction(
            vm,
            0x5000,
            x=x, y=y
        )

        assert vm.program_counter ==\
               DEFAULT_EXECUTION_START + (2 * INSTRUCTION_LENGTH)


class Test9XY0SkipsIfVxNotEqualsVy:

    @pytest.mark.parametrize(
        "x,y",
        (
            filter(
                lambda x: x[0] != x[1],
                product(
                    range(0, 16),
                    range(0, 16),
                )
            )
        )
    )
    def test_6xy0_skips_next_if_vx_not_equal_vy(self, x, y):
        vm = VM()
        vm.v_registers[x] = 0
        vm.v_registers[y] = 1

        load_and_execute_instruction(
            vm,
            0x9000,
            x=x, y=y
        )

        assert vm.program_counter ==\
               DEFAULT_EXECUTION_START + (2 * INSTRUCTION_LENGTH)


    @pytest.mark.parametrize(
        "x,y,equal_val",
        (
            product(
                range(0, 16),
                range(0, 16),
                (0, 1, 2, 3)
            )
        )
    )
    def test_9xy0_doesnt_skip_next_if_vx_eq_vy(self, x, y, equal_val):

        vm = VM()
        vm.v_registers[x] = 7
        vm.v_registers[y] = 7

        load_and_execute_instruction(
            vm,
            0x9000,
            x=x, y=y
        )

        assert vm.program_counter ==\
               DEFAULT_EXECUTION_START + INSTRUCTION_LENGTH


@pytest.mark.parametrize("x", range(0, 16))
@pytest.mark.parametrize("y", range(0, 16))
class Test8XY1OrsRegisters:

    def test_8xy1_sets_vx_to_logical_or_of_vx_and_vy(self, x, y):
        """8xy1 sets VX = VX OR VY"""

        vm = VM()
        original_x_value = 0b10101010
        default_y_value = 0b01010101

        vm.v_registers[x] = original_x_value
        if y != x:
            vm.v_registers[y] = default_y_value

        load_and_execute_instruction(vm, 0x8001, x=x, y=y)

        if y != x:
            assert vm.v_registers[x] == original_x_value | default_y_value
        else:
            assert vm.v_registers[x] == original_x_value

    def test_8xy1_leaves_other_registers_alone(self, x, y):
        """8xy1 leaves other registers alone"""

        vm = VM()
        vm.v_registers[x] = 0b10101010
        vm.v_registers[y] = 0b01010101

        load_and_execute_instruction(vm, 0x8001, x=x, y=y)

        assert other_registers_untouched(vm, (x, y))


@pytest.mark.parametrize("x", range(0, 16))
@pytest.mark.parametrize("y", range(0, 16))
class Test8XY2AndsRegisters:

    def test_8xy2_sets_vx_to_and_of_vx_and_vy(self, x, y):
        """8xy2 sets VX to VX AND VY"""

        vm = VM()

        left_half_filled = 0b11110000

        vm.v_registers[x] = 0xFF
        vm.v_registers[y] = left_half_filled

        # set vx = vx AND 0x11110000. If vx is already set to 0x11110000,
        # the value will still be 0x11110000 after the instruction runs.
        load_and_execute_instruction(vm, 0x8002, x=x, y=y)

        assert vm.v_registers[x] == left_half_filled

    def test_8xy2_leaves_other_registers_alone(self, x, y):
        """8xy2 leaves registers other than VX and VY alone"""

        vm = VM()
        vm.v_registers[x] = 0b10101010
        vm.v_registers[y] = 0b01010101

        load_and_execute_instruction(vm, 0x8002, x=x, y=y)

        assert other_registers_untouched(vm, (x, y))


@pytest.mark.parametrize("x", range(0, 16))
@pytest.mark.parametrize("y", range(0, 16))
class Test8XY3XorsRegisters:

    def test_8xy3_sets_vx_to_xor_of_vx_and_vy(self, x, y):
        """8xy3 sets VX to VX XOR VY"""

        vm = VM()

        vm.v_registers[x] = 0b10101111
        vm.v_registers[y] = 0b01011111

        load_and_execute_instruction(vm, 0x8003, x=x, y=y)

        if x != y:
            assert vm.v_registers[x] == 0b11110000

        else:  # any value xor itself yields zero
            assert vm.v_registers[x] == 0

    def test_8xy3_leaves_other_registers_alone(self, x, y):
        """8xy3 leaves registers other than VX and VY alone"""

        vm = VM()

        vm.v_registers[x] = 0b10101111
        vm.v_registers[y] = 0b01011111

        load_and_execute_instruction(vm, 0x8003, x=x, y=y)

        assert other_registers_untouched(vm, (x, y))


class Test8XY4AddsRegisters:

    # Avoiding setting VF as the destination is intentional here. It
    # always stores 0 or 1 to indicate if an overflow occurred. The next
    # test method verifies that behavior.
    @pytest.mark.parametrize("x", range(0, 0xF))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1,))
    def test_8xy4_sets_vx_to_sum_of_vx_and_vy(self, x, y, a, b):
        """8xy4 sets VX to VX + VY, clamped to 255 max"""

        vm = VM()

        vm.v_registers[x] = a

        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8004, x=x, y=y)

        if x != y:
            assert vm.v_registers[x] == min(a + b, 255)

        else:  # any value xor itself yields zero
            assert vm.v_registers[x] == min(2 * a, 255)

    # According to the spec, VF should override itself if it is set as the
    # destination of the sum. This behavior could be useful for checking
    # whether something overflows without overriding crucial values.
    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1,))
    def test_8xy4_sets_vf_to_carry_bit(self, x, y, a, b):
        """8xy4 sets VF to 1 if VX + VY > 255, otherwise 0"""
        vm = VM()

        vm.v_registers[x] = a
        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8004, x=x, y=y)

        assert vm.v_registers[0xF] == int(a + b > 255)

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    def test_8xy4_leaves_other_registers_alone_unless_theyre_vf(
        self,
        x,
        y
    ):
        """8xy4 leaves registers other than VX and VY alone except for VF"""

        vm = VM()

        vm.v_registers[x] = 255
        vm.v_registers[y] = 1

        load_and_execute_instruction(vm, 0x8004, x=x, y=y)

        # make sure we don't check VF since it should always be set
        touched = {x, y, 0xF}

        assert other_registers_untouched(vm, touched)


class Test8XY5SetsVxToVxMinusVy:

    # Avoiding setting VF as the destination is intentional. Any
    # difference written to VF will be overridden with a bit flag, as
    # with the addition operator.
    @pytest.mark.parametrize("x", range(0, 0xF))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 2))
    @pytest.mark.parametrize("b", (1, 0))
    def test_8xy5_sets_vx_to_vx_minus_vy(self, x, y, a, b):
        """8xy5 sets VX = VX - VY, clamped to 0 minimum"""

        vm = VM()

        vm.v_registers[x] = a

        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8005, x=x, y=y)

        if x != y:
            assert vm.v_registers[x] == max(a - b, 0)

        else:  # any value minus itself yields zero
            assert vm.v_registers[x] == 0

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1,))
    def test_8xy5_sets_vf_to_not_borrow(self, x, y, a, b):
        """8xy5 sets VF to 1 if VX >= VY, otherwise 0"""
        vm = VM()

        vm.v_registers[x] = a
        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8005, x=x, y=y)

        assert vm.v_registers[0xF] == int(a >= b)

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    def test_8xy5_leaves_other_registers_alone_unless_theyre_vf(
        self,
        x,
        y
    ):
        """8xy5 leaves registers other than VX and VY alone except for VF"""

        vm = VM()

        vm.v_registers[x] = 2
        vm.v_registers[y] = 1

        load_and_execute_instruction(vm, 0x8005, x=x, y=y)

        # make sure we don't check VF since it should always be set
        touched = {x, y, 0xF}

        assert other_registers_untouched(vm, touched)


class Test8XY6SetsVxToVyShiftedRight1:

    # Avoiding setting VF as the destination is intentional. Any
    # value written to VF will be overridden with a bit flag.
    @pytest.mark.parametrize("x", range(0, 0xF))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 2))
    @pytest.mark.parametrize("b", fullbits_generator(8))
    def test_8xy6_sets_vx_to_vy_shifted_right_one(self, x, y, a, b):
        """8xy6 sets VX = VY >> 1"""

        vm = VM()

        vm.v_registers[x] = a
        vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8006, x=x, y=y)

        assert vm.v_registers[x] == b >> 1

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1, 255, 0, 2))
    def test_8xy6_sets_vf_to_least_significant_digit_of_vy(self, x, y, a, b):
        """8xy6 sets VF to least significant"""
        vm = VM()

        vm.v_registers[x] = a
        vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8006, x=x, y=y)

        assert vm.v_registers[0xF] == b & 1

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    def test_8xy6_leaves_other_registers_alone_unless_theyre_vf(
        self,
        x,
        y
    ):
        """8xy6 leaves registers other than VX alone except for VF"""

        vm = VM()

        vm.v_registers[x] = 2
        vm.v_registers[y] = 1

        load_and_execute_instruction(vm, 0x8006, x=x, y=y)

        # make sure we don't check VF since it should always be set
        touched = {x, 0xF}

        assert other_registers_untouched(vm, touched)


class Test8XY7SetsVxToVyMinusVx:

    # Avoiding setting VF as the destination is intentional. Any
    # difference written to VF will be overridden with a bit flag.
    @pytest.mark.parametrize("x", range(0, 0xF))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 2))
    @pytest.mark.parametrize("b", (1, 0))
    def test_8xy7_sets_vx_to_vy_minus_vx(self, x, y, a, b):
        """8xy7 sets VX = VY - VX, clamped to 0 minimum"""

        vm = VM()

        vm.v_registers[x] = a

        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8007, x=x, y=y)

        if x != y:
            assert vm.v_registers[x] == max(b - a, 0)

        else:  # any value minus itself yields zero
            assert vm.v_registers[x] == 0

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1,))
    def test_8xy7_sets_vf_to_not_borrow(self, x, y, a, b):
        """8xy7 sets VF to 1 if VX >= VY, otherwise 0"""
        vm = VM()

        vm.v_registers[x] = a
        if x != y:
            vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x8007, x=x, y=y)

        if x != y:
            assert vm.v_registers[0xF] == int(b >= a)
        else:
            assert vm.v_registers[0xF] == 1

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    def test_8xy7_leaves_other_registers_alone_unless_theyre_vf(
        self,
        x,
        y
    ):
        """8xy7 leaves registers other than VX and VY alone except for VF"""

        vm = VM()

        vm.v_registers[x] = 1
        vm.v_registers[y] = 2

        load_and_execute_instruction(vm, 0x8007, x=x, y=y)

        # make sure we don't check VF since it should always be set
        touched = {x, 0xF}

        assert other_registers_untouched(vm, touched)


class Test8XYESetsVxToVyShiftedLeft1:

    # Avoiding setting VF as the destination is intentional. Any
    # value written to VF will be overridden with a bit flag.
    @pytest.mark.parametrize("x", range(0, 0xF))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 2))
    @pytest.mark.parametrize("b", fullbits_generator(8))
    def test_8xye_sets_vx_to_vy_shifted_left_one(self, x, y, a, b):
        """8xyE sets VX = VY >> 1"""

        vm = VM()

        vm.v_registers[x] = a
        vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x800E, x=x, y=y)

        assert vm.v_registers[x] == min(b << 1, 255)

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    @pytest.mark.parametrize("a", (1, 255))
    @pytest.mark.parametrize("b", (1, 255, 0, 2))
    def test_8xye_sets_vf_to_most_significant_digit_of_vy(self, x, y, a, b):
        """8xyE sets VF to most significant digit of VY"""
        vm = VM()

        vm.v_registers[x] = a
        vm.v_registers[y] = b

        load_and_execute_instruction(vm, 0x800E, x=x, y=y)

        assert vm.v_registers[0xF] == b & 0b10000000

    @pytest.mark.parametrize("x", range(0, 16))
    @pytest.mark.parametrize("y", range(0, 16))
    def test_8xye_leaves_other_registers_alone_unless_theyre_vf(
        self,
        x,
        y
    ):
        """8xy6 leaves registers other than VX alone except for VF"""

        vm = VM()

        vm.v_registers[x] = 2
        vm.v_registers[y] = 1

        load_and_execute_instruction(vm, 0x800E, x=x, y=y)

        # make sure we don't check VF since it should always be set
        touched = {x, 0xF}

        assert other_registers_untouched(vm, touched)
