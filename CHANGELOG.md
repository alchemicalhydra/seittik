# Changelog

For full details, see the [commit
history](https://github.com/alchemicalhydra/seittik/commits/master).

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
