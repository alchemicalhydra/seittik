import pytest

from seittik.pipes import END, Pipe


########################################################################
# END Sentinel

def test_end_not_eq_self():
    assert END != END


def test_end_repr():
    assert repr(END) == '<END>'


########################################################################
# Repr

def test_pipe_repr_no_source():
    p = Pipe()
    assert repr(p) == '<Pipe *>'

def test_pipe_repr_empty_list():
    p = Pipe([])
    assert repr(p) == '<Pipe []>'


########################################################################
# Missing source

def test_pipe_missing_source():
    p = Pipe()
    with pytest.raises(TypeError) as excinfo:
        list(p)
    assert str(excinfo.value) == "A source must be provided to evaluate a Pipe"


########################################################################
# Stage params

def test_pipe_good_step_param_mutseq():
    p = Pipe([1, 2, 3])
    def good_step_mutseq(mutseq):
        return mutseq
    p._steps.append(good_step_mutseq)
    assert list(p) == [1, 2, 3]


########################################################################
# Bad stage params

def test_pipe_bad_source_param():
    def bad_source(res):
        pass
    p = Pipe._with_source(bad_source)
    with pytest.raises(ValueError):
        list(p)


def test_pipe_bad_step_param_unknown():
    p = Pipe(3)
    def bad_step_unknown(unknown):
        pass
    p._steps.append(bad_step_unknown)
    with pytest.raises(ValueError):
        list(p)


def test_pipe_bad_step_param_res():
    p = Pipe(3)
    def bad_step_res(res):
        pass
    p._steps.append(bad_step_res)
    with pytest.raises(TypeError):
        list(p)


def test_pipe_bad_step_param_ix():
    p = Pipe(3)
    def bad_step_ix(ix):
        pass
    p._steps.append(bad_step_ix)
    with pytest.raises(TypeError):
        list(p)


def test_pipe_bad_step_param_seq():
    p = Pipe(3)
    def bad_step_seq(seq):
        pass
    p._steps.append(bad_step_seq)
    with pytest.raises(TypeError):
        list(p)


def test_pipe_bad_step_param_mutseq():
    p = Pipe(3)
    def bad_step_mutseq(mutseq):
        pass
    p._steps.append(bad_step_mutseq)
    with pytest.raises(TypeError):
        list(p)


def test_pipe_bad_step_param_pipe():
    p = Pipe(3)
    def bad_step_pipe(pipe):
        pass
    p._steps.append(bad_step_pipe)
    with pytest.raises(TypeError):
        list(p)


########################################################################
# Empty sources

def test_pipe_empty_dict():
    p = Pipe({})
    assert list(p) == []


def test_pipe_empty_list():
    p = Pipe([])
    assert list(p) == []


def test_pipe_empty_set():
    p = Pipe(set())
    assert list(p) == []


def test_pipe_empty_str():
    p = Pipe('')
    assert list(p) == []


def test_pipe_empty_tuple():
    p = Pipe(())
    assert list(p) == []


########################################################################
# Pipe step param

def test_pipe_step_param_pipe():
    p = Pipe(Pipe([1, 2, 3]))
    def pipe_step_pipe_param(pipe):
        return pipe
    p._steps.append(pipe_step_pipe_param)
    assert list(p) == [1, 2, 3]


########################################################################
# Direct iteration

def test_pipe_iter_list():
    p = Pipe([1, 2, 3, 4, 5])
    assert list(p) == [1, 2, 3, 4, 5]


########################################################################
# Cloning

def test_pipe_clone():
    p1 = Pipe([1, 2, 3, 4, 5])
    p2 = p1.clone()
    assert p2 is not p1
    assert p2._steps is not p1._steps
    assert p2._source is p1._source


def test_pipe_empty_call():
    p = Pipe()
    assert p([1, 2, 3, 4, 5]).list() == [1, 2, 3, 4, 5]


def test_pipe_nonempty_call():
    p = Pipe([6, 7, 8, 9, 10])
    assert p([1, 2, 3, 4, 5]).list() == [1, 2, 3, 4, 5]


########################################################################
# Indexing and Slicing

def test_pipe_getitem_indexing():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p[2] == 'c'


def test_pipe_getitem_slicing():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p[1:4].list() == ['b', 'c', 'd']


def test_pipe_getitem_bad():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    with pytest.raises(TypeError) as excinfo:
        p['meow']


########################################################################
# Reversal

def test_pipe_reversed_seq():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert reversed(p).list() == ['e', 'd', 'c', 'b', 'a']


def test_pipe_reversed_ix():
    p = Pipe(iter(['a', 'b', 'c', 'd', 'e']))
    assert reversed(p).list() == ['e', 'd', 'c', 'b', 'a']


########################################################################
# Caching

def test_pipe_cache():
    p1 = Pipe(iter([1, 2, 3, 4, 5])).cache()
    p2 = p1.map(lambda x: x * 2)
    p3 = p1.map(lambda x: x * 3)
    assert p2.list() == [2, 4, 6, 8, 10]
    # This would fail as an empty list without `.cache()` above, since the
    # iterator would now be exhausted
    assert p3.list() == [3, 6, 9, 12, 15]


########################################################################
# Random number generation setup

def test_pipe_rng_str_shared():
    import random
    from seittik.utils.randutils import SharedRandom
    p1 = Pipe([1, 2, 3], rng='shared')
    assert isinstance(p1._rng, SharedRandom)
    p2 = Pipe([1, 2, 3], rng='shared')
    assert isinstance(p2._rng, SharedRandom)
    assert p1._rng is p2._rng


def test_pipe_rng_str_pseudo():
    import random
    p = Pipe([1, 2, 3], rng='pseudo')
    assert isinstance(p._rng, random.Random)
    assert not isinstance(p._rng, random.SystemRandom)


def test_pipe_rng_str_crypto():
    import random
    p = Pipe([1, 2, 3], rng='crypto')
    assert isinstance(p._rng, random.Random)
    assert isinstance(p._rng, random.SystemRandom)


def test_pipe_rng_str_invalid():
    import random
    with pytest.raises(ValueError):
        Pipe([1, 2, 3], rng='invalid')


def test_pipe_rng_other_invalid():
    import random
    with pytest.raises(TypeError):
        Pipe([1, 2, 3], rng=13)


def test_pipe_rng_random_subclass():
    import random
    class FooRandom(random.Random):
        pass
    p = Pipe([1, 2, 3], rng=FooRandom())
    assert isinstance(p._rng, random.Random)
    assert not isinstance(p._rng, random.SystemRandom)


def test_pipe_rng_reset():
    import random
    from seittik.utils.randutils import SharedRandom, SHARED_RANDOM
    p = Pipe([1, 2, 3], rng='pseudo')
    assert isinstance(p._rng, random.Random)
    assert p._rng is not SHARED_RANDOM
    old_rng = p._rng
    # Reset
    p = p.set_rng()
    assert p._rng is SHARED_RANDOM
    assert p._rng is not old_rng


def test_pipe_rng_seed():
    p1 = Pipe.randrange(1, 6, rng='pseudo').seed_rng(0)
    assert list(p1.take(5)) == [4, 4, 1, 3, 5]
    p2 = Pipe.randrange(1, 6, rng='pseudo').seed_rng(1)
    assert list(p2.take(5)) == [2, 5, 1, 3, 1]
    assert list(p1.take(5)) == [4, 4, 4, 6, 4]
    assert list(p2.take(5)) == [2, 1, 4, 1, 4]


########################################################################
# Sources

# Pipe.items

def test_pipe_source_items():
    p = Pipe.items({'a': 1, 'b': 2, 'c': 3})
    assert list(p) == [('a', 1), ('b', 2), ('c', 3)]


# Pipe.iterfunc

def test_pipe_source_iterdir(fs):
    import pathlib
    fs.create_file('/tmp/meow.txt')
    fs.create_file('/tmp/woof.txt')
    p = Pipe.iterdir('/tmp').sort()
    meow, woof = p
    assert meow.name == 'meow.txt'
    assert isinstance(meow, pathlib.Path)
    assert woof.name == 'woof.txt'
    assert isinstance(woof, pathlib.Path)


# Pipe.iterfunc

def test_pipe_source_iterfunc():
    p = Pipe.iterfunc(lambda x: x + 1, 13)
    assert list(p.take(5)) == [13, 14, 15, 16, 17]


# Pipe.keys

def test_pipe_source_keys():
    p = Pipe.keys({'a': 1, 'b': 2, 'c': 3})
    assert list(p) == ['a', 'b', 'c']


# Pipe.randrange

def test_pipe_source_randrange(random_seed_0):
    p = Pipe.randrange(1, 6)
    assert list(p.take(5)) == [4, 4, 1, 3, 5]


# Pipe.randfloat

def test_pipe_source_randfloat_0_1(random_seed_0):
    p = Pipe.randfloat()
    assert list(p.take(5)) == pytest.approx([
        0.8444218515250481,
        0.7579544029403025,
        0.420571580830845,
        0.25891675029296335,
        0.5112747213686085,
    ])


def test_pipe_source_randfloat_13_101(random_seed_0):
    p = Pipe.randfloat(13, 101)
    assert list(p.take(5)) == pytest.approx([
        87.30912293420424,
        79.69998745874662,
        50.01029911311436,
        35.784674025780774,
        57.99217548043755,
    ])


# Pipe.range

def test_pipe_source_range_finite():
    p = Pipe.range(stop=5)
    assert list(p) == [0, 1, 2, 3, 4, 5]


def test_pipe_source_range_finite_negative():
    p = Pipe.range(stop=-5, step=-1)
    assert list(p) == [0, -1, -2, -3, -4, -5]


def test_pipe_source_range_infinite():
    p = Pipe.range(start=5)
    assert list(p.take(5)) == [5, 6, 7, 8, 9]


def test_pipe_source_range_infinite_negative():
    p = Pipe.range(start=5, step=-1)
    assert list(p.take(5)) == [5, 4, 3, 2, 1]


# Pipe.rangetil

def test_pipe_source_rangetil_finite():
    p = Pipe.rangetil(stop=5)
    assert list(p) == [0, 1, 2, 3, 4]


def test_pipe_source_rangetil_finite_negative():
    p = Pipe.rangetil(stop=-5, step=-1)
    assert list(p) == [0, -1, -2, -3, -4]


def test_pipe_source_rangetil_infinite():
    p = Pipe.rangetil(start=5)
    assert list(p.take(5)) == [5, 6, 7, 8, 9]


def test_pipe_source_rangetil_infinite_negative():
    p = Pipe.rangetil(start=5, step=-1)
    assert list(p.take(5)) == [5, 4, 3, 2, 1]


# Pipe.repeat

def test_pipe_source_repeat():
    p = Pipe.repeat('foo').take(3)
    assert list(p.take(3)) == ['foo', 'foo', 'foo']


# Pipe.repeatfunc

def test_pipe_source_repeatfunc_int():
    p = Pipe.repeatfunc(int, 6)
    assert list(p.take(5)) == [6, 6, 6, 6, 6]


def test_pipe_source_repeatfunc_dict():
    p = Pipe.repeatfunc(dict, a=1, b=2)
    assert list(p.take(2)) == [{'a': 1, 'b': 2}, {'a': 1, 'b': 2}]


def test_pipe_source_repeatfunc_randint(random_seed_0):
    import random
    p = Pipe.repeatfunc(random.randint, 1, 6)
    assert list(p.take(5)) == [4, 4, 1, 3, 5]


# Pipe.roll

def test_pipe_source_roll_size(random_seed_0):
    p = Pipe.roll(10)
    assert list(p.take(3)) == [7, 7, 1]


# Pipe.unfold

def test_pipe_source_unfold():
    build_pow2 = lambda x: (x, x * 2)
    p = Pipe.unfold(build_pow2, 2)
    assert list(p.take(6)) == [2, 4, 8, 16, 32, 64]


def test_pipe_source_unfold_endearly():
    def endearly(x):
        if x <= 8:
            return (x, x * 2)
        return
    p = Pipe.unfold(endearly, 2)
    assert list(p) == [2, 4, 8]


# Pipe.values

def test_pipe_source_values():
    p = Pipe.values({'a': 1, 'b': 2, 'c': 3})
    assert list(p) == [1, 2, 3]


# Pipe.walk

def test_pipe_source_walk():
    p = Pipe.walk(['a', ['b', ['c', ['d', ['e']]]]])
    assert list(p) == [
        (['a', ['b', ['c', ['d', ['e']]]]], 0, 'a'),
         (['a', ['b', ['c', ['d', ['e']]]]], 1, ['b', ['c', ['d', ['e']]]]),
         (['b', ['c', ['d', ['e']]]], 0, 'b'),
         (['b', ['c', ['d', ['e']]]], 1, ['c', ['d', ['e']]]),
         (['c', ['d', ['e']]], 0, 'c'),
         (['c', ['d', ['e']]], 1, ['d', ['e']]),
         (['d', ['e']], 0, 'd'),
         (['d', ['e']], 1, ['e']),
         (['e'], 0, 'e'),
    ]


# Pipe.walkdir

def test_pipe_source_walkdir(fs):
    import pathlib
    fs.create_file('/tmp/meow.txt')
    fs.create_file('/tmp/woof.txt')
    p = Pipe.walkdir('/')
    res = list(p)
    assert len(res) == 2
    root_path, root_dirs, root_files = res[0]
    assert isinstance(root_path, pathlib.Path)
    assert str(root_path) == '/'
    assert root_path.name == ''
    assert root_path.is_dir()
    assert root_dirs == ['tmp']
    assert root_files == []
    tmp_path, tmp_dirs, tmp_files = res[1]
    assert isinstance(tmp_path, pathlib.Path)
    assert str(tmp_path) == '/tmp'
    assert tmp_path.name == 'tmp'
    assert tmp_path.is_dir()
    assert tmp_dirs == []
    assert sorted(tmp_files) == ['meow.txt', 'woof.txt']


########################################################################
# Alternate source/step combos

# Pipe.cartesian_product

def test_pipe_sourcestep_cartesian_product_constructor():
    p = Pipe.cartesian_product('ABCD', 'xy')
    assert [''.join(v) for v in p] == ['Ax', 'Ay', 'Bx', 'By', 'Cx', 'Cy', 'Dx', 'Dy']


def test_pipe_sourcestep_cartesian_product_intermediate():
    p = Pipe(['ABCD', 'xy']).cartesian_product()
    assert [''.join(v) for v in p] == ['Ax', 'Ay', 'Bx', 'By', 'Cx', 'Cy', 'Dx', 'Dy']


# Pipe.chain

def test_pipe_sourcestep_chain_constructor():
    p = Pipe.chain([3, 4, 5], [6, 7, 8])
    assert list(p) == [3, 4, 5, 6, 7, 8]


def test_pipe_sourcestep_chain_intermediate():
    p = Pipe([[3, 4, 5], [6, 7, 8]]).chain()
    assert list(p) == [3, 4, 5, 6, 7, 8]


# Pipe.interleave

def test_pipe_sourcestep_interleave_constructor():
    p = Pipe.interleave('abc', 'def', 'ghi')
    assert list(p) == ['a', 'd', 'g', 'b', 'e', 'h', 'c', 'f', 'i']


def test_pipe_sourcestep_interleave_intermediate():
    p = Pipe(['abc', 'def', 'ghi']).interleave()
    assert list(p) == ['a', 'd', 'g', 'b', 'e', 'h', 'c', 'f', 'i']


def test_pipe_sourcestep_interleave_constructor_fair():
    p = Pipe.interleave('abc', 'def', 'gh', fair=True)
    assert list(p) == ['a', 'd', 'g', 'b', 'e', 'h']


def test_pipe_sourcestep_interleave_intermediate_fair():
    p = Pipe(['abc', 'def', 'gh']).interleave(fair=True)
    assert list(p) == ['a', 'd', 'g', 'b', 'e', 'h']


# Pipe.struct_unpack

def test_pipe_sourcestep_struct_unpack_constructor():
    p = Pipe.struct_unpack('<ffff', b'\x00\x00\xdaB\x00\x00\xcaB\x00\x00\xdeB\x00\x00\xeeB').zip().flatten().map(int)
    assert bytes(p) == b'meow'


def test_pipe_sourcestep_struct_unpack_intermediate():
    p = Pipe([b'\x00\x00\xdaB\x00\x00\xcaB\x00\x00\xdeB\x00\x00\xeeB']).struct_unpack('<ffff').zip().flatten().map(int)
    assert bytes(p) == b'meow'


# Pipe.zip

def test_pipe_sourcestep_zip_constructor():
    p = Pipe.zip('abc', [6, 7, 8])
    assert list(p) == [('a', 6), ('b', 7), ('c', 8)]


def test_pipe_sourcestep_zip_constructor_short():
    p = Pipe.zip('abc', [6, 7])
    assert list(p) == [('a', 6), ('b', 7)]


def test_pipe_sourcestep_zip_constructor_fillvalue():
    p = Pipe.zip('abc', [6, 7], fillvalue=None)
    assert list(p) == [('a', 6), ('b', 7), ('c', None)]


def test_pipe_sourcestep_zip_constructor_fillvalue_and_strict():
    with pytest.raises(TypeError) as excinfo:
        p = Pipe.zip('abc', [6, 7], fillvalue=None, strict=True)
    assert str(excinfo.value) == "'fillvalue' and 'strict' are mutually exclusive"


def test_pipe_sourcestep_zip_constructor_strict():
    p = Pipe.zip('abc', [6, 7], strict=True)
    with pytest.raises(ValueError) as excinfo:
        list(p)
    assert str(excinfo.value) == 'zip() argument 2 is shorter than argument 1'


def test_pipe_sourcestep_zip_intermediate():
    p = Pipe(['abc', [6, 7, 8]]).zip()
    assert list(p) == [('a', 6), ('b', 7), ('c', 8)]


def test_pipe_sourcestep_zip_intermediate_short():
    p = Pipe(['abc', [6, 7]]).zip()
    assert list(p) == [('a', 6), ('b', 7)]


def test_pipe_sourcestep_zip_intermediate_fillvalue():
    p = Pipe(['abc', [6, 7]]).zip(fillvalue=None)
    assert list(p) == [('a', 6), ('b', 7), ('c', None)]


def test_pipe_sourcestep_zip_intermediate_fillvalue_and_strict():
    with pytest.raises(TypeError) as excinfo:
        p = Pipe(['abc', [6, 7]]).zip(fillvalue=None, strict=True)
    assert str(excinfo.value) == "'fillvalue' and 'strict' are mutually exclusive"


def test_pipe_sourcestep_zip_intermediate_strict():
    p = Pipe(['abc', [6, 7]]).zip(strict=True)
    with pytest.raises(ValueError) as excinfo:
        list(p)
    assert str(excinfo.value) == 'zip() argument 2 is shorter than argument 1'


########################################################################
# Steps

# Pipe.append

def test_pipe_step_append_1():
    p = Pipe(['a', 'b', 'c']).append('d')
    assert list(p) == ['a', 'b', 'c', 'd']


def test_pipe_step_append_2():
    p = Pipe(['a', 'b', 'c']).append('d', 'e')
    assert list(p) == ['a', 'b', 'c', 'd', 'e']


# Pipe.broadcast

def test_pipe_step_broadcast():
    p = Pipe(['a']).broadcast(3)
    assert list(p) == [('a', 'a', 'a')]


# Pipe.broadmap

def test_pipe_step_broadmap():
    p = Pipe([1, 2, 3]).broadmap(str, lambda x: x * x)
    assert list(p) == [('1', 1), ('2', 4), ('3', 9)]


# Pipe.chunk

def test_pipe_step_chunk_even_2():
    p = Pipe('abcdef').chunk(2)
    assert list(p) == [('a', 'b'), ('c', 'd'), ('e', 'f')]


def test_pipe_step_chunk_even_3():
    p = Pipe('abcdef').chunk(3)
    assert list(p) == [('a', 'b', 'c'), ('d', 'e', 'f')]


def test_pipe_step_chunk_bad_mutex_args():
    with pytest.raises(TypeError) as excinfo:
        Pipe('abcde').chunk(2, fillvalue='x', fair=True)


def test_pipe_step_chunk_fillvalue():
    p = Pipe('abcde').chunk(2, fillvalue='x')
    assert list(p) == [('a', 'b'), ('c', 'd'), ('e', 'x')]


def test_pipe_step_chunk_nonstrict():
    p = Pipe('abcde').chunk(2)
    assert list(p) == [('a', 'b'), ('c', 'd'), ('e',)]


def test_pipe_step_chunk_sliding_window():
    p = Pipe('abc').chunk(2, step=1)
    assert list(p) == [('a', 'b'), ('b', 'c')]

    p = Pipe('abc').chunk(2)
    assert list(p) == [('a', 'b'), ('c',)]

    p = Pipe('abc').chunk(2, step=2, fillvalue='x')
    assert list(p) == [('a', 'b'), ('c', 'x')]

    p = Pipe('abcde').chunk(2, step=1)
    assert list(p) == [('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e')]

    p = Pipe('abcde').chunk(3, step=1)
    assert list(p) == [('a', 'b', 'c'), ('b', 'c', 'd'), ('c', 'd', 'e')]

    p = Pipe('abcde').chunk(2, step=2, fair=True)
    assert list(p) == [('a', 'b'), ('c', 'd')]

    p = Pipe('abcde').chunk(2, step=2, fillvalue='x')
    assert list(p) == [('a', 'b'), ('c', 'd'), ('e', 'x')]

    p = Pipe('abc').chunk(2, step=3)
    assert list(p) == [('a', 'b')]

    p = Pipe('abcde').chunk(2, step=3, fillvalue='x')
    assert list(p) == [('a', 'b'), ('d', 'e')]

    p = Pipe('abcde').chunk(3, step=4, fillvalue='x')
    assert list(p) == [('a', 'b', 'c'), ('e', 'x', 'x')]


# Pipe.chunkby

def test_pipe_step_chunkby():
    p = Pipe([1, 1, 3, 2, 4, 1, 3, 4, 4, 6, 4, 3, 1, 2]).chunkby(lambda x: x % 2 == 0)
    assert list(p) == [(1, 1, 3), (2, 4), (1, 3), (4, 4, 6, 4), (3, 1), (2,)]


# Pipe.combinations

def test_pipe_step_combinations():
    p = Pipe('abc').combinations(k=2)
    assert list(p) == [('a', 'b'), ('a', 'c'), ('b', 'c')]


# Pipe.concat

def test_pipe_step_concat():
    p = Pipe(['a', 'b', 'c']).concat(['d', 'e', 'f'])
    assert list(p) == ['a', 'b', 'c', 'd', 'e', 'f']


# Pipe.cycle

def test_pipe_step_cycle_infinite():
    p = Pipe([1, 2, 3]).cycle().take(5)
    assert list(p) == [1, 2, 3, 1, 2]


def test_pipe_step_cycle_1():
    p = Pipe([1, 2, 3]).cycle(1)
    assert list(p) == [1, 2, 3]


def test_pipe_step_cycle_n():
    p = Pipe([1, 2, 3]).cycle(3)
    assert list(p) == [1, 2, 3, 1, 2, 3, 1, 2, 3]


# Pipe.debug

def test_pipe_step_debug(capsys):
    p = Pipe([1, 2, 3]).debug()
    list(p)
    cap = capsys.readouterr()
    assert cap.out == '1\n2\n3\n'


# Pipe.depeat

def test_pipe_step_depeat():
    p = Pipe('abbcccacbba').depeat()
    assert list(p) == ['a', 'b', 'c', 'a', 'c', 'b', 'a']


def test_pipe_step_depeat_keyed():
    p = Pipe('abBCcCAcbBA').depeat(key=str.isupper)
    assert list(p) == ['a', 'B', 'c', 'C', 'c', 'B']


def test_pipe_step_depeat_bad_key():
    with pytest.raises(TypeError):
        list(Pipe('abbcccacbba').depeat(key=13))


# Pipe.dictmap

def test_pipe_step_dictmap():
    p = Pipe([1, 2, 3]).dictmap({'a': str, 'b': lambda x: x * x})
    assert list(p) == [{'a': '1', 'b': 1}, {'a': '2', 'b': 4}, {'a': '3', 'b': 9}]
    p = Pipe([1, 2, 3]).dictmap(a=str, b=lambda x: x * x)
    assert list(p) == [{'a': '1', 'b': 1}, {'a': '2', 'b': 4}, {'a': '3', 'b': 9}]


# Pipe.drop

def test_pipe_step_drop():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9]).drop(4)
    assert list(p) == [5, 6, 7, 8, 9]


# Pipe.dropwhile

def test_pipe_step_dropwhile():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9]).dropwhile(lambda x: x <= 4)
    assert list(p) == [5, 6, 7, 8, 9]


# Pipe.enumerate

def test_pipe_step_enumerate():
    [a_i, a_v], [b_i, b_v], [c_i, c_v] = Pipe('abc').enumerate().list()
    assert a_v == 'a'
    assert a_i == 0
    assert b_v == 'b'
    assert b_i == 1
    assert c_v == 'c'
    assert c_i == 2


# Pipe.enumerate_info

def test_pipe_step_enumerate_info():
    [a_i, a_v], [b_i, b_v], [c_i, c_v] = Pipe('abc').enumerate_info().list()
    assert a_v == 'a'
    assert a_i.index == 0
    assert a_i.is_first
    assert not a_i.is_last
    assert repr(a_i) == f'<EnumerateInfo index=0 is_first=True is_last=False>'
    assert b_v == 'b'
    assert b_i.index == 1
    assert not b_i.is_first
    assert not b_i.is_last
    assert repr(b_i) == f'<EnumerateInfo index=1 is_first=False is_last=False>'
    assert c_v == 'c'
    assert c_i.index == 2
    assert not c_i.is_first
    assert c_i.is_last
    assert repr(c_i) == f'<EnumerateInfo index=2 is_first=False is_last=True>'


# Pipe.filter

def test_pipe_step_filter():
    p = Pipe([1, 2, 3, 4, 5]).filter(lambda x: x % 2 == 0)
    assert list(p) == [2, 4]


# Pipe.interleave

def test_pipe_step_interleave():
    p = Pipe.interleave('abc', 'def', 'ghi')
    assert list(p) == ['a', 'd', 'g', 'b', 'e', 'h', 'c', 'f', 'i']


# Pipe.intersperse

def test_pipe_step_intersperse_1():
    p = Pipe(['a', 'b', 'c', 'd', 'e']).intersperse('x')
    assert list(p) == ['a', 'x', 'b', 'x', 'c', 'x', 'd', 'x', 'e']


def test_pipe_step_intersperse_2_uneven():
    p = Pipe(['a', 'b', 'c', 'd', 'e']).intersperse('x', n=2)
    assert list(p) == ['a', 'b', 'x', 'c', 'd', 'x', 'e']


def test_pipe_step_intersperse_2_uneven_fillvalue():
    p = Pipe(['a', 'b', 'c', 'd', 'e']).intersperse('x', n=2, fillvalue='y')
    assert list(p) == ['a', 'b', 'x', 'c', 'd', 'x', 'e', 'y']


def test_pipe_step_intersperse_twice():
    p = Pipe(['a', 'b', 'c', 'd', 'e']).intersperse('x').intersperse('y')
    assert list(p) == ['a', 'y', 'x', 'y', 'b', 'y', 'x', 'y', 'c', 'y', 'x', 'y', 'd', 'y', 'x', 'y', 'e']


# Pipe.label

def test_pipe_step_label():
    p = Pipe([(1, 2), (3, 4), (5, 6)]).label('x', 'y')
    assert list(p) == [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}, {'x': 5, 'y': 6}]


# Pipe.map

def test_pipe_step_map():
    p = Pipe([1, 2, 3, 4, 5]).map(lambda x: x * 2)
    assert list(p) == [2, 4, 6, 8, 10]


# Pipe.peek

def test_pipe_step_peek():
    p = Pipe([1, 2, 3]).peek()
    assert list(p) == [(1, 2), (2, 3), (3, END)]


def test_pipe_step_peek_empty():
    p = Pipe([]).peek()
    assert list(p) == []


# Pipe.permutations

def test_pipe_step_permutations():
    p = Pipe('abc').permutations(k=2)
    assert list(p) == [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]


# Pipe.precat

def test_pipe_step_precat():
    p = Pipe(['a', 'b', 'c']).precat(['d', 'e', 'f'])
    assert list(p) == ['d', 'e', 'f', 'a', 'b', 'c']


# Pipe.prepend

def test_pipe_step_prepend_1():
    p = Pipe(['a', 'b', 'c']).prepend('d')
    assert list(p) == ['d', 'a', 'b', 'c']


def test_pipe_step_prepend_2():
    p = Pipe(['a', 'b', 'c']).prepend('d', 'e')
    assert list(p) == ['d', 'e', 'a', 'b', 'c']


# Pipe.reject

def test_pipe_step_reject():
    p = Pipe([1, 2, 3, 4, 5]).reject(lambda x: x % 2 == 0)
    assert list(p) == [1, 3, 5]


# Pipe.sample

def test_pipe_step_sample_without_replacement(random_seed_0):
    p = Pipe('abc').sample(k=2).take(5)
    assert list(p) == [('b', 'c'), ('a', 'b'), ('c', 'b'), ('b', 'c'), ('b', 'c')]


def test_pipe_step_sample_with_replacement(random_seed_0):
    p = Pipe('abc').sample(k=2, replacement=True).take(5)
    assert list(p) == [('c', 'c'), ('b', 'a'), ('b', 'b'), ('c', 'a'), ('b', 'b')]


# Pipe.scan

def test_pipe_step_scan():
    p = Pipe([1, 2, 3, 4, 5]).scan(lambda a, b: a + b).list()
    assert list(p) == [1, 3, 6, 10, 15]


# Pipe.slice

def test_pipe_step_slice_noargs():
    p = Pipe([1, 2, 3, 4, 5]).slice()
    assert list(p) == [1, 2, 3, 4, 5]


def test_pipe_step_slice_stop_posarg():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).slice(4)
    assert list(p) == [1, 2, 3, 4]


def test_pipe_step_slice_stop_kwarg():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).slice(stop=4)
    assert list(p) == [1, 2, 3, 4]


def test_pipe_step_slice_start_kwarg():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).slice(start=4)
    assert list(p) == [5, 6, 7, 8, 9, 10]


# Pipe.starmap

def test_pipe_step_starmap():
    p = Pipe([(), (1,), (2, 3), (4, 5, 6), (7, 8, 9, 10)]).starmap(lambda *x: sum(x))
    assert list(p) == [0, 1, 5, 15, 34]


# Pipe.takewhile

def test_pipe_step_takewhile():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9]).takewhile(lambda x: x <= 4)
    assert list(p) == [1, 2, 3, 4]


# Pipe.tap

def test_pipe_step_tap():
    tapped = []
    def tapper(item):
        tapped.append(item.upper())
    p = Pipe(['a', 'b', 'c', 'd', 'e']).tap(tapper)
    assert list(p) == ['a', 'b', 'c', 'd', 'e']
    assert tapped == ['A', 'B', 'C', 'D', 'E']


# Pipe.unique

def test_pipe_step_unique():
    p = Pipe('abbcccacbba').unique()
    assert list(p) == ['a', 'b', 'c']


def test_pipe_step_unique_keyed():
    p = Pipe('abBCcCAcbBA').unique(key=str.upper)
    assert list(p) == ['a', 'b', 'C']


def test_pipe_step_unique_bad_key():
    with pytest.raises(TypeError):
        list(Pipe('abbcccacbba').unique(key=13))


########################################################################
# Sinks: Containers


# Pipe.array

def test_pipe_sink_array():
    import array
    p = Pipe(b'meow')
    assert p.array('i') == array.array('i', [109, 101, 111, 119])


# Pipe.bytes

def test_pipe_sink_bytes():
    p = Pipe([b'a', b'b', b'c', b'd', b'e'])
    assert p.bytes() == b'abcde'


# Pipe.deque

def test_pipe_sink_deque():
    import collections
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p.deque() == collections.deque(['a', 'b', 'c', 'd', 'e'])


# Pipe.dict

def test_pipe_sink_dict():
    p = Pipe([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)])
    assert p.dict() == {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}


# Pipe.list

def test_pipe_sink_list():
    p = Pipe([1, 2, 3, 4, 5])
    assert p.list() == [1, 2, 3, 4, 5]


# Pipe.set

def test_pipe_sink_set():
    p = Pipe([1, 2, 3, 4, 5])
    assert p.set() == {1, 2, 3, 4, 5}


# Pipe.str

def test_pipe_sink_str_sep():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p.str('-') == 'a-b-c-d-e'


# Pipe.tuple

def test_pipe_sink_tuple():
    p = Pipe([1, 2, 3, 4, 5])
    assert p.tuple() == (1, 2, 3, 4, 5)


########################################################################
# Sinks: Misc

# Pipe.all

def test_pipe_sink_all_simple_true():
    p = Pipe([1, 1, 2, 4, 3, 1])
    assert p.all()


def test_pipe_sink_all_simple_false():
    p = Pipe([1, 1, 0, 4, 3, 1])
    assert not p.all()


def test_pipe_sink_all_pred_true():
    p = Pipe([1, 1, 2, 4, 3, 1])
    assert p.all(lambda x: x != 5)


def test_pipe_sink_all_pred_false():
    p = Pipe([1, 5, 0, 4, 3, 1])
    assert not p.all(lambda x: x != 5)


# Pipe.any

def test_pipe_sink_any_simple_true():
    p = Pipe([0, 0, 0, 0, 3, 0])
    assert p.any()


def test_pipe_sink_any_simple_false():
    p = Pipe([0, 0, 0, 0, 0, 0])
    assert not p.any()


def test_pipe_sink_any_pred_true():
    p = Pipe([5, 5, 5, 5, 4, 5])
    assert p.any(lambda x: x != 5)


def test_pipe_sink_any_pred_false():
    p = Pipe([5, 5, 5, 5, 5, 5])
    assert not p.any(lambda x: x != 5)


# Pipe.contains

def test_pipe_sink_contains_true_seq():
    p = Pipe([5, 3, 4, 1, 2])
    assert p.contains(3)


def test_pipe_sink_contains_false_seq():
    p = Pipe([5, 3, 4, 1, 2])
    assert not p.contains(6)


def test_pipe_sink_contains_true_ix():
    p = Pipe(iter([5, 3, 4, 1, 2]))
    assert p.contains(3)


def test_pipe_sink_contains_false_ix():
    p = Pipe(iter([5, 3, 4, 1, 2]))
    assert not p.contains(6)


# Pipe.count

def test_pipe_sink_count_5_seq():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p.count() == 5


def test_pipe_sink_count_5_ix():
    p = Pipe(iter(['a', 'b', 'c', 'd', 'e']))
    assert p.count() == 5


def test_pipe_sink_count_empty():
    p = Pipe([])
    assert p.count() == 0


# Pipe.equal

def test_pipe_sink_equal_true():
    p = Pipe(['x', 'x', 'x', 'x', 'x'])
    assert p.equal()


def test_pipe_sink_equal_false():
    p = Pipe(['x', 'x', 'x', 'y', 'x'])
    assert not p.equal()


def test_pipe_sink_equal_empty_without_fillvalue():
    with pytest.raises(ValueError) as excinfo:
        p = Pipe([]).equal()


def test_pipe_sink_equal_empty_with_fillvalue():
    assert Pipe([]).equal(default='meow') == 'meow'


# Pipe.exhaust

def test_pipe_sink_exhaust():
    src = iter(['a', 'b', 'c', 'd', 'e'])
    p = Pipe(src)
    assert p.exhaust() is None
    with pytest.raises(StopIteration) as excinfo:
        next(src)
    with pytest.raises(StopIteration) as excinfo:
        next(iter(p))


# Pipe.fold

def test_pipe_sink_fold_without_initial():
    assert Pipe([1, 2, 3, 4, 5]).fold(lambda a, b: a + b) == 15


def test_pipe_sink_fold_with_initial():
    assert Pipe([1, 2, 3, 4, 5]).fold(lambda a, b: a + b, initial=6) == 21


# Pipe.frequencies

def test_pipe_sink_frequencies():
    from collections import Counter
    p = Pipe(['a', 'b', 'a', 'a', 'b', 'c', 'd', 'b', 'b', 'a', 'c', 'e', 'a'])
    assert p.frequencies() == Counter({'a': 5, 'b': 4, 'c': 2, 'd': 1, 'e': 1})


# Pipe.groupby

def test_pipe_sink_groupby_evens_odds():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert p.groupby(lambda x: 'even' if x % 2 == 0 else 'odd') == {'odd': [1, 3, 5, 7, 9], 'even': [2, 4, 6, 8, 10]}


# Pipe.identical

def test_pipe_sink_identical_true():
    x = object()
    p = Pipe([x, x, x, x, x])
    assert p.identical()


def test_pipe_sink_identical_false():
    x = object()
    y = object()
    p = Pipe([x, x, y, x, x])
    assert not p.identical()


def test_pipe_sink_identical_empty_without_fillvalue():
    with pytest.raises(ValueError) as excinfo:
        p = Pipe([]).identical()


def test_pipe_sink_identical_empty_with_fillvalue():
    assert Pipe([]).identical(default='meow') == 'meow'


# Pipe.max

def test_pipe_sink_max():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.max() == 5


def test_pipe_sink_max_key():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.max(key=lambda x: -x) == 1


def test_pipe_sink_max_default():
    p = Pipe([])
    assert p.max(default='meow') == 'meow'


def test_pipe_sink_max_empty():
    with pytest.raises(ValueError) as excinfo:
        p = Pipe([]).max()


# Pipe.mean

def test_pipe_sink_mean():
    p = Pipe([1, 2, 3, 5, 8])
    assert p.mean() == 3.8


def test_pipe_sink_mean_empty_error():
    import statistics
    with pytest.raises(statistics.StatisticsError):
        Pipe([]).mean()


def test_pipe_sink_mean_empty_default():
    p = Pipe([])
    assert p.mean(default='meow') == 'meow'


# Pipe.median

def test_pipe_sink_median_odd():
    p = Pipe([1, 2, 3, 5, 8])
    assert p.median() == 3


def test_pipe_sink_median_even():
    p = Pipe([1, 2, 3, 5, 8, 13])
    assert p.median() == 4


def test_pipe_sink_median_empty_error():
    import statistics
    with pytest.raises(statistics.StatisticsError):
        Pipe([]).median()


def test_pipe_sink_median_empty_default():
    p = Pipe([])
    assert p.median(default='meow') == 'meow'


# Pipe.min

def test_pipe_sink_min():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.min() == 1


def test_pipe_sink_min_key():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.min(key=lambda x: -x) == 5


def test_pipe_sink_min_default():
    p = Pipe([])
    assert p.min(default='meow') == 'meow'


def test_pipe_sink_min_empty():
    with pytest.raises(ValueError) as excinfo:
        p = Pipe([]).min()


# Pipe.minmax

def test_pipe_sink_minmax():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.minmax() == (1, 5)


def test_pipe_sink_minmax_key():
    p = Pipe([3, 2, 5, 1, 4])
    assert p.minmax(key=lambda x: -x) == (5, 1)


def test_pipe_sink_minmax_default():
    p = Pipe([])
    assert p.minmax(default='meow') == ('meow', 'meow')


def test_pipe_sink_minmax_empty():
    with pytest.raises(ValueError) as excinfo:
        p = Pipe([]).minmax()


# Pipe.mode

def test_pipe_sink_mode_single():
    p = Pipe([6, 1, 1, 2, 2, 3, 3, 4, 5, 1, 1, 6])
    assert p.mode() == (1,)


def test_pipe_sink_mode_multi():
    p = Pipe([6, 1, 1, 2, 2, 3, 3, 4, 5, 1, 1, 6, 6, 6])
    assert p.mode() == (6, 1)


def test_pipe_sink_mode_default():
    p = Pipe([])
    assert p.mode(default='meow') == 'meow'


def test_pipe_sink_mode_empty():
    Pipe([]).mode() == ()


# Pipe.none

def test_pipe_sink_none_simple_true():
    p = Pipe([0, 0, 0, 0, 0, 0])
    assert p.none()


def test_pipe_sink_none_simple_false():
    p = Pipe([0, 0, 0, 0, 3, 0])
    assert not p.none()


def test_pipe_sink_none_pred_true():
    p = Pipe([5, 5, 5, 5, 5, 5])
    assert p.none(lambda x: x != 5)


def test_pipe_sink_none_pred_false():
    p = Pipe([5, 5, 5, 5, 4, 5])
    assert not p.none(lambda x: x != 5)


# Pipe.nth

def test_pipe_sink_nth_seq():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p.nth(2) == 'c'


def test_pipe_sink_nth_ix():
    p = Pipe(iter(['a', 'b', 'c', 'd', 'e']))
    assert p.nth(2) == 'c'


def test_pipe_sink_nth_indexerror_seq():
    with pytest.raises(IndexError) as excinfo:
        Pipe(['a', 'b', 'c', 'd', 'e']).nth(5)


def test_pipe_sink_nth_indexerror_ix():
    with pytest.raises(IndexError) as excinfo:
        Pipe(iter(['a', 'b', 'c', 'd', 'e'])).nth(5)


def test_pipe_sink_nth_default_seq():
    p = Pipe(['a', 'b', 'c', 'd', 'e'])
    assert p.nth(5, default='meow') == 'meow'


def test_pipe_sink_nth_default_ix():
    p = Pipe(iter(['a', 'b', 'c', 'd', 'e']))
    assert p.nth(5, default='meow') == 'meow'


# Pipe.struct_pack

def test_pipe_sink_struct_pack():
    p = Pipe([*b'meow'])
    assert p.struct_pack('<ffff') == b'\x00\x00\xdaB\x00\x00\xcaB\x00\x00\xdeB\x00\x00\xeeB'


def test_pipe_sink_struct_pack_empty():
    p = Pipe([*b'meow'])
    assert p.struct_pack('') == b''


# Pipe.partition

def test_pipe_sink_partition_simple():
    p = Pipe([0, 0, 1, 0, 1, True, 1, 2, 0, 3, 0, False, 5])
    assert p.partition() == ((1, 1, True, 1, 2, 3, 5), (0, 0, 0, 0, 0, False))


def test_pipe_sink_partition_evenodd():
    p = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert p.partition(lambda x: x % 2 == 0) == ((2, 4, 6, 8, 10), (1, 3, 5, 7, 9))


# Pipe.product

def test_pipe_sink_product():
    p = Pipe([1, 2, 3, 4, 5])
    assert p.product() == 120


# Pipe.shuffle

def test_pipe_step_shuffle(random_seed_0):
    p = Pipe('abcdef')
    assert list(p.shuffle()) == ['e', 'c', 'b', 'a', 'f', 'd']


# Pipe.stdev

def test_pipe_sink_stdev_population():
    p = Pipe([4, 6, 6, 6, 7, 7, 9, 11])
    assert p.stdev() == 2


def test_pipe_sink_stdev_sample():
    p = Pipe([4, 6, 6, 6, 7, 7, 9, 11])
    assert p.stdev(sample=True) == pytest.approx(2.138089935299395)


# Pipe.sum

def test_pipe_sink_sum():
    p = Pipe([1, 2, 3, 4, 5])
    assert p.sum() == 15


# Pipe.variance

def test_pipe_sink_variance_population():
    p = Pipe([4, 6, 6, 6, 7, 7, 9, 11])
    assert p.variance() == 4


def test_pipe_sink_variance_sample():
    p = Pipe([4, 6, 6, 6, 7, 7, 9, 11])
    assert p.variance(sample=True) == pytest.approx(4.571428571428571)


# Pipe.width

def test_pipe_sink_width():
    p = Pipe([2, 5, 4, 1, 3])
    assert p.width() == 4


########################################################################
# Complex examples

def test_pipe_complex_mapfilter():
    p = Pipe([1, 2, 3, 4, 5]).map(lambda x: x * 3).filter(lambda x: x % 2 == 0)
    assert list(p) == [6, 12]

def test_pipe_complex_map_filter_fold():
    res = Pipe([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).map(lambda x: x * 3).filter(lambda x: x % 2 == 0).fold(lambda a, b: a + b)
    assert res == 90
