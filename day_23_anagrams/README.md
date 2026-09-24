# Day 23 — Anagrams

## Topic overview

An anagram is a string or sequence formed by rearranging the characters of another string while preserving the number of occurrences of every character.

For example:

- `listen` and `silent` are anagrams.
- `triangle` and `integral` are anagrams.
- `hello` and `world` are not anagrams.
- `aabb` and `abab` are anagrams because both contain two `a` characters and two `b` characters.

The central computational question is:

> Do two sequences contain exactly the same elements with exactly the same frequencies?

The answer depends on the problem definition. Some problems treat uppercase and lowercase letters as different. Others ignore case. Some ignore spaces and punctuation. Some restrict the input to lowercase English letters. Others require Unicode-aware processing.

This distinction is important because an algorithm can be correct for one definition and incorrect for another.

The implementations in this repository demonstrate three major programming approaches:

- Python for algorithmic exploration, reusable abstractions, testing, normalization, and multiple implementations.
- JavaScript for practical application-level implementations using objects, `Map`, typed arrays, classes, and executable runtime behavior.
- C++ for an industry-style text-record indexing system using classes, fixed-size frequency arrays, hashing, validation, sliding windows, and performance analysis.

---

## Fundamental concept

Two strings are anagrams when their character-frequency distributions are identical.

For example:

`listen`

has the frequency distribution:

- `l` → 1
- `i` → 1
- `s` → 1
- `t` → 1
- `e` → 1
- `n` → 1

`silent` has the same frequencies.

The ordering differs, but the frequency distribution is identical.

This gives two fundamental ways to solve the problem:

1. Put both strings into a common canonical order and compare them.
2. Count every character and compare the resulting frequencies.

---

## Important terminology

### Character

A character is an individual element of a textual sequence.

For basic English examples, characters may be letters such as `a`, `b`, or `z`.

For Unicode text, the concept becomes more complicated because a visible symbol can consist of multiple code points or combining characters.

### Frequency

Frequency means the number of times an element occurs.

For `banana`:

- `b` occurs once.
- `a` occurs three times.
- `n` occurs twice.

### Frequency map

A frequency map stores an association between an element and its count.

Conceptually:

`character → count`

Python can represent this with `dict` or `collections.Counter`.

JavaScript can use `Map` or an object.

C++ can use `unordered_map`, `map`, or a fixed-size array when the alphabet is known.

### Canonical representation

A canonical representation converts equivalent inputs into the same representation.

For anagrams, sorting can provide a canonical representation.

The words `listen`, `silent`, and `enlist` all produce the same sorted signature:

`eilnst`

If two strings have the same sorted signature, they are anagrams.

### Character alphabet

An alphabet is the set of characters permitted by a problem.

A problem may specify:

- lowercase English letters,
- uppercase and lowercase English letters,
- ASCII characters,
- arbitrary Unicode characters,
- digits and letters,
- or another explicitly defined character set.

The choice affects the data structure and complexity.

---

## Sorting-based anagram checking

The simplest general technique is sorting.

Given two strings:

1. Sort the first string.
2. Sort the second string.
3. Compare the sorted results.

For example:

`listen`

becomes:

`eilnst`

and:

`silent`

also becomes:

`eilnst`

Therefore they are anagrams.

The Python implementation is represented by `are_anagrams_sorting`.

The JavaScript implementation is represented by `areAnagramsSorting`.

The C++ implementation is represented by `areAnagramsBySorting`.

### Complexity

For a string of length `n`:

- Sorting requires approximately `O(n log n)` time.
- The sorted representations require `O(n)` additional storage in typical implementations.

This method is easy to understand and is useful when simplicity is more important than optimal asymptotic performance.

### Advantages

Sorting-based comparison:

- is conceptually simple,
- is easy to verify,
- works for arbitrary sortable characters,
- provides a useful canonical representation,
- is convenient for grouping anagrams.

### Limitations

Sorting:

- is slower asymptotically than linear frequency counting,
- performs work that is unnecessary when only frequencies matter,
- requires rearranging or copying the data.

---

## Frequency-based checking

Anagram checking can be performed directly through character counts.

For:

`listen`

the frequency map is equivalent to:

`{l: 1, i: 1, s: 1, t: 1, e: 1, n: 1}`

For:

`silent`

the frequency map contains exactly the same counts.

Therefore the strings are anagrams.

The Python implementation contains both a manually constructed dictionary frequency map and `collections.Counter`.

The JavaScript implementation demonstrates both object-based and `Map`-based frequency counting.

The C++ implementation uses a fixed-size `array<int, 26>` because the case study explicitly restricts normalized input to lowercase English letters.

### Complexity

For a general frequency map:

- Time: `O(n)` average.
- Space: `O(k)`.

Here, `k` represents the number of distinct characters.

If the alphabet is fixed and small, the auxiliary space can be considered constant.

---

## Character maps

A character map stores the number of occurrences of each character.

The Python function `character_frequency` demonstrates manual frequency counting:

- Read one character.
- Look up its current count.
- Increment the count.
- Continue until the string is exhausted.

The JavaScript implementation demonstrates:

- object-based frequency counting,
- `Map`-based frequency counting.

The C++ implementation demonstrates a fixed array because the allowed alphabet is known.

### Dictionary versus fixed array

A dictionary or hash map is useful when the character universe is unknown or large.

A fixed array is useful when the alphabet is small and known.

For lowercase English letters:

`a` through `z`

only 26 counters are needed.

A character can be mapped to an array index using its numeric character code.

For example:

`a` → `0`

`b` → `1`

`z` → `25`

This avoids hash-table operations and gives predictable memory usage.

---

## Python implementation

The Python program provides several levels of implementation.

### Sorting

`are_anagrams_sorting` compares sorted strings.

The optional normalization parameter allows the same function to support a different problem definition.

For example, with normalization enabled:

`Dormitory`

and:

`Dirty room`

can be treated as equivalent because spaces and case are ignored.

### Manual frequency dictionary

`character_frequency` demonstrates the fundamental frequency-map algorithm without hiding the mechanism behind a library function.

The implementation uses:

`frequencies.get(character, 0) + 1`

This is useful for understanding what a frequency counter actually does internally.

### Counter

`are_anagrams_counter` uses Python's `Counter`.

`Counter` is a specialized frequency-counting data structure and provides a concise representation of the same concept.

### Fixed alphabet

`are_anagrams_ascii_array` demonstrates the fixed-array technique.

This implementation is intentionally restricted to ASCII English letters because a fixed 26-element array cannot represent an arbitrary Unicode alphabet.

### Grouping

`group_anagrams_sorting` groups strings according to their sorted-character signature.

For example:

`eat`, `tea`, and `ate`

share the same signature.

`tan` and `nat`

share another signature.

### Frequency-based grouping

`group_anagrams_frequency` uses a 26-element frequency tuple as the group key.

This avoids sorting each individual word.

### Anagram windows

`find_anagram_windows` finds every substring whose character frequencies equal those of a pattern.

For:

`text = "cbaebabacd"`

and:

`pattern = "abc"`

the result is:

`[0, 6]`

The substring beginning at index `0` is `cba`.

The substring beginning at index `6` is `bac`.

Both are permutations of `abc`.

### Optimized windows

`find_anagram_windows_optimized` maintains a fixed 26-element frequency state.

It also maintains a `matches` value representing how many character counts currently match the pattern.

This avoids comparing an entire frequency map for every window.

---

## JavaScript implementation

JavaScript provides several useful ways to represent character frequencies.

### Object frequency map

`characterFrequencyObject` creates an object without a normal prototype.

This prevents inherited property names from interfering with character keys.

The object is suitable for straightforward frequency counting.

### Map

`characterFrequencyMap` uses JavaScript's `Map`.

`Map` explicitly represents key-value associations and is convenient when keys are dynamic.

The implementation uses:

`character -> frequency`

and the helper `mapsEqual` compares two maps.

### Typed array

The JavaScript implementation uses `Int32Array(26)` for the fixed ASCII alphabet.

Typed arrays provide compact numeric storage and are appropriate when the problem has a fixed numeric state.

### Unicode iteration

JavaScript's `Array.from` is used in several places rather than relying exclusively on indexing.

This is important because JavaScript strings use UTF-16 internally, meaning some Unicode code points occupy more than one UTF-16 code unit.

Using `Array.from` provides code-point-oriented iteration for many common Unicode cases.

It does not fully solve every Unicode text problem. Grapheme clusters, normalization forms, combining characters, and locale-specific behavior can require additional processing.

---

## C++ case study

The C++ program models an industry-style text-record indexing service.

Each record contains:

- an integer record ID,
- the original text,
- a normalized representation.

The system accepts textual records and indexes them by an anagram signature.

### Example records

The case study includes records such as:

`Listen`

`Silent`

`Enlist`

and:

`Debit Card`

`card debit`

After normalization, equivalent character collections receive the same signature.

### Record index

`AnagramRecordIndex` maintains:

- record storage,
- signature-to-record mappings,
- record lookup,
- anagram queries,
- group counts.

The main structure is an `unordered_map`.

The key is a frequency signature.

The value is a collection of record IDs belonging to that anagram class.

### Why use a frequency signature?

Sorting produces a signature that can be easy to understand.

For a large indexing service, a fixed frequency representation can be more efficient when the alphabet is known.

The C++ implementation uses 26 counts:

`a` through `z`.

Those counts are serialized into a deterministic string signature.

Two normalized strings with identical frequencies therefore receive the same signature.

---

## C++ normalization

The C++ case study deliberately uses ASCII letters.

The normalization function:

`normalizeAsciiLetters`

does three things:

1. Converts uppercase ASCII letters to lowercase.
2. Keeps lowercase ASCII letters.
3. Removes other characters.

For example:

`Debit Card`

becomes:

`debitcard`

and:

`card debit`

also becomes:

`carddebit`

Both contain the same character frequencies.

### Why not implement arbitrary Unicode directly?

Unicode text processing is significantly more complex than ASCII processing.

A production implementation may need to consider:

- Unicode code points,
- normalization forms,
- combining marks,
- grapheme clusters,
- locale-sensitive case conversion,
- canonical equivalence.

Treating raw bytes as independent characters can produce incorrect results for general Unicode text.

The case study therefore makes its ASCII constraint explicit instead of silently pretending to support all Unicode text.

---

## Grouping anagrams

Grouping anagrams is a natural extension of pairwise anagram checking.

Given:

`["eat", "tea", "tan", "ate", "nat", "bat"]`

the expected conceptual groups are:

- `eat`, `tea`, `ate`
- `tan`, `nat`
- `bat`

The key insight is that every anagram in the same group has the same signature.

### Sorting signature

A sorting signature can be created by:

1. copying the word,
2. sorting its characters,
3. using the sorted result as the key.

This gives:

`eat` → `aet`

`tea` → `aet`

`ate` → `aet`

### Frequency signature

A frequency signature instead records the number of occurrences of every alphabet character.

For a fixed alphabet, this has predictable size.

This approach avoids sorting each individual word.

---

## Anagram detection

Anagram detection can mean several related problems.

### Pair detection

Given a collection of words, identify pairs that are anagrams.

A naive solution compares every pair.

For `n` words, there are approximately:

`n(n - 1) / 2`

pairs.

This gives quadratic pair-count growth.

The Python implementation contains both a grouped approach and a naive approach for comparison.

### Group-based detection

A more scalable strategy is:

1. Compute a signature for each word.
2. Store words by signature.
3. Generate pairs only inside matching groups.

This avoids performing a full anagram comparison against every unrelated word.

---

## Anagram windows

An anagram window problem asks whether any contiguous substring of a larger string is an anagram of a smaller pattern.

Example:

`text = "cbaebabacd"`

`pattern = "abc"`

The valid windows begin at:

`0`

and:

`6`

The important property is that the window has a fixed size equal to the pattern length.

Instead of repeatedly sorting every substring, a sliding-window algorithm maintains character frequencies.

---

## Sliding-window mechanism

Suppose the pattern has length `m`.

The first window contains the first `m` characters.

Then the window moves one position to the right.

One character:

- enters the window.

One character:

- leaves the window.

The algorithm updates only those two frequencies.

This is much more efficient than reconstructing the complete frequency distribution from scratch for every position.

### Window example

For:

`text = "abab"`

and:

`pattern = "ab"`

the windows are:

- `ab`
- `ba`
- `ab`

All three have the same frequency distribution.

Therefore the result is:

`[0, 1, 2]`

---

## Frequency matching

Frequency matching is the central mechanism behind the optimized sliding-window algorithm.

Suppose the pattern frequency is:

`a → 1`

`b → 1`

`c → 1`

A window is a valid anagram exactly when its frequencies are identical.

A naive sliding-window implementation can compare two maps after every movement.

A more optimized implementation maintains a state representing how many frequency positions currently match.

For a 26-character alphabet, there are only 26 positions to maintain.

When one character enters or leaves:

1. Its old equality state is recorded.
2. Its frequency is updated.
3. Its new equality state is recorded.
4. The number of matching frequency positions is adjusted.

A complete window match occurs when all 26 frequency positions match.

This makes the update operation constant time.

---

## Complexity comparison

| Technique | Typical time | Auxiliary space | Main characteristic |
|---|---:|---:|---|
| Sorting comparison | `O(n log n)` | `O(n)` | Simple canonical representation |
| Dictionary frequency | `O(n)` average | `O(k)` | General character support |
| `Counter` | `O(n)` average | `O(k)` | Concise Python implementation |
| Fixed 26-element array | `O(n)` | `O(1)` | Efficient fixed alphabet |
| Grouping by sorting | `O(n × m log m)` | Depends on groups | Simple grouping key |
| Grouping by frequency | `O(n × m)` | Depends on groups | Efficient fixed alphabet |
| Naive pair detection | `O(n² × m)` | Varies | Simple but scales poorly |
| Sliding-window search | Approximately `O(n)` | `O(k)` | Efficient moving-window state |
| Optimized ASCII window | `O(n)` | `O(1)` | Fixed alphabet and constant-size state |

Here:

- `n` is generally the length of a string or the size of the larger text.
- `m` is the typical word or pattern length.
- `k` is the number of distinct characters.

Average-time hash-map complexity assumes typical hash-table behavior.

---

## Important distinction: exact versus normalized anagrams

Anagram algorithms do not automatically know what the problem means by "same."

Consider:

`A`

and:

`a`

They are not exact matches under a case-sensitive definition.

They may be considered equivalent under a case-insensitive definition.

Similarly:

`rail safety`

and:

`fairy tales`

are only anagrams if spaces are ignored.

A correct implementation must establish the normalization rules before selecting the algorithm.

---

## Case sensitivity

There are at least two common interpretations.

### Case-sensitive

`A` and `a` are different characters.

### Case-insensitive

`A` and `a` are treated as equivalent.

The implementations expose normalization explicitly rather than silently applying one interpretation to every problem.

---

## Spaces and punctuation

A problem may:

- treat spaces as meaningful characters,
- ignore spaces,
- ignore punctuation,
- ignore both spaces and punctuation.

For example:

`a gentleman`

and:

`elegant man`

can only be treated as anagrams if the problem ignores spaces.

The normalization functions in Python and JavaScript demonstrate this behavior.

The C++ case study removes all non-ASCII letters.

---

## Unicode considerations

ASCII and Unicode should not be treated as interchangeable concepts.

For basic algorithm problems, the alphabet is often explicitly limited to lowercase English letters.

That makes a 26-element frequency array appropriate.

For unrestricted Unicode text, a frequency map is more general.

Even a Unicode code-point map is not always enough to model user-visible characters correctly because one visible grapheme can consist of multiple code points.

Examples can involve:

- accented characters,
- combining marks,
- emoji sequences,
- variation selectors,
- zero-width joiners.

Production systems that require full Unicode equivalence should define normalization semantics explicitly.

---

## Empty strings

Two empty strings contain the same number of every character.

Therefore they are anagrams under the standard mathematical definition.

The implementations treat:

`""`

and:

`""`

as anagrams.

An empty pattern in a window-search problem is a separate design question. The implementations return an empty result for an empty pattern rather than treating every position as a match.

This is a deliberate API choice.

---

## Unequal lengths

If two strings have different lengths, they cannot be anagrams under the standard definition.

This provides an important early-exit optimization.

For example:

`abc`

and:

`abcd`

can immediately return `false`.

No frequency counting or sorting is required.

---

## Repeated characters

Repeated characters are fundamental to anagram checking.

For example:

`aabb`

and:

`abab`

are anagrams.

But:

`aabb`

and:

`abbb`

are not.

An algorithm that checks only whether the same unique characters exist is incorrect because it ignores multiplicity.

Frequency counting solves this by preserving the number of occurrences.

---

## Common mistakes

### Checking only character membership

An implementation may incorrectly verify that every character from one string appears in the other.

This fails for repeated characters.

`aab`

and:

`abb`

contain the same unique characters but are not anagrams.

### Forgetting length checks

A length check is a cheap early rejection condition.

### Sorting without normalization

Sorting is correct only relative to the characters being sorted.

If the problem says to ignore spaces, spaces must be removed first.

### Using a fixed alphabet for unrestricted text

A 26-element array cannot represent arbitrary Unicode characters.

### Comparing only sets

Sets discard duplicate counts.

Anagrams require multiplicity, not only membership.

### Rebuilding every sliding-window frequency map

This can introduce unnecessary work.

The sliding-window technique exists specifically to update the previous window incrementally.

### Confusing byte length and character length

This is particularly important in languages and environments with Unicode text.

---

## Python implementation details

The Python implementation demonstrates:

- normal `dict` frequency maps,
- `Counter`,
- fixed-size frequency arrays,
- sorting signatures,
- frequency signatures,
- grouping,
- pair detection,
- sliding windows,
- optimized sliding windows,
- reusable `FrequencyMap`,
- reusable `AnagramIndex`,
- assertions,
- performance measurement,
- error handling.

The script is designed as an executable study file rather than a collection of isolated definitions.

The `main` function runs the demonstrations sequentially.

---

## JavaScript implementation details

The JavaScript implementation demonstrates:

- sorting strings through arrays,
- object-based frequency maps,
- `Map`,
- typed arrays,
- classes,
- Unicode-aware iteration with `Array.from`,
- sliding windows,
- fixed-alphabet optimization,
- error handling,
- assertions,
- performance measurement.

The JavaScript implementation emphasizes runtime-level data structures and application-oriented representations.

`Map` is especially useful when the set of possible characters is not known in advance.

`Int32Array` is useful when the problem guarantees a small fixed numeric state.

---

## C++ implementation details

The C++ case study demonstrates:

- `std::array`,
- `std::unordered_map`,
- classes,
- records,
- validation,
- exception handling,
- canonical signatures,
- indexing,
- sliding windows,
- lambdas,
- `chrono` performance measurement,
- automated tests,
- modular functions.

The central class is `AnagramRecordIndex`.

It stores records separately from the anagram groups, allowing a group to contain lightweight IDs while the full record data remains accessible through the record store.

This separation resembles a common indexing pattern in larger systems.

---

## C++ design decisions

### Fixed-size array

The case study uses:

`array<int, 26>`

because the normalized domain is explicitly lowercase ASCII letters.

This gives:

- predictable memory consumption,
- constant auxiliary state size,
- direct character-to-index conversion,
- no hash lookup for individual character counts.

### Hash index

`unordered_map<string, vector<int>>` maps a frequency signature to record IDs.

This provides expected constant-time lookup for a signature under normal hash-table assumptions.

### Validation

The case study rejects:

- duplicate record IDs,
- empty normalized records,
- invalid characters in frequency-based operations,
- invalid sliding-window input.

Explicit validation is preferable to silently producing an incorrect result.

---

## Security considerations

Anagram algorithms are generally not security-sensitive by themselves, but production implementations can still have operational risks.

### Resource exhaustion

Very large inputs can consume significant:

- CPU,
- memory,
- storage,
- hash-table capacity.

Input size limits may therefore be appropriate in services processing untrusted data.

### Hash-table behavior

Hash-based grouping relies on hash tables.

Implementations should use established standard-library structures rather than custom hashing without a clear reason.

### Unicode ambiguity

Security-sensitive text processing should define normalization rules carefully.

Two visually similar strings are not necessarily identical at the code-point level.

### Input validation

Input should be validated before it enters a fixed-alphabet algorithm.

The C++ case study throws an exception when unsupported characters reach functions that require lowercase ASCII.

---

## Performance considerations

The choice of algorithm depends on the problem constraints.

### Use sorting when

- implementation simplicity matters,
- input sizes are modest,
- a canonical sorted representation is useful,
- the alphabet is not fixed.

### Use a frequency map when

- the alphabet is dynamic,
- Unicode or arbitrary characters are relevant,
- linear average-time processing is desired.

### Use a fixed array when

- the alphabet is known,
- the alphabet is small,
- performance and predictable memory usage matter.

### Use a sliding window when

- searching for anagrams inside a larger sequence,
- the pattern length is fixed,
- consecutive windows overlap heavily.

The overlapping structure is what makes incremental frequency updates effective.

---

## Testing strategy

The implementations include tests for:

- positive anagrams,
- negative cases,
- empty strings,
- unequal lengths,
- repeated characters,
- normalized strings,
- anagram windows,
- repeated windows,
- invalid characters,
- duplicate identifiers,
- empty patterns.

Assertions are particularly useful for algorithmic study because they verify that the implementation satisfies explicit invariants.

The C++ implementation throws an exception when an expected invariant fails in its test suite.

---

## Important invariants

An anagram frequency algorithm should maintain the following invariant:

> The frequency state represents exactly the number of occurrences of every relevant character in the current input or window.

For a sliding window:

> After each movement, the frequency state represents exactly the characters currently inside the window.

For the optimized fixed-alphabet implementation:

> `matches` equals the number of alphabet positions whose current window frequency equals the pattern frequency.

These invariants explain why the algorithms work.

---

## Practical applications

Anagram algorithms appear in several types of systems.

### Text indexing

A service can group textual records according to character composition.

### Search

A sliding-window algorithm can identify permutations of a pattern inside a larger text.

### Data processing

Frequency signatures can be used to classify records according to their character distributions.

### Deduplication

Normalization plus signatures can identify records that are equivalent under a defined transformation.

### Puzzle and word-processing systems

Word games frequently require anagram detection and grouping.

### Information retrieval

Character-frequency signatures can be used as one component of candidate generation, although they are generally not sufficient by themselves for semantic matching.

---

## Sorting versus frequency counting

| Property | Sorting | Frequency counting |
|---|---|---|
| Basic idea | Canonical ordering | Count occurrences |
| Typical time | `O(n log n)` | `O(n)` average |
| General alphabet | Yes | Yes with a map |
| Fixed alphabet optimization | Possible | Excellent |
| Implementation simplicity | Very high | High |
| Useful as group key | Yes | Yes |
| Preserves original order | No | No |
| Best use | Simple canonical comparison | Large-scale counting and windows |

Neither approach is universally correct for every environment.

The appropriate method depends on constraints and the definition of the input domain.

---

## Object versus Map in JavaScript

| Structure | Characteristics |
|---|---|
| Object | Simple property-based dictionary |
| `Map` | Explicit key-value collection |
| `Int32Array` | Compact fixed-size numeric state |

Objects can be convenient for simple character maps.

`Map` provides a more explicit mapping abstraction.

Typed arrays are particularly appropriate when the key space has already been reduced to a small numeric range.

---

## Dictionary versus array in Python

A Python dictionary is preferable when:

- characters are arbitrary,
- the alphabet is unknown,
- Unicode input is possible,
- readability and generality are important.

A fixed list is preferable when:

- the alphabet is known,
- the input is restricted to ASCII lowercase letters,
- constant-size auxiliary storage is desired.

The Python program demonstrates both approaches so the distinction is visible in executable form.

---

## Signature design

A signature must satisfy an important property:

> Equivalent inputs must produce the same signature.

For anagram grouping, it should also avoid unnecessary collisions where different frequency distributions receive the same signature.

A sorted string is a direct signature.

A frequency vector is another direct signature.

A poorly designed signature can produce false matches.

For example, simply concatenating counts without fixed boundaries can create ambiguous representations. The C++ frequency signature therefore places separators between counts.

---

## Production considerations

A production anagram service would need to define:

- accepted character set,
- normalization rules,
- maximum input size,
- case behavior,
- punctuation behavior,
- Unicode behavior,
- indexing lifetime,
- concurrency requirements,
- memory limits,
- error-handling policy,
- API semantics,
- persistence requirements.

The algorithm itself is only one component of a production system.

The C++ case study intentionally models several surrounding concerns through validation, indexing, record storage, error handling, and performance measurement.

---

## Relationship between the three implementations

### Python

Python emphasizes algorithmic clarity and experimentation.

It contains the largest collection of educational implementations, including multiple representations of frequency information.

### JavaScript

JavaScript emphasizes runtime data structures and application-level behavior.

It demonstrates objects, `Map`, typed arrays, classes, and JavaScript-specific string iteration behavior.

### C++

C++ emphasizes explicit system design.

The case study combines data structures, validation, indexing, fixed-size state, exceptions, performance measurement, and automated tests into one cohesive program.

The underlying algorithmic ideas remain the same across the three languages, while the implementation choices reflect the strengths and constraints of each language.

---

## Core principles demonstrated

The complete implementations establish several general algorithmic principles:

1. Define the equivalence relation before implementing the algorithm.
2. Use frequency information when order does not matter.
3. Use canonical signatures to group equivalent objects.
4. Exploit fixed alphabets with fixed-size arrays when appropriate.
5. Use sliding windows when consecutive ranges overlap.
6. Update changing state incrementally rather than rebuilding it.
7. Validate assumptions explicitly.
8. Handle edge cases deliberately.
9. Match data structures to input constraints.
10. Analyze both asymptotic complexity and practical resource usage.

These principles extend beyond anagrams to many problems involving strings, arrays, multisets, hashing, classification, and sliding windows.
