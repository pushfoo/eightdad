import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction as load_and_execute


class TestStateSet:

    def test_vm_created_with_zero_pressed(self):
        vm = VM()
        for key in range(0, 16):
            assert not vm.pressed(key)

    def test_pressing_keys_sets_state(self):
        vm = VM()
        for key in range(0, 16):
            vm.press(key)
            assert vm.pressed(key)

    def test_releasing_keys_works(self):
        vm = VM()

        for key in range(0, 16):
            vm.press(key)

        for key in range(0,16):
            vm.release(key)
            assert not vm.pressed(key)

@pytest.mark.parametrize("x,key", list(product(range(0,1), range(0,1))))
class TestFX0APauseTillAnyKeypress:
    """
    Tests for waiting for a key press
    """

    def test_fx0a_pauses_execution(self, x: int, key: int):
        """Ticking the VM after fx0a is executed does not advance state"""
        vm = VM()
        start_position = vm.program_counter
        load_and_execute(vm, 0xF00A,x=x)
        vm.memory[514] = 0xA0
        vm.tick(1/20.0)
        assert vm.program_counter == start_position + INSTRUCTION_LENGTH

    def test_fx0a_resumes_after_keypress(self, x: int, key: int):
        """Execution is resumed after fx0a after a key is pressed"""
        vm = VM()
        start_position = vm.program_counter
        vm.memory[514] = 0xA0
        load_and_execute(vm, 0xF00A, x=x)
        vm.press(key)
        vm.tick(1/20.0)
        assert vm.program_counter == start_position + (INSTRUCTION_LENGTH * 2)

    def test_fx0a_sets_register_targeted(self, x: int, key: int):
        """A keypress while waiting sets the register to the requested state"""
        vm = VM()
        start_position = vm.program_counter
        load_and_execute(vm, 0xF00A, x=x)
        # effectively a no-op, store "load 0 to I" at next instruction to be executed
        vm.memory[514] = 0xA0
        vm.press(key)
        vm.tick(1/20.0)
        assert vm.v_registers[x] == key



