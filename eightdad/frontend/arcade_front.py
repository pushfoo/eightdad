"""
An frontend that draws video ram to a 1-bit OpenGL texture.

A modified version of einarf's Chip-8 display example in the arcade
library. Original is under MIT license.

"""
import arcade
from arcade.gl import geometry
from arcade import get_projection

from eightdad.core import Chip8VirtualMachine

SCREEN_WIDTH = 64 * 10
SCREEN_HEIGHT = 32 * 10

class Chip8Front(arcade.Window):

    def __init__(self, width, height, title):
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
        self.vm = Chip8VirtualMachine()

        # draw 0 at VX,VY, add 5 to x, jump to start
        self.vm.memory[0x200] = 0xD0
        self.vm.memory[0x201] = 0x15

        self.vm.memory[0x202] = 0x70
        self.vm.memory[0x203] = 0x06

        self.vm.memory[0x204] = 0x12

        # get a bytestring that can be written to GL texture
        self.screen_buffer = memoryview(self.vm.video_ram.pixels)

        self.program['projection'] = get_projection().flatten()
        self.program['screen'] = 0

        self.quad = geometry.screen_rectangle(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.texture = self.ctx.texture((8, 32), components=1, dtype='i1')

    def on_update(self, delta_time: float):
        self.vm.tick(delta_time)
        self.texture.use(0)
        self.texture.write(self.screen_buffer)


    def on_draw(self):
        self.clear()
        self.texture.use(0)
        self.quad.render(self.program)

if __name__ == "__main__":
    Chip8Front(SCREEN_WIDTH, SCREEN_HEIGHT, "EightDAD")
    arcade.run()


