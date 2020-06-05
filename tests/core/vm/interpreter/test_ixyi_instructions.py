from itertools import product

import pytest
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction


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
            0x5000,
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

