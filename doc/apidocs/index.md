# API Reference

```{toctree}
:hidden:
seittik/seittik
```

```{autodoc2-summary}
seittik
```

## Pipes

```{autodoc2-summary}
seittik.pipes
```

### Sources: General

```{autodoc2-summary}
seittik.pipes.Pipe
seittik.pipes.Pipe.iterfunc
seittik.pipes.Pipe.range
seittik.pipes.Pipe.rangetil
seittik.pipes.Pipe.repeat
seittik.pipes.Pipe.repeatfunc
seittik.pipes.Pipe.unfold
seittik.pipes.Pipe.walk
```

### Sources: Mappings

```{autodoc2-summary}
seittik.pipes.Pipe.items
seittik.pipes.Pipe.keys
seittik.pipes.Pipe.values
```

### Sources: Paths

```{autodoc2-summary}
seittik.pipes.Pipe.iterdir
seittik.pipes.Pipe.walkdir
```

### Sources: Random

```{autodoc2-summary}
seittik.pipes.Pipe.randfloat
seittik.pipes.Pipe.randrange
seittik.pipes.Pipe.roll
```

### Source/Step Hybrids

These act as sources when used as class methods, and steps otherwise.

```{autodoc2-summary}
seittik.pipes.Pipe.cartesian_product
seittik.pipes.Pipe.chain
seittik.pipes.Pipe.interleave
seittik.pipes.Pipe.struct_unpack
seittik.pipes.Pipe.zip
```

### Steps: Filtering/Shortening

```{autodoc2-summary}
seittik.pipes.Pipe.depeat
seittik.pipes.Pipe.drop
seittik.pipes.Pipe.dropwhile
seittik.pipes.Pipe.filter
seittik.pipes.Pipe.reject
seittik.pipes.Pipe.slice
seittik.pipes.Pipe.take
seittik.pipes.Pipe.takewhile
seittik.pipes.Pipe.unique
```

### Steps: Lengthening

```{autodoc2-summary}
seittik.pipes.Pipe.append
seittik.pipes.Pipe.concat
seittik.pipes.Pipe.cycle
seittik.pipes.Pipe.intersperse
seittik.pipes.Pipe.precat
seittik.pipes.Pipe.prepend
```

### Steps: Chunking, Flattening, and Grouping

```{autodoc2-summary}
seittik.pipes.Pipe.chunk
seittik.pipes.Pipe.chunkby
seittik.pipes.Pipe.flatten
```

### Steps: Ordering

```{autodoc2-summary}
seittik.pipes.Pipe.reverse
seittik.pipes.Pipe.sort
```

### Steps: Mapping/Transforming

```{autodoc2-summary}
seittik.pipes.Pipe.broadcast
seittik.pipes.Pipe.broadmap
seittik.pipes.Pipe.dictmap
seittik.pipes.Pipe.label
seittik.pipes.Pipe.map
seittik.pipes.Pipe.scan
seittik.pipes.Pipe.starmap
```

### Steps: Combinations/Permutations

```{autodoc2-summary}
seittik.pipes.Pipe.combinations
seittik.pipes.Pipe.permutations
```

### Steps: Randomness/Statistics

```{autodoc2-summary}
seittik.pipes.Pipe.sample
```

### Steps: Extra Info

```{autodoc2-summary}
seittik.pipes.Pipe.enumerate
seittik.pipes.Pipe.enumerate_info
seittik.pipes.Pipe.peek
```

### Steps: Side Effects

```{autodoc2-summary}
seittik.pipes.Pipe.tap
```

### Steps: RNG Control

```{autodoc2-summary}
seittik.pipes.Pipe.set_rng
seittik.pipes.Pipe.seed_rng
```

### Sinks: Collections

```{autodoc2-summary}
seittik.pipes.Pipe.array
seittik.pipes.Pipe.bytes
seittik.pipes.Pipe.deque
seittik.pipes.Pipe.dict
seittik.pipes.Pipe.list
seittik.pipes.Pipe.set
seittik.pipes.Pipe.str
seittik.pipes.Pipe.tuple
```

### Sinks: Math/Randomness/Statistics

```{autodoc2-summary}
seittik.pipes.Pipe.frequencies
seittik.pipes.Pipe.max
seittik.pipes.Pipe.mean
seittik.pipes.Pipe.median
seittik.pipes.Pipe.min
seittik.pipes.Pipe.minmax
seittik.pipes.Pipe.mode
seittik.pipes.Pipe.product
seittik.pipes.Pipe.shuffle
seittik.pipes.Pipe.stdev
seittik.pipes.Pipe.sum
seittik.pipes.Pipe.variance
seittik.pipes.Pipe.width
```

### Sinks: Predicate Tests

```{autodoc2-summary}
seittik.pipes.Pipe.all
seittik.pipes.Pipe.any
seittik.pipes.Pipe.contains
seittik.pipes.Pipe.equal
seittik.pipes.Pipe.identical
seittik.pipes.Pipe.none
```

### Sinks: Sorting/Binning

```{autodoc2-summary}
seittik.pipes.Pipe.groupby
seittik.pipes.Pipe.partition
```

### Sinks: Miscellaneous

```{autodoc2-summary}
seittik.pipes.Pipe.count
seittik.pipes.Pipe.exhaust
seittik.pipes.Pipe.fold
seittik.pipes.Pipe.nth
seittik.pipes.Pipe.struct_pack
```

## Shears

```{autodoc2-summary}
seittik.shears
```

```{autodoc2-summary}
seittik.shears.ShearVar
```

