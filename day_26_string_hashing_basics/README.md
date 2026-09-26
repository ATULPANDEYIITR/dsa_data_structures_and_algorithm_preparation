# Day 26 — String Hashing Basics

## Topic

String hashing is the process of converting a string into a compact numerical representation called a hash. The representation allows algorithms to compare, index, group, or search strings efficiently.

This day focuses on four core ideas:

- Hashing concept
- Hash representation
- Collision concept
- Practical string hashing use cases

The implementations progress from a deliberately weak character-sum hash to polynomial rolling hashes, prefix hashes, double hashing, collision verification, Rabin-Karp searching, duplicate-substring detection, and a C++ document-indexing case study.

The Python implementation is the broadest teaching implementation. The JavaScript implementation emphasizes exact integer arithmetic with `BigInt`, Unicode-aware string handling, and JavaScript collection behavior. The C++ implementation develops the same ideas into an industry-style document indexing system.

---

## 1. What Is Hashing?

A hash function maps an input value to a numerical representation.

Conceptually:

`string -> hash value`

For example, a simple character-sum hash could calculate:

`hash("abc") = code('a') + code('b') + code('c')`

The important characteristic is that the result is usually much smaller and easier to manipulate than the complete input.

A hash is therefore a representation of data, not a replacement for the data.

For string algorithms, hashing is especially useful when an algorithm needs to answer questions such as:

- Are these two substrings equal?
- Does this pattern occur in the text?
- Does this substring occur elsewhere?
- Are two documents likely to contain the same fragment?
- Which strings belong to the same hash bucket?
- Does a repeated substring exist?
- Can many substring comparisons be performed efficiently?

---

## 2. Hash Representation

A hash representation is usually a fixed-size integer or a small tuple of integers.

The Python implementation demonstrates this progression:

1. Character-sum hash
2. Polynomial hash
3. Prefix hash
4. Double hash

The character-sum implementation is intentionally weak.

For example:

`abc`

and

`acb`

produce the same sum because addition does not depend on order.

This demonstrates the central collision principle.

A better string hash should incorporate character order.

---

## 3. Collision

A collision occurs when two different inputs produce the same hash value.

For example:

`hash("abc") == hash("acb")`

does not imply:

`"abc" == "acb"`

The two strings are different even though their hashes are equal.

Collisions are unavoidable for a finite hash representation when the possible input space is sufficiently large. There are infinitely many possible strings but only a finite number of values in a fixed-size hash space.

This is a fundamental application of the pigeonhole principle.

### Collision handling

A robust algorithm should not blindly treat hash equality as proof of string equality.

A common pattern is:

1. Calculate the hash.
2. Compare hashes.
3. If hashes differ, the strings are definitely different.
4. If hashes match, verify the actual strings when exact correctness is required.

This makes hashing a very effective filtering mechanism.

---

## 4. Polynomial Rolling Hash

A polynomial rolling hash incorporates character order.

For characters represented by numeric values:

`c0, c1, c2, ..., cn-1`

a polynomial representation can be written as:

`c0 * base^(n-1) + c1 * base^(n-2) + ... + cn-1`

The implementation evaluates this incrementally:

`H = (H * base + character_value) mod modulus`

This has two important benefits:

- character order affects the result
- the hash can be updated efficiently

The modulus keeps the hash inside a manageable numerical range.

The Python implementation contains this logic in `polynomial_hash`.

The JavaScript implementation performs the same operation with `BigInt`, avoiding precision problems associated with large integer values represented by ordinary JavaScript `Number` values.

---

## 5. Base and Modulus

A polynomial hash normally uses:

- a base
- a modulus

For example:

`base = 257`

and:

`modulus = 1,000,000,007`

The base determines how strongly character positions influence the result.

The modulus limits the resulting value.

There is no single universally correct pair of parameters for every application. Parameters should be selected according to the algorithm and its collision requirements.

Poor parameter choices can increase collision risk.

---

## 6. Prefix Hashes

The most important optimization demonstrated in the implementations is prefix hashing.

For a string:

`abcdef`

the prefix structure stores hash information for:

- `""`
- `"a"`
- `"ab"`
- `"abc"`
- `"abcd"`
- `"abcde"`
- `"abcdef"`

A prefix hash array allows a substring hash to be calculated from two prefix values.

For substring `[left, right)`:

`substring_hash = prefix[right] - prefix[left] * base^(right-left)`

with the entire expression evaluated modulo the selected modulus.

The exact implementation appears in:

- Python: `RollingHash.substring_hash`
- JavaScript: `RollingHash.substringHash`
- C++: `RollingHash::substringHash`

### Complexity

Building prefix hashes:

`O(n)`

Substring hash query:

`O(1)`

Additional storage:

`O(n)`

This is the major reason rolling hashes are useful for algorithms involving many substring comparisons.

---

## 7. Half-Open Intervals

All three implementations use the common interval convention:

`[left, right)`

This means:

- `left` is included
- `right` is excluded

For `"abcdef"`:

`[1, 4)` represents `"bcd"`.

The length is:

`right - left`

This convention makes prefix-hash formulas and loop boundaries easier to reason about.

---

## 8. Why Hash Equality Is Not Enough

Suppose two substrings produce:

`hash(A) = 12345`

and:

`hash(B) = 12345`

There are two possibilities:

1. `A` and `B` are actually equal.
2. They are different strings that collided.

Therefore, a hash comparison has asymmetric information:

- Different hashes prove inequality.
- Equal hashes provide evidence of equality but do not mathematically prove equality.

The implementations therefore use direct substring verification after a matching hash whenever exact results are required.

This is especially important in:

- duplicate detection
- Rabin-Karp search
- substring equality
- longest repeated substring

---

## 9. Double Hashing

A single polynomial hash has a collision probability determined by its hash space and parameter choices.

Double hashing uses two independently parameterized hashes:

`(hash1, hash2)`

Two different strings must collide under both hash functions to produce the same pair.

This dramatically reduces accidental collision probability when the two hash systems are suitably chosen.

The Python implementation provides `DoubleRollingHash`.

The JavaScript implementation provides the same abstraction.

The C++ implementation represents the pair using:

`HashPair`

and provides:

`HashPairHasher`

so the pair can be used as a key in an `unordered_map`.

Double hashing reduces risk. It does not turn a rolling hash into a cryptographic proof.

For applications where an exact answer is mandatory, direct verification remains an important design option.

---

## 10. Rabin-Karp Pattern Matching

Rabin-Karp is a classic string-search technique based on rolling hashes.

Suppose:

`text = "abracadabra"`

and:

`pattern = "abra"`

The algorithm:

1. Hashes the pattern.
2. Hashes the first text window of the same length.
3. Compares the hashes.
4. Moves the window.
5. Calculates the next window hash efficiently.
6. Verifies characters if a hash match occurs.

The advantage is that the algorithm does not need to compare the complete pattern against every text position unless the hash indicates a possible match.

The Python implementation is:

`rabin_karp_search`

The JavaScript implementation is:

`rabinKarpSearch`

The C++ case study incorporates the same idea in:

`DocumentIndex::findPattern`

### Complexity

Typical or expected performance is close to:

`O(n + m)`

where:

- `n` is text length
- `m` is pattern length

Worst-case behavior can approach:

`O(n * m)`

when many hash matches require character verification.

---

## 11. Overlapping Matches

A pattern can occur at overlapping positions.

For example:

`text = "aaaaa"`

and:

`pattern = "aaa"`

The valid starting positions are:

`0, 1, 2`

A correct string-search implementation must not automatically skip ahead by the pattern length after finding a match.

The implementations explicitly test this case.

---

## 12. Empty Pattern

An empty pattern requires a defined policy.

The implementations treat an empty pattern as matching at every boundary:

For `"abc"`:

`0, 1, 2, 3`

This corresponds to the mathematical interpretation that an empty string occurs between every pair of characters and at both ends.

Applications may choose a different API policy, but the behavior must be documented and tested.

---

## 13. Duplicate Substring Detection

A useful application of hashing is detecting whether two substrings of a fixed length are equal.

The basic process is:

1. Calculate the hash of each substring.
2. Store previously seen hashes.
3. When a hash appears again, compare the corresponding strings.
4. Return a duplicate when exact verification succeeds.

For a string of length `n` and substring length `L`, there are:

`n - L + 1`

candidate substrings.

Prefix hashing means each candidate hash can be retrieved in constant time.

The implementations use a hash table to store candidate positions.

---

## 14. Longest Repeated Substring

The implementations also demonstrate a more advanced algorithm.

The problem is:

> Find one longest substring that occurs at least twice.

For example, in:

`banana`

a longest repeated substring is:

`ana`

The technique combines:

- prefix hashing
- double hashing
- hash-table lookup
- collision verification
- binary search

The key observation is monotonicity.

If a repeated substring of length `L` exists, then a repeated substring of every smaller positive length also exists.

Therefore:

`exists repeated substring of length L`

is a monotonic predicate.

Binary search can be applied to the possible substring lengths.

The resulting expected complexity is approximately:

`O(n log n)`

for the demonstrated approach, subject to hashing and verification costs.

---

## 15. Hashing and Hash Tables

String hashing is closely related to hash tables.

A hash table typically uses a hash function to determine where a key should be stored.

Common operations include:

- insertion
- lookup
- deletion

Under favorable conditions, hash-table operations have expected:

`O(1)`

time complexity.

The Python implementation demonstrates exact word frequency counting with a Python dictionary.

The JavaScript implementation uses `Map`.

The C++ implementation uses `map` for the word-frequency example and `unordered_map` for hash-based duplicate-fragment indexing.

The standard library should normally be preferred instead of manually implementing a hash table unless the educational or algorithmic purpose specifically requires it.

---

## 16. Python Implementation

The Python script is designed as the primary comprehensive learning implementation.

### Main components

`simple_character_sum_hash`

Demonstrates the fundamental idea of mapping a string to a numeric value and deliberately exposes collisions.

`polynomial_hash`

Implements a standard polynomial rolling hash.

`RollingHash`

Stores prefix hashes and powers for constant-time substring hash queries.

`DoubleRollingHash`

Combines two polynomial hashes.

`rabin_karp_search`

Demonstrates hash-based pattern matching.

`duplicate_substring_positions`

Detects repeated fixed-length fragments.

`longest_repeated_substring`

Combines duplicate detection and binary search.

`BidirectionalStringHash`

Demonstrates forward and reverse hashing for palindrome checking.

The script also contains:

- edge-case demonstrations
- normalization
- hash-table applications
- performance comparisons
- security distinctions
- mixed assessment problems
- assertions and self-tests

---

## 17. Python Prefix Hash Example

For a text such as:

`abracadabra`

the `RollingHash` object builds:

- `prefix`
- `power`

The `substring_hash` method then extracts a substring representation without scanning the entire substring.

This is useful when the same long string must be queried repeatedly.

For example, comparing thousands of pairs of substrings can be transformed from repeated full scans into mostly constant-time hash queries.

---

## 18. JavaScript Implementation

The JavaScript implementation is deliberately complementary to the Python implementation.

It emphasizes language-specific concerns.

### `BigInt`

JavaScript's ordinary `Number` type uses IEEE-754 floating-point representation.

Large integers cannot all be represented exactly as `Number`.

Rolling hashes use multiplication and modular arithmetic, so exact integer behavior matters.

The JavaScript implementation therefore uses `BigInt` for:

- bases
- moduli
- prefix hashes
- powers
- arithmetic operations

Values are converted back to strings when printed.

### Unicode handling

JavaScript strings are based on UTF-16 code units.

The implementation uses:

`Array.from(text)`

when character-level code-point handling is useful.

This prevents certain Unicode characters from being accidentally treated as two independent characters when the algorithm conceptually works with Unicode code points.

Unicode normalization is a separate concern. Two visually equivalent strings can have different underlying representations unless an explicit normalization policy is applied.

---

## 19. JavaScript Collections

The JavaScript implementation uses:

`Map`

for frequency counting and hash buckets.

`Set`

is used for distinct-substring assessment.

These are standard collection abstractions and hide the internal collision-management details of their implementations.

The educational rolling hash is therefore separate from the runtime's internal hash-table implementation.

---

## 20. C++ Document Indexing Case Study

The C++ program models a small document indexing engine.

The scenario is:

A document-processing system needs to search text for phrases and identify repeated fragments.

The system must support:

- pattern searching
- repeated-fragment detection
- longest repeated fragment detection
- word-frequency indexing
- collision verification
- error handling
- predictable data structures

This provides a more realistic use of string hashing than isolated arithmetic examples.

---

## 21. C++ Architecture

The C++ case study is divided into several components.

### `HashParameters`

Stores:

- base
- modulus

This keeps hashing configuration explicit.

### `RollingHash`

Responsible for:

- prefix-hash construction
- power calculation
- substring hash queries

### `HashPair`

Stores two hash values.

### `HashPairHasher`

Allows a `HashPair` to be used as an `unordered_map` key.

### `DoubleHashIndex`

Provides two independent rolling hashes and collision-aware substring comparisons.

### `DocumentIndex`

Provides pattern searching.

It implements a Rabin-Karp-style workflow:

1. Hash the query.
2. Examine same-length document windows.
3. Compare double hashes.
4. Verify actual text after a hash match.

### `DuplicateFragmentDetector`

Searches for two identical fragments of a requested length.

### `LongestRepeatedFragment`

Uses binary search over possible fragment lengths.

### Word-frequency functions

Demonstrate a conventional application of hash-table concepts to document processing.

---

## 22. Why Collision Verification Exists in the C++ Case Study

Consider two different strings:

`A`

and:

`B`

with:

`hash(A) == hash(B)`

If the document index treated that equality as absolute, a false search result could be produced.

The C++ implementation therefore performs:

1. Double-hash comparison.
2. Exact `string::compare` verification.

This creates a two-stage filtering architecture.

The hash is the fast filter.

The string comparison is the correctness check.

This pattern is useful when candidate comparisons are expensive but a cheap representation can eliminate most non-matching candidates.

---

## 23. C++ Memory Design

Prefix hashing requires additional memory.

For a string of length `n`, each rolling-hash instance stores approximately:

- `n + 1` prefix values
- `n + 1` power values

Double hashing uses two such structures.

Therefore the memory requirement is linear:

`O(n)`

This is appropriate for many in-memory algorithms but can become significant for very large documents.

A production system processing extremely large data may need:

- chunking
- streaming
- external storage
- compact integer representations
- indexed storage
- specialized text-search structures

The correct architecture depends on document size and query workload.

---

## 24. Complexity

### Character-sum hash

For a string of length `n`:

`O(n)`

### Polynomial hash

For one complete string:

`O(n)`

### Prefix construction

`O(n)`

### Substring hash query

`O(1)`

after preprocessing.

### Rabin-Karp

Expected or typical:

`O(n + m)`

Worst case:

`O(nm)`

when many candidates require verification.

### Fixed-length duplicate detection

Expected approximately:

`O(n)`

for hash lookup, with additional verification costs for hash collisions.

### Longest repeated substring

With binary search over length:

approximately:

`O(n log n)`

expected for the demonstrated implementation.

### Dynamic-programming longest common substring

The Python and JavaScript assessment uses a different algorithm:

`O(nm)` time

and:

`O(m)` space

This distinction is important because hashing is not automatically the best technique for every string problem.

---

## 25. Hashing Versus Direct Comparison

### Direct comparison

Advantages:

- exact
- simple
- no collision problem
- often highly optimized by the language runtime

Disadvantages:

- repeated comparisons can scan many characters

### Rolling hash

Advantages:

- fast substring comparison after preprocessing
- useful for many repeated substring queries
- useful for Rabin-Karp
- useful for duplicate detection

Disadvantages:

- requires additional memory
- collisions exist
- parameter selection matters
- collision verification may still be required
- implementation is more complicated

For ordinary application code, a native string operation may be faster and simpler than a custom rolling-hash implementation.

Rolling hashing becomes especially valuable when its algorithmic structure provides a clear advantage.

---

## 26. Rolling Hash Versus Cryptographic Hash

These are different categories of hashing.

### Algorithmic rolling hash

Designed primarily for:

- string algorithms
- fast comparisons
- substring processing
- pattern matching

A polynomial rolling hash is an example.

### Cryptographic hash

Designed to provide security properties such as:

- preimage resistance
- second-preimage resistance
- collision resistance

Examples include SHA-256 and SHA-3.

### Password storage

A fast rolling hash should not be used for password storage.

Password storage requires a password-hashing or key-derivation design intended for that purpose, such as a memory-hard password hashing scheme.

The important distinction is:

**Fast hashing is useful for algorithms but is generally undesirable for password hashing.**

---

## 27. Security Considerations

Collision behavior becomes particularly important when input can be controlled by an attacker.

A malicious actor may deliberately construct inputs that create problematic hash behavior if the hashing design is predictable or weak.

Potential consequences include:

- excessive processing
- degraded hash-table behavior
- incorrect algorithmic results if collisions are treated as equality

Defensive measures can include:

- stronger parameter selection
- randomized hashing where appropriate
- double hashing
- exact verification
- carefully designed standard-library containers
- algorithm-specific protections

A polynomial rolling hash should not be presented as a cryptographic security mechanism.

---

## 28. Unicode and Character Encoding

Hashing operates on representations.

Two strings that appear identical to a user may have different underlying character sequences.

For example, accented characters can sometimes be represented as:

- a single precomposed character
- a base character followed by a combining mark

If an application requires canonical equivalence, normalization must be performed before hashing.

Case sensitivity is another policy decision.

For example:

`Apple`

and:

`apple`

are normally different strings.

An application that treats them as equivalent should normalize them before hashing.

The Python implementation uses `casefold` for a case-insensitive demonstration.

The JavaScript implementation uses locale-aware lowercasing for its simple normalization demonstration.

Normalization should be defined as part of the application's data model rather than being silently applied.

---

## 29. Edge Cases

The implementations explicitly consider:

- empty strings
- one-character strings
- repeated characters
- patterns longer than the text
- empty patterns
- overlapping matches
- substring boundaries
- invalid bounds
- Unicode characters
- identical strings
- completely different strings
- collisions

These cases are important because string algorithms often fail not in their main logic but in boundary handling.

---

## 30. Common Mistakes

### Mistake 1: Treating equal hashes as guaranteed equality

Incorrect reasoning:

`hash(A) == hash(B) -> A == B`

Correct reasoning:

`hash(A) != hash(B) -> A != B`

while:

`hash(A) == hash(B) -> A and B are candidates for equality`

Exact verification may still be required.

### Mistake 2: Forgetting modular arithmetic

Without a modulus, polynomial values grow rapidly.

The hash becomes unnecessarily large and arithmetic becomes expensive.

### Mistake 3: Using an unsuitable base or modulus

Poor parameter choices can increase collision risk.

### Mistake 4: Ignoring integer precision

In JavaScript, large integer arithmetic with `Number` can lose precision.

The implementation therefore uses `BigInt`.

### Mistake 5: Confusing rolling hashing with cryptographic hashing

They solve different problems.

### Mistake 6: Mishandling substring boundaries

Mixing inclusive and exclusive indexes creates off-by-one errors.

The implementations consistently use `[left, right)`.

### Mistake 7: Forgetting overlapping matches

A pattern can start at consecutive positions.

### Mistake 8: Using custom hashing when native functionality is already better

A custom algorithm should have a concrete algorithmic reason for existing.

---

## 31. Best Practices

1. Define the hash representation clearly.
2. Document the base and modulus.
3. Use prefix hashes for repeated substring queries.
4. Consider double hashing for lower accidental collision probability.
5. Verify matching substrings when exact correctness matters.
6. Test empty and boundary cases.
7. Keep substring indexing conventions consistent.
8. Measure performance instead of assuming a custom implementation is faster.
9. Separate algorithmic hashing from security hashing.
10. Treat normalization as an explicit application-level policy.
11. Use standard library hash tables for ordinary dictionary-style tasks.
12. Avoid exposing hash values as security credentials or authentication tokens.

---

## 32. Practical Applications

String hashing can support:

### Pattern matching

Finding occurrences of a pattern in large text.

### Duplicate detection

Finding repeated fragments in:

- documents
- source code
- logs
- datasets

### Plagiarism and similarity systems

Hashing can act as one stage of candidate detection before more expensive similarity analysis.

### Document indexing

A system can use compact representations to identify candidate text fragments.

### DNA and sequence processing

Hashing can be used for fixed-length sequence indexing.

### Caching

A normalized representation can identify equivalent computational inputs.

### Deduplication

Content fingerprints can identify candidate duplicate objects.

### Search systems

Hashing can accelerate candidate generation before exact verification.

---

## 33. Important Distinction: Hashing Is Not Compression

A hash does not preserve enough information to reconstruct the original string.

For example:

`string -> hash`

is generally many-to-one.

Therefore, a hash is not a compressed version of the string that can be decompressed.

It is a representation intended for specific algorithmic purposes.

---

## 34. Important Distinction: Hashing Is Not Encryption

Encryption is designed to transform data so that authorized parties can recover the original information with the appropriate key.

A hash normally does not provide reversible transformation.

Therefore:

- hashing is not encryption
- rolling hashing is not encryption
- a hash value should not be treated as encrypted text

---

## 35. Assessment Problems Demonstrated

The implementations include a mixed assessment section rather than solving every string problem exclusively through hashing.

### Distinct substring count

The baseline implementation stores actual substrings in a set.

This provides a clear reference solution but is not the most memory-efficient general algorithm.

### Longest common substring

Dynamic programming is used.

This demonstrates an important algorithm-design principle:

**A problem should be solved with the technique that matches its structure.**

Hashing is powerful, but it is not a universal replacement for dynamic programming, suffix structures, tries, or direct string algorithms.

### Repeated word detection

A hash table is used to count repeated words.

This demonstrates a common practical use of hashing that is different from rolling substring hashes.

---

## 36. Implementation Comparison

| Feature | Python | JavaScript | C++ |
|---|---|---|---|
| Basic hash | Yes | Yes | Yes |
| Polynomial hash | Yes | Yes | Yes |
| Prefix hashes | Yes | Yes | Yes |
| Double hashing | Yes | Yes | Yes |
| Collision verification | Yes | Yes | Yes |
| Rabin-Karp | Yes | Yes | Yes |
| Duplicate substrings | Yes | Yes | Yes |
| Longest repeated substring | Yes | Yes | Yes |
| Hash-table usage | `dict` / `defaultdict` | `Map` / `Set` | `map` / `unordered_map` |
| Unicode-focused handling | Yes | Yes | Byte-oriented `std::string` handling |
| Dynamic-programming assessment | Yes | Yes | Case-study focus |
| Large-integer handling | Python integers | `BigInt` | `uint64_t` |

The Python implementation emphasizes broad algorithmic study.

The JavaScript implementation emphasizes runtime-specific integer and string behavior.

The C++ implementation emphasizes modular architecture, explicit data structures, type choices, error handling, and a realistic document-processing scenario.

---

## 37. Production Considerations

A production string-indexing system may require more than rolling hashes.

For large-scale text search, alternatives can include:

- suffix arrays
- suffix automata
- tries
- inverted indexes
- finite-state search structures
- specialized full-text search engines

Rolling hashing is particularly useful when:

- many substring comparisons are required
- exact verification is inexpensive
- a linear preprocessing phase is acceptable
- memory proportional to input size is acceptable
- the problem benefits from binary-searchable substring predicates

The choice should be based on workload characteristics rather than on the fact that hashing has favorable asymptotic behavior in one operation.

---

## 38. Testing Strategy

The supplied implementations contain self-tests covering:

- empty hashes
- known substring hashes
- collision demonstrations
- overlapping pattern matches
- absent patterns
- repeated characters
- longest repeated substrings
- longest common substrings
- distinct substring counts
- invalid substring bounds

The tests use assertions in Python and JavaScript and explicit exception-based checks in C++.

A robust string-hashing implementation should test both normal and adversarial-looking inputs.

Useful test categories include:

- empty input
- minimum input
- maximum expected input
- repeated-character input
- random input
- Unicode input
- patterns at the beginning
- patterns at the end
- overlapping patterns
- no matches
- complete matches
- collision candidates

---

## 39. Central Algorithmic Insight

The most important idea in this topic is not merely calculating a hash.

The deeper technique is:

**Replace repeated expensive string work with compact representations, while preserving correctness through collision-aware design.**

Prefix hashing turns repeated substring processing into constant-time hash queries after linear preprocessing.

Rabin-Karp uses that property to search efficiently.

Duplicate-substring detection combines hashes with a hash table.

Longest repeated substring detection combines hashing with binary search.

This demonstrates how one data representation can become a building block for several higher-level algorithms.
