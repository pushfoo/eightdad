from itertools import product

import pytest
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction


class Test5XY0SkipsIfVxEqVy:

    @pytest.mark.parametrize(
        "x,x_val,y,y_val",
        (
            product(
                range(0, 16),
                (0, 1),
                range(9, 16),
                (2, 3)
            )
        )
    )
    def test_5xy0_doesnt_skip_next_if_vx_ne_vy(self, x, x_val, y, y_val):
        vm = VM()
        vm.v_registers[x] = x_val
        vm.v_registers[y] = y_val

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
                range(9, 16),
                (0, 1, 2, 3)
            )
        )
    )
    def test_5xy0_skips_next_if_vx_ne_vy(self, x, y, equal_val):

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

