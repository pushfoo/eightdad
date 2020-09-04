import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH
from tests.util import load_and_execute_instruction as load_and_execute
from tests.util import load_multiple

# should find a way to make this a configurable project-wide fixture
KEYS_AND_REGISTERS = list(product(range(0,1), range(0,1)))


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

@pytest.mark.parametrize("x,key", KEYS_AND_REGISTERS)
class TestFX0APauseTillAnyKeypress:
    """
    Tests for waiting for a key press
    """
    def setup_vm(self, x: int) -> VM:
        """
        Helper to create a VM with appropriate instructions loaded.

        This might be better as a fixture once I understand them better.
        """
        vm = VM()
        load_multiple(vm,
            (0xF00A, {'x':x}),
            # no-op, store "load 0 to I" as next to be executed
            0xA000
        )
        return vm
        
    def test_fx0a_pauses_execution(self, x: int, key: int):
        """Ticking the VM after fx0a is executed does not advance state"""
        vm = self.setup_vm(x)
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + INSTRUCTION_LENGTH

    def test_fx0a_resumes_after_keypress(self, x: int, key: int):
        """Execution is resumed after fx0a after a key is pressed"""
        vm = self.setup_vm(x)
        vm.press(key)
        # tick twice to make sure we execute both instructions
        vm.tick(1/20.0)
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + (INSTRUCTION_LENGTH * 2)

    def test_fx0a_sets_register_targeted(self, x: int, key: int):
        """A keypress while waiting sets the register to the requested state"""
        vm = self.setup_vm(x)
        vm.press(key)
        vm.tick(1/20.0)
        assert vm.v_registers[x] == key

@pytest.mark.parametrize("x,key", KEYS_AND_REGISTERS) 
class TestEX9ESkipIfKeyInXPressed:
    
    def setup_vm(self, x: int, key: int) -> VM:
        """
        Helper function to set up the VM and template instructions
        """
        vm = VM()
        load_multiple(
            vm,
            (0xE09E, { 'x' : x } ),
            # set the I register. This command can't touch that I, and
            # I is set to zero on VM initialization. Therefore, it is
            # safe to use I as a test condition for ex9e.
            0xA0FF
        )
        vm.v_registers[x] = key
        return vm

    def test_ex9e_skips_if_key_pressed(self, x: int, key: int):
        """EX9E Skips the next instruction if key in VX is pressed"""
        vm = self.setup_vm(x, key)
        vm.i_register = 1
        vm.press(key)
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + (2 * INSTRUCTION_LENGTH)
        assert vm.i_register == 1

    def test_ex9e_does_not_skip_if_key_up(self, x: int, key: int):
        """EX9E doesn't skip next instruction if key is up"""
        vm = self.setup_vm(x, key)
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + INSTRUCTION_LENGTH

@pytest.mark.parametrize("x,key", KEYS_AND_REGISTERS) 
class TestEXA1SkipIfKeyInXNotPressed:
    
    def setup_vm(self, x: int, key: int) -> VM:
        """
        Helper function to set up the VM and template instructions
        """
        vm = VM()
        load_multiple(
            vm,
            (0xE0A1, { 'x' : x } ),
            # set the I register. This command can't touch that I, and
            # I is set to zero on VM initialization. Therefore, it is
            # safe to use I as a test condition for ex9e.
            0xA0FF
        )
        vm.v_registers[x] = key
        return vm

    def test_exa1_skips_next_instruction_if_key_in_vx_is_up(self, x: int, key: int):
        """EXA1 Skips next instruction if the key in VX is up"""
        vm = self.setup_vm(x, key)
        vm.i_register = 1
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + (2 * INSTRUCTION_LENGTH)
        assert vm.i_register == 1

    def test_exa1_executes_next_instruction_if_key_in_vx_down(self, x: int, key: int):
        """EXA1 allows next instruction to execute if the key in VX is down"""
        vm = self.setup_vm(x, key)
        vm.press(key)
        vm.tick(1/20.0)
        assert vm.program_counter == DEFAULT_EXECUTION_START + INSTRUCTION_LENGTH

