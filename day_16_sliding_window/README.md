# Day 16 — Sliding Window

## Topic overview

The sliding-window technique is an algorithmic method for processing contiguous portions of an array, string, or other sequential data without repeatedly rebuilding the same range.

A window is represented by two boundaries, commonly called `left` and `right`. The right boundary usually expands the window by including new elements. The left boundary contracts the window when a constraint is violated or when a better answer may be obtained by removing unnecessary elements.

The main advantage is incremental state maintenance. Instead of calculating every subarray independently, information about the current window is reused when the window moves.

For many problems, this changes an algorithm from `O(n²)` or `O(nk)` into `O(n)`.

This chapter covers:

- fixed-size windows
- variable-size windows
- window expansion
- window contraction
- maximum-sum subarrays
- minimum-size subarrays
- longest valid subarrays
- frequency-based windows
- distinct-element windows
- string windows
- monotonic deques
- edge cases
- implementation constraints
- performance considerations
- a network-traffic monitoring case study

---

## Fundamental concept

Consider an array:

`[2, 1, 5, 1, 3, 2]`

Suppose the window size is `3`.

The windows are:

`[2, 1, 5]`

`[1, 5, 1]`

`[5, 1, 3]`

`[1, 3, 2]`

A naive algorithm calculates the sum of each window independently. That repeats work.

The first window has sum:

`2 + 1 + 5 = 8`

When the window moves one position to the right:

`[1, 5, 1]`

The value `2` leaves the window and `1` enters it.

Therefore:

`new_sum = old_sum - outgoing + incoming`

`new_sum = 8 - 2 + 1 = 7`

Only two updates are required.

This is the central idea behind fixed-size sliding windows.

---

## Window boundaries

The two most important variables are usually:

- `left`: index of the first element in the current window
- `right`: index of the last element in the current window

The current window is:

`values[left:right + 1]`

Its length is:

`right - left + 1`

A common source of errors is confusing the window length with the distance between the two pointers.

For example, if:

`left = 2`

and:

`right = 5`

then the window contains indices `2`, `3`, `4`, and `5`.

Its length is:

`5 - 2 + 1 = 4`

---

## Fixed-size windows

A fixed-size window always contains exactly `k` elements.

The basic structure is:

1. Construct the first window.
2. Store its state.
3. Move the right side one position.
4. Remove the element leaving from the left.
5. Add the new element entering from the right.
6. Update the answer.
7. Continue until the sequence ends.

The window invariant is:

`window length = k`

The Python implementation demonstrates this technique through `max_sum_subarray()`, `minimum_sum_subarray()`, `fixed_window_sums()`, and `maximum_average_subarray()`.

The JavaScript implementation provides corresponding functions using arrays and `Map`.

The C++ implementation uses `vector<int>` and `long long` for accumulated sums.

---

## Maximum sum subarray of size k

The problem is:

Given an array and an integer `k`, find the largest sum among all contiguous subarrays of exactly `k` elements.

For:

`[2, 1, 5, 1, 3, 2]`

and:

`k = 3`

the window sums are:

- `[2, 1, 5]` → `8`
- `[1, 5, 1]` → `7`
- `[5, 1, 3]` → `9`
- `[1, 3, 2]` → `6`

Therefore the maximum is `9`.

### Brute-force approach

For each possible starting position, sum all `k` elements.

There are approximately `n` windows, and each window requires `k` operations.

Time complexity:

`O(nk)`

Space complexity:

`O(1)`

### Sliding-window approach

Calculate the first window once.

For every subsequent window:

`window_sum += incoming`

`window_sum -= outgoing`

The total number of updates is proportional to `n`.

Time complexity:

`O(n)`

Space complexity:

`O(1)`

The Python program contains both `max_sum_subarray_bruteforce()` and `max_sum_subarray()` so their algorithmic difference can be compared directly.

---

## Negative values

A fixed-size sum window works correctly with negative numbers.

For example:

`[-5, -2, -8]`

with:

`k = 2`

produces:

- `[-5, -2]` → `-7`
- `[-2, -8]` → `-10`

The maximum is `-7`.

An important implementation detail is to initialize the best result from the first valid window rather than using `0`.

If the array contains only negative values, initializing the result to zero would incorrectly return zero even though zero is not a valid window sum.

The implementations use the first window as the initial answer.

---

## Integer overflow

In C++, the individual array elements may be `int`, while the accumulated window sum is stored in `long long`.

This is important when a large number of values are added.

For example, if a window contains millions of large integers, an `int` accumulator can overflow.

The C++ implementation therefore uses `long long` for window sums and traffic totals.

Python integers automatically expand to accommodate large integer values.

JavaScript uses the `Number` type for ordinary numeric calculations. For values exceeding the exact integer range of `Number`, `BigInt` may be required in a production implementation.

---

## Window expansion

Variable-size windows do not have a fixed length.

The right pointer normally moves forward and adds data to the current window.

Conceptually:

`right → right + 1`

The state of the window is updated to account for the new element.

For a sum constraint, this may mean:

`window_sum += values[right]`

For a frequency constraint, it may mean:

`frequency[value] += 1`

For a distinct-element constraint, the frequency map may gain a new key.

Expansion continues until the window becomes invalid or the sequence ends.

---

## Window contraction

When a variable window becomes invalid, the left pointer moves forward.

Conceptually:

`left → left + 1`

The element leaving the window must be removed from the maintained state.

For a sum:

`window_sum -= values[left]`

For a frequency map:

`frequency[values[left]] -= 1`

If the resulting frequency becomes zero, the key should normally be removed.

This produces an important invariant:

> After contraction finishes, the active window satisfies the problem's validity condition.

---

## Minimum-size subarray

A common problem is:

Find the minimum length of a contiguous subarray whose sum is at least a target.

For:

`[2, 3, 1, 2, 4, 3]`

and target:

`7`

one valid window is:

`[4, 3]`

with length `2`.

The algorithm expands the right boundary until the sum reaches the target.

It then contracts from the left while the window remains valid.

This is important because the goal is not to find the longest valid window. The algorithm is deliberately trying to make a valid window smaller.

The Python function is `minimum_size_subarray_sum()`.

The JavaScript function is `minimumSizeSubarraySum()`.

The C++ function is `minimumSizeSubarraySum()`.

---

## Why non-negative values matter

The minimum-size sum technique depends on monotonic behavior.

When values are non-negative:

- adding an element cannot decrease the sum
- removing an element cannot increase the sum

This makes pointer movement predictable.

With negative values, these properties disappear.

For example, adding `-10` can decrease the sum substantially.

As a result, the simple two-pointer algorithm is not generally correct for arbitrary arrays containing negative values.

This distinction is one of the most important limitations of sliding-window algorithms.

A sliding-window solution must not be applied merely because the problem involves contiguous subarrays. The conditions that make the window invariant valid must be checked first.

---

## Longest valid subarray

Many problems ask for the longest contiguous subarray satisfying a constraint.

A common structure is:

1. Expand the right pointer.
2. Add the new value to the state.
3. Check whether the window is valid.
4. If invalid, contract from the left.
5. Once valid, update the maximum length.

The Python implementation demonstrates this with `longest_subarray_sum_at_most()` and distinct-element functions.

The JavaScript implementation uses the same conceptual pattern with `Map`.

The C++ implementation uses `unordered_map`.

---

## At most k distinct elements

Consider:

`[1, 2, 1, 2, 3]`

Suppose a window may contain at most two distinct values.

The window:

`[1, 2, 1, 2]`

contains only two distinct values and is valid.

When `3` enters:

`[1, 2, 1, 2, 3]`

the window contains three distinct values and becomes invalid.

The left pointer moves forward until the number of distinct values returns to two.

A frequency map is useful because it distinguishes between:

- a value appearing many times
- a value disappearing completely

For example:

`1 → 3 occurrences`

Removing one `1` produces:

`1 → 2 occurrences`

The value remains part of the distinct set.

Only when its frequency reaches zero should it be removed from the map.

---

## Frequency-based windows

Frequency-based sliding windows maintain counts for elements inside the current window.

A common structure is:

`frequency[value] += 1`

when expanding.

When contracting:

`frequency[value] -= 1`

If the count reaches zero:

`delete frequency[value]`

or the equivalent operation in the chosen language.

Frequency maps are useful for:

- anagram detection
- duplicate detection
- distinct-element constraints
- character replacement problems
- frequency thresholds
- counting-based validity rules

---

## Longest substring without repeating characters

The string:

`abcabcbb`

contains the longest non-repeating substring:

`abc`

with length `3`.

A frequency-map implementation can contract the window one character at a time.

A more optimized technique stores the most recent index of each character.

When a duplicate is found, the left boundary can jump directly to one position after the previous occurrence.

The Python implementation uses `last_seen`.

The C++ implementation uses an `unordered_map<char, int>`.

The JavaScript implementation uses a `Map`.

The important invariant is:

> The current window contains no repeated character.

---

## Distinct-element windows

The function `count_distinct_in_every_window()` in Python and `distinctCountInEveryWindow()` in JavaScript demonstrate a fixed-size frequency window.

For:

`[1, 2, 1, 3, 4, 2, 3]`

and:

`k = 4`

the windows are:

- `[1, 2, 1, 3]` → `3` distinct values
- `[2, 1, 3, 4]` → `4`
- `[1, 3, 4, 2]` → `4`
- `[3, 4, 2, 3]` → `3`

The frequency map lets the algorithm update the distinct count without rescanning the entire window.

---

## Anagram and permutation windows

An anagram has the same character frequencies as another string.

For example:

`abc`

and:

`bca`

have identical frequency counts.

A permutation search can therefore use a fixed-size window with:

`window length = pattern length`

For every window, compare its frequency distribution against the pattern's frequency distribution.

The Python implementation contains:

`permutation_in_string()`

and:

`find_all_anagram_starts()`

The JavaScript implementation contains:

`containsPermutation()`

and:

`findAnagramStarts()`

The key idea is that character order does not matter, but frequency does.

---

## Binary-array windows

A useful variable-window pattern treats a limited resource as the constraint.

For example:

Find the longest sequence of ones after flipping at most `k` zeros.

The current window is valid when:

`number_of_zeros <= k`

When another zero causes:

`zero_count > k`

the left pointer moves until the constraint is restored.

This technique generalizes to many resource-budget problems.

The resource might be:

- number of zero values
- number of replacements
- number of errors
- number of mismatches
- total cost
- number of special events

The important part is identifying a state variable that accurately represents the validity constraint.

---

## Character replacement

Consider:

`AABABBA`

Suppose at most one character may be replaced.

For a window of length `L`, let the most frequent character appear `F` times.

The number of replacements needed is:

`L - F`

The window is valid when:

`L - F <= k`

This creates a useful frequency-based invariant.

The Python function is `longest_repeating_character_replacement()`.

The JavaScript implementation provides `longestRepeatingCharacterReplacement()`.

---

## Product-based windows

For strictly positive values, a variable window can also be used for product constraints.

For example:

`[10, 5, 2, 6]`

with target product `100`.

A window can expand by multiplying the incoming value.

When the product becomes large enough, the left side can be contracted by dividing out the outgoing value.

The positive-value restriction is important.

Zeros and negative values change the behavior of the product and invalidate the simple monotonic reasoning used by this implementation.

The Python implementation provides `minimum_size_subarray_product()`.

The JavaScript implementation provides `minimumSizeSubarrayProduct()`.

---

## Monotonic deque

A frequency map is not enough when the task is:

Find the maximum value in every fixed-size window.

A naive approach scans every window.

That costs:

`O(nk)`

A monotonic deque can solve the problem in:

`O(n)`

The deque stores indices rather than just values.

For a maximum window, values represented by the deque are maintained in decreasing order.

Therefore:

`deque.front()`

always points to the current maximum.

Before inserting a new value, smaller values at the back can be removed because they cannot become the maximum while the larger new value remains inside the active window.

Expired indices are removed from the front.

Each index enters the deque once and leaves at most once, producing amortized `O(n)` time.

---

## Sliding-window maximum

For:

`[1, 3, -1, -3, 5, 3, 6, 7]`

with:

`k = 3`

the maximum values are:

`[3, 3, 5, 5, 6, 7]`

The Python implementation is `sliding_window_maximum()`.

The JavaScript implementation uses the `IndexDeque` class.

The C++ implementation uses `std::deque<int>`.

The C++ version demonstrates why indices are preferable to values: indices allow the algorithm to determine whether a candidate has expired.

---

## Sliding-window minimum

The same idea works for minimum values.

For a minimum deque, the values represented by indices are maintained in increasing order.

The smallest candidate is therefore at the front.

The Python implementation provides `sliding_window_minimum()`.

The JavaScript implementation provides the same functionality.

The C++ program focuses primarily on the maximum case and also uses monotonic deques for simultaneous maximum and minimum tracking.

---

## Longest subarray where max minus min is bounded

Consider a problem requiring:

`max(window) - min(window) <= limit`

Two deques can maintain the extrema.

The maximum deque is decreasing.

The minimum deque is increasing.

When the difference becomes greater than the limit, the left pointer contracts the window.

The Python function is `longest_subarray_absolute_difference()`.

The JavaScript function is `longestSubarrayAbsoluteDifference()`.

The C++ function is `longestAbsoluteDifferenceWindow()`.

The important insight is that sliding-window state does not have to be a simple sum or frequency count. It can consist of sophisticated data structures that maintain a window invariant efficiently.

---

## Amortized analysis

A common concern is that a loop such as:

`while window is invalid`

appears to be nested inside the main loop.

This does not automatically mean the algorithm is `O(n²)`.

If the left pointer only moves forward and never moves backward, then over the entire algorithm it can advance at most `n` times.

Similarly, the right pointer advances at most `n` times.

Therefore:

`total pointer movement <= 2n`

which is:

`O(n)`

This is amortized analysis.

It is fundamental to understanding why many sliding-window algorithms are linear.

---

## Sliding window versus prefix sum

Prefix sums and sliding windows both process contiguous ranges, but they solve different structural problems.

A prefix sum allows an arbitrary range sum to be computed quickly after preprocessing.

For an array:

`a[0], a[1], ..., a[n-1]`

define:

`prefix[i + 1] = prefix[i] + a[i]`

Then:

`sum(left, right) = prefix[right + 1] - prefix[left]`

This is particularly useful when there are many arbitrary range queries.

Sliding windows are often more appropriate when:

- the window moves incrementally
- the range is contiguous
- a validity condition determines expansion and contraction
- state can be updated efficiently when one element enters and another leaves

The Python and JavaScript implementations include prefix-sum examples for comparison.

---

## Generic variable-window framework

A useful way to design sliding-window solutions is to separate three responsibilities:

1. Add an incoming value.
2. Remove an outgoing value.
3. Determine whether the window is valid.

The Python implementation contains `longest_valid_window()`.

The JavaScript implementation contains `longestValidWindow()`.

This abstraction demonstrates that the same pointer structure can solve many different problems while the maintained state changes.

For example, validity might depend on:

`sum <= limit`

or:

`distinct_count <= k`

or:

`zero_count <= k`

or:

`max_value - min_value <= limit`

The algorithmic structure remains similar.

---

## Edge cases

Sliding-window implementations should explicitly consider boundary cases.

### Empty input

An empty sequence may be invalid for problems requiring at least one window.

The implementations validate this condition where appropriate.

### k equals 1

Every individual element forms its own window.

This is a useful test for pointer calculations.

### k equals n

Only one window exists.

The algorithm should return a result based on the entire sequence.

### k greater than n

No valid fixed-size window exists.

The implementations reject this input rather than silently producing an incorrect result.

### k equals zero

A zero-sized window is normally outside the definition of the problem.

The fixed-window implementations reject it.

### All negative values

Maximum-sum problems must not initialize their answer to zero.

The first valid window should normally initialize the result.

### Repeated values

Frequency-based algorithms must distinguish between:

- a value still present with a smaller count
- a value that has disappeared completely

### No valid variable window

Minimum-size algorithms commonly return `0` when no valid window exists.

### Very large values

Accumulation may require a wider integer type.

The C++ case study uses `long long`.

---

## Common mistakes

### Recomputing the entire window

This removes the main benefit of the technique.

For a fixed-size sum, update:

`new_sum = old_sum - outgoing + incoming`

instead of summing all `k` values again.

### Moving only one pointer

Variable-window algorithms generally need both expansion and contraction.

The right pointer discovers new possibilities.

The left pointer restores validity or searches for a smaller valid window.

### Forgetting to remove outgoing state

If an element leaves the window, its contribution must also leave the maintained state.

### Forgetting to delete zero-frequency keys

A frequency map's size represents the number of distinct values only if zero-frequency entries are removed.

### Using the wrong assumptions

A sum-based sliding window may require non-negative values.

A product-based version may require strictly positive values.

The implementation conditions must match the mathematical properties of the problem.

### Off-by-one errors

The inclusive window length is:

`right - left + 1`

The outgoing element for a fixed window of size `k` is commonly:

`values[right - k]`

### Returning the window length instead of the requested value

A problem may ask for:

- maximum sum
- minimum length
- maximum length
- number of valid windows
- actual window contents

The maintained answer must match the requested output.

---

## Python implementation

The Python script provides a broad collection of implementations.

### Fixed-size algorithms

The following functions demonstrate fixed-size windows:

- `max_sum_subarray_bruteforce()`
- `max_sum_subarray()`
- `fixed_window_sums()`
- `minimum_sum_subarray()`
- `maximum_average_subarray()`

The brute-force and optimized maximum-sum versions make the performance improvement explicit.

### Variable-size algorithms

The script includes:

- `minimum_size_subarray_sum()`
- `longest_subarray_sum_at_most()`
- `longest_subarray_at_most_k_distinct()`
- `longest_subarray_exactly_k_distinct()`

These demonstrate expansion and contraction.

### Frequency-based algorithms

The script includes:

- `longest_substring_without_repeating_characters()`
- `longest_substring_with_at_most_k_distinct()`
- `permutation_in_string()`
- `find_all_anagram_starts()`
- `count_distinct_in_every_window()`

### Advanced algorithms

The script includes:

- `sliding_window_maximum()`
- `sliding_window_minimum()`
- `longest_subarray_absolute_difference()`
- `longest_valid_window()`

The monotonic-deque implementations demonstrate an advanced form of window state management.

### Testing

The script contains deterministic assertions and randomized differential testing.

The randomized test compares the optimized maximum-sum implementation against a brute-force reference implementation.

This is useful for detecting pointer and boundary errors.

---

## JavaScript implementation

The JavaScript file mirrors the major algorithmic patterns while taking advantage of JavaScript-specific data structures.

### Map for frequencies

JavaScript's `Map` provides a convenient representation for frequency tables.

The helper functions:

- `incrementFrequency()`
- `decrementFrequency()`

centralize the common frequency-update behavior.

### String processing

JavaScript strings can be processed directly using indexed access such as `text[index]`.

The implementation demonstrates:

- non-repeating substring detection
- distinct-character windows
- anagram detection
- character replacement

### Custom deque

JavaScript arrays can implement queues, but repeatedly removing from the front using `shift()` can cause unnecessary work.

The `IndexDeque` class maintains a logical head position and supports:

- `pushBack()`
- `popBack()`
- `popFront()`
- `front()`
- `back()`
- `isEmpty()`

This makes the monotonic-deque example more explicit.

### Runtime behavior

The program is executable with Node.js and does not require external npm packages.

---

## C++ case study

The C++ program models a network-traffic monitoring system.

Each integer represents the number of packets observed during one sampling interval.

For example:

`[120, 130, 145, 300, 280, 290, 150, 140, 135]`

A monitoring policy may define:

- a window of three observations
- an alert threshold of `750` packets

The system evaluates each three-observation window.

If the total reaches or exceeds the threshold, the window is reported as an alert.

This is a practical fixed-size sliding-window application because the monitoring interval is explicitly defined.

---

## C++ system design

The case study uses a `TrafficAlert` structure containing:

- `startIndex`
- `endIndex`
- `totalPackets`
- `averagePackets`

The `TrafficMonitor` class stores:

- `windowSize`
- `alertThreshold`

Its `analyze()` method processes the traffic stream using a rolling sum.

This separates domain configuration from the algorithm.

The algorithmic state is maintained incrementally rather than recalculating every window.

---

## C++ validation

The case study validates:

- positive window size
- non-negative thresholds
- non-empty packet streams
- packet counts that are not negative
- window sizes that do not exceed the input length

The program also demonstrates explicit exception handling.

This is important in production-oriented implementations because invalid inputs should produce deterministic failure behavior rather than undefined assumptions.

---

## C++ data structures

The case study uses standard-library containers.

### `vector`

`vector<int>` stores sequential input data.

It provides efficient random access, which is important when calculating:

`values[right - k]`

for the outgoing element.

### `unordered_map`

The frequency-based examples use `unordered_map<int, int>`.

It provides average constant-time insertion, lookup, and deletion.

### `deque`

`std::deque<int>` is used for monotonic-window processing.

The deque stores indices rather than values.

---

## C++ memory considerations

The fixed-size sum algorithm uses constant auxiliary space:

`O(1)`

The frequency-based implementation requires storage proportional to the number of distinct values.

The monotonic deque requires storage proportional to the window size in the worst case:

`O(k)`

For a production system processing extremely large streams, memory limits should be considered when selecting the maintained state.

---

## Complexity analysis

| Technique | Time | Auxiliary space |
|---|---:|---:|
| Brute-force fixed window | `O(nk)` | `O(1)` |
| Fixed-size sliding sum | `O(n)` | `O(1)` |
| Minimum-size non-negative sum | `O(n)` | `O(1)` |
| Longest at-most-k distinct | `O(n)` average | `O(k)` |
| Non-repeating substring | `O(n)` average | `O(alphabet)` |
| Fixed-size distinct counts | `O(n)` average | `O(k)` |
| Anagram window | depends on frequency comparison | `O(alphabet)` |
| Sliding maximum with deque | `O(n)` | `O(k)` |
| Sliding minimum with deque | `O(n)` | `O(k)` |
| Max-min constrained window | `O(n)` | `O(k)` |

The exact practical complexity of frequency-map operations depends on the data structure and language implementation.

Hash-table operations are typically average `O(1)`, while ordered maps generally provide `O(log k)` operations.

---

## Performance considerations

The major performance benefit of sliding windows comes from avoiding repeated work.

For a fixed-size window:

`remove one + add one`

is cheaper than:

`recalculate k elements`

for every position.

For variable windows, the two-pointer approach is efficient when each pointer moves monotonically forward.

For monotonic deques, each index is inserted and removed a bounded number of times, producing amortized `O(n)` processing.

For frequency windows, the number of tracked keys should be controlled by the problem's constraints.

---

## Security and production considerations

Sliding-window algorithms themselves are not security mechanisms, but production systems using them must handle input safely.

Relevant considerations include:

- validate window sizes
- reject malformed input
- prevent integer overflow
- bound memory usage for untrusted streams
- validate assumptions such as non-negative values
- avoid unbounded frequency maps
- handle empty inputs explicitly
- handle unusually large sequences
- avoid silently converting invalid data into valid-looking results
- preserve numerical precision when the language's numeric representation requires it

In monitoring systems, threshold values should be configurable and validated.

A traffic monitor should also distinguish between a genuine sustained spike and an isolated measurement if the business requirement is based on a rolling interval.

---

## Implementation trade-offs

### Array versus deque

An array is sufficient for simple sums.

A deque is more appropriate when the algorithm needs to maintain candidates for a minimum or maximum.

### Frequency map versus set

A set only answers whether a value exists.

A frequency map also knows how many times the value appears.

Therefore a frequency map is necessary when contraction must distinguish between:

`value still present`

and:

`value completely removed`

### Hash map versus ordered map

A hash map usually provides average `O(1)` operations.

An ordered map provides sorted ordering but usually costs `O(log n)` per operation.

The required behavior should determine the data structure.

### Sliding window versus prefix sum

Sliding windows are well suited to moving contiguous ranges with an incremental validity condition.

Prefix sums are well suited to repeated arbitrary range-sum queries.

Neither technique universally replaces the other.

---

## Recognizing a sliding-window problem

A problem is a strong candidate for sliding-window techniques when it contains several of these characteristics:

- the data is sequential
- the answer concerns a contiguous subarray or substring
- a window moves from left to right
- the state can be updated when one item enters
- the state can be updated when one item leaves
- the problem asks for maximum or minimum window length
- the problem has a fixed window size
- the problem contains frequency constraints
- the problem contains a bounded resource
- the validity of a window can be expressed as an invariant

Typical wording includes:

- maximum sum of a subarray of size `k`
- longest substring without repeating characters
- longest subarray with at most `k` distinct values
- minimum length subarray whose sum reaches a target
- find all anagrams
- longest sequence after at most `k` replacements
- maximum in every window
- minimum in every window

---

## A systematic problem-solving method

For a new sliding-window problem, determine the following.

### Identify the window

Ask:

What contiguous region am I currently examining?

### Identify the state

Ask:

What information about the window must be maintained?

Examples:

- sum
- product
- frequency map
- distinct count
- zero count
- maximum
- minimum

### Identify validity

Ask:

When is the current window valid?

Examples:

`sum <= target`

`distinct_count <= k`

`zero_count <= k`

`max - min <= limit`

### Identify expansion

Ask:

What happens when the right pointer includes another element?

Update the state.

### Identify contraction

Ask:

What happens when the window becomes invalid?

Remove elements from the left until validity is restored.

### Identify the answer

Ask:

Should the algorithm update:

- a maximum length
- a minimum length
- a maximum sum
- a minimum sum
- a count
- a collection of starting indices
- the actual window

This final distinction prevents many implementation errors.

---

## Important distinction: fixed versus variable windows

| Property | Fixed-size window | Variable-size window |
|---|---|---|
| Length | Always `k` | Changes |
| Main pointer behavior | Move both boundaries together | Expand and contract independently |
| Typical state | Sum, count, extrema | Sum, frequency, resource count |
| Common objective | Best value for each window | Best valid window |
| Typical complexity | `O(n)` | `O(n)` when invariants apply |

A fixed window does not normally need a validity loop because its size is predetermined.

A variable window generally requires contraction logic.

---

## Important distinction: longest versus shortest

For a longest-valid-window problem:

- expand the right pointer
- contract only when invalid
- update the answer after restoring validity

For a minimum-size-valid-window problem:

- expand until valid
- contract aggressively while still valid
- update the minimum before each contraction

The pointer mechanics are similar, but the timing of the answer update is different.

---

## Important distinction: exact versus at-most constraints

A condition such as:

`at most k distinct values`

is often directly maintained by a frequency map.

An exact condition:

`exactly k distinct values`

can sometimes be handled by maintaining a window with no more than `k` distinct values and checking when the count equals `k`.

Another useful mathematical relationship is:

`exactly(k) = atMost(k) - atMost(k - 1)`

for counting problems.

For maximum-length problems, directly maintaining the exact condition can be simpler.

---

## Testing strategy

A sliding-window implementation should be tested against:

- an empty sequence
- one-element input
- `k = 1`
- `k = n`
- `k > n`
- repeated values
- all equal values
- all negative values where supported
- zeros
- duplicate characters
- no valid window
- every possible window valid
- very large values
- minimal valid target
- target larger than the total possible value

For algorithmic correctness, a brute-force implementation is valuable as a reference for small random inputs.

The Python program demonstrates this through randomized differential testing.

---

## Practical applications

Sliding-window processing appears in many real systems.

### Network monitoring

A rolling packet-count window can identify sustained traffic spikes.

### Log analysis

A system can examine the number of errors occurring during each rolling time interval.

### Time-series processing

Rolling statistics can be calculated over fixed observation periods.

### Text processing

Substring and frequency-window algorithms support pattern detection and duplicate detection.

### Fraud and anomaly detection

A system can enforce rules such as:

`at most k suspicious events within a rolling interval`

### Resource monitoring

A rolling CPU, memory, request, or transaction window can support threshold-based alerts.

### Rate limiting

A rolling window can track requests during a bounded period.

Production rate-limit systems may use more specialized structures, distributed counters, or token-bucket techniques, but the conceptual window model remains important.

---

## Limitations

Sliding windows are not universally applicable.

The technique becomes difficult or incorrect when:

- the data is not contiguous
- the validity condition is not incrementally maintainable
- pointer movement is not monotonic
- negative values destroy required monotonic properties
- the required state cannot be updated efficiently
- the problem asks for arbitrary non-contiguous combinations
- the window depends on future information in a way that prevents incremental processing

The correct algorithm should be selected based on the mathematical structure of the problem rather than the appearance of the input.

---

## Python, JavaScript, and C++ comparison

### Python

Python is particularly concise for demonstrating algorithmic ideas.

Dictionaries, `Counter`, `defaultdict`, `deque`, and lists make frequency and pointer-based algorithms easy to express.

The Python implementation emphasizes:

- readability
- direct experimentation
- reference implementations
- randomized testing
- broad algorithm coverage

### JavaScript

JavaScript demonstrates the same concepts in an application-oriented environment.

`Map` provides frequency tracking.

The custom `IndexDeque` demonstrates how a monotonic queue can be implemented explicitly.

The implementation also illustrates how sliding-window techniques apply naturally to string processing and application-level data handling.

### C++

C++ is useful when the implementation needs explicit data structures, strong control over numeric types, and predictable performance characteristics.

The case study uses:

- `vector`
- `unordered_map`
- `deque`
- classes
- structures
- exceptions
- `long long`

The C++ program emphasizes system-style design through the `TrafficMonitor` class.

---

## Files represented by this study

The study contains three implementations:

- Python: comprehensive algorithmic tutorial and testing program
- JavaScript: executable sliding-window implementation with `Map` and a custom deque
- C++: industry-style network traffic monitoring case study

The implementations are intentionally related but not identical. Each language demonstrates the same algorithmic principles through structures that are natural for that language.

---

## Core invariants to remember

A successful sliding-window solution usually has a clearly stated invariant.

Examples include:

`window length == k`

`window sum >= target`

`distinct_count <= k`

`zero_count <= k`

`max(window) - min(window) <= limit`

`no character appears more than once`

The invariant is the foundation of the algorithm.

When the invariant is broken, contraction restores it.

When the invariant holds, the algorithm can safely evaluate the current window according to the problem's objective.

---

## Final reference table

| Pattern | State | Expansion | Contraction |
|---|---|---|---|
| Fixed sum | Running sum | Add incoming | Remove outgoing |
| Minimum sum window | Running sum | Add incoming | Remove outgoing |
| Minimum target sum | Running sum | Until target reached | While still valid |
| At-most-k distinct | Frequency map | Add frequency | Remove frequency |
| No repeated characters | Last-seen positions | Add character | Jump or move left |
| Anagram search | Frequency map | Add character | Remove outgoing character |
| At-most-k zeros | Zero count | Count zero | Remove zero |
| Character replacement | Frequency map + max frequency | Add character | Remove until valid |
| Sliding maximum | Decreasing deque | Add index | Remove expired/smaller candidates |
| Sliding minimum | Increasing deque | Add index | Remove expired/larger candidates |
| Max-min constraint | Two monotonic deques | Update both | Contract until valid |

The essential technique is consistent across these patterns: maintain the current contiguous window incrementally, preserve a clearly defined invariant, and move the boundaries only as required by that invariant.
