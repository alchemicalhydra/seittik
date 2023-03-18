import random

import pytest


@pytest.fixture
def random_seed_0():
    random.seed(0)
