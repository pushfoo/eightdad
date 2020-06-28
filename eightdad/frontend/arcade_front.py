"""
An frontend that draws video ram to a 1-bit OpenGL texture.

A modified version of einarf's Chip-8 display example in the arcade
library. Original is under MIT license.

"""
import sys
from pathlib import Path

import arcade
from arcade.gl import geometry
from arcade import get_projection

from eightdad.core import Chip8VirtualMachine
from eightdad.core.vm import upper_hex

SCREEN_WIDTH = 64 * 10
SCREEN_HEIGHT = 32 * 10


class Chip8Front(arcade.Window):

    def __init__(self, width, height, title, vm, paused: bool = False):
        super().__init__(width, height, title)

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
        self.vm: Chip8VirtualMachine = vm
        self.paused = paused

        # get a bytestring that can be written to GL texture
        self.screen_buffer = memoryview(self.vm.video_ram.pixels)

        self.program['projection'] = get_projection().flatten()
        self.program['screen'] = 0

        self.quad = geometry.screen_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.texture = self.ctx.texture((8, 32), components=1, dtype='i1')
        self.update_rate = 1.0 / 30
        self.breakpoints = set()

    def report_state(self) -> None:
        vm = self.vm
        print(
            f"== state ==\n"
            f"PC       : {vm.dump_current_pc_instruction_raw()}\n"
            f"stack    : {vm.call_stack}\n"
            f"registers: {[i for i in vm.v_registers]}"
        )

    def set_update_rate(self, rate: float):
        """
        Wrapper that also sets a local update variable.

        :param rate:
        :return:
        """
        super().set_update_rate(rate)
        self.update_rate = rate

    def tick(self, delta_time: float):
        vm = self.vm

        self.report_state()

        if vm.program_counter in self.breakpoints:
            if not self.paused:
                print(f"BREAKPOINT at {upper_hex(vm.program_counter)}")
                self.paused = True
                return

        vm.tick(delta_time)

        if self.vm.instruction_unhandled:
            print(f"unhandled {self.vm.dump_current_pc_instruction_raw()}")

        # screen updated always, for now
        self.texture.use(0)
        self.texture.write(self.screen_buffer)

    def on_update(self, delta_time: float):
        # only update when executing?
        vm = self.vm

        if not self.paused:
            self.tick(delta_time)

    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.quad.render(self.program)

    def on_key_press(self, symbol: int, modifiers: int):

        if symbol == arcade.key.SPACE:
            self.paused = not self.paused

        if self.paused:
            if symbol == arcade.key.ENTER:
                self.tick(self.update_rate)


def exit_with_error(msg: str, error_code: int=1) -> None:
    """
    Display an error message and exit loudly with error code

    :param msg: message to display
    :param error_code: return error code to give to the shell
    :return:
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    exit(error_code)


def main() -> None:
    """
    Hacky launch function that stubs VM init and launch.

    Most of this should probably go into a frontend baseclass.

    :return:
    """

    data_file_path = Path(sys.argv[1]).resolve().expanduser()

    if not data_file_path.exists():
        exit_with_error(f"Can't find {data_file_path}")

    vm = Chip8VirtualMachine()

    with open(data_file_path, "rb") as rom_file:
        rom_data = rom_file.read()

        if len(rom_data) > len(vm.memory) - vm.program_counter:
            exit_with_error(f"Rom file too big ({len(rom_data)})!")

    # load data into the VM
    vm.load_to_memory(rom_data, 0x200)

    display_filename = data_file_path.stem + ''.join(data_file_path.suffixes)
    front = Chip8Front(
        SCREEN_WIDTH, SCREEN_HEIGHT,
        f"EightDAD - {display_filename}",
        vm,
        #paused=True
    )
    front.breakpoints.add(0x34E)

    arcade.run()

if __name__ == "__main__":
    main()

