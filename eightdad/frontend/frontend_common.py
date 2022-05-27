import sys
import argparse
from abc import ABC, abstractmethod
from typing import Union


from eightdad.core import Chip8VirtualMachine
from eightdad.frontend.keymap import build_hexkey_mapping
from eightdad.frontend.util import clean_path, load_rom_to_vm


# set up the common arg parser to use
BASE_ARG_PARSER = argparse.ArgumentParser(
    description='EightDAD Chip-8 Emulator')
BASE_ARG_PARSER.add_argument(
    '-r', '--rom-file', type=str, required=True, help="Which ROM file to run")
BASE_ARG_PARSER.add_argument(
    '-P', '--start-paused', help="Start the VM paused", action='store_true')
BASE_ARG_PARSER.set_defaults(start_paused=False)


def build_window_title(paused: bool, current_file) -> str:
    """
    Returns a neatly formatted window title.

    :param bool paused: whether the VM is currently paused
    :param current_file: the name of the file to display
    :return str: a neatly formatted window title
    """
    return f"EightDAD {'(PAUSED)' if paused else '-'} {current_file}"


def exit_with_error(msg: str, error_code: int = 1) -> None:
    """
    Display an error message and exit loudly with error code

    :param msg: message to display
    :param error_code: return error code to give to the shell
    :return:
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    exit(error_code)


class Frontend(ABC):
    """
    Common base to wrap other frontend systems.

    Inherit from it to set up your own frontends.
    """

    def __init__(self, arg_parser=BASE_ARG_PARSER):

        self.launch_args = vars(arg_parser.parse_args())

        self._rom_path = None
        self._vm: Union[Chip8VirtualMachine, None] = None
        self._shown_filename = None
        self.load_vm()

        self._vm_display = self._vm.video_ram

        self.breakpoints = None
        self._tick_rate = 1.0 / 30
        self._key_mapping = build_hexkey_mapping()

        self.load_vm()

    @property
    @abstractmethod
    def paused(self) -> bool:
        raise NotImplementedError()

    @paused.setter
    @abstractmethod
    def paused(self, pause: bool):

        raise NotImplementedError()

    @property
    def key_mapping(self):
        return self._key_mapping

    @property
    def rom_path(self):
        return self._rom_path

    @property
    def shown_filename(self) -> str:
        return self._shown_filename

    @rom_path.setter
    def rom_path(self, rom_path):
        path = clean_path(rom_path)
        self._rom_path = path
        self._shown_filename = path.stem + ''.join(path.suffixes)

    def load_vm(self) -> Chip8VirtualMachine:
        self.rom_path = clean_path(self.launch_args['rom_file'])

        try:
            self._vm = load_rom_to_vm(self.rom_path)
        except IOError as e:
            exit_with_error(f"Could not read file {self.rom_path!r} : {e!r}")
        except IndexError as e:
            exit_with_error(f"Could not load rom: {e!r}")

        self.breakpoints = set()

    @abstractmethod
    def run(self):
        raise NotImplementedError()

    @property
    def tick_rate(self) -> float:
        return self._tick_rate

    @tick_rate.setter
    def tick_rate(self, new_rate):
        self._tick_rate = new_rate


FRONTENDS = {}
