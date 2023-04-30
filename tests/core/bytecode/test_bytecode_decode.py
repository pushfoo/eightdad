import pytest
from eightdad.core.bytecode import Chip8Instruction as Instruction


INSTRUCTION_FIELDS = ['type_nibble', 'nnn', 'x', 'nn', 'y', 'kk',  'n']

INSTRUCTION_AND_FIELDS = [
    (
            0x00EE,
            {'type_nibble': 0}
    ),
    (
            0x1ABC,
            {'type_nibble': 1, 'nnn': 0xABC}
    ),
    (
            0x2DEF,
            {'type_nibble': 2, 'nnn': 0xDEF}
    ),
    (
            0x3F05,
            {'type_nibble': 3, 'x': 0xF, 'kk': 0x05}
    ),
    (
            0x4A19,
            {'type_nibble': 4, 'x': 0xA, 'kk': 0x19}
    ),
    (
            0x51A0,
            {'type_nibble': 5, 'x': 0x1, 'y': 0xA}
    ),
    (
            0x6AF2,
            {'type_nibble': 6, 'x': 0xA, 'kk': 0xF2}
    ),
    (
            0x7824,
            {'type_nibble': 7, 'x': 0x8, 'kk': 0x24}
    ),
    (
            0x8120,
            {'type_nibble': 8, 'x': 1, 'y': 2}
    ),
    (
            0x9870,
            {'type_nibble': 9, 'x': 8, 'y': 7}
    ),
    (
            0xADEF,
            {'type_nibble': 10, 'nnn': 0xDEF}
    ),
    (
            0xB789,
            {'type_nibble': 0xB, 'nnn': 0x789}
    ),
    (
            0xC678,
            {'type_nibble': 0xC, 'x': 6, 'kk': 0x78}
    ),
    (
            0xD4E7,
            {'type_nibble': 0xD, 'x': 4, 'y': 0xE, 'n': 7}
    ),
    (
            0xEF9E,
            {'type_nibble': 0xE, 'x': 0xF}
    ),
    (
            0xFB00,
            {'type_nibble': 0xF, 'x': 0xB}
    )
]


class TestReadAccess:
    @pytest.mark.parametrize(
        "raw_instruction,components",
        INSTRUCTION_AND_FIELDS
    )
    def test_instructions_reading_goodvars(self, raw_instruction, components):
        """
        Test whether decode of instructions sets attrs correctly

        :param raw_instruction: the raw instruction value
        :param components: what the components should be set to
        :return:
        """
        instruction = Instruction()

        instruction.decode(raw_instruction.to_bytes(2, byteorder="big"))

        for varname, expected_value in components.items():
            assert getattr(instruction, varname) == expected_value

    @pytest.mark.parametrize(
        "raw_instruction,good_fields",
        INSTRUCTION_AND_FIELDS
    )
    def test_access_exceptions_on_patterns(self, raw_instruction, good_fields):
        """Exceptions are raised on access attempts for dissallowed fields"""
        instruction = Instruction()

        instruction.decode(raw_instruction.to_bytes(2, byteorder="big"))

        for field in INSTRUCTION_FIELDS:
            if field not in good_fields:
                with pytest.raises(AttributeError):
                    getattr(instruction, field)
