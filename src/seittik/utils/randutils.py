import random as random_mod

from .sentinels import _MISSING


class SharedRandom:
    """
    A random generator that proxies to the shared instance in the `random`
    module.

    We *could* simply access `random._inst` directly and call it a day, but
    we'd rather not touch private module attributes if we can help it.
    """
    def __init__(self, seed=_MISSING, /):
        if seed is not _MISSING:
            random_mod.seed(seed)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    betavariate = random_mod.betavariate
    choice = random_mod.choice
    choices = random_mod.choices
    expovariate = random_mod.expovariate
    gammavariate = random_mod.gammavariate
    gauss = random_mod.gauss
    getrandbits = random_mod.getrandbits
    getstate = random_mod.getstate
    lognormvariate = random_mod.lognormvariate
    normalvariate = random_mod.normalvariate
    paretovariate = random_mod.paretovariate
    randbytes = random_mod.randbytes
    randint = random_mod.randint
    random = random_mod.random
    randrange = random_mod.randrange
    sample = random_mod.sample
    seed = random_mod.seed
    setstate = random_mod.setstate
    shuffle = random_mod.shuffle
    triangular = random_mod.triangular
    uniform = random_mod.uniform
    vonmisesvariate = random_mod.vonmisesvariate
    weibullvariate = random_mod.weibullvariate


SHARED_RANDOM = SharedRandom()
