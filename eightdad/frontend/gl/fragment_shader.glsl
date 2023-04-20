#version 330
// Based on einarf's original proof of concept from the arcade library
#define ALMOST_ZERO 0.01

// Inputs, names map to keys in the dictionary
in      vec2       v_uv;           // input translated from pixels to uv coords
uniform vec4       off_pixel_color;
uniform vec4       on_pixel_color;
uniform usampler2D raw_vm_pixels;  // unsigned sampler reading from texture

out vec4 out_color;


void main() {
    // Calculate the bit position on the x axis
    uint bit_pos_x = uint(round((v_uv.x * 64) - 0.5)) % 8u;

    // Create bit mask we can AND the fragment with to extract the pixel value
    uint bit_selection_mask = uint(pow(2u, 7u - bit_pos_x));

    // Read the fragment value (We reverse the y axis here as well)
    uint frag = texture(
        raw_vm_pixels,
        v_uv * vec2(1.0, -1.0) // reverse y axis of sampled texture
    ).r;

    // Use on_pixel_color if any bits are set, else use off_pixel_color
    out_color = mix( // lerp
        off_pixel_color, // 0.0 value
        on_pixel_color,  // 1.0 value
        // Set the edge threshold as close to 0.0 as possible
        step(ALMOST_ZERO, float(frag & bit_selection_mask))
    );
}