"""
Core VM-related functionality for executing programs

Timer and VM are implemented here.

"""
from typing import Tuple, List
from eightdad.core.bytecode import (
    PATTERN_IXII,
)
from eightdad.core.bytecode import Chip8Instruction
from eightdad.core.video import VideoRam, DEFAULT_DIGITS


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
            execution_start: int = 0x200,
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

        else:
            raise NotImplementedError("Instruction not yet supported")

        self.program_increment += 1

    def tick(self, dt: float) -> None:
        """
        Execute a single instruction at the allotted speed.

        The length is specified so the timers know how fast to decrement.

        :param dt: float, how long the instruction will take to execute.
        :return:
        """
        # clear temp vars keeping
        self.program_increment = 0

        # move timing forward
        if not dt:
            dt += self.tick_length

        self._delay_timer.tick(dt)
        self._sound_timer.tick(dt)

        # start interpretation
        self.instruction_parser.decode(self.memory, self.program_counter)

        if self.instruction_parser.pattern == PATTERN_IXII:
            self.handle_ixii()
        else:
            raise NotImplementedError("Instruction not yet supported")

        # advance by any amount we need to
        self.program_counter += self.program_increment

