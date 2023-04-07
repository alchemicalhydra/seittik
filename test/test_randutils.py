import random

from seittik.utils.randutils import SHARED_RANDOM


def test_shared_random_repr():
    assert repr(SHARED_RANDOM) == '<SharedRandom>'


def test_shared_random_seed():
    random.seed(13)
    assert [random.randint(1, 6) for _ in range(5)] == [3, 3, 6, 6, 2]
    random.seed(13)
    assert [SHARED_RANDOM.randint(1, 6) for _ in range(5)] == [3, 3, 6, 6, 2]
    SHARED_RANDOM.seed(6)
    assert [random.randint(1, 6) for _ in range(5)] == [5, 1, 4, 3, 1]
    SHARED_RANDOM.seed(6)
    assert [SHARED_RANDOM.randint(1, 6) for _ in range(5)] == [5, 1, 4, 3, 1]
