import pytest
from itertools import product
from typing import Tuple, Any, Iterable, Dict, Generator

from eightdad.core import Chip8VirtualMachine
from eightdad.core.bytecode import Chip8Instruction as Instruction
from eightdad.core.vm import DEFAULT_EXECUTION_START, INSTRUCTION_LENGTH


@pytest.helpers.register
def dict_to_argtuples(
    src: Dict[Tuple,Iterable[Any]]
) -> Generator[Tuple, None, None]:
    """
    Turn structured parameter dicts into legible test case parameters.

    The generator yields one set of testcase parameters per tuple. This
    ensures the user can tell what specific data caused a test case to
    fail while still allowing compact expression of test parameters.
    """
    out_raw = []

    for prefix, suffixes in src.items():
        out_raw.extend(product((prefix,), suffixes))

    return (prefix + (suffix, ) for prefix, suffix  in out_raw)


@pytest.helpers.register
def load_instruction(
    vm: Chip8VirtualMachine,
    template: int,
    load_point: int = DEFAULT_EXECUTION_START,
    **kwargs
) -> None:
    """
    Load an instruction with specified args into memory of a VM.

    :param vm:
    :param template: a finished instruction or template for kwargs
    :param load_point: where to load it
    :param kwargs: variables on the instruction
    :return:
    """

    i = Instruction(template)
    for arg, value in kwargs.items():
        setattr(i, arg, value)

    i.pack_into(vm.memory, offset=load_point)


@pytest.helpers.register
def load_multiple(
    vm: Chip8VirtualMachine,
    *instructions,
    load_point: int = DEFAULT_EXECUTION_START
) -> None:
    """
    Attempts to template and load multiple instructions to memory.

    the templates_and_args parameters should be in one of the 
    following forms:
        ( template_int, dict_of_kwargs )
        template_int

    :param vm: the chip8 VM to load to
    :param templates_and_args: iterables with at least a template
    :param load_point: a position in memory to start loading to
    """
    current_location = load_point
    for instruction in instructions:
        if isinstance(instruction, int):
            load_instruction(vm, instruction, load_point=current_location)

        else:
            template, kwargs = instruction
            load_instruction(
                vm,
                template,
                **kwargs,
                load_point=current_location
            )
        current_location += INSTRUCTION_LENGTH


@pytest.helpers.register
def load_and_execute_instruction(
    vm: Chip8VirtualMachine,
    template: int,
    load_point:int= DEFAULT_EXECUTION_START,
    **kwargs
) -> None:
    """


    :param vm: the chip8 vm to execute on
    :param template: instruction template
    :param load_point: where we will load the instruction
    :param kwargs: valid properties on a bytecode instruction
    :return:
    """
    load_instruction(
        vm,
        template,
        load_point=load_point,
        **kwargs
    )
    vm.tick(1/200.0)


@pytest.helpers.register
def registers_untouched(
        vm: Chip8VirtualMachine,
        registers: Iterable[int]
) -> bool:
    """
    Return true if the specified registers are equal to zero

    :param vm:
    :param registers:
    :return:
    """
    return all(map(lambda x: vm.v_registers[x] == 0, registers))


@pytest.helpers.register
def other_registers_untouched(
        vm: Chip8VirtualMachine,
        touched_registers: Iterable[int],
        num_registers: int = 16
) -> bool:
    """
    Return true if all registers other than the passed one are zero.

    Converts the source iterable to a set, so repetition of register
    args is ok.

    :param vm: the VM to check
    :param touched_registers: registers not expected to be untouched
    :param num_registers: how many registers the machine has
    :return:
    """
    return registers_untouched(
        vm,
        set(touched_registers).difference(range(0, num_registers))
    )


@pytest.helpers.register
def fullbits_generator(max_num_bits: int):
    """
    Generate a range of values from 0 to 2 ** max_num_bits

    :param num_bits: the maximum number of bits to generate
    :return:
    """

    yield 0

    bits = 1
    for i in range(0, max_num_bits):
        yield bits
        bits <<= 1
        bits |= 1
