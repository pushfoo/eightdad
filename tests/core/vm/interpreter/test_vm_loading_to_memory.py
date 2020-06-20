import pytest
from eightdad.core import Chip8VirtualMachine as VM


class TestLoadDataToMemoryLocation:

    def test_bad_type_on_data_causes_typerror(self):
        vm = VM()
        with pytest.raises(TypeError):
            vm.load_to_memory("bad", 0x200)

    def test_negative_location_causes_indexerror(self):
        vm = VM()
        with pytest.raises(IndexError):
            vm.load_to_memory(b"aaa", -5)

    @pytest.mark.parametrize("ram_size", (1024, 2048, 4096))
    @pytest.mark.parametrize("location", (0x200, 1024))
    def test_data_past_ram_end_raises_indexerror(self, ram_size, location):
        vm = VM(memory_size=ram_size)

        # 1 after end of RAM
        data_len = 1 + ram_size - location

        with pytest.raises(IndexError):
            vm.load_to_memory(b"a" * data_len, location)

    @pytest.mark.parametrize(
        "data",
        (
            b"aaaa",
            bytearray(b"aaaa"),
            memoryview(b"aaaa")
        )
    )
    def test_good_values_sets_data(self, data):
        vm = VM()
        vm.load_to_memory(data, 0x200)
        assert vm.memory[0x200:0x204] == data







