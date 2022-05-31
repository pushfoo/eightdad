"""
An frontend that draws video ram to a 1-bit OpenGL texture.

A modified version of einarf's Chip-8 display example in the arcade
library. Original is under MIT license.

"""
import arcade
import pyglet
from arcade.gl import geometry
from arcade import get_projection

from eightdad.core import Chip8VirtualMachine
from eightdad.core.vm import upper_hex, report_state
from eightdad.frontend.common import Frontend, build_window_title


class ArcadeWindow(arcade.Window):

    def __init__(
            self,
            width: int, height: int,
            vm: Chip8VirtualMachine,
            current_file: str,
            keymap,
            paused: bool = False
    ):
        super().__init__(
            width, height,
            build_window_title(paused, current_file)
        )
        self._paused = paused
        self._current_file = current_file

        self.vm: Chip8VirtualMachine = vm

        # from einarf's original
        self.program = self.ctx.program(
            vertex_shader="""
                    #version 330
                    uniform mat4 projection;
                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 v_uv;
                    void main() {
                        gl_Position = projection * vec4(in_vert, 0.0, 1.0);
                        v_uv = in_uv;
                    }
                    """,
            fragment_shader="""
                    #version 330
                    // Unsigned integer sampler for reading uint data from texture
                    uniform usampler2D screen;
                    in vec2 v_uv;
                    out vec4 out_color;
                    void main() {
                        // Calculate the bit position on the x axis
                        uint bit_pos = uint(round((v_uv.x * 64) - 0.5)) % 8u;
                        // Create bit mask we can AND the fragment with to extract the pixel value
                        uint flag = uint(pow(2u, 7u - bit_pos));
                        // Read the fragment value (We reverse the y axis here as well)
                        uint frag = texture(screen, v_uv * vec2(1.0, -1.0)).r;
                        // Write the pixel value. Values above 1 will be clamped to 1.
                        out_color = vec4(vec3(frag & flag), 1.0);
                    }
                    """
        )
        self.keymap = keymap

        # get a bytestring that can be written to GL texture
        self.screen_buffer = memoryview(self.vm.video_ram.pixels)

        self.program['projection'] = get_projection()
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
            self.vm.release(mapped)
            print(
                f"Released {chr(symbol)!r}, maps to chip8 key"
                f"{upper_hex(mapped)}"
            )

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol in self.keymap:
            mapped = self.keymap[symbol]
            self.vm.press(self.keymap[symbol])
            print(
                f"Pressed {chr(symbol)!r}, maps to chip8 key"
                f" {upper_hex(mapped)}"
            )

        elif symbol == arcade.key.H:
            pyglet.app.exit()

        elif symbol == arcade.key.SPACE:
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
            self.launch_args['rom_file'],
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
