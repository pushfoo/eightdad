import pytest
from eightdad.core import Chip8VirtualMachine as VM
from eightdad.types import DigitTooTall, DigitTooWide


@pytest.fixture
def vm():
    return VM()


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


class TestLoadDigitData:

    @pytest.mark.parametrize('bad_data_length', (1, 17))
    def test_load_digits_raises_index_error_when_data_too_short(
            self,
            vm,
            bad_data_length
    ):
        with pytest.raises(IndexError):
            vm.load_digits([b"\xFF"] * 5, 0)

    def test_load_digits_raises_digit_too_tall_when_digit_tall(self, vm):
        with pytest.raises(DigitTooTall):
            vm.load_digits([b"\1\1\1\1\1\1"] * 16, 0)

    def test_load_digits_raises_digit_too_wide_when_digit_wide(self, vm):
        with pytest.raises(DigitTooWide):
            vm.load_digits([bytes([0b11111000])] * 16, 0)

    def test_load_digits_works_when_digit_data_valid(self, vm):
        digit_data = [b"\xF0\xF0\xF0\xF0\xF0" for i in range(16)]
        vm.load_digits(digit_data, 0)
        assert vm.memory[0:5*16] == b''.join(digit_data)

