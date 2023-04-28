import pytest
from eightdad.core import Chip8VirtualMachine


load_and_execute_instruction = pytest.helpers.load_and_execute_instruction


@pytest.mark.parametrize(
    "patterned_unrecognizeable_instruction",
    (
        0xFFFF,
        0xE1FF,
        0x5001,
    )
)
def test_valuerror_on_unhandled_instruction(
        patterned_unrecognizeable_instruction
):
    """Unhandled instructions raise ValueError"""
    vm = Chip8VirtualMachine()
    with pytest.raises(ValueError):
        load_and_execute_instruction(
            vm,
            patterned_unrecognizeable_instruction
        )
