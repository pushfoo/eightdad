"""

Test the breakpoint object used by the interpreter

"""
import pytest

from eightdad.core.vm import Breakpoint

class TestNameAssignment:
    def test_name_set_from_passed_name(self):
        bp_name = "start_program"
        b = Breakpoint(0x200, name=bp_name)
        assert b.name == bp_name

    def test_name_generated_when_no_arg_passed(self):
        b = Breakpoint(0x200)
        assert b.name == "breakpoint-0x200"

def test_assigning_name_after_creation_raises_exception():
    b = Breakpoint(0x200)
    with pytest.raises(AttributeError):
        b.name = "a"

def test_assigning_address_after_creation_raises_exception():
    b = Breakpoint(0x200)
    with pytest.raises(AttributeError):
        b.address = 0x202
