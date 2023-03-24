# Design Notes

This is an informal riff on Seittik's design.

## Goals

- **Do:** Make functional programming in Python feel pleasing and
  expressive.
  - Python does so many things right, but strong support for a functional
    programming style hasn't been one of them. The language's other features
    give us some great tools to (mostly) work around that, though!
  - Abuse the daylights out of descriptors, metaclasses, operators, and
    special methods. Do whatever it takes.

- **Do:** Use a fluent API.
  - Reading and describing the flow of data transformations should be a
    left-to-right, top-to-bottom experience. You shouldn't have to visually
    and mentally "unwrap" transformations, inside-out.

- **Do:** Provide a REPL-first experience.
  - Emphasize the experience in the IPython REPL first and foremost ---
    that's my bias, since that's how I iterate on most of the code I write,
    and Seittik can still be quite useful there even if it isn't fully
    performant (yet).
  - The experience in a proper text editor (e.g., Neovim, Emacs) and in a
    standard library or application should come next. This is an important
    longer-term goal.
  - The experience in an IDE should not be given any special consideration.
    I refuse to make any changes where IDEs are the sole beneficiaries.

- **Do:** Go whole-hog kitchen-sink with including functional patterns.
  - Unless you're working with heavy data science, you shouldn't have to
    reach for another functional library, not even itertools. Err on the
    side of including patterns.

- **Do:** Borrow ideas from everywhere.
  - Check out what other similar libraries are doing, both in Python-land
    and elsewhere. Don't be afraid to borrow anything that looks useful.

- **Do:** Document all components of the public API.
  - I'm using [MyST](https://myst-parser.readthedocs.io/en/latest/), a
    CommonMark-Sphinx bridge, instead of reStructuredText. I was an early
    adopter of reStructuredText many years ago, even writing all my personal
    notes in it, but CommonMark is where it's at today. (As an aside,
    Python-land has a weird case of "not invented here" syndrome; another
    example that comes to mind is how long it took the majority of Python
    projects to switch away from Mercurial to Git.)
  - I'm aiming to have [IPython Sphinx
    Directives](https://ipython.readthedocs.io/en/stable/sphinxext.html) in
    as many places as possible; they're much nicer to read than plain
    doctests.
    - I had to monkey-patch the directive to support resetting history between
      IPython blocks, so you don't end up with `In [378]` at the start of a
      block later in the docs.
  - I'm trying to use marble diagrams, a concept I first came across in the
    [RxJS API Documentation](https://rxjs.dev/api), to visually explain how
    various Pipe sources, steps, and sinks work. (You might strictly say I'm
    *abusing* marble diagrams, since they're intended to help document
    [Observables](https://en.wikipedia.org/wiki/Observer_pattern) rather
    than [Iterators](https://en.wikipedia.org/wiki/Iterator_pattern), but
    they seem to fit the use case fairly well.)
    - I originally tried using [Mermaid](https://mermaid.js.org/intro/) sequence
      diagrams, but they're really not well suited for this purpose.
    - I'm currently using [dooble](https://github.com/MainRo/dooble) for this,
      which seems like a dead project; I had to monkey-patch it to prevent the
      diagrams from being cut off.
    - [Swirly](https://github.com/timdp/swirly) seems like it generates much
      nicer marble diagrams while being actively maintained, but there isn't
      an existing Sphinx extension for it, and I didn't feel like writing one
      myself just yet.

- **Do:** Aim for 100% test coverage.
  - We have a lot of complex interacting parts, and empirical tests are the
    only way to trust what we've written.
  - I'm initially publishing this with 100% coverage, and I'd like to keep
    it that way.

- **Do:** Once everything feels right, work on speed.
  - It would be nice to consistently beat similar Python libraries on
    benchmarks. But at the same time, we're trying to stay lightweight ---
    again, we're trying to replace libraries like itertools, not Pandas.
  - Cython might be an option here, if it doesn't distort things too badly.

## Non-Goals

- **Don't:** Worry about API stability (yet).
  - This project is still in the early stages. I'm concentrating on the REPL
    experience first and foremost. Once that's nailed down, I'll shift my
    focus and start stabilizing things. Don't count on me to go through
    deprecation periods anytime soon, although I *will* mention breaking
    changes in release notes.

- **Don't:** Add static type hints.
  - Three reasons:
    - **Pragmatic:** Python's static typing support has absolutely terrible
      support for some of our most important implementation details, such as
      {term}`descriptors <descriptor>`.

      Want an example? Go ahead and try reimplementing `classmethod` from
      scratch in Python. It's not hard, and you can even crib the example
      provided in the Python documentation's [Descriptor HowTo
      Guide](https://docs.python.org/3/howto/descriptor.html#class-methods).

      Feeling lazy? Here's the gist:

      ```python
      from types import MethodType

      class ClassMethod:
          def __init__(self, f):
              self.f = f

          def __get__(self, obj, cls=None):
              if cls is None:
                  cls = type(obj)
              return MethodType(self.f, cls)
      ```

      *Now* try to get your pure-Python `ClassMethod` to typecheck in *any*
      static type checker for Python. Try something simple:

      ```python
      class Foo:
          def __init__(self, a, b):
              self.a = a
              self.b = b

          @ClassMethod
          def bar(cls, x: int):
              return cls(x, x)

      obj = Foo.bar(3)
      print(obj.a + obj.b)
      ```

      None of the static Python type-checkers can figure out what ClassMethod
      is doing here (it's wrapping an alternate constructor), and they'll all
      freak out inside `bar`. The best I can tell? They'll all cheating by
      special-casing the builtin `classmethod`.

      Of course, if you can't even type-check `classmethod` without cheating,
      imagine something like Seittik's `multimethod`, which is a descriptor
      that's written as a nested class where your method would live,
      dispatches to different sub-methods depending on whether it's called
      from a class or an instance, *and* it has a metaclass. Something tells
      me it will be a *while* before we'll get static typing support for that
      sort of pattern --- if ever.

    - **Aesthetic:** I find Python's particular syntactical implementation of
      type hints to be *hideously* ugly for what's largely been a
      gorgeous-to-read language. (Well, warts like
      [`lambda`](inv:python:std:label#lambda) aside.)

      There *are* type systems out there that are easy on the eyes, with
      Haskell's perhaps being the cleanest. Claims that Python's dynamic
      heritage forces a grotesque syntax kluge are nonsense, since JavaScript
      has an even messier history and TypeScript function type signatures are
      actually *readable*. Seriously, compare `(x: string => string)` with
      `Callable[[str], str]`. It's not even close, and that's *before* you
      start dealing with higher-order functions!

      Maybe the syntax will improve over time, but I'm not holding my breath.

    - **Philosophical:** I'm an
      [empiricist](https://en.wikipedia.org/wiki/Empiricism). I consider
      [rationalism](https://en.wikipedia.org/wiki/Rationalism) to be lunacy. I
      liken static typing to rationalism, and testing to empiricism.

      "But," my hypothetical interlocutor cries out, "your position defeats
      itself, for empirical studies have shown static typing to raise software
      quality!" My rejoinder: *For whom?* Studies have *many* innate problems,
      but the most relevant here is that their results generalize to a
      "typical" subject --- in this case, a typical software developer. What
      works for the masses doesn't work for the outliers, and I'm nothing if
      not a weirdo in most domains.

  My fear? Python will start deprecating and removing language features
  that get in the way of supposedly-"optional" static typing. "But it's
  optional!" is a line of hogwash I've heard time and again. If Python is
  going to evolve toward becoming more like C or more like Lisp, give me
  Lisp any day.

- **Don't:** Do anything special to support non-free platforms.
  - Seittik isn't doing anything intentional at this point that should
    matter in this direction, but I have no intention of ever testing it on
    a non-open-source platform. I run Linux full-time everywhere, and I'm
    not installing some bloated, malware-ridden OS (or, cats forbid, buying
    into an entire *proprietary hardware ecosystem*) for what's supposed to
    be a fun side project.

- **Don't:** Use semantic versioning.
  - Seittik uses [CalVer](https://calver.org/). I used to be a SemVer True
    Believer until I came across a very persuasive series of arguments that
    outlined how much of an anti-pattern SemVer is for all but the largest
    projects.

    Here's some good reading on the topic:

    - <https://hynek.me/articles/semver-will-not-save-you/>
    - <https://iscinumpy.dev/post/bound-version-constraints/>
    - <https://snarky.ca/why-i-dont-like-semver/>

  - We use Poetry for packaging, which insists on SemVer-style pinning any
    dependencies added to a project by default. It's gotten mildly tedious
    having to replace every `^` with a `>=`, but it's otherwise *so* much
    better than pip that I can't complain much.

- **Don't:** Use virtualenvs for development.
  - Here's a dirty little secret: I haven't used virtualenvs in *years*. I
    wrote myself a [PEP 582](https://peps.python.org/pep-0582/)-style
    `usercustomize` module before PEP 582 was created (according to my local
    git history), inspired by Node's `node_modules` behavior, and I've been
    iterating on it ever since. I guess I'm not the only one who thought
    virtualenvs were a terrible mistake. (PEP 582 makes several suboptimal
    design decisions IMHO, so I'll keep on trucking with my
    `python_packages` solution.)

    If that's not enough isolation for you, use Docker.

## Nomenclature

When choosing a name for a Pipe method, I try to follow these rules:

- Prefer action verbs if the intent is clearly expressed; otherwise, use
  a noun describing the result.
- Avoid any sort of redundant prefix like "make" or "build". That's
  implicit.
- If there's universal agreement on a name, try to go with that.
- If multiple names each see strong use in the wild (e.g., `fold` versus
  `reduce`), go with whichever feels better subjectively.
- Try to avoid names that would carry a confusing connotation in Python
  (e.g., `iterate`).
- Don't go with the name Python uses *just* because Python uses it (e.g.,
  `count`, `filterfalse`).
- Prefer shorter names if they're still clear.
- If a method combines multiple functionalities via keyword flags, use
  the most basic form as the method name.
- Don't be afraid to make something up if it captures the essence of
  what's going on (e.g., `depeat`).

## Pipe Design

### Inspirations

Given that Seittik aims to be something of a kitchen sink of functional
tooling, I've tried to research as many functional languages and
libraries as I could manage, including:

- [Clojure](https://clojure.github.io/clojure/)
- [Erlang: stdlib](https://www.erlang.org/doc/apps/stdlib/index.html)
- [FSharp: Collections](https://fsharp.github.io/fsharp-core-docs/reference/fsharp-collections.html)
- [Haskell: Data.List](https://hackage.haskell.org/package/base/docs/Data-List.html)
- [JavaScript: FxTS](https://fxts.dev/docs/index/)
- [JavaScript: Lazy.js](https://danieltao.com/lazy.js/docs/)
- [JavaScript: itertools.js](https://github.com/nvie/itertools.js)
- [JavaScript: lfi](https://github.com/TomerAberbach/lfi/blob/main/docs/modules.md)
- [JavaScript: Lodash](https://lodash.com/docs)
- [JavaScript: Ramda](https://ramdajs.com/docs/)
- [Kotlin: collections](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.collections/)
- [Kotlin: sequences](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.sequences/)
- [Python: funcy](https://funcy.readthedocs.io/en/stable/)
- [Python: Itertools](https://docs.python.org/3/library/itertools.html)
- [Python: More Itertools](https://more-itertools.readthedocs.io/en/stable/)
- [Python: Pandas](https://pandas.pydata.org/pandas-docs/stable/reference/index.html)
- [Python: Toolz](https://toolz.readthedocs.io/en/latest/api.html)
- [Ruby: Enumerable](https://ruby-doc.org/3.2.1/Enumerable.html)
- [Rust: Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html)
- [Rust: itertools](https://docs.rs/itertools/latest/itertools/)
- [Scala: collection](https://scala-lang.org/api/3.x/scala/collection.html)

I've listed many of the similar functions I could find alongside the
`Pipe` methods below, regardless of whether it was an actual inspiration
or not, to help cross-reference similar behavior.

The cross-references listed are incomplete, but I'll keep updating them
over time.

### Pipe: Sources

These create a new source.

#### {py:meth}`.items() <seittik.pipes.Pipe.items>`

- {py-stdtypes}`dict.items`

#### {py:meth}`.iterdir() <seittik.pipes.Pipe.iterdir>`

- {py-pathlib}`Path.iterdir`

#### {py:meth}`.iterfunc() <seittik.pipes.Pipe.iterfunc>`

- {clj-core}`iterate`
- {hs-data-list}`iterate`
- {py-more-itertools}`iterate`

I felt the term "iterate" was too similar to {py-builtins}`iter` and the
Python concept of iteration in general.

#### {py:meth}`.keys() <seittik.pipes.Pipe.keys>`

- {py-stdtypes}`dict.keys`

#### {py:meth}`.randfloat() <seittik.pipes.Pipe.randfloat>`

- {py-random}`random`
- {py-random}`uniform`

Acts like {external:py:func}`random.random` without arguments, and
{external:py:func}`random.uniform` with them.

#### {py:meth}`.randrange() <seittik.pipes.Pipe.randrange>`

- {py-random}`randint`
- {py-random}`randrange`

Like {py:meth}`Pipe.range`, this is *inclusive* of the upper bound.

#### {py:meth}`.range() <seittik.pipes.Pipe.range>` / {py:meth}`.rangetil() <seittik.pipes.Pipe.rangetil>`

- {clj-core}`range`
- {js-fxts}`range`
- {py-builtins}`func-range`
- {py-itertools}`count`

Since including the upper bound is such a common scenario, two variants
are provided: `range` (inclusive on the upper bound) and `rangetil`
(exclusive on the upper bound).

I'm sure having the name `range` include the upper bound will be a tad
controversial, but almost the only time I find excluding it useful is
when using the builtin `range` for a numeric `for` loop. The rest of the
time, I'm using an upper bound number that's offset by `1` from the
number I actually care about.

#### {py:meth}`.repeat() <seittik.pipes.Pipe.repeat>`

- {js-fxts}`repeat`
- {hs-data-list}`repeat`
- {hs-data-list}`replicate`
- {js-lfi}`repeat`
- {py-itertools}`repeat`

#### {py:meth}`.repeatfunc() <seittik.pipes.Pipe.repeatfunc>`

- {py-more-itertools}`repeatfunc` (`itertools` recipe)

#### {py:meth}`.roll() <seittik.pipes.Pipe.roll>`

I love tabletop games. This supports the typical `'3d6'` and `'2d12+4'`
style of notation.

#### {py:meth}`.unfold() <seittik.pipes.Pipe.unfold>`

- {js-ramda}`unfold`
- {hs-data-list}`unfoldr`

#### {py:meth}`.values() <seittik.pipes.Pipe.values>`

- {py-stdtypes}`dict.values`

#### {py:meth}`.walk() <seittik.pipes.Pipe.walk>`

Iterating over all the nodes of a collection as `(parent, key, value)`
triples is a pattern I've had to implement countless times, until I sat
down and made a single function that handled pretty much all of my use
cases. It uses `deque` internally as a processing pipeline to avoid
recursion.

There are a bunch of options for BFS vs. DFS, maximum depth, controlling
what gets descended into and how, etc.

#### {py:meth}`.walkdir() <seittik.pipes.Pipe.walkdir>`

- `pathlib.Path.walk` in Python 3.12+

I made sure to match the same algorithm as the newer `pathlib.Path.walk`
method, as there are subtle differences between it and the existing
{external:py:func}`os.walk`.

### Pipe: Source/Step Hybrids

These can be used either to create a new data source, or as an
intermediate transformation of a pipe's data.

#### {py:meth}`.cartesian_product() <seittik.pipes.Pipe.cartesian_product>`

- {py-itertools}`product`

Not to be confused with {py:meth}`Pipe.product`, which performs
multiplication.

#### {py:meth}`.chain() <seittik.pipes.Pipe.chain>`

- {clj-core}`concat`
- {clj-medley}`join`
- {hs-data-list}`concat`
- {js-ramda}`unnest`
- {kt-collections}`flatten`
- {py-itertools}`chain`

For a more powerful variant, see {py:meth}`Pipe.flatten`.

#### {py:meth}`.interleave() <seittik.pipes.Pipe.interleave>`

- {clj-core}`interleave`
- {clj-medley}`interleave-all`
- {py-more-itertools}`interleave`
- {py-more-itertools}`interleave_longest`
- {py-more-itertools}`roundrobin` (`itertools` recipe)

#### {py:meth}`.struct_unpack() <seittik.pipes.Pipe.struct_unpack>`

- {py-struct}`iter_unpack`
- {py-struct}`unpack`

#### {py:meth}`.zip() <seittik.pipes.Pipe.zip>`

- {hs-data-list}`unzip`
- {hs-data-list}`zip`
- {js-fxts}`zip`
- {js-ramda}`zip`
- {py-builtins}`zip`
- {rb-enumerable}`zip`

This works as an `unzip`, too, so there's no need for a separate method.

### Pipe: Steps

These are intermediate transformations of a pipe's data.

#### {py:meth}`.broadcast() <seittik.pipes.Pipe.broadcast>`

I found myself frequently using a pattern where I wanted each iterator
value transformed into a tuple made of `n` copies of the same value, so
I could perform parallel transformations of the data in a subsequent
step.

I couldn't find a good existing name for this, other than "repetition"
(and "repeat" was already taken) or "echo" (which is strongly associated
with printing to a console), so I borrowed this partly from networking
terminology.

#### {py:meth}`.broadmap() <seittik.pipes.Pipe.broadmap>`

Combines {py:meth}`Pipe.broadcast` and {py:meth}`Pipe.map` in a single
operation. I use this for reporting on data while retaining the original
value via an identity function (such as a naked shear).

#### {py:meth}`.chunk() <seittik.pipes.Pipe.chunk>`

- {clj-core}`partition`
- {clj-core}`partition-all`
- {js-fxts}`chunk`
- {js-lfi}`chunked`
- {js-lfi}`windowed`
- {js-ramda}`splitEvery`
- {kt-collections}`chunked`
- {kt-collections}`windowed`
- {py-itertools}`pairwise` (`n=2` only, `step=1` only)
- {py-more-itertools}`chunked`
- {py-more-itertools}`grouper` (`itertools` recipe)
- {py-more-itertools}`sliced`
- {py-more-itertools}`sliding_window` (`step=1` only; `itertools`
  recipe)
- {py-more-itertools}`triplewise` (`n=3` only, `step=1` only;
  `itertools` recipe)
- {py-more-itertools}`windowed`
- {rb-enumerable}`each_cons` (`step=1` only)
- {rb-enumerable}`each_slice` (`step=n` only)

One chunker to rule them all.

Clojure's `partition` convinced me that chunking and windowing were
really the same operation.

#### {py:meth}`.chunkby() <seittik.pipes.Pipe.chunkby>`

- {clj-core}`partition-by`
- {hs-data-list}`groupBy`
- {js-ramda}`groupWith`
- {py-itertools}`groupby`
- {py-more-itertools}`batched` (`itertools` recipe)
- {py-more-itertools}`grouper` (`itertools` recipe)

Groups adjacent elements into tuples.

I felt both the name and behavior of `itertools.groupby` were confusing
and not as useful to work with; this `Pipe` step simply yields tuples of
adjacent items that have matching keys, without yielding the keys.

For behavior that groups all elements by a key function regardless of
their position in the source, see {py:meth}`Pipe.groupby`.

#### {py:meth}`.combinations() <seittik.pipes.Pipe.combinations>`

- {hs-data-list}`subsequences`
- {py-itertools}`combinations`
- {py-itertools}`combinations_with_replacement`

I saw no reason to keep these as separate functions.

#### {py:meth}`.cycle() <seittik.pipes.Pipe.cycle>`

- {clj-core}`cycle`
- {hs-data-list}`cycle`
- {js-fxts}`cycle`
- {js-lfi}`cycle`
- {py-itertools}`cycle`
- {py-more-itertools}`ncycles` (`itertools` recipe)
- {rb-enumerable}`cycle`

#### {py:meth}`.debug() <seittik.pipes.Pipe.debug>`

A simple printout of the current item.

#### {py:meth}`.depeat() <seittik.pipes.Pipe.depeat>`

- {clj-core}`dedupe`
- {clj-medley}`dedupe-by`
- {js-ramda}`dropRepeats`
- {py-more-itertools}`unique_justseen` (`itertools` recipe)

Not to be confused with `unique`, which removes *all* duplicates.

I wanted a short and memorable name that would stick in my mind for
"don't repeat", and this seemed to work.

#### {py:meth}`.dictmap() <seittik.pipes.Pipe.dictmap>`

Essentially combines {py:meth}`Pipe.broadmap` and {py:meth}`Pipe.label`
in a single operation. Better than `broadmap` if you need your data
labeled.

#### {py:meth}`.drop() <seittik.pipes.Pipe.drop>`

- {clj-core}`drop`
- {hs-data-list}`drop`
- {js-fxts}`drop`
- {js-lfi}`drop`
- {js-ramda}`drop`
- {kt-collections}`drop`
- {rb-enumerable}`drop`

#### {py:meth}`.dropwhile() <seittik.pipes.Pipe.dropwhile>`

- {clj-core}`drop-while`
- {hs-data-list}`dropWhile`
- {js-fxts}`dropWhile`
- {js-lfi}`dropWhile`
- {js-ramda}`dropWhile`
- {kt-collections}`dropWhile`
- {rb-enumerable}`drop_while`

#### {py:meth}`.enumerate() <seittik.pipes.Pipe.enumerate>`

- {clj-medley}`indexed`
- {js-fxts}`zipWithIndex`
- {py-builtins}`enumerate`
- {rb-enumerable}`each_with_index`

#### {py:meth}`.enumerate_info() <seittik.pipes.Pipe.enumerate_info>`

- {py-more-itertools}`mark_ends`

There are a bunch of iterator patterns that are made easier by knowing
if we're dealing with the first and/or last item.

#### {py:meth}`.filter() <seittik.pipes.Pipe.filter>`

- {clj-core}`filter`
- {hs-data-list}`filter`
- {js-fxts}`filter`
- {js-lfi}`filter`
- {js-ramda}`filter`
- {kt-collections}`filter`
- {py-builtins}`filter`
- {rb-enumerable}`find_all`

#### {py:meth}`.flatten() <seittik.pipes.Pipe.flatten>`

- {clj-core}`flatten`
- {js-fxts}`flat`
- {js-ramda}`flatten`
- {py-more-itertools}`collapse`
- {py-more-itertools}`flatten` (`itertools` recipe)

Internally calls the same logic as {py:meth}`Pipe.walk` to recursively
flatten either all levels of nesting, or a specified number.

#### {py:meth}`.intersperse() <seittik.pipes.Pipe.intersperse>`

- {clj-core}`interpose`
- {hs-data-list}`intersperse`
- {js-ramda}`intersperse`
- {py-more-itertools}`intersperse`

#### {py:meth}`.label() <seittik.pipes.Pipe.label>`

Sequence goes in, labeled `dict` comes out.

#### {py:meth}`.map() <seittik.pipes.Pipe.map>`

- {clj-core}`map`
- {hs-data-list}`map`
- {js-fxts}`map`
- {js-ramda}`map`
- {kt-collections}`map`
- {py-builtins}`map`
- {rb-enumerable}`collect`

#### {py:meth}`.peek() <seittik.pipes.Pipe.peek>`

There are a bunch of iterator patterns that are made easier by knowing
if we're dealing with the last item.

This is a building block for `enumerate_info`, which calls `.peek`
internally.

#### {py:meth}`.permutations() <seittik.pipes.Pipe.permutations>`

- {hs-data-list}`permutations`
- {py-itertools}`permutations`

#### {py:meth}`.reject() <seittik.pipes.Pipe.reject>`

- {clj-core}`remove`
- {js-fxts}`reject`
- {js-ramda}`reject`
- {kt-collections}`filterNot`
- {py-itertools}`filterfalse`
- {rb-enumerable}`reject`

`reject` feels like a cleaner name than `filterfalse`.

#### {py:meth}`.reverse() <seittik.pipes.Pipe.reverse>`

- {clj-core}`reverse`
- {hs-data-list}`reverse`
- {js-fxts}`reverse`
- {kt-collections}`reversed`
- {py-builtins}`reversed`
- {rb-enumerable}`reverse_each`

I prefer verb names over adjectives.

#### {py:meth}`.scan() <seittik.pipes.Pipe.scan>`

- {clj-core}`reductions`
- {hs-data-list}`scanl`
- {hs-data-list}`scanl1`
- {js-fxts}`scan`
- {js-ramda}`scan`
- {kt-collections}`runningFold`
- {kt-collections}`runningReduce`
- {kt-collections}`scan`
- {py-itertools}`accumulate`

#### {py:meth}`.sample() <seittik.pipes.Pipe.sample>`

- {py-more-itertools}`random_permutation`
- {py-random}`choices`
- {py-random}`sample`
- {py-random}`shuffle`

Supports arbitrary sample sizes both with, and without, replacement.

Without arguments, equivalent to yielding a shuffle.

A random permutation and a random sample (without replacement) are
actually the same thing.

#### {py:meth}`.slice() <seittik.pipes.Pipe.slice>`

- {clj-core}`take-nth` (using `step`)
- {js-fxts}`slice`
- {js-ramda}`slice`
- {kt-collections}`slice`
- {py-itertools}`islice`

#### {py:meth}`.sort() <seittik.pipes.Pipe.sort>`

- {clj-core}`sort`
- {clj-core}`sort-by`
- {hs-data-list}`sort`
- {hs-data-list}`sortOn`
- {js-fxts}`sort`
- {js-fxts}`sortBy`
- {js-ramda}`sort`
- {js-ramda}`sortBy`
- {kt-collections}`sorted`
- {kt-collections}`sortedBy`
- {kt-collections}`sortedByDescending`
- {kt-collections}`sortedDescending`
- {py-builtins}`sorted`
- {rb-enumerable}`sort`
- {rb-enumerable}`sort_by`

I prefer verb names over adjectives.

#### {py:meth}`.starmap() <seittik.pipes.Pipe.starmap>`

- {py-itertools}`starmap`

#### {py:meth}`.take() <seittik.pipes.Pipe.take>`

- {hs-data-list}`take`
- {js-fxts}`take`
- {js-lfi}`take`
- {js-ramda}`take`
- {kt-collections}`take`
- {py-more-itertools}`take` (`itertools` recipe)
- {rb-enumerable}`take`

#### {py:meth}`.takewhile() <seittik.pipes.Pipe.takewhile>`

- {clj-core}`take-while`
- {hs-data-list}`takeWhile`
- {js-fxts}`takeWhile`
- {js-lfi}`takeWhile`
- {js-ramda}`takeWhile`
- {kt-collections}`takeWhile`
- {py-itertools}`takewhile`
- {rb-enumerable}`take_while`

#### {py:meth}`.tap() <seittik.pipes.Pipe.tap>`

- {clj-core}`for`
- {js-fxts}`each`
- {js-fxts}`peek`
- {js-fxts}`tap`
- {js-ramda}`tap`
- {kt-collections}`forEach`
- {kt-collections}`onEach`

#### {py:meth}`.unique() <seittik.pipes.Pipe.unique>`

- {clj-core}`distinct`
- {clj-medley}`distinct-by`
- {hs-data-list}`nub`
- {hs-data-list}`nubBy`
- {js-fxts}`uniq`
- {js-fxts}`uniqBy`
- {js-lfi}`unique`
- {js-ramda}`uniq`
- {js-ramda}`uniqBy`
- {kt-collections}`distinct`
- {kt-collections}`distinctBy`
- {py-more-itertools}`unique_everseen` (`itertools` recipe)
- {rb-enumerable}`uniq`

Not to be confused with `depeat`, which only removes *consecutive*
duplicates.

### Pipe: Sinks: containers

These are terminal transformations of a pipe that result in a single new
container.

#### {py:meth}`.array() <seittik.pipes.Pipe.array>`

- {py-array}`array`

#### {py:meth}`.bytes() <seittik.pipes.Pipe.bytes>`

- {py-builtins}`func-bytes`

#### {py:meth}`.deque() <seittik.pipes.Pipe.deque>`

- {py-collections}`deque`

#### {py:meth}`.dict() <seittik.pipes.Pipe.dict>`

- {py-builtins}`func-dict`

#### {py:meth}`.list() <seittik.pipes.Pipe.list>`

- {py-builtins}`func-list`

#### {py:meth}`.set() <seittik.pipes.Pipe.set>`

- {clj-core}`set`
- {py-builtins}`func-set`

#### {py:meth}`.str() <seittik.pipes.Pipe.str>`

- {js-fxts}`join`
- {py-builtins}`func-str`

#### {py:meth}`.tuple() <seittik.pipes.Pipe.tuple>`

- {py-builtins}`func-tuple`

### Pipe: Sinks: non-containers

These are all other terminal transformations of a pipe.

#### {py:meth}`.all() <seittik.pipes.Pipe.all>`

- {clj-core}`every?`
- {hs-data-list}`all`
- {js-fxts}`every`
- {js-ramda}`all`
- {kt-collections}`all`
- {py-builtins}`all`
- {rb-enumerable}`all?`

#### {py:meth}`.any() <seittik.pipes.Pipe.any>`

- {hs-data-list}`any`
- {js-fxts}`some`
- {js-ramda}`any`
- {kt-collections}`any`
- {py-builtins}`any`
- {rb-enumerable}`any?`

#### {py:meth}`.contains() <seittik.pipes.Pipe.contains>`

- {clj-core}`contains?` (not quite?)
- {hs-data-list}`elem`
- {kt-collections}`contains`
- {rb-enumerable}`member?`

#### {py:meth}`.count() <seittik.pipes.Pipe.count>`

- {clj-core}`count`
- {hs-data-list}`length`
- {js-fxts}`size`
- {kt-collections}`count`
- {py-builtins}`len`
- {py-more-itertools}`ilen`
- {rb-enumerable}`count`

I went with SQL's `COUNT` as the most intuitive name, since we're
effectively counting items "as they go by".

#### {py:meth}`.equal() <seittik.pipes.Pipe.equal>`

- {js-ramda}`equals`
- {py-more-itertools}`all_equal` (`itertools` recipe)

#### {py:meth}`.exhaust() <seittik.pipes.Pipe.exhaust>`

- {js-fxts}`consume`
- {py-more-itertools}`consume` (`itertools` recipe)

This performs a full exhaustion of the source, and has no options to
partially consume it; use {py:meth}`Pipe.drop` for that.

#### {py:meth}`.fold() <seittik.pipes.Pipe.fold>`

- {clj-core}`reduce`
- {hs-data-list}`foldl`
- {hs-data-list}`foldl1`
- {js-fxts}`reduce`
- {js-lfi}`fold`
- {js-lfi}`reduce`
- {js-ramda}`reduce`
- {kt-collections}`fold`
- {kt-collections}`reduce`
- {py-functools}`reduce`
- {rb-enumerable}`inject`

This name just comes down to subjective preference.

#### {py:meth}`.frequencies() <seittik.pipes.Pipe.frequencies>`

- {clj-core}`frequencies`
- {py-collections}`Counter`
- {rb-enumerable}`tally`

#### {py:meth}`.groupby() <seittik.pipes.Pipe.groupby>`

- {clj-core}`group-by`
- {js-fxts}`groupBy`
- {js-ramda}`groupBy`
- {rb-enumerable}`group_by`

This is akin to SQL's `GROUP BY`, and *not* like `itertools.groupby`.

For behavior that only groups adjacent elements, see
{py:meth}`Pipe.chunkby`.

#### {py:meth}`.identical() <seittik.pipes.Pipe.identical>`

- {js-ramda}`identical`

#### {py:meth}`.max() <seittik.pipes.Pipe.max>`

- {clj-medley}`greatest`
- {clj-medley}`greatest-by`
- {hs-data-list}`maximum`
- {hs-data-list}`maximumBy`
- {js-fxts}`max`
- {js-lfi}`max`
- {js-lfi}`maxBy`
- {js-ramda}`max`
- {js-ramda}`maxBy`
- {kt-collections}`max`
- {kt-collections}`maxBy`
- {kt-collections}`maxByOrNull`
- {kt-collections}`maxOrNull`
- {py-builtins}`max`
- {rb-enumerable}`max`
- {rb-enumerable}`max_by`

#### {py:meth}`.mean() <seittik.pipes.Pipe.mean>`

- {js-fxts}`average`
- {js-ramda}`mean`
- {kt-collections}`average`
- {py-statistics}`mean`

#### {py:meth}`.median() <seittik.pipes.Pipe.median>`

- {js-ramda}`median`
- {py-statistics}`median`

#### {py:meth}`.min() <seittik.pipes.Pipe.min>`

- {clj-medley}`least`
- {clj-medley}`least-by`
- {hs-data-list}`minimum`
- {hs-data-list}`minimumBy`
- {js-fxts}`min`
- {js-lfi}`min`
- {js-lfi}`minBy`
- {js-ramda}`min`
- {js-ramda}`minBy`
- {kt-collections}`min`
- {kt-collections}`minBy`
- {kt-collections}`minByOrNull`
- {kt-collections}`minOrNull`
- {py-builtins}`min`
- {rb-enumerable}`min`
- {rb-enumerable}`min_by`

#### {py:meth}`.minmax() <seittik.pipes.Pipe.minmax>`

- {js-lfi}`minmax`
- {js-lfi}`minmaxby`
- {py-more-itertools}`minmax`
- {rb-enumerable}`minmax`
- {rb-enumerable}`minmax_by`

#### {py:meth}`.mode() <seittik.pipes.Pipe.mode>`

- {py-statistics}`mode`

#### {py:meth}`.none() <seittik.pipes.Pipe.none>`

- {js-ramda}`none`
- {kt-collections}`none`
- {rb-enumerable}`none?`

#### {py:meth}`.nth() <seittik.pipes.Pipe.nth>`

- {clj-core}`nth`
- {js-fxts}`nth`
- {js-ramda}`nth`
- {kt-collections}`elementAt`
- {kt-collections}`elementAtOrElse`
- {kt-collections}`elementAtOrNull`
- {py-more-itertools}`nth` (`itertools` recipe)

#### {py:meth}`.struct_pack() <seittik.pipes.Pipe.struct_pack>`

- {py-struct}`pack`

#### {py:meth}`.partition() <seittik.pipes.Pipe.partition>`

- {hs-data-list}`partition`
- {js-fxts}`partition`
- {js-ramda}`partition`
- {kt-collections}`partition`
- {py-more-itertools}`partition` (`itertools` recipe)
- {rb-enumerable}`partition`

It drives me crazy that some implementations return the true list first,
and others return the false set first.

#### {py:meth}`.product() <seittik.pipes.Pipe.product>`

- {hs-data-list}`product`
- {py-math}`prod`

Not to be confused with {py:meth}`Pipe.cartesian_product`.

#### {py:meth}`.shuffle() <seittik.pipes.Pipe.shuffle>`

- {py-random}`shuffle`

{py:meth}`Pipe.sample` is more flexible, but sometimes all you want is a
single shuffle.

#### {py:meth}`.stdev() <seittik.pipes.Pipe.stdev>`

- {py-statistics}`pstdev`
- {py-statistics}`stdev`

It strikes me as odd that Python's {external:py:mod}`statistics` module
treats the *sample* standard deviation as "standard" and the
*population* standard deviation as a variant. I merged them into a
single method via a flag, with population being the default.

#### {py:meth}`.sum() <seittik.pipes.Pipe.sum>`

- {hs-data-list}`sum`
- {js-fxts}`sum`
- {kt-collections}`sum`
- {py-builtins}`sum`
- {rb-enumerable}`sum`

#### {py:meth}`.variance() <seittik.pipes.Pipe.variance>`

- {py-statistics}`pvariance`
- {py-statistics}`variance`

The same discussion for `stdev` above applies here.

#### {py:meth}`.width() <seittik.pipes.Pipe.width>`

This is the same as `.max() - .min()`, the statistical "range".
