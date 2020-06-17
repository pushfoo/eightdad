import pytest
from itertools import product
from eightdad.core import Chip8VirtualMachine, VideoRam


@pytest.mark.parametrize(
    "ram_size",
    [
        512,
        1024,
        2048,
        4096,
        8192
    ]
)
def test_ram_size(ram_size):
    vm = Chip8VirtualMachine(memory_size=ram_size)
    print(vm.memory)
    assert len(vm.memory) == ram_size


class VRamSubclass(VideoRam):
    """Dummy that makes sure subclasses work as VideoRam type args"""
    pass


class BadClass:
    """Not a subclass of VideoRam"""
    pass


class TestVideoRamArg:

    @pytest.mark.parametrize("vram_type", (VideoRam, VRamSubclass))
    def test_vm_raises_no_error_on_good_types(self, vram_type):
        vm = Chip8VirtualMachine(video_ram_type=vram_type)

    def test_typeerror_on_bad_vram_type(self):
        """Non-VideoRam class passed in video_ram_type"""
        with pytest.raises(TypeError):
            vm = Chip8VirtualMachine(video_ram_type=BadClass)

    def test_typeerror_on_not_a_type(self):
        """Non-type passed in video_ram_type"""
        with pytest.raises(TypeError):
            vm = Chip8VirtualMachine(video_ram_type="not a type")
