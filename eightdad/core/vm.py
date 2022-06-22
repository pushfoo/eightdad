"""
Core VM-related functionality for executing programs

Timer and VM are implemented here.

"""
from collections import namedtuple
from copy import copy
from collections.abc import ByteString
from typing import Tuple, List, Iterable, Union, Dict
from random import randrange

from eightdad.core.bytecode import (
    PATTERN_IXII,
    PATTERN_INNN,
    PATTERN_IIII,
    PATTERN_IXKK,
    PATTERN_IXYI,
    PATTERN_IXYN
)
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


def upper_hex(src: Union[int, Iterable[int]]) -> str:
    """
    Return uppercase hex of an int or byte source

    :param src: an integer
    :return: the number as uppercase hex, minus
    """
    if isinstance(src, int):
        s = hex(src)[2:].upper()
        if len(s) < 2:
            return "0" + s
        return s

    return "".join((upper_hex(i) for i in src))


VMState = namedtuple(
    'VMState', [
        'program_counter',
        'next_instruction',
        'v_registers',
        'timers',
        'stack',
        'keys'
    ],
)


def report_state(state: VMState):
    pc = state.program_counter
    next_instr = state.next_instruction
    print(
        f"== state ==\n"
        f"PC       : 0x{upper_hex(next_instr)} @ 0x{upper_hex(pc)}\n"
        f"stack    : {state.stack}\n"
        f"registers: {state.v_registers}\n"
        f"keys     : {state.keys}\n"
    )


class Chip8VirtualMachine:

    def load_to_memory(self, data: ByteString, location: int) -> None:
        """
        Load given data to a specific location in memory.

        Data must be a ByteString or support the buffer protocol.

        Raises IndexError if data is too long to be inserted at the passed
        location, ie would extend past the end of memory.

        :param data: a bytestring that supports buffer protocol
        :param location: where in memory to load to
        :return:
        """
        if location < 0:
            raise IndexError("Location must be positive")

        end = location + len(data)
        if end > len(self.memory):
            raise IndexError("Passed data extends past the end of memory")

        # if it doesn't implement buffer protocol, error
        try:
            view = memoryview(data)
        except Exception as e:
            raise TypeError(
                "data must be a ByteString or otherwise support the "
                "buffer protocol."
            ) from e

        self.memory[location:end] = view

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
        for digit_data in source:
            self.load_to_memory(digit_data, current_start)
            current_start += self.digit_length

    def __init__(
            self,
            display_size: Tuple[int, int] = (64, 32),
            display_wrap: bool = False,
            memory_size: int = 4096,
            execution_start: int = DEFAULT_EXECUTION_START,
            digit_start: int = 0x0,
            ticks_per_frame: int = 20,
            frames_per_second: int = 30,
            video_ram_type: type = VideoRam
    ):
        """

        Build a Chip-8 VM.

        The video_ram_type is intended for passing subclasses that keep
        track of tiling or other platform-specific display features to
        improve drawing performance.

        Avoiding redraw of unchanged pixels is the major intended
        usecase for this feature. For example, a curses frontend
        using braille characters as pixel blocks is one possibility.

        :param display_size: A pair of values for the screen type.
        :param display_wrap: whether drawing wraps
        :param memory_size: how big RAM should be
        :param execution_start: where to start execution
        :param digit_start: where digits should start in ram
        :param ticks_per_frame: how many instructions execute per frame
        :param frames_per_second: how many frames/sec execute
        :param video_ram_type: a VideoRam class or subclass
        """
        # initialize display-related functionality
        self.memory = bytearray(memory_size)
        width, height = display_size

        if not isinstance(video_ram_type, type) \
            or not issubclass(video_ram_type, VideoRam):

            raise TypeError(
                f"VideoRam subclass expected,"
                f" not a {type(video_ram_type)}")

        self.video_ram = video_ram_type(width, height, display_wrap)

        self.digits_memory_location, self.digit_length = 0, 0
        self.load_digits(DEFAULT_DIGITS, digit_start)

        # set up execution-related state

        self.program_counter = execution_start
        self.program_increment = 0  # how much PC will be incremented by

        self.i_register = 0
        self.v_registers = bytearray(16)
        self.call_stack = []

        # key-related variables
        self.waiting_for_key = False
        self.waiting_register = None
        self._keystates = [False] * 16  # Whether each key is down
        
        self._delay_timer = Timer()
        self._sound_timer = Timer()

        self.ticks_per_frame = ticks_per_frame
        self.frames_per_second = frames_per_second
        self.ticks_per_second = ticks_per_frame * frames_per_second
        self.tick_length = 1.0 / self.ticks_per_second

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

    def press(self, key: int) -> None:
        self._keystates[key] = True
   
    def pressed(self, key: int) -> bool:
        return self._keystates[key]

    def release(self, key: int) -> None:
        self._keystates[key] = False

    def dump_state(self) -> VMState:
        """
        Return a named tuple representing VM state.

        It is the responsibility of the frontend implementation to
        render this object into a form readable to the user.

        :return: named tuple of registers, keys, and stack
        """
        pc = self.program_counter
        mem = self.memory

        # get the instruction as big endian int, skip struct
        next_instruction = mem[pc] << 8
        next_instruction += mem[pc + 1]

        return VMState(
            pc,
            next_instruction,
            copy(self.v_registers),
            {'delay_timer': self.delay_timer, 'sound_timer': self.sound_timer},
            copy(self.call_stack),
            copy(self._keystates)
        )

    def skip_next_instruction(self):
        """
        Sugar to skip instructions.
        """
        self.program_increment += INSTRUCTION_LENGTH

    def handle_ixii(self):
        """
        Execute F and E type nibble instructions.

        This includes:
            - keypress handling
            - setting timers
            - some manipulation of I register (sprites, addition)
            - bulk register save/load to/from location I in memory
        """
        type_nibble = self.instruction_parser.type_nibble
        lo_byte = self.instruction_parser.lo_byte
        x = self.instruction_parser.x
        
        if type_nibble == 0xF:
            
            if lo_byte == 0x07:
                self.v_registers[x] = self._delay_timer.value

            elif lo_byte == 0x0A:  # Enter wait state until the VM gets a keypress
                self.waiting_for_key = True
                self.waiting_register = x

            # Timers
            elif lo_byte == 0x15:
                self._delay_timer.value = self.v_registers[x]
            elif lo_byte == 0x18:
                self._sound_timer.value = self.v_registers[x]
            
            # I manipulation
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

            elif lo_byte == 0x65:  # Load register from memory starting at I
                i = self.i_register

                for register in range(0, x + 1):
                    self.v_registers[register] = self.memory[i + register]

            else:
                self.instruction_unhandled = True
        elif type_nibble == 0xE:
            # one of the keypress skip instructions

            # get the key for value in VX
            key_pressed = self._keystates[self.v_registers[x]]
            
            if lo_byte == 0xA1:
                if not key_pressed:
                    self.skip_next_instruction()

            elif lo_byte == 0x9E:
                # skip next instruction if key in register X is pressed
                if key_pressed:
                    self.skip_next_instruction()
            else:
                self.instruction_unhandled = True
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
                self.skip_next_instruction()

        elif type_nibble == 0x4:
            if self.v_registers[x] != kk:
                self.skip_next_instruction()

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

        if lo_nibble == 0:  # register assignment
            self.v_registers[x] = self.v_registers[y]

        elif lo_nibble == 0x1:
            self.v_registers[x] = self.v_registers[x] | self.v_registers[y]

        elif lo_nibble == 0x2:
            self.v_registers[x] = self.v_registers[x] & self.v_registers[y]

        elif lo_nibble == 0x3:
            self.v_registers[x] = self.v_registers[x] ^ self.v_registers[y]

        elif lo_nibble == 0x4:
            unclamped_sum = self.v_registers[x] + self.v_registers[y]

            # store the result, masking anything higher than 256
            # to imitate rollover. may be faster than modulo.
            self.v_registers[x] = unclamped_sum & 0xFF
            # set vf to 1 if the operation overflowed
            self.v_registers[0xF] = int(unclamped_sum > 255)

        elif lo_nibble == 0x5:
            unclamped_diff = self.v_registers[x] - self.v_registers[y]

            # store the difference clamped to 0 as the minimum
            self.v_registers[x] = max(unclamped_diff, 0)

            # set VF to 1 if a borrow didn't occur, otherwise 0
            self.v_registers[0xF] = int(unclamped_diff >= 0)

        elif lo_nibble == 0x6:  # vx = vy >> 1, vf = least bit of vy

            # we need to store the least bit ahead of time because
            # x could == y and both could be 0xF.
            y_val = self.v_registers[y]

            self.v_registers[x] = y_val >> 1
            self.v_registers[0xF] = y_val & 1

        elif lo_nibble == 0x7:
            unclamped_diff = self.v_registers[y] - self.v_registers[x]

            # store the difference clamped to 0 as the minimum
            self.v_registers[x] = max(unclamped_diff, 0)

            # set VF to 1 if a borrow didn't occur, otherwise 0
            self.v_registers[0xF] = int(unclamped_diff >= 0)

        elif lo_nibble == 0xE:  # vx = vy << 1, vf = greatest bit of vy

            # we need to store the least bit ahead of time because
            # x could == y and both could be 0xF.
            y_val = self.v_registers[y]

            self.v_registers[x] = (y_val << 1) & 0xFF
            self.v_registers[0xF] = (y_val >> 7) & 1


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

    def execute_instruction(self) -> None:
        """
        Execute an instruction if needed.

        This differs from tick as tick steps timers, then decides whether
        to execute instruction based on waiting state.

        """
        # reset bookeeping to defaults
        self.program_increment = INSTRUCTION_LENGTH
        self.instruction_unhandled = False


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
            # don't need hi byte, all base chip 8 IIII
            # instructions have 00 hi byte
            lo_byte = self.instruction_parser.lo_byte

            if lo_byte == 0xEE:
                self.stack_return()

            elif lo_byte == 0xE0:
                self.video_ram.clear_screen()

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
                        self.skip_next_instruction()

                elif type_nibble == 0x9 and end_nibble == 0:
                    if self.v_registers[x] != self.v_registers[y]:
                        self.skip_next_instruction()

                else:
                    self.instruction_unhandled = True

        elif pattern == PATTERN_IXYN:

            x = self.instruction_parser.x
            y = self.instruction_parser.y
            n = self.instruction_parser.n

            self.v_registers[0xF] = int(
                self.video_ram.draw_sprite(
                    self.v_registers[x],
                    self.v_registers[y],
                    self.memory,
                    num_bytes=n,
                    offset=self.i_register
                )
            )

        else:
            self.instruction_unhandled = True

        if self.instruction_unhandled:
            raise ValueError(
                f"Unrecognized instruction "
                f"{self.dump_current_pc_instruction_raw()}"
            )

        # advance by any amount we need to
        self.program_counter += self.program_increment

    def tick(self, dt: float = None) -> None:
        """
        Execute a single instruction at the allotted speed.

        The length is specified so the timers know how fast to decrement.

        :param dt: float, how long the instruction will take to execute.
        :return:
        """

        # Advance timers, happens even when waiting for keypress.
        dt = dt or self.tick_length
        
        self._delay_timer.tick(dt)
        self._sound_timer.tick(dt)
        
#        self.waiting_for_key = False
#        self.waiting_register = None
#        self._keystates = [False] * 16  # Whether each key is down

        # this is crude and only registers the first keypress
        # numerically. in the future an event queueing method may be
        # better for this. YAGNI applies for now though.
        if self.waiting_for_key:
            keys = self._keystates
            if self.waiting_register != None:
                pressed_indices = [i for i, v in enumerate(keys) if v]
                if pressed_indices:
                    self.v_registers[self.waiting_register] = pressed_indices[0]
                    self.waiting_for_key = False

        # check again because we might have had a keypress happen
        if not self.waiting_for_key:
           self.execute_instruction()

    def dump_current_pc_instruction_raw(self) -> str:
        """
        Debug helper that returns raw instruction + location

        :return: raw instruction + address
        """
        pc = self.program_counter
        return f"{upper_hex(self.memory[pc: pc + 2])}" \
               f" @ 0x{upper_hex(pc)}"



