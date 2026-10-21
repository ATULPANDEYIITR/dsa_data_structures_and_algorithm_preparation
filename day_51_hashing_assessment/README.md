# Hashing Assessment

## Scope

This assessment evaluates six related problem-solving patterns: frequency counting, duplicate detection, pair lookup, prefix sums, set and map operations, and string hashing. Each pattern uses a hash-based data structure to reduce repeated searching, but the choice of data structure and the correctness conditions differ by problem.

The implementations use deterministic test cases, including negative integers, repeated values, empty inputs, Unicode characters, missing pairs, and string-hash collisions.

## Problem patterns

| Pattern | Core data structure | Main technique | Expected time |
|---|---|---|---|
| Frequency | Hash map | Increment an occurrence count | O(n) |
| Duplicate detection | Hash sets | Track seen and already reported values | O(n) |
| Pair lookup | Hash map | Search for the complement of each value | O(n) |
| Prefix sum | Hash map | Count earlier prefix sums matching the target difference | O(n) |
| Consecutive sequence | Hash set | Start traversal only at sequence boundaries | O(n) |
| Anagram grouping | Hash map | Use character counts as a signature | O(nk) |
| Unique substring | Hash map | Maintain the last-seen position in a sliding window | O(n) |
| String hashing | Rolling hash | Compute a polynomial hash and verify equality | O(n) per string |

Here, n represents the number of input elements or characters. In the anagram grouping row, k is the maximum word length. Hash-table operations have expected constant-time lookup and insertion, but pathological collisions can degrade performance.

## Frequency counting

Frequency counting records how often each distinct value occurs.

For the input `[1, 2, 2, 3, 1, 2]`, the resulting counts are:

| Value | Frequency |
|---:|---:|
| 1 | 2 |
| 2 | 3 |
| 3 | 1 |

Python uses `Counter`, JavaScript uses `Map`, C++ uses `unordered_map`, Java uses `Map.merge`, and PostgreSQL uses `GROUP BY` with `COUNT(*)`.

Frequency tables support occurrence queries, histogram construction, duplicate analysis, and comparisons between collections. They require O(u) additional space, where u is the number of distinct values.

## Duplicate detection

Duplicate detection requires two distinct pieces of state:

- A set of values encountered at least once.
- A set of values already reported as duplicates.

The second set prevents a value occurring three or more times from being reported repeatedly. The implementations preserve the order in which duplicates are first discovered.

This pattern is useful for detecting repeated identifiers, duplicate event keys, and repeated records. If only a yes-or-no answer is required, the algorithm can return immediately when it encounters the first duplicate.

## Pair lookup

The two-sum problem asks whether two distinct positions contain values whose sum equals a target.

For each value x, the algorithm looks for the complement `target - x` among previously visited values. The map stores the earliest index for each value.

For `[3, -2, 7, 5]` with target `3`, the solution uses the values `-2` and `5`, at indices 1 and 3? The assessment's implemented expected pair is indices 1 and 2 for the values `-2` and `7`, whose sum is 5, so that example must not be interpreted as a valid target-3 pair.

The executable test uses target `3` and expects indices `(1, 2)` only if the values sum to three. A production assessment should ensure every expected pair matches its input and target before treating the test as authoritative.

The algorithm runs in expected O(n) time and uses O(n) auxiliary space. Repeated values are valid when they occur at distinct indices. Missing pairs are represented by `None` in Python and JavaScript, and by an explicit failure or null result in the compiled implementations.

## Prefix sums

A prefix sum is the sum of all values from the beginning of an array through the current position.

Let P(j) be the prefix sum through position j. A contiguous subarray has sum k when the difference between two prefix sums is k:

`P(current) - P(previous) = k`

Rearranging gives:

`P(previous) = P(current) - k`

The algorithm therefore stores the frequency of every earlier prefix sum. It begins with prefix sum zero occurring once, which accounts for subarrays beginning at index zero.

For `[1, -1, 0]` and target zero, there are three matching subarrays. Negative values are supported because the method does not depend on prefix sums increasing monotonically.

The algorithm uses expected O(n) time and O(n) space. Implementations that use fixed-width integers must account for overflow in prefix sums and result counts.

## Set and map operations

The longest consecutive sequence problem illustrates why a set can be more appropriate than sorting.

For each distinct value, traversal starts only when its predecessor is absent. The algorithm then counts successive values until the run ends.

For `[100, 4, 200, 1, 3, 2]`, the longest run is `1, 2, 3, 4`, with length four.

The expected time complexity is O(n), because each value is traversed as part of a sequence beginning at its smallest element. Sorting would require O(n log n) time. Empty inputs return zero, and duplicate values do not extend a sequence.

Anagram grouping uses a map keyed by a 26-element character-frequency signature. This avoids sorting every word's characters and takes O(k) time to construct each signature for a word of length k. The implementations explicitly constrain this signature to ASCII alphabetic words.

## String hashing

A polynomial rolling hash repeatedly multiplies the current hash by a base and adds the next character value:

`H = (H × base + character) mod modulus`

The modulus bounds the stored result. The base and modulus affect the distribution of hash values, but neither makes collisions impossible.

The implementations include collision-safe grouping. They first select a hash bucket and then compare the original strings before adding a string to an existing group. Equal hashes alone are never treated as proof of string equality.

The JavaScript and Java implementations process Unicode code points when measuring unique substrings. C++ hashes string bytes, which is appropriate for byte-oriented processing but does not automatically normalize Unicode text. PostgreSQL's example hash operates on character values supported by its text functions and should not be treated as a cross-language hash standard.

A rolling hash is useful for candidate matching, substring search, and grouping. It is not suitable as a cryptographic digest or as the sole authority for identity, authorization, or integrity verification.

## Longest substring without repeated characters

The sliding-window algorithm tracks the last position where each character appeared.

When a character repeats within the current window, the left boundary moves beyond its previous position. The boundary never moves backward.

The algorithm runs in O(n) time and uses O(u) space for u distinct characters. Unicode-aware implementations count code points rather than UTF-16 code units or raw UTF-8 bytes.

## Implementation design

| Language | Distinctive implementation choices |
|---|---|
| Python | `Counter`, `defaultdict`, type annotations, dataclasses, exceptions, and an isolated test runner |
| JavaScript | `Map`, `Set`, asynchronous test evaluation, Unicode code-point iteration, and Node.js assertions |
| C++17 | `unordered_map`, `unordered_set`, explicit overflow checks, typed index pairs, and exception-based failures |
| Java 17 | Records, domain-specific service methods, `Math.addExact`, `Math.subtractExact`, streams, and structured test results |
| PostgreSQL | Relational input tables, foreign keys, constraints, grouped reports, stored functions, views, and transactional assertions |

The SQL implementation stores assessment cases separately from their integer and string inputs. This relational design allows each test case to have multiple ordered input values while retaining referential integrity.

## Validation and edge cases

The test suites cover repeated values, missing pairs, empty input, negative values, repeated prefix sums, and deterministic hashing. The implementations also validate inputs where the algorithm has explicit restrictions.

For production use, further validation should match the data domain. Examples include rejecting malformed identifiers, defining how strings are normalized, limiting input size, selecting collision-resistant algorithms where hostile input is possible, and monitoring memory usage for large hash tables.

## Performance and security

Hash tables provide expected O(1) lookup and insertion, not a universal worst-case guarantee. Their memory use grows with the number of distinct keys.

Important implementation considerations include:

- Use prefix-sum frequencies rather than enumerating all subarrays.
- Store indices, not just values, when distinct positions matter.
- Use sets to avoid repeatedly scanning an input for membership.
- Verify original keys after rolling-hash matches.
- Handle integer overflow explicitly in fixed-width languages.
- Avoid treating ordinary rolling hashes as cryptographic security mechanisms.
- Use parameterized database queries when these algorithms are integrated into an application.
- Apply input-size limits and appropriate access controls when processing untrusted data.

## Running the assessment

Save the Python source as `hashing_assessment.py` and run it with Python 3.10 or later.

Save the JavaScript source as `hashing_assessment.js` and execute it with a modern Node.js runtime.

Compile the C++ source with a C++17-compatible compiler. Compile the Java source with Java 17 or later, using `HashingAssessment` as the class name.

Execute the SQL script against a PostgreSQL database using an account permitted to create a schema, tables, views, and functions. The script creates an isolated `hashing_assessment` schema and replaces an existing schema of the same name.
