"""
Abstractions for legibly handling bytecode.

Instructions are classified into the following Pattern groups by which nibbles
they use to store information:

PATTERN_IIII
    00EE - CLR, turn all pixels off
    00E0 - return from subroutine. jump to last address on stack and pop stack

PATTERN_INNN
    1nnn - JP addr : set execution pointer to nnn
    2nnn - CALL addr : push current execution pointer to stack, and set
           execution pointer to nnn.
    Annn - Set the I register to nnn.
    Bnnn - JP v0, addr : Jump to location nnn + V0.

PATTERN_IXII
    Ex9E - Skip next instruction if key with the value of Vx is pressed.
    ExA1 - SKNP Vx - Skip next instruction if key with value of VX ISN'T
           pressed.
    Fx07 - LD Vx, DT - Set Vx = DT
    Fx0A - LD Vx, K  - Wait for a key press, store the value of the key in Vx.
    Fx15 - LD DT, Vx - Set DT = vX
    Fx18 - LD ST, Vx - Set ST = Vx.
    Fx1E - ADD I, Vx - Set I = I + Vx. The values of I and Vx are added, and
           the results are stored in I.
    Fx29 - LD F, Vx - Set I = location of sprite for digit Vx.
    Fx33 - LD B, Vx - Store BCD of Vx at I, I + 1, I + 2
    Fx55 - LD [I], Vx - Store V0 through Vx  to mem, starting at I
    Fx65 - LD Vx, [I] - Read mem into V0-VX, starting at I

PATTERN_IXKK
    3xkk - Skip next instruction if Vx = kk.
    4xkk - Skip next instruction if Vx != kk.
    6xkk - Set Vx = kk
    7xkk - Set Vx = Vx + kk.
    Cxkk - Set Vx = random byte AND kk.

PATTERN_IXYI
    5xy0 - Skip next instruction if Vx ==Vy
    8xy0 - Set Vx = Vy
    8xy1 - Set Vx = Vx OR Vy.
    8xy2 - Set Vx = Vx AND Vy.
    8xy3 - Set Vx = Vx XOR Vy.
    8xy4 - Set Vx = Vx + Vy, set VF = carry.
    8xy5 - Set Vx = Vx - Vy, set VF = NOT borrow.
    8xy6 - If the least-significant bit of Vx is 1, then VF is set to 1,
           otherwise 0. Then Vx is divided by 2.
    8xy7 - If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted
           from Vy, and the results stored in Vx.
    8xyE - If the most-significant bit of Vx is 1, then VF is set to 1,
           otherwise to 0. Then Vx is multiplied by 2.
    9xy0 - Skip next instruction if Vx != Vy.

PATTERN_IXYN
    Dxyn - DRW Vx, Vy, nibble - draw sprite to ram

"""
from typing import Iterable, Dict, ByteString, Any, Union

#
from eightdad.core.util import ValidateInt

USES_NNN = 0x1
USES_X = 0x2
USES_Y = 0x4
USES_N = 0x8
USES_KK = 0x10


USE_TO_LOC = {
    USES_NNN : "INNN",
    USES_X : "IXII",
    USES_Y : "IIYI",
    USES_N : "IIIN",
    USES_KK : "IIKK"
}


USE_TO_NAME = {
    USES_NNN : "NNN",
    USES_X : "X",
    USES_Y : "Y",
    USES_N : "N",
    USES_KK : "KK"
}


"""
I - stands for Instruction in this context. It means a slot that defines a
specific instruction.
"""
PATTERN_IIII = 0
PATTERN_INNN = USES_NNN
PATTERN_IXII = USES_X
PATTERN_IXYI = USES_X | USES_Y
PATTERN_IXKK = USES_X | USES_KK
PATTERN_IXYN = PATTERN_IXYI | USES_N

FIRST_NIBBLE_TO_PATTERN = {
    0x0: PATTERN_IIII
}

def build_pattern_registrar(d: Dict):
    """

    :param d: a dictionary-like object that patterns will be registered to
    :return: a function that
    """

    def registrar(pattern: int, first_nibbles: Iterable) -> None:
        """

        :param pattern: a combination of pattern flags describing variable storage
        :param first_nibbles: an iterable of first nibbles
        :return: a fu
        """
        for first_nibble in first_nibbles:
            d[first_nibble] = pattern

    return registrar


register_patterns_for_nibbles =\
    build_pattern_registrar(FIRST_NIBBLE_TO_PATTERN)

IXYI_INSTRUCTIONS = {0x5, 0x8, 0x9}
IXII_INSTRUCTIONS = {0xE, 0xF}

register_patterns_for_nibbles(PATTERN_IXII, IXII_INSTRUCTIONS)
register_patterns_for_nibbles(PATTERN_IXKK, (0x3, 0x4, 0x6, 0x7, 0xC))
register_patterns_for_nibbles(PATTERN_IXYI, IXYI_INSTRUCTIONS)
register_patterns_for_nibbles(PATTERN_IXYN, (0xD,))
register_patterns_for_nibbles(PATTERN_INNN, (0x1, 0x2, 0xA, 0xB))


class InvalidInstructionException(Exception):
    pass


IntOrByteString = Union[int, ByteString]


class Chip8Instruction:
    """

    Abstraction for reading & writing chip8 instructions

    The setters aren't likely to be very fast, and exist to make writing
    tests and the assembler cleaner.

    """
    PATTERN_MAP = FIRST_NIBBLE_TO_PATTERN

    def __init__(
            self,
            source: IntOrByteString = None,
            offset: int = 0
    ):

        self.pattern = 0
        self.type_nibble = 0

        self._hi_byte = 0
        self._lo_byte = 0

        self._x = None
        self._y = None
        self._nnn = None
        self._n = None

        if source is not None:
            if isinstance(source, int):
                self.decode(source.to_bytes(2, "big"), 0)
            else:
                self.decode(source, offset)

    def decode(self, source: ByteString, offset: int = 0):
        """
        Decode an instruction from the passed bytes-like object

        :param source: the bytes-like object to read from
        :param offset: how far into the code to start reading

        :return:
        """

        self._lo_byte = source[offset + 1]
        self._hi_byte = source[offset]

        self.type_nibble = (self._hi_byte & 0xF0) >> 4

        if self.type_nibble not in self.PATTERN_MAP:
            raise ValueError(f"Illegal instruction header {hex(self.type_nibble)}")

        pattern = self.PATTERN_MAP[self.type_nibble]
        self.pattern = pattern

        if pattern == PATTERN_INNN:
            self._nnn = self._lo_byte
            self._nnn |= (self._hi_byte & 0xF) << 8

        else:
            if pattern & USES_X:
                self._x = self._hi_byte & 0xF

            if not pattern & USES_KK:
                if pattern & USES_Y:
                    self._y = (self._lo_byte & 0xF0) >> 4

                if pattern & USES_N:
                    self._n = self._lo_byte & 0xF

    def access_check(self, usage: int) -> AttributeError:
        if not self.pattern & usage:
            raise AttributeError(
                f"Invalid access attempt on"
                f" {USE_TO_NAME[usage]} in {USE_TO_LOC[usage]}"
                f" on instruction on {hex(self.raw)[2:].upper()}")

    def pack_into(self, buffer: Any, offset: int = 0) -> None:
        """
        Packs the value into a buffer object.

        Relies on setters below to alter the values of the object.

        :param buffer: an object implementuing the buffer protocol
        :param offset: how far into the object to write
        :return:
        """
        buffer[offset] = self.hi_byte
        buffer[offset + 1] = self.lo_byte

    @property
    def hi_byte(self) -> int:
        return self._hi_byte

    @property
    def lo_byte(self) -> int:
        return self._lo_byte

    @property
    def nnn(self) -> int:
        self.access_check(USES_NNN)
        return self._nnn

    @nnn.setter
    @ValidateInt(0, 0xFFF)
    def nnn(self, nnn) -> None:
        self.access_check(USES_NNN)
        self._lo_byte = nnn & 0xFF
        self._hi_byte &= 0xF0
        self._hi_byte |= (nnn >> 8)

        self._nnn = nnn

    @property
    def x(self) -> int:
        self.access_check(USES_X)
        return self._x

    @x.setter
    @ValidateInt(0, 0xF)
    def x(self, value: int) -> None:

        self._hi_byte &= 0xF0
        self._hi_byte |= value

        self._x = value

    @property
    def y(self) -> int:
        self.access_check(USES_Y)

        return self._y

    @y.setter
    @ValidateInt(0, 0xF)
    def y(self, value: int) -> None:
        self.access_check(USES_Y)

        self._lo_byte &= 0x0F
        self._lo_byte |= value << 4

        self._y = value

    @property
    def kk(self) -> int:
        self.access_check(USES_KK)

        return self._lo_byte

    @kk.setter
    @ValidateInt(0, 0xFF)
    def kk(self, value) -> None:
        self._lo_byte = value

    @property
    def n(self) -> int:
        self.access_check(USES_N)
        return self._n

    @n.setter
    @ValidateInt(0, 0xF)
    def n(self, value: int) -> None:
        self.access_check(USES_N)

        self._lo_byte &= 0xF0
        self._lo_byte |= value

        self._n = value
