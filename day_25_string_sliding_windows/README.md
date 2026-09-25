# Day 25 — String Sliding Window

## Topic

**String Sliding Window**

This study covers the sliding-window technique for contiguous string and sequence problems. The central pattern uses one or two moving boundaries to maintain a current window while updating only the state that changes when characters enter or leave.

The implementations cover:

- Longest substring without repetition
- Character-frequency windows
- Minimum-window substring concepts
- Window expansion and contraction
- At-most-K-distinct-character problems
- Exactly-K-distinct-character problems
- Fixed-size windows
- Frequency-constrained windows
- Anagram detection
- Frequency-based replacement problems
- Structured event processing
- Time-based windows
- Validation, testing, debugging, complexity, and implementation trade-offs

---

## 1. What Is a Sliding Window?

A sliding window is an algorithmic technique for processing a contiguous portion of a sequence.

For a string such as `abcdef`, a window may initially represent:

`abc`

and then move to:

`bcd`

then:

`cde`

The window is normally represented by two boundaries:

- `left`: beginning of the current window
- `right`: end of the current window

For an inclusive window, the current length is:

`right - left + 1`

The important idea is that the algorithm does not repeatedly rebuild every substring from scratch. Instead, it maintains information about the current window and updates that information incrementally.

This is especially useful when a problem asks for:

- a longest contiguous substring,
- a shortest valid substring,
- the number of valid substrings,
- a fixed-size contiguous region,
- a region satisfying a frequency constraint,
- a region containing at most or exactly a given number of distinct characters.

---

## 2. Why Sliding Windows Matter

A naive solution may examine many overlapping substrings repeatedly.

For a string of length `n`, there can be approximately `n²` contiguous substrings. If each substring is independently inspected, the resulting algorithm can become O(n²) or worse.

A sliding-window algorithm often reduces the work to O(n).

The main reason is that:

1. The right boundary moves forward.
2. The left boundary also moves forward.
3. Neither boundary normally moves backward.
4. Each character therefore enters the active window once and leaves it at most once.

This produces a total number of pointer movements proportional to the input size.

---

## 3. Fundamental Terminology

### Window

The current contiguous section being analyzed.

For the string `abcdef`, the window `[1, 3]` represents `bcd`.

### Left boundary

The index from which the current window begins.

### Right boundary

The index at which the current window ends.

### Expansion

Moving the right boundary forward and adding a new element to the window.

### Contraction

Moving the left boundary forward and removing an element from the window.

### Window state

The information maintained about the current window.

Examples include:

- character set,
- character frequencies,
- number of distinct characters,
- number of required characters satisfied,
- sum of values,
- maximum frequency,
- number of zeros,
- number of events.

### Invariant

A condition that should remain true at a specific point in the algorithm.

For example:

`distinct <= K`

is the invariant after a variable-size window has been contracted in an at-most-K-distinct problem.

---

## 4. Fixed-Size Sliding Windows

A fixed-size window always contains exactly `k` elements.

Suppose:

`values = [2, 1, 5, 1, 3, 2]`

and:

`k = 3`

The windows are:

- `[2, 1, 5]`
- `[1, 5, 1]`
- `[5, 1, 3]`
- `[1, 3, 2]`

The Python, JavaScript, and C++ implementations demonstrate this structure.

The update is incremental.

Instead of recalculating the sum of every three-element window:

1. subtract the value leaving from the left,
2. add the value entering from the right.

This produces O(n) time.

---

## 5. Variable-Size Windows

Variable-size windows change their length according to a condition.

A common structure is:

1. Move `right`.
2. Add the new character to the window state.
3. Check whether the window is invalid.
4. While invalid, move `left`.
5. Remove each outgoing character from the state.
6. Once valid, evaluate the window.

A typical structure is:

`expand -> validate -> contract if necessary -> record answer`

The exact order depends on whether the problem asks for a longest or shortest window.

---

# 6. Longest Substring Without Repetition

Consider:

`abcabcbb`

The longest substring containing no repeated character has length `3`.

Possible valid windows include:

- `abc`
- `bca`
- `cab`

The critical rule is:

`Every character inside the active window must be unique.`

## Set-Based Approach

A set can store the characters currently inside the window.

When a new character is already present:

1. remove characters from the left,
2. continue until the duplicate disappears,
3. add the new character,
4. update the best answer.

This produces O(n) time because every character is inserted and removed at most once.

## Last-Seen Index Approach

The implementations also use a more direct technique.

Store:

`character -> most recent index`

If the current character was previously seen at index `p`, the left boundary can jump directly to:

`p + 1`

The critical operation is:

`left = max(left, previous_index + 1)`

The `max` is necessary because the previous occurrence may already be outside the current window.

For example, with:

`abba`

when the final `a` is processed, the previous `a` is at index `0`, but the current window already starts after index `1`. The left boundary must not move backward.

---

# 7. Character-Frequency Windows

Some problems do not care only whether a character exists. They care how many times it occurs.

A frequency map represents:

`character -> count`

For:

`aabccbb`

the frequencies are:

- `a -> 2`
- `b -> 2`
- `c -> 2`

Python uses `Counter` and dictionaries.

JavaScript uses `Map`.

C++ uses `unordered_map`.

The underlying algorithmic concept is the same.

---

# 8. At-Most-K Distinct Characters

The problem asks for the longest substring containing no more than `K` distinct characters.

Example:

`eceba`

with:

`K = 2`

The answer has length `3`.

The window maintains:

- character frequencies,
- number of distinct characters.

When a new character has frequency zero before insertion, the distinct-character count increases.

If:

`distinct > K`

the window becomes invalid.

The algorithm then contracts from the left.

When the frequency of a removed character reaches zero, that character is no longer represented in the window and the distinct count decreases.

The invariant after contraction is:

`distinct <= K`

---

# 9. Why Frequency Zero Matters

Suppose the current window is:

`aabbc`

Its distinct characters are:

`a`, `b`, `c`

If the left boundary removes one `a`, the window becomes:

`abbc`

The frequency of `a` changes from `2` to `1`.

`a` is still inside the window, so the number of distinct characters does not change.

If the second `a` is removed:

`bbc`

the frequency becomes zero.

Only then should the distinct count decrease.

This distinction is essential for correct frequency-based sliding windows.

---

# 10. Exactly-K Distinct Characters

Counting substrings with exactly `K` distinct characters can be transformed using two at-most problems.

The identity is:

`exactly(K) = atMost(K) - atMost(K - 1)`

The reason is that:

- `atMost(K)` includes substrings with 0, 1, 2, ..., K distinct characters.
- `atMost(K - 1)` includes substrings with 0, 1, 2, ..., K - 1 distinct characters.
- Subtracting leaves only substrings containing exactly K distinct characters.

This is a general algorithmic transformation that appears in many counting problems.

---

# 11. Counting At-Most-K Substrings

Suppose the current valid window is:

`text[left:right]`

for a particular `right`.

If the window contains at most K distinct characters, then every substring ending at `right` and beginning at one of:

`left, left + 1, ..., right`

is also valid.

The number of such substrings is:

`right - left + 1`

Therefore:

`count += right - left + 1`

This avoids explicitly generating every substring.

The complete counting algorithm therefore remains O(n).

---

# 12. Longest Substring With Exactly K Distinct Characters

For a longest-window problem, the implementation can maintain:

`distinct <= K`

After contraction, when:

`distinct == K`

the current window is a candidate.

This differs from the at-most-K problem only in the condition under which the result is recorded.

The algorithm still contracts whenever:

`distinct > K`

---

# 13. Minimum Window Substring

Minimum-window problems reverse the optimization direction.

Instead of asking:

> What is the longest valid window?

the problem asks:

> What is the shortest window satisfying all requirements?

For:

`text = ADOBECODEBANC`

and:

`target = ABC`

the result is:

`BANC`

The algorithm:

1. Expands from the right.
2. Updates frequency information.
3. Determines whether the current window satisfies the target.
4. Once valid, contracts from the left.
5. Records the smallest valid window.
6. Stops contracting when removing a character would make the window invalid.
7. Continues expanding.

---

# 14. Duplicate Requirements in Minimum Windows

A target can contain duplicate characters.

For example:

`target = AABC`

requires:

- two `A` characters,
- one `B`,
- one `C`.

A window containing only:

`ABC`

is insufficient.

The frequency comparison must therefore be based on required counts rather than merely checking whether each distinct character exists.

This is why the implementation maintains two frequency structures:

- required frequencies,
- current window frequencies.

---

# 15. Satisfied Character Counts

The minimum-window implementation maintains the number of distinct required characters whose required frequencies have been reached.

Suppose:

`required[A] = 2`

and the window currently contains:

`A -> 2`

Then the A requirement is satisfied.

If another A is added:

`A -> 3`

the requirement remains satisfied.

If an A is removed and the count becomes:

`A -> 1`

the A requirement becomes unsatisfied.

This provides an efficient way to determine whether the entire window satisfies the target without comparing every frequency on every iteration.

---

# 16. Longest Repeating Character Replacement

Another important frequency-window problem asks for the longest substring that can be transformed into one repeated character using at most `K` replacements.

For:

`AABABBA`

and:

`K = 1`

a valid maximum-length window has length `4`.

The key calculation is:

`window_length - highest_frequency`

This represents how many characters must be replaced if the most frequent character is retained.

The validity condition is:

`window_length - highest_frequency <= K`

This is a frequency constraint rather than a distinct-character constraint.

---

# 17. Stale Maximum Frequency

In the character-replacement algorithm, the stored `highest_frequency` does not necessarily decrease when the left boundary moves.

This can look suspicious.

The implementation intentionally keeps the historical maximum.

For determining the maximum achievable window length, recomputing the exact maximum frequency after every contraction is unnecessary.

This is an example of an implementation optimization that depends on a carefully understood invariant.

The distinction is important:

- exact current frequency information may be required for some problems,
- a safe historical maximum can be sufficient for this specific optimization.

The technique should not be copied blindly to unrelated sliding-window problems.

---

# 18. Anagram Windows

An anagram window has exactly the same character frequencies as a pattern.

For:

`text = cbaebabacd`

and:

`pattern = abc`

valid starting indices are:

`0` and `6`

because:

- `cba` is an anagram of `abc`,
- `bac` is an anagram of `abc`.

This is a fixed-size sliding window because every candidate window has:

`window_size = pattern_length`

The algorithm:

1. Adds the incoming character.
2. Removes the outgoing character when the window becomes too large.
3. Compares the maintained frequency state with the target requirements.

---

# 19. Unicode Considerations

Python strings provide Unicode-aware character semantics.

JavaScript strings are based on UTF-16 code units. The JavaScript implementation uses `Array.from()` in the important string algorithms so that Unicode code points such as many emoji are handled more naturally.

C++ `std::string` is fundamentally a byte sequence. The C++ case study therefore treats ordinary string input as bytes.

This distinction matters in production systems.

For ASCII data, byte-based processing is straightforward.

For arbitrary UTF-8 text, C++ code that indexes `std::string` by position does not automatically treat each Unicode code point as one character.

A production Unicode-aware C++ implementation would first decode UTF-8 into code points or use an appropriate Unicode library.

---

# 20. Structured Sliding Windows

Sliding windows are not limited to strings.

The C++ implementation demonstrates the same pattern on security events.

Each event contains:

- user ID,
- action,
- timestamp.

The objective is to find the longest contiguous event sequence in which no action repeats.

Instead of:

`character -> last index`

the system maintains:

`action -> last event index`

The algorithm is otherwise structurally similar to the longest unique substring problem.

This demonstrates an important abstraction:

> Sliding-window algorithms operate on ordered sequences, not specifically on text.

---

# 21. Time-Based Sliding Windows

A second C++ case-study component processes timestamps.

Suppose timestamps are:

`100, 101, 102, 105, 106, 110`

and the allowed duration is two time units.

A window is valid when:

`timestamps[right] - timestamps[left] <= duration`

If the difference becomes too large, the left boundary advances.

When timestamps are already sorted, the scan is O(n).

If timestamps are unsorted and must first be sorted, the total process becomes dominated by sorting:

`O(n log n)`

followed by the O(n) window scan.

---

# 22. Why Two Pointers Usually Produce O(n)

Consider a variable-size window.

The right pointer can advance at most `n` times.

The left pointer can also advance at most `n` times.

Therefore, even though there is a nested `while` loop, the total number of pointer movements is usually O(n).

This is a common source of confusion.

A loop nested syntactically inside another loop does not automatically mean O(n²).

The correct analysis depends on how many total times each pointer can move.

---

# 23. Space Complexity

The extra space depends on the maintained state.

For a frequency map:

`O(number of distinct characters)`

For a fixed alphabet:

`O(alphabet size)`

For arbitrary input where every character may be distinct:

`O(n)`

The answer itself may also occupy O(n) space if the actual substring is returned rather than only its length.

---

# 24. Python Implementation

The Python implementation demonstrates a broad collection of patterns.

### Set-Based Unique Window

`longest_substring_without_repetition_set()`

This version uses a set and contracts one character at a time.

It is particularly useful for learning the fundamental expand-contract process.

### Last-Seen Unique Window

`longest_substring_without_repetition_last_seen()`

This version stores the last position of every character and jumps the left boundary.

### At-Most-K Distinct

`longest_substring_with_at_most_k_distinct()`

This demonstrates frequency tracking and distinct-count maintenance.

### Minimum Window

`minimum_window_substring()`

This demonstrates a requirement frequency map and a satisfied-requirement count.

### Exactly-K Counting

`count_substrings_with_exactly_k_distinct()`

This demonstrates the at-most transformation.

### Frequency Replacement

`longest_repeating_character_replacement()`

This demonstrates a frequency-based validity condition.

### Anagrams

`find_anagram_start_indices()`

This demonstrates fixed-size frequency windows.

### Structured Data

`longest_unique_action_sequence()`

This demonstrates that the technique can operate on structured records.

---

# 25. JavaScript Implementation

JavaScript provides useful demonstrations of the same algorithms in an application-oriented environment.

The implementation uses:

- `Map` for frequency tables,
- `Array.from()` for Unicode-friendly character iteration,
- arrays for fixed-size numeric windows,
- explicit validation with exceptions,
- executable tests,
- console-based state tracing.

The JavaScript implementation also exposes how sliding windows fit naturally into client-side and server-side application code.

For example, a browser application could use similar logic to analyze:

- user-entered strings,
- search terms,
- log streams,
- text-processing requests,
- event sequences.

---

# 26. C++ Case Study

The C++ implementation models a security-event analysis system.

Each event contains:

- `userId`
- `action`
- `timestamp`

The system analyzes ordered event streams.

The primary class is `SecurityEventAnalyzer`.

Its main operation identifies the longest contiguous event sequence containing unique actions.

For example, a sequence such as:

`LOGIN -> SEARCH -> VIEW -> DOWNLOAD`

is valid if each action appears only once within the current window.

When `SEARCH` occurs again, the left boundary jumps past its previous occurrence.

This is directly analogous to the longest substring without repetition problem.

---

# 27. C++ Architectural Components

The C++ program contains several distinct layers.

### Data Model

`SecurityEvent`

Represents one event.

### Result Types

`StringWindowResult`

Stores the length and actual string for string algorithms.

`EventWindowResult`

Stores the beginning and length of a selected event sequence.

### Algorithm Functions

The program separates algorithms into independent functions such as:

- `longestUniqueSubstring`
- `longestAtMostKDistinct`
- `countAtMostKDistinct`
- `countExactlyKDistinct`
- `minimumWindow`
- `longestRepeatingReplacement`
- `maximumEventsInTimeWindow`

### Domain Service

`SecurityEventAnalyzer`

Encapsulates event-window analysis.

### Validation

Invalid parameters generate standard C++ exceptions.

### Tests

The program uses explicit assertions implemented through helper functions.

This organization keeps the algorithmic logic testable and reusable.

---

# 28. Security-Relevant Applications

Sliding windows have many legitimate applications in security and systems engineering.

Examples include:

- rate-limit detection,
- authentication-event analysis,
- repeated-action detection,
- session analysis,
- burst detection,
- network traffic analysis,
- log-stream processing,
- anomaly feature construction,
- request throttling,
- event aggregation.

For example, a service may want to determine:

> How many requests occurred during the most recent 10-second interval?

A timestamp-based sliding window can answer that without recomputing the count for every possible interval.

---

# 29. Rate Limiting

A rate limiter may maintain recent request timestamps.

For a fixed time interval:

`window = [current_time - duration, current_time]`

Old timestamps are removed from the left as they become too old.

The remaining number of timestamps represents the requests currently inside the time window.

This is conceptually the same expand-contract mechanism used for strings.

The production design must also consider:

- concurrent requests,
- clock behavior,
- memory limits,
- distributed servers,
- synchronization,
- persistence,
- eviction policies,
- denial-of-service resistance.

---

# 30. Common Mistakes

## Mistake 1: Moving the Left Boundary Backward

Incorrect logic can accidentally assign:

`left = previous_index + 1`

without checking whether the previous index belongs to the current window.

The safer form is:

`left = max(left, previous_index + 1)`

---

## Mistake 2: Forgetting to Remove Frequencies

When a character leaves the window, its count must be decremented.

If the count reaches zero, it should usually be removed from the frequency map.

Otherwise the distinct-character count becomes incorrect.

---

## Mistake 3: Counting Distinct Characters Instead of Frequencies

For minimum-window problems, simply knowing whether a character exists is insufficient.

If the target is `AABC`, the window needs two copies of `A`.

---

## Mistake 4: Contracting Only Once

When a window is invalid, removing exactly one character may not be enough.

The correct pattern is usually:

`while window is invalid: contract`

not merely:

`if window is invalid: contract once`

---

## Mistake 5: Using the Wrong Optimization Direction

Longest-window problems generally:

1. expand,
2. contract when invalid,
3. record valid windows.

Minimum-window problems generally:

1. expand,
2. wait until valid,
3. contract aggressively,
4. record smaller valid windows.

---

## Mistake 6: Confusing Exactly K With At Most K

These are different conditions.

`at most K`

allows:

`0, 1, 2, ..., K`

distinct characters.

`exactly K`

allows only:

`K`

distinct characters.

---

## Mistake 7: Assuming Every Nested While Loop Is O(n²)

The sliding-window contraction loop often advances the left pointer monotonically.

The total number of contractions is therefore bounded by O(n).

---

## Mistake 8: Ignoring Encoding

A C++ byte-oriented algorithm should not automatically be described as Unicode-character aware.

JavaScript UTF-16 semantics also require attention.

The unit being processed must be explicitly defined.

---

# 31. Edge Cases

Important test cases include:

### Empty Input

`""`

The result is normally an empty window or zero.

### Single Character

`"a"`

The longest unique substring has length one.

### All Characters Equal

`"aaaaaa"`

The longest unique substring has length one.

### All Characters Different

`"abcdef"`

The entire string is unique.

### K Equals Zero

An at-most-zero-distinct problem has an empty result for a non-empty input.

### K Greater Than the Number of Distinct Characters

The entire string can be valid for an at-most-K problem.

### Target Longer Than Source

A minimum-window result is impossible.

### Duplicate Target Characters

Frequency requirements must be respected.

### Unicode Text

The character model must be explicitly understood.

### Invalid Numeric Parameters

Negative K values or zero-size fixed windows should be rejected where the operation requires a positive size.

---

# 32. Debugging Sliding-Window Algorithms

The most useful debugging information is usually:

- current `left`,
- current `right`,
- incoming character,
- outgoing character,
- current frequencies,
- current distinct count,
- validity condition,
- current best result.

The Python and JavaScript implementations include tracing examples.

For a problematic input such as:

`abcad`

a trace can reveal that:

1. `a`, `b`, `c` create a valid unique window.
2. the second `a` creates a duplicate,
3. the left boundary jumps beyond the earlier `a`,
4. the active window becomes `bcda`.

Writing the invariant next to the trace is often more useful than printing the entire program state.

---

# 33. Invariant-First Design

Before implementing a sliding window, explicitly define the invariant.

Examples:

### Unique Characters

`No character appears more than once in the window.`

### At Most K Distinct

`The window contains no more than K distinct characters.`

### Minimum Target Window

`The window contains every required character with the required frequency.`

### Character Replacement

`window_length - highest_frequency <= K`

### Time Window

`timestamp[right] - timestamp[left] <= duration`

Once the invariant is clear, the contraction condition becomes much easier to derive.

---

# 34. Longest Versus Minimum Windows

The distinction can be expressed as follows.

## Longest Valid Window

Expand until invalid.

Then contract until valid again.

Record the largest valid window.

Typical pattern:

`expand -> contract while invalid -> maximize`

## Minimum Valid Window

Expand until valid.

Then contract while validity remains.

Record the smallest valid window.

Typical pattern:

`expand -> contract while valid -> minimize`

Recognizing this distinction is one of the most important skills in sliding-window problems.

---

# 35. Fixed-Size Versus Variable-Size Windows

| Property | Fixed-Size | Variable-Size |
|---|---|---|
| Window length | Constant | Changes |
| Typical control | One outgoing and one incoming element | Expand and contract |
| Example | Anagram search | Minimum window |
| Typical state | Sum/frequency | Constraint/frequency |
| Pointer movement | Right advances continuously | Both boundaries advance according to validity |

Neither pattern is inherently better. The correct choice depends on the problem's constraints.

---

# 36. Set Versus Frequency Map

A set is appropriate when the only question is:

> Does this character currently exist?

A frequency map is appropriate when the question is:

> How many times does this character currently exist?

Use a set for simple uniqueness.

Use a frequency map for:

- K distinct problems,
- minimum windows,
- anagram detection,
- replacement problems,
- count constraints.

Choosing the smallest state representation that supports the invariant usually improves clarity.

---

# 37. Performance Considerations

For a string of length `n`, the main target for a sliding-window solution is usually:

`O(n)`

For minimum-window substring with target length `m`, the typical complexity is:

`O(n + m)`

Space is generally:

`O(number of distinct keys)`

assuming hash-map operations are average O(1).

For fixed alphabets such as lowercase English letters, arrays of fixed size can sometimes replace hash maps.

For example, a 26-element integer array may be faster and more memory-predictable than a hash map when the input domain is explicitly limited to lowercase English letters.

That optimization should not be applied when the input domain is unrestricted.

---

# 38. Hash Map Trade-Offs

Python dictionaries, JavaScript `Map`, and C++ `unordered_map` generally provide average constant-time insertion and lookup.

The trade-offs include:

- hashing overhead,
- memory overhead,
- possible collision behavior,
- allocation costs,
- cache locality,
- implementation complexity.

For small fixed alphabets, direct indexing can be more efficient.

For arbitrary characters or structured keys, hash-based maps are more flexible.

---

# 39. Production Considerations

A production implementation should define:

- accepted input encoding,
- maximum input size,
- memory limits,
- expected character domain,
- timestamp semantics,
- ordering guarantees,
- error-handling behavior,
- concurrency requirements,
- logging requirements,
- testing strategy.

For untrusted input, resource limits matter.

A theoretically O(n) algorithm can still consume excessive memory if a malicious input contains a very large number of distinct keys.

---

# 40. Testing Strategy

A reliable sliding-window implementation should include:

### Known Examples

Use standard examples where the expected result is known.

### Boundary Cases

Test:

- empty input,
- one element,
- all identical elements,
- all unique elements,
- K = 0,
- K = 1,
- K larger than the input's distinct count.

### Impossible Cases

For example:

`text = "a"`

`target = "aa"`

The expected minimum window is empty.

### Randomized Comparison

For complex implementations, a simple brute-force implementation can serve as a reference for small random inputs.

The Python implementation includes a naive unique-substring algorithm and compares its answer length with the optimized implementation.

This is a useful general testing technique:

`simple reference implementation -> optimized implementation -> compare results`

---

# 41. Implementation Comparison

| Concept | Python | JavaScript | C++ |
|---|---|---|---|
| Frequency map | `Counter` / `dict` | `Map` | `unordered_map` |
| Set | `set` | `Set` | `unordered_set` |
| String handling | Unicode-oriented | UTF-16 with `Array.from()` used for code points | `std::string` byte sequence |
| Error handling | Exceptions | Exceptions | Exceptions |
| Testing | Assertions | Explicit test helper | Explicit assertion helpers |
| Structured case study | Dataclass records | Application-oriented functions | Security-event class |
| Time-window case study | Demonstrated conceptually | Demonstrated conceptually | Implemented with timestamps |
| Low-level control | Moderate | Moderate | High |

The algorithms are language-independent, but each language exposes different implementation concerns.

---

# 42. Python-Specific Characteristics

Python is particularly convenient for studying sliding windows because dictionaries, sets, and `Counter` make state maintenance concise.

Examples:

- `set()` for uniqueness,
- `Counter()` for frequency requirements,
- `defaultdict(int)` for mutable counts.

This reduces implementation overhead and makes the algorithmic invariant easier to see.

Python can also be useful for quickly validating an algorithm against a brute-force reference implementation.

---

# 43. JavaScript-Specific Characteristics

JavaScript's `Map` and `Set` are natural structures for sliding-window state.

The implementation also demonstrates why string indexing deserves attention.

Using:

`text[index]`

operates on UTF-16 code units.

Using:

`Array.from(text)`

allows iteration over Unicode code points for many common cases.

This does not make every possible Unicode-grapheme problem automatically solved. User-perceived characters can consist of multiple Unicode code points.

For advanced internationalized text processing, the semantic definition of "character" must be explicit.

---

# 44. C++-Specific Characteristics

C++ provides more direct control over:

- memory,
- object lifetime,
- containers,
- exception behavior,
- data structures,
- performance characteristics.

The C++ case study therefore moves beyond isolated string examples into a structured event-processing design.

`unordered_map` supports average constant-time lookup, while vectors provide contiguous storage and predictable iteration.

For very performance-sensitive systems, fixed-size frequency arrays can be considered when the input alphabet is known.

---

# 45. Practical Problem-Solving Checklist

When encountering a new string problem, ask:

1. Is the problem about a contiguous region?
2. Is the region a substring or subarray?
3. Is the window size fixed?
4. If not, what makes the window valid?
5. What information must be maintained?
6. Can that information be updated when an element enters?
7. Can it be updated when an element leaves?
8. When does the window become invalid?
9. When should the left boundary move?
10. Is the objective to maximize or minimize?
11. Is the problem asking for a count?
12. Can exactly-K be transformed into at-most-K?
13. What is the invariant?
14. Can each pointer move only forward?
15. What is the resulting time complexity?
16. What is the required extra space?
17. Are Unicode or encoding semantics relevant?
18. What happens for empty input?
19. What happens for impossible constraints?
20. What test cases can expose an incorrect boundary update?

---

# 46. Core Patterns to Recognize

### Pattern A: Longest Unique

State:

`set` or `last_seen`

Validity:

`no duplicate`

Optimization:

`maximize`

### Pattern B: Longest At Most K Distinct

State:

`frequency map + distinct count`

Validity:

`distinct <= K`

Optimization:

`maximize`

### Pattern C: Minimum Window

State:

`required frequencies + current frequencies`

Validity:

`all requirements satisfied`

Optimization:

`minimize`

### Pattern D: Exactly K Counting

State:

`frequency map`

Transformation:

`atMost(K) - atMost(K - 1)`

### Pattern E: Fixed-Size Frequency Window

State:

`frequency map`

Window:

`exactly pattern length`

Application:

`anagram detection`

### Pattern F: Frequency Replacement

State:

`frequency map + maximum frequency`

Validity:

`window length - maximum frequency <= K`

---

# 47. Final Complexity Reference

| Algorithm | Typical Time | Extra Space |
|---|---:|---:|
| Fixed-size window | O(n) | O(1) to O(k), depending on state |
| Longest unique substring | O(n) | O(distinct characters) |
| At-most-K distinct | O(n) | O(distinct characters) |
| Exactly-K count | O(n) | O(distinct characters) |
| Minimum window | O(n + m) | O(distinct target characters) |
| Anagram search | O(n) | O(distinct pattern characters) |
| Character replacement | O(n) | O(distinct characters) |
| Sorted timestamp window | O(n) | O(1) auxiliary for the scan |

Here, `n` represents the source sequence length and `m` represents the target length where applicable.

---

# 48. Implementation Files

The Python implementation is designed as a broad study and experimentation file. It progresses from basic window mechanics through optimized algorithms, testing, tracing, and structured-data examples.

The JavaScript implementation provides equivalent algorithmic patterns with JavaScript-specific handling for `Map`, `Set`, Unicode iteration, validation, and executable tests.

The C++ implementation develops the concept into a security-event analysis case study. It demonstrates how the same sliding-window abstractions can operate over structured records and timestamp sequences rather than only strings.
