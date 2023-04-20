"""
An frontend that draws video ram to a 1-bit OpenGL texture.

A modified version of einarf's Chip-8 display example in the arcade
library. Original is under MIT license.

"""
from pathlib import Path

import pyglet
import arcade
from arcade.types import RGBA255, Color
from arcade.gl import geometry

from eightdad.core import Chip8VirtualMachine
from eightdad.core.vm import upper_hex, report_state
from eightdad.frontend import build_window_title, Frontend
from eightdad.frontend.common.keymap import ControlButton

from eightdad.types import PathLike


# Shader & default config constants
SHADER_ROOT = Path(__file__).parent
VERTEX_SHADER_PATH = SHADER_ROOT / "vertex_shader.glsl"
FRAGMENT_SHADER_PATH = SHADER_ROOT / "fragment_shader.glsl"

DEFAULT_OFF_PIXEL_COLOR = Color.from_hex_string("#b05e00")
DEFAULT_ON_PIXEL_COLOR = Color.from_hex_string("#ffc400")


def _read_shader_source_from(path: PathLike) -> str:
    path = Path(path).resolve()
    return path.read_text()


class ArcadeWindow(arcade.Window):

    def __init__(
            self,
            width: int, height: int,
            vm: Chip8VirtualMachine,
            current_file: str,
            keymap,
            paused: bool = False,
            off_pixel_color: RGBA255 = DEFAULT_OFF_PIXEL_COLOR,
            on_pixel_color: RGBA255 = DEFAULT_ON_PIXEL_COLOR,
            vertex_shader_path: PathLike = VERTEX_SHADER_PATH,
            fragment_shader_path: PathLike = FRAGMENT_SHADER_PATH
    ):
        # Non-GL setup
        super().__init__(
            width, height,
            build_window_title(paused, current_file)
        )
        self._paused = paused
        self._current_file = current_file
        self.vm = vm
        self.keymap = keymap
        self.update_rate = 1.0 / 30

        # Attempt to load & compile shaders
        vertex_shader = _read_shader_source_from(vertex_shader_path)
        fragment_shader = _read_shader_source_from(fragment_shader_path)
        self.program = program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )

        # Allocate resources for use in shaders
        self.quad = geometry.screen_rectangle(0, 0, self.width, self.height)
        self.texture = self.ctx.texture((8, 32), components=1, dtype='i1')

        # Ideally, this would use .toreadonly() on the memoryview, but
        # there's an unclosed ctypes ticket blocking this.
        # https://github.com/python/cpython/issues/72832
        self.screen_buffer = memoryview(self.vm.video_ram.pixels)

        # Bind resources to shader program inputs
        program['projection'] = self.projection
        program['off_pixel_color'] = Color.from_iterable(off_pixel_color).normalized
        program['on_pixel_color'] = Color.from_iterable(on_pixel_color).normalized
        program['raw_vm_pixels'] = 0

    @property
    def paused(self) -> bool:
        return self._paused

    @paused.setter
    def paused(self, paused: bool):
        self._paused = paused
        self.set_caption(build_window_title(paused, self._current_file))

    def set_update_rate(self, rate: float):
        """
        Wrapper that also sets a local update variable.

        :param rate:
        :return:
        """
        super().set_update_rate(rate)
        self.update_rate = rate

    def on_update(self, delta_time: float):
        # only update when executing?
        vm = self.vm

        if not self.paused:
            for i in range(vm.ticks_per_frame):
                vm_state = vm.dump_state()
                report_state(vm_state)
                vm.tick()

                if self.vm.instruction_unhandled:
                    print("INSTRUCTION UNHANDLED!")
                    self.paused = True

        self.texture.use(0)
        self.texture.write(self.screen_buffer)  # type: ignore

    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.quad.render(self.program)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in self.keymap:
            mapped = self.keymap[symbol]
            value = mapped.value
            if value <= 0xF:
                self.vm.release(value)
            print(
                f"Released {chr(symbol)!r}, maps to control"
                f"{mapped!r}"
            )

    def on_key_press(self, symbol: int, modifiers: int):

        if symbol not in self.keymap:
            return

        mapped_button = self.keymap[symbol]
        mapped_value = mapped_button.value

        # if it's a hex key
        if mapped_value <= 0xF:
            self.vm.press(mapped_value)
            print(
                f"Pressed {chr(symbol)!r}, maps to control"
                f" {mapped_button!r}"
            )

        elif mapped_button == ControlButton.QUIT:
            pyglet.app.exit()

        elif mapped_button == ControlButton.PAUSE:
            self.paused = not self.paused

        if self.paused:
            if symbol == arcade.key.ENTER:
                self.vm.tick()


class ArcadeFrontend(Frontend):

    def __init__(self, pixel_size: int = 10):
        super().__init__()

        display_width_px = self._vm_display.width * pixel_size
        display_height_px = self._vm_display.height * pixel_size

        self._window = ArcadeWindow(
            display_width_px, display_height_px,
            self._vm,
            self.rom_path,
            self._key_mapping,
            self.launch_args['start_paused']
        )

    def run(self):
        self._window.run()
        arcade.run()

    @property
    def paused(self) -> bool:
        """
        Return whether the VM is currently paused.

        Stored on the window to make update logic simpler.

        :return: whether the VM is paused.
        """
        return self._window.paused

    @paused.setter
    def paused(self, pause: bool):
        self._window.paused = pause


def main() -> None:
    frontend = ArcadeFrontend()
    frontend.run()


if __name__ == "__main__":
    main()
