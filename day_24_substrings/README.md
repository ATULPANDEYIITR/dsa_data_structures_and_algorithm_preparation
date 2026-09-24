# Day 24 — Substrings

## Topic overview

A substring is a sequence of characters taken from a string where all selected characters remain contiguous and in their original order.

For a string of length `n`, the number of non-empty substring occurrences is:

`n(n + 1) / 2`

For example, the string `abc` has six substring occurrences:

`a`, `ab`, `abc`, `b`, `bc`, `c`

The important distinction is that a substring must be contiguous. A subsequence only requires the characters to remain in the same relative order.

For example, in `ABCDE`:

- `ABC` is a substring and a subsequence.
- `BCD` is a substring and a subsequence.
- `ACE` is a subsequence but not a substring.
- `AEC` is neither a substring nor a subsequence.

This distinction is central to many string algorithms and interview problems.

---

## Fundamental terminology

### String

A string is an ordered sequence of characters.

Examples include:

- `hello`
- `database`
- `ABABC`
- `12345`
- `user@example.com`

### Substring

A substring is a contiguous portion of a string.

For `banana`, examples include:

- `b`
- `ba`
- `ban`
- `ana`
- `nan`
- `anana`

The characters must occupy consecutive positions.

### Subsequence

A subsequence preserves character order but allows characters to be skipped.

For `ABCDE`, `ACE` is a subsequence because `A`, `C`, and `E` appear in that order.

`AEC` is not a subsequence because `E` occurs after `C`.

### Prefix

A prefix starts at index `0`.

For `computer`:

- `c`
- `co`
- `com`
- `comp`

are prefixes.

Every prefix is a substring, but not every substring is a prefix.

### Suffix

A suffix ends at the final character.

For `computer`:

- `r`
- `er`
- `ter`
- `puter`
- `computer`

are suffixes.

Every suffix is a substring, but not every substring is a suffix.

### Proper prefix

A proper prefix is a prefix shorter than the complete string.

For `abc`, `a` and `ab` are proper prefixes.

### Proper suffix

A proper suffix is a suffix shorter than the complete string.

For `abc`, `c` and `bc` are proper suffixes.

---

## Generating substrings

A straightforward generation algorithm chooses:

1. A starting index.
2. An ending index after the starting index.
3. The characters between those positions.

For a string of length `n`, there are `n` possible starting positions, and the number of possible endings decreases as the starting position moves forward.

This produces:

`n + (n - 1) + ... + 1`

which equals:

`n(n + 1) / 2`

The Python implementation provides `all_substrings()` and `all_substrings_with_positions()`.

The JavaScript implementation provides the same fundamental mechanism using `slice()`.

The C++ implementation uses `string::substr()` and explicitly reserves capacity for the expected number of substring occurrences.

---

## Complexity of substring generation

There are two different complexity considerations.

The number of substring occurrences is:

`O(n²)`

But actually constructing each substring also copies characters. The total number of copied characters can reach cubic order in a straightforward implementation.

For example, generating all substrings of a long string is substantially more expensive than merely counting how many substrings exist.

Therefore, when a problem asks only for the number of substrings, use the mathematical formula instead of physically generating them.

---

## Counting substrings

The number of non-empty substring occurrences in a string of length `n` is:

`n(n + 1) / 2`

Examples:

| String length | Number of non-empty substring occurrences |
|---:|---:|
| 0 | 0 |
| 1 | 1 |
| 2 | 3 |
| 3 | 6 |
| 4 | 10 |
| 5 | 15 |
| 10 | 55 |
| 100 | 5050 |

This formula counts occurrences, not distinct substring values.

---

## Occurrences versus distinct substrings

Consider:

`aaa`

Its substring occurrences are:

`a`, `aa`, `aaa`, `a`, `aa`, `a`

There are six occurrences.

The distinct substring values are only:

`a`, `aa`, `aaa`

There are three distinct substrings.

This distinction becomes important in problems involving repeated characters.

The Python implementation uses a `set` for a simple distinct-substring calculation.

The C++ case study uses `unordered_set<string>` for the same conceptual purpose.

A direct set-based solution is useful for learning but can require substantial memory for large strings.

---

## Fixed-length substrings

A string of length `n` has:

`n - k + 1`

substring occurrences of length `k`, provided:

`1 <= k <= n`

For example, `ABCDE` has four substrings of length two:

`AB`, `BC`, `CD`, `DE`

It has three substrings of length three:

`ABC`, `BCD`, `CDE`

This relationship is useful in sliding-window problems.

---

## Contiguous versus non-contiguous sequences

The difference can be expressed as a structural rule.

A substring requires:

- same order
- no skipped positions
- contiguous positions

A subsequence requires:

- same order
- skipped positions are allowed
- contiguity is not required

For example:

`ABCDE`

`BCD` is a substring.

`BDE` is a subsequence but not a substring.

`DB` is neither because the order is reversed.

The implementations contain `isSubstring()` and `isSubsequence()` functions to make this distinction executable.

---

## String search

String searching asks whether a pattern occurs inside a larger text and, often, where it occurs.

Given:

`text = "hello world"`

and:

`pattern = "world"`

the pattern begins at index `6`.

Different algorithms provide different performance characteristics.

The three main implementations in this project are:

- brute-force search
- Knuth-Morris-Pratt
- Rabin-Karp

The Z algorithm is also demonstrated.

---

## Brute-force string search

The brute-force approach tries every possible starting position.

At each position, it compares the pattern character-by-character with the text.

For text length `n` and pattern length `m`, the worst-case time complexity is:

`O(nm)`

The algorithm is valuable because it is simple and provides the baseline against which optimized algorithms can be understood.

Its advantages include:

- simple implementation
- low conceptual complexity
- no preprocessing structure
- useful for small inputs

Its main limitation is repeated character comparison on unfavorable inputs.

---

## Knuth-Morris-Pratt

The Knuth-Morris-Pratt algorithm, usually called KMP, avoids unnecessary comparisons.

Its key data structure is the LPS array.

LPS means:

`Longest Proper Prefix which is also a Suffix`

For every position in the pattern, the LPS value records how much of the pattern can be reused after a mismatch.

The Python, JavaScript, and C++ implementations all build the LPS structure.

For the pattern:

`ABABCABAB`

the prefix-function information allows KMP to avoid starting the comparison from the beginning after every mismatch.

The complexity is:

- preprocessing: `O(m)`
- search: `O(n)`
- total: `O(n + m)`

The additional space is:

`O(m)`

where `m` is the pattern length.

---

## Why KMP is faster than naive search

Suppose the text and pattern contain long repeated prefixes.

A brute-force algorithm may repeatedly compare the same characters.

KMP recognizes that some previously matched characters are still useful.

Instead of discarding all previous information, it uses the LPS array to determine the next valid pattern position.

This is the fundamental optimization behind KMP.

---

## Overlapping matches

A common substring-search mistake is confusing overlapping and non-overlapping occurrences.

Consider:

`aaaa`

and:

`aa`

The overlapping occurrences begin at:

`0`, `1`, and `2`

Therefore the overlapping count is `3`.

A non-overlapping scan selects:

`aa` at position `0`

and then:

`aa` at position `2`

giving a count of `2`.

The KMP `searchAll` implementations preserve overlapping matches by falling back using the LPS value after a successful match instead of resetting the pattern index to zero.

---

## Rabin-Karp

Rabin-Karp uses hashing.

Instead of directly comparing every substring with the pattern, it computes a numerical hash for the pattern and for each text window.

A rolling hash allows the next window's hash to be calculated from the previous one without rebuilding the complete hash.

The general structure is:

`new_hash = adjusted_old_hash + incoming_character`

after removing the contribution of the outgoing character and shifting the remaining characters.

Hash equality does not prove string equality because different strings can theoretically have the same hash.

Therefore, the implementations verify the actual characters after a hash match.

This prevents a collision from producing a false positive.

Rabin-Karp is particularly useful when hashing can be reused across many comparisons.

---

## Rabin-Karp complexity

With suitable hashing, the expected performance is approximately:

`O(n + m)`

The worst case can become:

`O(nm)`

if many hash collisions occur and verification is repeatedly required.

The choice of modulus, base, and collision strategy matters in serious implementations.

Multiple independent hashes can reduce collision probability, although deterministic verification remains the strongest correctness mechanism.

---

## Z algorithm

The Z algorithm computes a Z-array.

For each position `i`, `Z[i]` represents the length of the longest substring starting at `i` that matches the prefix of the entire string.

Pattern searching can be reduced to a Z computation on:

`pattern + separator + text`

When a Z value equals the pattern length, the pattern occurs at that location.

The Z algorithm runs in:

`O(n + m)`

for a pattern and text of lengths `m` and `n`.

The implementation uses a left and right matching window to avoid repeatedly comparing characters.

---

## Sliding-window substring problems

Not every substring problem requires generating all substrings.

A large class of problems can be solved with a sliding window.

The window has:

- a left boundary
- a right boundary
- an invariant that describes what the current window satisfies

The right boundary usually expands the window.

When the invariant becomes invalid, the left boundary moves forward.

This can reduce quadratic algorithms to linear algorithms.

---

## Longest substring without repeating characters

For:

`abcabcbb`

the answer is:

`abc`

The sliding-window implementation stores the most recent position of each character.

When a repeated character occurs inside the current window, the left boundary jumps directly beyond its previous position.

The resulting complexity is approximately:

`O(n)`

with a hash map.

This is substantially better than examining every possible substring.

---

## At most K distinct characters

A window containing at most `k` distinct characters can be maintained with a frequency map.

When the number of distinct characters exceeds `k`, the left side of the window moves forward until the condition is restored.

For each right boundary, the number of valid substrings ending at that position is:

`right - left + 1`

Adding this quantity for every right position counts all valid substrings.

---

## Exactly K distinct characters

A useful identity is:

`exactly(k) = atMost(k) - atMost(k - 1)`

The reason is that the set of substrings containing at most `k` distinct characters includes both:

- substrings containing at most `k - 1`
- substrings containing exactly `k`

Subtracting the first category leaves the second.

This converts an exact-count problem into two easier sliding-window calculations.

---

## Minimum window substring

The minimum-window problem asks for the shortest substring containing all required characters.

For example:

`text = ADOBECODEBANC`

`target = ABC`

The answer is:

`BANC`

The algorithm maintains character requirements and a sliding window.

The window expands until all requirements are satisfied.

Then it contracts from the left while remaining valid.

The complexity is:

`O(n + m)`

when the frequency-map operations are treated as constant-time operations.

---

## Longest palindromic substring

A palindrome reads identically in both directions.

Examples:

- `a`
- `aa`
- `aba`
- `racecar`

A palindrome can have:

- an odd-length center
- an even-length center

The expand-around-center algorithm checks both cases.

For each possible center, it expands outward while characters match.

Its complexity is:

`O(n²)`

time and:

`O(1)`

auxiliary space, excluding the returned string.

The approach is substantially simpler than more advanced linear-time algorithms such as Manacher's algorithm and is often appropriate when the input size permits quadratic time.

---

## Longest common substring

The longest common substring problem asks for the longest contiguous sequence appearing in two strings.

This differs from longest common subsequence.

For example, the strings:

`ABABC`

and:

`BABCA`

have the common substring:

`BABC`

A dynamic-programming solution defines a state based on matching suffixes.

When two characters match:

`dp[i][j] = dp[i-1][j-1] + 1`

When they do not match:

`dp[i][j] = 0`

The reset to zero is important because the characters must be contiguous.

The C++ implementation uses two rows rather than a complete two-dimensional matrix.

This reduces auxiliary space from:

`O(nm)`

to:

`O(m)`

while retaining:

`O(nm)`

time complexity.

---

## Suffix-based substring analysis

For more advanced substring analysis, suffix structures become useful.

A suffix array stores all suffixes in lexicographic order.

For `banana`, the suffixes are conceptually:

`banana`

`anana`

`nana`

`ana`

`na`

`a`

After sorting them lexicographically, adjacent suffixes reveal shared prefixes.

The longest common prefix between adjacent suffixes can identify repeated substrings.

The Python implementation includes a straightforward educational suffix-array approach.

It is intentionally not an optimized industrial suffix-array construction.

Its purpose is to show the relationship between:

- suffix ordering
- longest common prefixes
- repeated substrings
- distinct substring counting

---

## Distinct substring counting through suffixes

There are:

`n(n + 1) / 2`

substring occurrences in total.

Duplicates can be removed conceptually using suffix ordering.

For each suffix, the number of new distinct substrings it contributes equals:

`suffix length - LCP with the previous suffix`

Therefore:

`distinct substrings = n(n + 1) / 2 - sum(LCP values)`

This provides a powerful connection between elementary substring counting and suffix-array algorithms.

---

## Polynomial rolling hashes

The Python implementation includes `PolynomialRollingHash`.

A prefix-hash structure stores cumulative hashes so that substring hashes can be calculated quickly.

The general idea is:

`hash(l, r) = prefix[r] - prefix[l] * power[r-l]`

with modular arithmetic.

This allows substring hash queries in constant time after preprocessing.

Hash-based substring comparison has an important limitation: collisions are possible.

The implementation therefore verifies equal hashes using exact string comparison when correctness is required.

---

## Unicode and character representation

Substring algorithms depend on how a programming language represents text.

Python strings operate naturally on Unicode text.

JavaScript strings are based on UTF-16 code units. This means indexing and `length` can behave differently for characters represented by surrogate pairs.

C++ `std::string` is a byte-oriented container. It does not inherently understand Unicode characters as user-perceived characters.

Therefore, an algorithm that treats each `char` as a complete character is appropriate for ASCII or byte-oriented data but is not automatically a Unicode-aware text-processing solution.

For production internationalized systems, text encoding and character segmentation must be considered separately from the basic substring algorithm.

---

## Python implementation

The Python script progresses from elementary operations to advanced algorithms.

It demonstrates:

- substring generation
- substring positions
- subsequence testing
- mathematical substring counting
- fixed-length substring counting
- distinct substring counting
- overlapping occurrence counting
- brute-force search
- KMP
- Rabin-Karp
- Z algorithm
- longest common prefix
- longest palindromic substring
- longest unique substring
- exactly-K-distinct substring counting
- minimum-window substring
- suffix arrays
- longest repeated substring
- suffix-based distinct substring counting
- rolling hashes
- practical substring problem solutions
- assertions and edge-case testing

The Python version emphasizes readability and algorithmic progression.

It uses built-in data structures such as lists, sets, dictionaries, `Counter`, and `defaultdict`.

---

## JavaScript implementation

The JavaScript implementation demonstrates the same domain through JavaScript's string APIs and collection types.

Important JavaScript mechanisms include:

- `slice()`
- `includes()`
- `startsWith()`
- `Map`
- `Set`
- `Array.from()`
- string indexing
- character-code hashing

The JavaScript implementation also introduces a `LogSubstringAnalyzer` class.

This provides an application-level example in which substring searching is used to inspect log records.

JavaScript is particularly useful for demonstrating substring operations in browser and application environments because string processing commonly appears in:

- search interfaces
- validation
- filtering
- client-side analytics
- log viewers
- data transformation
- web applications

---

## C++ case study

The C++ implementation models an industry-style log search engine.

The system contains structured log records with:

- an identifier
- severity
- service name
- message

The `LogSearchEngine` class provides:

- brute-force message search
- KMP message search
- occurrence counting by severity
- exact occurrence positions

This turns isolated substring algorithms into components of a larger text-processing system.

The case study demonstrates why algorithm selection matters.

For small log collections, the difference between brute-force search and KMP may not be significant.

For large collections, repeated searches over long messages can make algorithmic complexity important.

---

## C++ architectural decisions

The case study separates concerns into several components.

### Search algorithms

Brute-force, KMP, and Rabin-Karp are implemented independently.

This makes their behavior directly comparable.

### Rolling hash

`RollingHash` encapsulates the Rabin-Karp implementation rather than exposing hash state throughout the application.

### Log records

`LogRecord` models a structured application event.

### Search engine

`LogSearchEngine` provides a higher-level interface to the algorithms.

This separation makes the algorithm reusable without coupling it to the representation of the complete application.

### Validation

The program uses assertions for deterministic correctness tests and exceptions for invalid input.

---

## Error handling

Search functions in the examples treat an empty pattern explicitly.

There is no universal definition for what an empty pattern should mean in every application.

Some APIs return index `0`.

Some return all possible insertion positions.

Some reject empty patterns.

The implementations choose explicit behavior depending on the function.

The C++ case study throws `invalid_argument` for APIs where an empty search pattern would make the intended operation ambiguous.

Explicit handling prevents silent and unexpected behavior.

---

## Important edge cases

Substring algorithms should be tested against:

- empty strings
- one-character strings
- repeated characters
- patterns longer than the text
- patterns equal to the complete text
- patterns at the beginning
- patterns at the end
- overlapping occurrences
- no matches
- repeated prefixes
- repeated suffixes
- Unicode text
- very large inputs

For example:

`aaaa`

with:

`aa`

is an important test because it exposes the difference between overlapping and non-overlapping occurrence counting.

---

## Common mistakes

### Confusing substring with subsequence

`ACE` is a subsequence of `ABCDE`, but not a substring.

### Using `count()` when overlapping matches are required

A standard non-overlapping count can miss valid overlapping occurrences.

### Resetting KMP after a match

After a successful KMP match, the pattern index should use the LPS information when overlapping matches are required.

### Forgetting the empty string case

Many formulas and search APIs have special behavior for empty strings.

### Generating every substring unnecessarily

If the question only asks for the number of substring occurrences, use:

`n(n + 1) / 2`

instead of generating all substrings.

### Confusing longest common substring with longest common subsequence

Substring requires contiguity.

Subsequence does not.

### Treating a hash match as proof of equality

Hashes can collide.

For correctness-sensitive applications, verify the actual characters after a hash match or use an appropriately designed multi-hash strategy.

### Ignoring memory consumption

A set containing every distinct substring can become extremely large.

An algorithm can be computationally correct while still being impractical because of memory usage.

---

## Brute-force versus optimized approaches

| Approach | Main idea | Typical time | Extra space |
|---|---|---:|---:|
| Direct substring generation | Enumerate all ranges | At least O(n²) occurrences | O(n²) outputs |
| Brute-force search | Try every alignment | O(nm) worst case | O(1) |
| KMP | Prefix/LPS reuse | O(n + m) | O(m) |
| Rabin-Karp | Rolling hash | Average O(n + m) | O(1) basic search |
| Z algorithm | Prefix matching | O(n + m) | O(n + m) |
| Sliding window | Maintain valid interval | Often O(n) | O(alphabet/window data) |
| Longest common substring DP | Match contiguous suffixes | O(nm) | O(m) optimized |
| Suffix-array analysis | Ordered suffixes + LCP | Depends on construction | Depends on implementation |

No single algorithm is universally appropriate.

A simple brute-force method can be preferable when:

- inputs are small
- implementation simplicity matters
- the code is not performance-sensitive

An optimized algorithm becomes more useful when:

- the input is large
- searches are repeated
- predictable performance is required
- worst-case complexity matters

---

## Performance considerations

Substring processing can become expensive because the number of possible substrings grows quadratically.

For a string of length:

`1,000`

there are:

`500,500`

non-empty substring occurrences.

For:

`100,000`

there are:

`5,000,050,000`

non-empty substring occurrences.

Physically generating all of them is usually infeasible.

This is why many advanced substring problems avoid enumeration and instead use:

- prefix functions
- rolling hashes
- suffix arrays
- suffix trees
- suffix automata
- sliding windows
- dynamic programming
- specialized palindrome algorithms

---

## Security considerations

Substring searching appears in security-sensitive systems such as:

- log analysis
- input validation
- malware-signature matching
- URL filtering
- request inspection
- audit processing
- intrusion detection

Important considerations include:

### Denial-of-service risk

An algorithm with poor worst-case behavior can become expensive when supplied with deliberately chosen inputs.

### Regular-expression complexity

Although regular expressions are related to string searching, they can introduce their own performance risks when poorly designed.

### Input size limits

Production systems should establish sensible maximum input sizes.

### Encoding normalization

Visually identical text can have different underlying Unicode representations.

Security-sensitive matching may require normalization before comparison.

### Exact matching requirements

Hash-based matching should not be treated as deterministic unless collisions are appropriately handled.

---

## Implementation considerations

### Python

Python is effective for learning and prototyping because its string operations and collections are concise.

Its main limitation for extremely large substring workloads can be memory and object-management overhead.

### JavaScript

JavaScript is useful for browser and application-side text processing.

The runtime's string representation and UTF-16 behavior must be considered when working with Unicode beyond basic ASCII-like data.

### C++

C++ provides precise control over memory, data structures, and performance.

The C++ case study is appropriate for systems in which large data volumes, predictable performance, and low-level control matter.

---

## Real-world applications

Substring algorithms are used in many practical systems.

### Search systems

User queries can be located within documents, logs, filenames, metadata, or indexed content.

### Log analysis

Operational tools search logs for:

- `ERROR`
- `timeout`
- `database`
- request identifiers
- exception names

### Validation

Applications inspect strings for expected prefixes, suffixes, tokens, or patterns.

### Bioinformatics

DNA and protein sequences can be searched for repeated or significant contiguous patterns.

### Cybersecurity

Signature and indicator matching can use efficient substring-search algorithms.

### Text analytics

Substring frequency and repetition can reveal patterns in large text collections.

### Data cleaning

Substring operations can detect and transform structured text such as identifiers, URLs, filenames, and records.

---

## Important distinctions

### Substring versus subsequence

A substring is contiguous.

A subsequence is ordered but may skip characters.

### Substring versus prefix

A prefix must begin at index `0`.

### Substring versus suffix

A suffix must end at the final index.

### Occurrences versus distinct values

`aaa` contains six substring occurrences but only three distinct substring values.

### Overlapping versus non-overlapping matches

`aaaa` contains three overlapping occurrences of `aa` but two non-overlapping occurrences.

### Search versus generation

Searching asks whether a particular pattern occurs.

Generation enumerates possible substrings.

These are different computational tasks.

---

## Testing strategy

A reliable substring implementation should test simple cases before complicated cases.

Representative tests include:

`""`

`"a"`

`"aaaa"`

`"abc"`

`"abababab"`

`"banana"`

For search algorithms, test:

- match at index `0`
- match at the final possible index
- no match
- pattern longer than text
- complete-text match
- repeated pattern
- overlapping pattern
- empty pattern according to the selected API contract

The Python, JavaScript, and C++ implementations include executable correctness checks.

---

## Practical algorithm-selection guide

For basic substring generation, direct nested loops are appropriate.

For a single small search, direct library functions or brute force are often sufficient.

For guaranteed linear-time pattern searching, KMP or Z-based searching is appropriate.

For hash-oriented workloads or comparing many windows, rolling hashes can be useful.

For constrained substring problems, first investigate whether a sliding window maintains a useful invariant.

For repeated-substring and distinct-substring analysis, suffix arrays, suffix trees, suffix automata, or suffix-based hashing can be more appropriate.

For longest palindromic substring problems, center expansion is simple and quadratic, while more advanced algorithms can provide linear-time behavior for demanding inputs.

The central lesson is to identify the structure of the substring problem before selecting the algorithm.
