"""
An frontend that draws video ram to a 1-bit OpenGL texture.

A modified version of einarf's Chip-8 display example in the arcade
library. Original is under MIT license.

"""
from pathlib import Path

import arcade
import pyglet
from arcade.gl import geometry

from eightdad.core import Chip8VirtualMachine
from eightdad.core.vm import upper_hex, report_state
from eightdad.frontend import build_window_title, Frontend
from eightdad.frontend.common.keymap import ControlButton

from eightdad.types import PathLike


SHADER_ROOT = Path(__file__).parent
VERTEX_SHADER_PATH = SHADER_ROOT / "vertex_shader.glsl"
FRAGMENT_SHADER_PATH = SHADER_ROOT / "fragment_shader.glsl"


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
            vertex_shader_path: PathLike = VERTEX_SHADER_PATH,
            fragment_shader_path: PathLike = FRAGMENT_SHADER_PATH
    ):
        super().__init__(
            width, height,
            build_window_title(paused, current_file)
        )
        self._paused = paused
        self._current_file = current_file

        self.vm: Chip8VirtualMachine = vm

        vertex_shader = _read_shader_source_from(vertex_shader_path)
        fragment_shader = _read_shader_source_from(fragment_shader_path)

        # from einarf's original
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        self.keymap = keymap

        # get a bytestring that can be written to GL texture
        self.screen_buffer = memoryview(self.vm.video_ram.pixels)

        self.program['projection'] = self.projection
        self.program['screen'] = 0

        self.quad = geometry.screen_rectangle(0, 0, self.width, self.height)
        self.texture = self.ctx.texture((8, 32), components=1, dtype='i1')
        self.update_rate = 1.0 / 30

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
