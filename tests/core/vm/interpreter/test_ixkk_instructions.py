import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction

EXECUTION_STARTS = (0x200,0x500,0xF00)
NIBBLE_VALUES = (0, 0xA, 0xD)

class Test3XKKInstruction:

    @pytest.mark.parametrize(
        "vx,vx_and_kk_value,exec_start",
        product(
            range(0,16),
            NIBBLE_VALUES,
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
            vm,
            0x3000,
            load_point=exec_start,
            x=vx,
            kk=vx_and_kk_value
        )
        assert vm.program_counter == exec_start + 2

    @pytest.mark.parametrize(
        "vx,vx_value,kk_value,exec_start",
        product(
            range(0,16),
            NIBBLE_VALUES,
            map(lambda x: x + 1, NIBBLE_VALUES),
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
            vm,
            0x3000,
            load_point=exec_start,
            x=vx_value,
            kk=kk_value,
        )
        assert vm.program_counter == exec_start + 1


class Test4XKKInstruction:

    @pytest.mark.parametrize(
        "vx,vx_and_kk_value,exec_start",
        product(
            range(0,16),
            NIBBLE_VALUES,
            EXECUTION_STARTS
        )
    )
    def test_4xkk_does_not_skip_next_instruction_if_vx_eq_kk(
        self,
        vx: int,
        vx_and_kk_value: int,
        exec_start: int
    ):
        vm = VM(execution_start=exec_start)
        vm.v_registers[vx] = vx_and_kk_value
        load_and_execute_instruction(
            vm,
            0x4000,
            load_point=exec_start,
            x=vx,
            kk=vx_and_kk_value
        )
        assert vm.program_counter == exec_start + 1

    @pytest.mark.parametrize(
        "vx,vx_value,kk_value,exec_start",
        product(
            range(0,16),
            NIBBLE_VALUES,
            map(lambda x: x + 1, NIBBLE_VALUES),
            EXECUTION_STARTS
        )
    )
    def test_4xkk_skips_next_instruction_if_vx_neq_kk(
        self,
        vx: int,
        vx_value,
        kk_value,
        exec_start
    ):
        vm = VM(execution_start=exec_start)
        vm.v_registers[vx] = vx_value
        load_and_execute_instruction(
            vm,
            0x4000,
            load_point=exec_start,
            x=vx_value,
            kk=kk_value,
        )
        assert vm.program_counter == exec_start + 2


@pytest.mark.parametrize(
    "vx, value_to_set",
    product(
        range(0, 16),
        (5, 0xFF)
    )
)
def test_6xkk_sets_vx_to_kk(vx, value_to_set):
    vm = VM()
    load_and_execute_instruction(
        vm,
        0x6000,
        x=vx,
        kk=value_to_set
    )
    assert vm.v_registers[vx] == value_to_set


@pytest.mark.parametrize(
    "vx, initial_value, value_to_add",
    product(
        range(0, 16),
        (5, 0xFF),
        (0x1, 0x2, 0x3)
    )
)
def test_7xkk_adds_kk_to_vx(
    self,
    vx,
    initial_value,
    value_to_add
):
    vm = VM()
    vm.v_registers[vx] = initial_value
    load_and_execute_instruction(
        vm,
        0x7000,
        x=vx,
        kk=value_to_add
    )
    # yes, no VF flag is set according to multiple specs :(
    assert vm.v_registers[vx] == (initial_value + value_to_add) % 256
