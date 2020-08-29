import pytest
from eightdad.core import Chip8VirtualMachine as VM
from tests.util import load_and_execute_instruction


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

