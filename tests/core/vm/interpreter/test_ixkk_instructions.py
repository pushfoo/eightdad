import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction

EXECUTION_STARTS = (0x200,0x500,0xF00)
BYTE_VALUES = (0, 0x1, 0xAA, 0xFF)

class Test3XKKInstruction:

    @pytest.mark.parametrize(
        "vx,vx_and_kk_value,exec_start",
        product(
            range(0,16),
            BYTE_VALUES,
            EXECUTION_STARTS
        )
    )
    def test_3xkk_skips_next_instruction_if_vx_eq_kk(
        self,
        vx: int,
        vx_and_kk_value: int,
        exec_start: int
    ):
        vm = VM(execution_start=exec_start)
        vm.v_registers[vx] = vx_and_kk_value
        load_and_execute_instruction(
            0x3000,
            x=vx_and_kk_value,
            kk=vx_and_kk_value
        )
        assert vm.program_counter == exec_start + 2

    @pytest.mark.parametrize(
        "vx,vx_value,kk_value,exec_start",
        product(
            range(0,16),
            BYTE_VALUES,
            BYTE_VALUES,
            EXECUTION_STARTS
        )
    )
    def test_3xkk_does_not_skip_next_instruction_if_vx_neq_kk(
        self,
        vx: int,
        vx_value,
        kk_value,
        exec_start
    ):
        vm = VM(execution_start=exec_start)
        vm.v_registers[vx] = vx_value
        load_and_execute_instruction(
            0x3000,
            x=vx_value,
            kk=kk_value,
        )
        assert vm.program_counter == exec_start + 1
