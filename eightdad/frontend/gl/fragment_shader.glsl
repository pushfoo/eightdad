#version 330
// Based on einarf's original proof of concept from the arcade library

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