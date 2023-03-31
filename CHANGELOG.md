# Changelog

For full details, see the [commit
history](https://github.com/alchemicalhydra/seittik/commits/master).

## 2023.03.5 (2023-03-30)

- A first draft of a User Guide was added to the docs
- Teach Pipes sinks to act as partials when missing sources
  - Entire pipe instances can now be used as partials
- Fix `{ipython}` directive to work without `{eval-rst}`
- Fix `{ipython}` directive's `:doctest:` option
- Add a global `ipython_doctest` flag
- Guard against accidental infinite loops from shears, e.g., `foo in X`
- Clean up `Pipe.__repr__` a bit more
- The cross-references section of the Design Notes was further fleshed
  out

## 2023.03.4 (2023-03-28)

- Add `Pipe.remap` step
- Add `Pipe.sponge` step
- Add `Pipe.merge` sink
- Add various internal helpers and reduce boilerplate code.
- Minor cleanups/fixes.

## 2023.03.3 (2023-03-24)

- Add `Pipe.clamp` step
- Add `Pipe.split` step
- Add new append/prepend steps:
  - `Pipe.append`
  - `Pipe.prepend`
  - `Pipe.concat`
  - `Pipe.precat`
- Add new mapping sources:
  - `Pipe.keys`
  - `Pipe.values`
  - `Pipe.items`
- **Breaking change:** Rename `Pipe.pack` to `Pipe.struct_pack`
- **Breaking change:** Rename `Pipe.unpack` to `Pipe.struct_unpack`
- Fix sentinels to no longer be callables.
- Fix the license getting Python syntax highlighting on the
  documentation site.
- Fix the Ruby cross-reference links to always point to the current Ruby
  version's docs.
- Make minor documentation fixes.
- Poetry settings were changed to undo breakage from upstream changes
  there.
  - Details:
    - https://github.com/python-poetry/poetry/pull/7358
    - https://github.com/pydata/pydata-sphinx-theme/issues/1253
- Development dependencies were updated.

## 2023.03.2 (2023-03-22)

- `Pipe` now supports pluggable random number generators (RNGs), along
  with two new methods:
  - `Pipe.set_rng`
  - `Pipe.seed_rng`
- The internal stage evaluation protocol was further improved:
  - The internal `Pipe` step/sink evaluation protocol was extended to
    sources as well.
  - "Stages" is the new collective term for sources, steps, and sinks.
  - The internal `Pipe` stage evaluation protocol now supports mutable
    sequences as distinct from normal sequences.
  - The internal `Pipe` stage evaluation protocol now supports requesting
    the Pipe's RNG via dependency injection.
- A new source, `Pipe.randfloat`, was added.
- A new sink, `Pipe.shuffle`, was added.
- **Breaking change:** The `Pipe.random_permutations` step was
  refactored into `Pipe.sample`.
- **Breaking change:** Various statistical and set-theory Pipe methods had
  their `r` parameters renamed to `k`.
- The cross-references section of the Design Notes was further fleshed
  out.
- The `sphinx.ext.extlinks` Sphinx extension was replaced with one of our
  own that allows for more flexibility in massaging URLs and captions.
- The `Pipe.zip` documentation saw a minor correction.
- Nox was set up for multi-version testing.
- Development dependencies were updated.

## 2023.03.1 (2023-03-20)

- The internal step/sink evaluation protocol is greatly improved.
  - It now leverages dependency injection so steps and sinks can request
    specifically what they need from the previous result (e.g., an iterator,
    a sequence, the result wrapped in a new Pipe).
  - This allows us to preserve iterators and sequences for as long as
    possible in the pipeline, avoiding unnecessary and expensive coercions.
  - This also allows us to intelligently dispatch based on whether an
    iterator or a sequence is received; for instance, we can directly index
    if we receive a sequence in the `Pipe.nth` sink, instead of slowly
    iterating.
- `Pipe.interleave` had some minor implementation issues that were
  corrected.
- The various marble diagrams were cleaned up (and an erroneous label
  corrected in one case).
- Development dependencies were updated.

## 2023.03 (2023-03-18)

Initial release.
