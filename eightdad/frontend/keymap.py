from typing import Dict, Any

DEFAULT = {
    0x1: '1',
    0x2: '2',
    0x3: '3',
    0xC: '4',
    0x4: 'q',
    0x5: 'w',
    0x6: 'e',
    0xD: 'r',
    0x7: 'a',
    0x8: 's',
    0x9: 'd',
    0xE: 'f',
    0xA: 'z',
    0x0: 'x',
    0xB: 'c',
    0xF: 'f'
}

def build_hexkey_mapping(
        src_dict: Dict[int, Any] = DEFAULT
) -> Dict[int, Any]:
    """
    Build a dictionary that maps character codes to chip8 hex keys.

    This works for both asciimatics and arcade at the moment as they
    both use the ordinal unicode value for keys in their key press
    representations.

    :param src_dict:
    :return:
    """
    final_keymap = {}
    for vm_keyid, char in src_dict.items():
        final_keymap[ord(char)] = vm_keyid
        # account for the possibility of shift being held down
        final_keymap[ord(char.upper())] = vm_keyid

    return final_keymap
