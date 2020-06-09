from itertools import product

import pytest
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction, other_registers_untouched


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

    def test_8xy1_sets_target_to_or(self, x, y):
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

        vm = VM()
        vm.v_registers[x] = 0b10101010
        vm.v_registers[y] = 0b01010101

        load_and_execute_instruction(vm, 0x8001, x=x, y=y)

        assert other_registers_untouched(vm, (x, y))
