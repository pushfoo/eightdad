import argparse
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Set


from eightdad.core import Chip8VirtualMachine, VideoRam
from eightdad.frontend.common.keymap import load_key_map
from eightdad.frontend.common.util import clean_path, load_rom_to_vm
from eightdad.types import PathLike

BASE_ARG_PARSER = argparse.ArgumentParser(
    description='EightDAD Chip-8 Emulator')
# set up the common arg parser to use
BASE_ARG_PARSER.add_argument(
    '-r', '--rom-file', type=str, required=True, help="Which ROM file to run")
BASE_ARG_PARSER.add_argument(
    '-P', '--start-paused', help="Start the VM paused", action='store_true')
BASE_ARG_PARSER.set_defaults(start_paused=False)


def build_window_title(paused: bool, current_file: PathLike, show_full: bool = False) -> str:
    """
    Returns a neatly formatted window title.

    :param bool paused: whether the VM is currently paused
    :param current_file: the current file path to display
    :param show_full: whether to show the full path
    :return str: a neatly formatted window title
    """
    final = Path(current_file) if show_full else Path(current_file).name
    return f"EightDAD {'(PAUSED)' if paused else '-'} {final}"


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
        self._shown_filename = None

        self._vm: Union[Chip8VirtualMachine, None] = None
        self._vm_display: Union[VideoRam, None] = None
        self.breakpoints: Union[Set, None] = None
        self.load_vm(self.launch_args['rom_file'])

        self._tick_rate = 1.0 / 30
        self._key_mapping = load_key_map()

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

    def load_vm(self, raw_path: str) -> None:
        """
        Load a ROM to the VM.

        :param raw_path: the file path to attempt to load
        :return:
        """
        self.rom_path = clean_path(raw_path)

        try:
            self._vm = load_rom_to_vm(self.rom_path)
        except IOError as e:
            exit_with_error(f"Could not read file {self.rom_path!r} : {e!r}")
        except IndexError as e:
            exit_with_error(f"Could not load rom: {e!r}")

        self._vm_display = self._vm.video_ram
        self.breakpoints = set()

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError()

    @property
    def tick_rate(self) -> float:
        return self._tick_rate

    @tick_rate.setter
    def tick_rate(self, new_rate):
        self._tick_rate = new_rate
