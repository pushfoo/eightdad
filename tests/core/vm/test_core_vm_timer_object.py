import pytest

from eightdad.core.vm import Timer

TWO_HUNDREDTH = 1.0 / 200


class TestTick:

    def test_ticking_timer_advances_elapsed(self):
        timer = Timer()
        assert timer.elapsed == 0

        timer.tick(TWO_HUNDREDTH)
        assert timer.elapsed == TWO_HUNDREDTH

    def test_overflowing_threshold__decrements_elapsed(self):

        timer = Timer()

        initial_value = TWO_HUNDREDTH * 199
        timer.elapsed = initial_value

        timer.tick(TWO_HUNDREDTH)

        assert timer.elapsed < initial_value

    def test_zeroed_timer_doesnt_decrement(self):

        timer = Timer()
        assert timer.value == 0

        timer.tick(timer.decrement_threshold + 0.01)
        assert timer.value == 0

    @pytest.mark.parametrize(
        "initial_value",
        [1, 255, 2]
    )
    def test_non_zero_timer_decrements(self, initial_value):
        timer = Timer()

        timer.elapsed = 199 * TWO_HUNDREDTH
        timer.value = initial_value

        timer.tick(TWO_HUNDREDTH)

        assert timer.value == initial_value - 1




