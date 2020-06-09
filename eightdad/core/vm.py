"""
Core VM-related functionality for executing programs

Timer and VM are implemented here.

"""
from typing import Tuple, List
from random import randrange
from eightdad.core.bytecode import (
    PATTERN_IXII,
    PATTERN_INNN,
    PATTERN_IIII,
    PATTERN_IXKK,
    PATTERN_IXYI)
from eightdad.core.bytecode import Chip8Instruction
from eightdad.core.video import VideoRam, DEFAULT_DIGITS

DEFAULT_EXECUTION_START = 0x200

INSTRUCTION_LENGTH = 2 # 2 bytes, 16 bits


class Timer:
    """
    Simple timer that decrements at 60hz, per the spec
    """

    def __init__(self, hz_decrement_rate: float = 60.0):
        self.decrement_threshold = 1.0 / hz_decrement_rate
        self.elapsed = 0.0
        self.value = 0

    def tick(self, dt: float) -> None:
        """
        Advance the timer by dt seconds.

        Assumes only small values of dt will be sent, doesn't apply multiple
        decrements per dt. Values of dt larger than decrement threshold may
        cause issues.

        :param dt: how large a time step to apply
        :return:
        """
        self.elapsed += dt

        if self.elapsed >= self.decrement_threshold:
            self.elapsed -= self.decrement_threshold

            if self.value > 0:
                self.value -= 1


class Chip8VirtualMachine:

    def load_digits(self, source: List[bytes], location: int) -> None:
        """
        Load hex digit data into a location memory.

        The largest digit size is used as the digit length.

        :param source: the list of bytes objects to load from.
        :param location: where in memory to load the data
        :return: None
        """
        self.digits_memory_location = location
        self.digit_length = max(map(len, source))

        current_start = location
        current_end = self.digit_length
        for digit_data in source:

            self.memory[current_start:current_end] = digit_data
            current_start += self.digit_length
            current_end += self.digit_length

    def __init__(
            self,
            display_size: Tuple[int, int] = (64, 32),
            display_wrap: bool = False,
            memory_size: int = 4096,
            execution_start: int = DEFAULT_EXECUTION_START,
            digit_start: int = 0x0,
            ticks_per_second: int = 200
    ):
        # initialize display-related functionality
        self.memory = bytearray(memory_size)
        width, height = display_size
        self.video_ram = VideoRam(width, height, display_wrap)

        self.digits_memory_location, self.digit_length = 0, 0
        self.load_digits(DEFAULT_DIGITS, digit_start)

        # set up execution-related state

        self.program_counter = execution_start
        self.program_increment = 0  # how much PC will be incremented by

        self.i_register = 0
        self.v_registers = bytearray(16)
        self.call_stack = []
        self.waiting_for_keypress = False

        self._delay_timer = Timer()
        self._sound_timer = Timer()

        self.ticks_per_second = ticks_per_second
        self.tick_length = 1.0 / ticks_per_second

        self.instruction_parser = Chip8Instruction()
        self.instruction_unhandled = False

    @property
    def delay_timer(self):
        return self._delay_timer.value

    @delay_timer.setter
    def delay_timer(self, value):
        self._delay_timer.value = value

    @property
    def sound_timer(self):
        return self._sound_timer.value

    @sound_timer.setter
    def sound_timer(self, value):
        self._sound_timer.value = value

    def handle_ixii(self):
        """
        Execute timer-related instructions
        """
        lo_byte = self.instruction_parser.lo_byte
        x = self.instruction_parser.x

        if lo_byte == 0x07:
            self.v_registers[x] = self._delay_timer.value
        elif lo_byte == 0x15:
            self._delay_timer.value = self.v_registers[x]
        elif lo_byte == 0x18:
            self._sound_timer.value = self.v_registers[x]
        elif lo_byte == 0x1E:
            self.i_register += self.v_registers[x]
        elif lo_byte == 0x29:  # Fx29, I = Address of digit for value in Vx
            digit = self.v_registers[x]
            self.i_register = self.digits_memory_location +\
                              (digit * self.digit_length)

        # Store BCD of Vx at I, I+1, I+2
        elif lo_byte == 0x33:
            reg_value = self.v_registers[x]

            ones = reg_value % 10
            tens = ((reg_value - ones) % 100) // 10
            hundreds = reg_value // 100

            self.memory[self.i_register] = hundreds
            self.memory[self.i_register + 1] = tens
            self.memory[self.i_register + 2] = ones

        elif lo_byte == 0x55:  # save registers to memory starting at I
            i = self.i_register

            for register in range(0, x + 1):
                self.memory[i + register] = self.v_registers[register]

        elif lo_byte == 0x65:
            i = self.i_register

            for register in range(0, x + 1):
                self.v_registers[register] = self.memory[i + register]

        else:
            self.instruction_unhandled = True

    def _handle_innn(self) -> None:
        """
        Execute address-related instructions

        This includes such jumps, calls, and setting the I register.

        :return: None
        """
        nnn = self.instruction_parser.nnn
        type_nibble = self.instruction_parser.type_nibble

        if type_nibble == 0xA:  # set I to nnn
            self.i_register = nnn
            self.program_increment += INSTRUCTION_LENGTH

        elif type_nibble == 0x2:  # call instruction
            self.program_increment = 0
            self.stack_call(nnn)


        elif type_nibble == 0x1 or type_nibble == 0xB:  # jump instruction
            self.program_increment = 0
            self.program_counter = nnn
            if type_nibble == 0xB:  # includes a shift
                self.program_counter += self.v_registers[0]

        else:
            self.instruction_unhandled = True

    def handle_ixkk(self) -> None:
        x = self.instruction_parser.x
        kk = self.instruction_parser.kk
        type_nibble = self.instruction_parser.type_nibble

        if type_nibble == 0x3:
            if self.v_registers[x] == kk:
                self.program_increment += INSTRUCTION_LENGTH

        elif type_nibble == 0x4:
            if self.v_registers[x] != kk:
                self.program_increment += INSTRUCTION_LENGTH

        elif type_nibble == 0x6:
            self.v_registers[x] = kk

        elif type_nibble == 0x7:
            self.v_registers[x] = (self.v_registers[x] + kk) % 0x100

        elif type_nibble == 0xC:
            self.v_registers[x] = randrange(0, 0xFF) & kk

        else:
            self.instruction_unhandled = True

    def _handle_math(self):
        x = self.instruction_parser.x
        y = self.instruction_parser.y
        lo_nibble = self.instruction_parser.lo_byte & 0xF

        if lo_nibble == 0x1:
            self.v_registers[x] = self.v_registers[x] | self.v_registers[y]

        elif lo_nibble == 0x2:
            self.v_registers[x] = self.v_registers[x] & self.v_registers[y]

        elif lo_nibble == 0x3:
            self.v_registers[x] = self.v_registers[x] ^ self.v_registers[y]

        else:
            self.instruction_unhandled = True


    def stack_return(self) -> None:
        """
        Return to the last location on the stack

        :return:
        """
        self.program_counter = self.call_stack.pop()

    def stack_call(self, location: int) -> None:
        """
        Jump to the passed location and put the current one onto the stack

        :param location: where to jump to
        :return:
        """
        self.call_stack.append(self.program_counter)
        self.program_counter = location

    @property
    def stack_size(self) -> int:
        """
        Abstract the call stack size

        :return: current size of the call stack
        """
        return len(self.call_stack)

    @property
    def stack_top(self) -> int:
        """
        Abstraction for the top of the stack

        :return: what the top of the call stack is below
        """
        return self.call_stack[-1]


    def tick(self, dt: float) -> None:
        """
        Execute a single instruction at the allotted speed.

        The length is specified so the timers know how fast to decrement.

        :param dt: float, how long the instruction will take to execute.
        :return:
        """

        # reset bookeeping to defaults
        self.program_increment = INSTRUCTION_LENGTH
        self.instruction_unhandled = False

        # move timing forward
        if not dt:
            dt += self.tick_length

        self._delay_timer.tick(dt)
        self._sound_timer.tick(dt)

        # start interpretation
        self.instruction_parser.decode(self.memory, self.program_counter)

        pattern = self.instruction_parser.pattern

        if pattern == PATTERN_IXII:
            self.handle_ixii()

        elif pattern == PATTERN_INNN:
            self._handle_innn()

        elif pattern == PATTERN_IXKK:
            self.handle_ixkk()

        elif pattern == PATTERN_IIII:
            if self.instruction_parser.lo_byte == 0xEE:
                self.stack_return()
                self.program_increment = 0

            else:
                self.instruction_unhandled = True

        elif pattern == PATTERN_IXYI:

            type_nibble = self.instruction_parser.type_nibble

            if type_nibble == 0x8:
                self._handle_math()

            else:
                x = self.instruction_parser.x
                y = self.instruction_parser.y
                end_nibble = self.instruction_parser.lo_byte & 0xF

                if type_nibble == 0x5 and end_nibble == 0:
                    if self.v_registers[x] == self.v_registers[y]:
                        self.program_increment += INSTRUCTION_LENGTH

                elif type_nibble == 0x9 and end_nibble == 0:
                    if self.v_registers[x] != self.v_registers[y]:
                        self.program_increment += INSTRUCTION_LENGTH

                else:
                    self.instruction_unhandled = True

        else:
            self.instruction_unhandled = True

        if self.instruction_unhandled:
            raise ValueError(
                f"Unrecognized instruction "
                f"{hex(self.memory[self.program_counter])}"
                f"{hex(self.memory[self.program_counter+1])[2:]} "
                f"at address {hex(self.program_counter)}"
            )

        # advance by any amount we need to
        self.program_counter += self.program_increment


vm = Chip8VirtualMachine()

vm.v_registers[0xF] = 0b10101010
vm.v_registers[1] = 0b01010101

vm.memory[0x200] = 0x8F
vm.memory[0x201] = 0x11
vm.tick(1 / 200.0)