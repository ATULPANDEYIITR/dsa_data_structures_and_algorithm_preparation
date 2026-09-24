# Day 22 — Palindromes

## Topic introduction

A palindrome is a sequence that reads the same from left to right and from right to left.

Examples include:

- `racecar`
- `level`
- `abba`
- `1221`

Non-palindromes include:

- `hello`
- `python`
- `12345`

Palindrome problems are useful because they combine string processing, indexing, two-pointer techniques, arithmetic reasoning, dynamic programming, recursion, center expansion, and linear-time algorithms.

This study covers four closely related problems:

1. Character-based palindrome checking
2. Two-pointer palindrome checking
3. Number palindrome checking
4. Palindromic substring analysis

The implementations then extend those foundations to:

- valid palindromes
- removing at most one character
- longest palindromic substring
- distinct palindromic substrings
- palindrome permutations
- longest palindromic subsequences
- palindrome partitioning
- Manacher's algorithm
- testing
- defensive input handling
- performance comparison

---

## Fundamental concept

For a sequence `S` of length `n`, a palindrome satisfies:

`S[i] == S[n - 1 - i]`

for every index `i` in the first half of the sequence.

Only the first half needs to be compared because the second half is determined by those mirrored comparisons.

For example:

`racecar`

has the following pairs:

- `r` with `r`
- `a` with `a`
- `c` with `c`

The middle character does not need a matching partner.

For an even-length palindrome such as `abba`:

- `a` matches `a`
- `b` matches `b`

The center lies between the two middle characters.

---

## Core terminology

### Character

A character is an individual symbol in a sequence.

Examples include:

- `a`
- `Z`
- `7`
- `?`

The exact representation of a character depends on the programming language and encoding model.

### String

A string is an ordered sequence of characters.

Examples:

`"racecar"`

`"hello"`

### Palindrome

A sequence whose forward and reverse representations are equal under the chosen comparison rules.

### Substring

A substring is a contiguous portion of a string.

For `abcde`, examples include:

- `a`
- `bc`
- `cde`
- `abcde`

`ace` is not a substring because its characters are not contiguous.

### Subsequence

A subsequence preserves character order but does not require characters to be contiguous.

For `abcde`, `ace` is a subsequence.

This distinction is important because longest palindromic substring and longest palindromic subsequence are different problems.

### Two pointers

Two pointers are variables that represent positions in a sequence.

For palindrome checking, one pointer starts at the beginning and another starts at the end.

They move toward the center.

### Center expansion

A palindrome can be identified by selecting a possible center and expanding outward while both sides contain equal characters.

There are two types of centers:

- a character, producing odd-length palindromes
- a gap between two characters, producing even-length palindromes

### Dynamic programming

Dynamic programming stores solutions to smaller subproblems so they do not have to be recomputed.

For palindrome substrings, a typical state is:

`dp[left][right]`

meaning that the substring from `left` through `right` is a palindrome.

### Manacher's algorithm

Manacher's algorithm finds the longest palindromic substring in linear time.

Its complexity is:

`O(n)`

This is substantially better asymptotically than the usual `O(n^2)` center-expansion approach.

---

## Character-based palindrome

The simplest implementation compares a string with its reverse.

The Python implementation provides `is_character_palindrome`.

Conceptually:

`text == reverse(text)`

This is easy to understand, but constructing the reversed string requires additional memory.

The explicit loop implementation demonstrates the underlying comparisons without relying on a built-in reversal operation.

For a string of length `n`:

- Time: `O(n)`
- Auxiliary space for explicit two-pointer checking: `O(1)`
- Space for creating a reversed copy: `O(n)`

---

## Two-pointer palindrome

The two-pointer technique is one of the most important patterns in palindrome problems.

The algorithm starts with:

`left = 0`

and:

`right = n - 1`

It repeatedly performs:

1. Compare `text[left]` and `text[right]`.
2. Return `False` if they differ.
3. Increment `left`.
4. Decrement `right`.
5. Stop when the pointers meet or cross.

The Python, JavaScript, and C++ implementations all contain this technique.

### Why two pointers are useful

The algorithm does not need to inspect every character independently.

Each comparison simultaneously checks two mirrored positions.

For a string of length `n`, approximately `n / 2` comparisons are sufficient.

### Complexity

Time:

`O(n)`

Auxiliary space:

`O(1)`

The returned Boolean value does not depend on allocating another sequence.

---

## Valid palindrome

A common variation ignores:

- spaces
- punctuation
- capitalization

For example:

`A man, a plan, a canal: Panama`

is considered valid because the normalized sequence is equivalent to:

`amanaplanacanalpanama`

The Python implementation `is_valid_palindrome` performs the normalization logically while using two pointers.

The JavaScript implementation filters Unicode letters and numbers before comparison.

The C++ implementation demonstrates an ASCII-oriented approach using `std::isalnum` and `std::tolower`.

### Important implementation distinction

Unicode text requires care.

A visible character is not always equivalent to one byte or one UTF-16 code unit.

JavaScript strings use UTF-16 code units, while Python strings expose Unicode code points at the language level. C++ standard-library character functions such as `std::isalnum` are not a complete Unicode text-processing solution.

For production Unicode applications, normalization and case-folding requirements should be explicitly defined.

---

## Number palindrome

A number such as:

`121`

is a palindrome.

A number such as:

`123`

is not.

A negative value such as:

`-121`

is normally considered non-palindromic because the minus sign does not appear at the end.

### String approach

The simplest approach is:

1. Convert the number to a string.
2. Reverse it.
3. Compare.

This is straightforward and easy to verify.

### Mathematical approach

The mathematical implementation avoids string conversion.

For `121`:

1. Extract the final digit.
2. Add it to a reversed accumulator.
3. Remove the final digit from the original number.
4. Continue until approximately half the number has been processed.
5. Compare the remaining half with the reversed half.

Only half of the digits need to be reversed.

The Python and JavaScript implementations demonstrate this technique.

### Trailing zero rule

A positive number ending in zero cannot normally be a palindrome.

For example:

`10`

would require:

`01`

on the other side.

The exception is zero itself.

---

## Basic palindrome problem

The fundamental palindrome problem asks:

> Does the complete sequence read identically in both directions?

The implementations provide multiple versions because comparing different implementations is useful for learning.

The Python tests include:

- empty strings
- single characters
- ordinary palindromes
- ordinary non-palindromes
- numeric examples

The JavaScript and C++ programs provide equivalent tests.

---

## Remove-one-character palindrome

A common interview problem asks whether a string can become a palindrome after deleting at most one character.

Example:

`abca`

The first mismatch is:

`b` versus `c`

There are only two relevant choices:

- remove `b`
- remove `c`

The resulting candidates are:

`aca`

and:

`aba`

Both are palindromes.

Therefore the answer is true.

### Important observation

There is no need to try deleting every character.

Once the first mismatch is found, any valid solution must resolve that mismatch by removing one of its two characters.

This produces:

`O(n)`

time and:

`O(1)`

extra space.

The Python, JavaScript, and C++ implementations all use this strategy.

---

## Substring palindrome

A substring is identified by boundaries.

The Python implementation uses:

`start`

and:

`end`

where `end` is exclusive.

For example:

`text[start:end]`

follows normal Python slicing conventions.

The C++ implementation similarly accepts a half-open interval:

`[start, endExclusive)`

Half-open intervals are useful because:

- the length is `end - start`
- an empty interval is represented naturally
- adjacent ranges do not overlap
- they match many standard-library conventions

---

## Enumerating palindromic substrings

A string of length `n` has:

`n(n + 1) / 2`

possible non-empty substrings.

Therefore the number of candidate substrings is already:

`O(n^2)`

before checking whether each one is a palindrome.

A straightforward implementation can therefore become:

`O(n^3)`

when substring construction and palindrome testing are both counted.

The Python implementation `brute_force_palindromic_substrings` demonstrates this direct approach.

It is useful educationally, but it is generally not the preferred approach for large inputs.

---

## Center expansion

Center expansion improves longest-palindromic-substring processing.

Every palindrome has a center.

For odd-length palindromes:

`racecar`

the center is the character `e`.

For even-length palindromes:

`abba`

the center lies between the two `b` characters.

For every position, the algorithm checks:

1. `(center, center)`
2. `(center, center + 1)`

It then expands outward while the characters match.

### Complexity

There are `O(n)` possible centers.

Each expansion can take `O(n)` time.

Therefore:

`O(n^2)`

time in the worst case.

The algorithm uses:

`O(1)`

auxiliary space apart from the returned substring.

This is often an excellent practical trade-off because it is simple and memory-efficient.

---

## Dynamic programming for longest palindromic substring

The dynamic-programming implementation uses the state:

`dp[left][right]`

The value is true when the substring from `left` to `right` is a palindrome.

The recurrence is:

`text[left] == text[right]`

and either:

`length <= 2`

or:

`dp[left + 1][right - 1]`

must already be true.

### Base cases

Every single character is a palindrome.

Therefore:

`dp[i][i] = true`

A two-character substring is a palindrome when its two characters are equal.

### Complexity

Time:

`O(n^2)`

Space:

`O(n^2)`

The extra memory makes DP less memory-efficient than center expansion, but the table is useful when related subproblem information is needed later.

---

## Manacher's algorithm

Manacher's algorithm finds the longest palindromic substring in linear time.

The main difficulty is handling odd- and even-length palindromes with a single representation.

The algorithm transforms the input.

For example:

`abba`

becomes conceptually similar to:

`^#a#b#b#a#$`

The separators allow every palindrome to have a center at a transformed position.

The algorithm maintains:

- a current center
- the rightmost boundary reached by a known palindrome
- an array containing palindrome radii

A previously computed mirrored radius can be reused when processing a new position.

This reuse is the key reason the algorithm achieves linear complexity.

### Complexity

Time:

`O(n)`

Space:

`O(n)`

### Practical trade-off

Manacher's algorithm has the best asymptotic runtime among the implementations in this study, but it is substantially more complex than center expansion.

For many ordinary applications, center expansion is easier to maintain.

Manacher's algorithm becomes especially relevant when the input is large and strict linear-time behavior is required.

---

## All palindromic substrings

The center-expansion implementation can be extended to collect every palindromic substring.

For each center it expands outward and records every successful interval.

For example, `aaa` contains palindromic occurrences:

- `a`
- `a`
- `a`
- `aa`
- `aa`
- `aaa`

The repeated `a` values are distinct occurrences even though the substring values are identical.

---

## Distinct palindromic substrings

A set can remove duplicate values.

For `aaa`, the distinct palindrome values are:

- `a`
- `aa`
- `aaa`

The C++ implementation uses `std::unordered_set<std::string>`.

The Python implementation uses `set`.

The JavaScript implementation uses `Set`.

### Memory consideration

Collecting all distinct substrings can consume substantial memory.

The number of distinct palindromic substrings can grow linearly with the input length, but each stored string may itself require memory proportional to its length.

Therefore production systems should avoid collecting all values unless the output is actually required.

---

## Palindrome permutation

A different palindrome property concerns rearrangement.

The question is:

> Can the characters be rearranged into some palindrome?

For example:

`carrace`

can be rearranged into:

`racecar`

The condition is based on character frequencies.

For an even-length palindrome, every character frequency must be even.

For an odd-length palindrome, exactly one character may have an odd frequency.

Therefore:

`number of odd-frequency characters <= 1`

is sufficient.

This problem is different from checking whether the current string is already a palindrome.

---

## Longest palindromic subsequence

A substring must be contiguous.

A subsequence does not.

For:

`bbbab`

a longest palindromic subsequence has length `4`.

The important distinction is that the selected characters do not need to occupy one continuous interval.

The recurrence is:

If:

`text[left] == text[right]`

then:

`dp[left][right] = dp[left + 1][right - 1] + 2`

Otherwise:

`dp[left][right] = max(dp[left + 1][right], dp[left][right - 1])`

### Complexity

Time:

`O(n^2)`

Space:

`O(n^2)`

This problem demonstrates why the words "substring" and "subsequence" must not be treated as interchangeable.

---

## Palindrome partitioning

Palindrome partitioning asks for partitions in which every component is itself a palindrome.

For:

`aab`

valid partitions include:

`a | a | b`

and:

`aa | b`

This is naturally represented as a backtracking problem.

At every position, the algorithm tries every possible next substring.

If the selected substring is a palindrome, it is added to the current partition and the search continues.

When the end of the string is reached, the current partition is stored.

### Complexity

The output itself can be exponential in size.

Therefore an algorithm producing every valid partition cannot generally be expected to run in polynomial time with respect to only the input length.

The Python and JavaScript implementations deliberately demonstrate the complete backtracking process.

---

## Python implementation

The Python script is organized from simple palindrome checks toward advanced algorithms.

### Basic functions

`is_character_palindrome` demonstrates direct reversal.

`is_character_palindrome_loop` demonstrates explicit mirrored comparison.

`is_two_pointer_palindrome` demonstrates the classic two-pointer technique.

### Input normalization

`normalize_for_palindrome` creates a normalized representation.

`is_valid_palindrome` avoids creating a complete normalized copy and instead skips irrelevant characters during the two-pointer scan.

This illustrates a common engineering trade-off:

- explicit normalization is simple
- streaming-style pointer logic can reduce temporary memory

### Number processing

`is_number_palindrome_string` uses conversion.

`is_number_palindrome_math` uses arithmetic.

The second implementation is useful for understanding how digit extraction works.

### Advanced string algorithms

The Python script includes:

- brute-force substring enumeration
- center expansion
- dynamic programming
- Manacher's algorithm
- palindrome partitioning
- longest palindromic subsequence
- distinct palindrome extraction

### Testing

The script includes deterministic tests and randomized cross-checking.

Randomized cross-checking compares the lengths produced by three independent longest-palindrome algorithms.

This is valuable because independent implementations can reveal errors that ordinary fixed examples may not expose.

---

## JavaScript implementation

The JavaScript file focuses on executable application-oriented behavior.

### String processing

JavaScript's string representation makes Unicode handling an important consideration.

The examples use spread syntax such as:

`[...text]`

when operating at the code-point level for several demonstrations.

### Validation

The JavaScript valid-palindrome implementation uses Unicode-aware regular-expression properties for letters and numbers.

This demonstrates a feature that is particularly useful for JavaScript text-processing code.

### Safe integer handling

JavaScript's ordinary `Number` type cannot exactly represent every possible integer.

The mathematical number-palindrome implementation therefore validates values with:

`Number.isSafeInteger`

This prevents silently applying exact integer arithmetic to values outside JavaScript's safe-integer range.

### Asynchronous processing

`analyzePalindromesAsync` demonstrates how palindrome analysis can be placed behind a Promise-based interface.

The current implementation is local and does not need asynchronous work, but the structure resembles application code where inputs may arrive from:

- network requests
- databases
- files
- worker threads
- asynchronous user interactions

The implementation does not require an external package.

---

## C++ case study

The C++ implementation models a small text-analysis service.

The service receives text and produces a `PalindromeReport`.

The report contains:

- the original input
- exact palindrome status
- valid-palindrome status
- remove-one-character status
- longest palindromic substring
- distinct palindromic substring count when the input is small enough

### Domain model

`PalindromeReport` represents the output of the analysis service.

This keeps analysis results together instead of returning unrelated values from several independent calls.

### Input validation

`InputValidator` enforces a maximum input length.

This is important because some palindrome algorithms require quadratic memory or can produce very large outputs.

An unrestricted user-controlled input can therefore cause unnecessary resource consumption.

### Algorithm layer

`PalindromeAlgorithms` contains the actual algorithms.

This separation means the service layer does not need to know how each palindrome operation is implemented.

### Service layer

`PalindromeAnalysisService` orchestrates the algorithms.

It:

1. validates the input
2. computes the exact palindrome result
3. computes the normalized valid-palindrome result
4. checks the remove-one-character condition
5. finds the longest palindromic substring
6. conditionally calculates distinct palindromic substrings

The service intentionally skips distinct-substring collection for large inputs because producing and storing all values is substantially more expensive than a single Boolean palindrome test.

### Reporting layer

`printReport` converts the domain result into readable output.

This separation between analysis and presentation is useful in larger applications because the same service could later return:

- JSON
- database records
- API responses
- command-line output
- GUI data

without rewriting the algorithms.

---

## C++ algorithmic implementation decisions

### `std::string_view`

Several functions accept `std::string_view`.

This allows read-only access without requiring another string allocation when the caller already has an existing string.

It is particularly appropriate for algorithms that only inspect the input.

### Half-open ranges

The substring function uses:

`[start, endExclusive)`

This provides a natural length calculation:

`endExclusive - start`

It also avoids ambiguity around empty substrings.

### `std::isalnum`

The C++ valid-palindrome example uses:

`std::isalnum`

with explicit conversion to `unsigned char`.

That conversion is important because the C character-classification functions have undefined behavior for negative `char` values other than EOF.

The example is intentionally ASCII-oriented. Full Unicode processing requires a different design.

### Exception handling

The service throws exceptions for invalid input conditions.

`main` catches `std::exception` and reports the error before returning a non-zero status.

This demonstrates a basic boundary between normal program operation and failure handling.

---

## Complexity comparison

| Technique | Time | Extra space | Main use |
|---|---:|---:|---|
| Reverse comparison | O(n) | O(n) | Simple palindrome check |
| Two pointers | O(n) | O(1) | Efficient palindrome check |
| Remove one character | O(n) | O(1) | One-deletion palindrome |
| Center expansion | O(n²) | O(1) | Longest palindromic substring |
| Dynamic programming | O(n²) | O(n²) | Palindrome state reuse |
| Manacher | O(n) | O(n) | Linear-time longest substring |
| LPS dynamic programming | O(n²) | O(n²) | Longest palindromic subsequence |
| Partitioning | Potentially exponential | Output-dependent | All palindrome partitions |

The complexity of an algorithm must be considered together with its implementation complexity and output requirements.

---

## Important distinctions

### Palindrome versus valid palindrome

A strict palindrome compares the original sequence.

A valid palindrome may apply normalization rules first.

For example:

`A man, a plan, a canal: Panama`

is not an exact palindrome because spaces, commas, and capitalization differ.

After normalization it becomes a palindrome under the chosen rules.

### Substring versus subsequence

Substring:

- contiguous
- cannot skip characters

Subsequence:

- preserves order
- may skip characters

This distinction changes both the problem definition and the algorithm.

### Longest palindrome versus all palindromes

Finding one longest palindrome requires only one result.

Finding all palindromic substrings requires potentially large output.

The latter can therefore require considerably more memory.

### Current ordering versus rearrangement

`carrace` is not itself a palindrome.

It can nevertheless be rearranged into one.

These are separate properties.

---

## Edge cases

The implementations explicitly consider several edge conditions.

### Empty string

An empty string is normally considered a palindrome because there is no mismatching pair.

### Single character

Every single-character string is a palindrome.

### Two characters

For a two-character string, both characters must be equal for it to be a palindrome.

### Negative integers

Negative integers are treated as non-palindromic in the number examples because of the minus sign.

### Trailing zero

A positive number ending in zero is not a palindrome.

### Punctuation-only input

When punctuation is ignored, a string containing no alphanumeric characters can normalize to an empty sequence.

The valid-palindrome implementation therefore treats it consistently with the empty sequence.

### Very large input

Quadratic algorithms can become impractical for large input.

Production services should impose limits and select algorithms according to the workload.

---

## Common mistakes

### Comparing only the first and last characters

Checking one pair is insufficient.

All mirrored pairs must be considered until the center is reached.

### Reversing unnecessarily

Creating a reversed copy is easy but uses additional memory.

A two-pointer implementation can perform the same logical test with constant auxiliary space.

### Treating substring as subsequence

A substring must be contiguous.

This is one of the most common conceptual errors in string problems.

### Checking every possible deletion

For the remove-one-character problem, trying every deletion creates unnecessary work.

Only the two characters involved in the first mismatch need to be considered.

### Ignoring even-length centers

A center-expansion implementation that checks only `(center, center)` finds odd-length palindromes but can miss values such as:

`abba`

The `(center, center + 1)` case is essential.

### Ignoring number representation limits

JavaScript's `Number` type has a safe integer range.

Exact integer algorithms should account for this constraint.

### Assuming bytes equal characters

Unicode text can contain multi-byte encodings and characters represented by multiple code units.

Production text-processing systems need explicit encoding and normalization requirements.

---

## Performance considerations

For a simple palindrome test, the two-pointer approach is normally sufficient.

It provides:

`O(n)`

time and:

`O(1)`

auxiliary space.

For longest palindromic substring:

### Center expansion

Use when:

- implementation simplicity matters
- input sizes are moderate
- constant auxiliary space is useful

### Dynamic programming

Use when:

- palindrome state information is needed elsewhere
- a table of palindrome relationships is useful
- quadratic memory is acceptable

### Manacher's algorithm

Use when:

- input can be large
- strict linear-time behavior is important
- algorithmic complexity justifies the additional implementation complexity

The best asymptotic complexity is not automatically the best engineering choice for every workload.

---

## Security and defensive programming

Palindrome algorithms are not normally security-sensitive by themselves, but their resource behavior matters when inputs are externally controlled.

### Input limits

A service should avoid accepting unlimited input when an algorithm requires:

`O(n²)`

memory.

The C++ service therefore establishes a maximum input length.

### Output explosion

Operations that return every palindrome or every partition can produce large outputs.

The number of generated objects should therefore be bounded where appropriate.

### Denial-of-service considerations

An attacker-controlled input can be deliberately selected to maximize processing time or memory consumption.

Potential controls include:

- maximum input size
- algorithm selection based on input size
- output limits
- request timeouts
- workload quotas
- streaming or incremental processing

### Unicode considerations

Normalization, case folding, and character classification should be specified explicitly.

A production system should not assume that ASCII operations correctly model all human-language text.

---

## Implementation considerations

A useful design principle is to separate the following responsibilities:

1. Input validation
2. Algorithm execution
3. Domain modeling
4. Result formatting
5. Error handling
6. Testing

The C++ case study demonstrates this separation explicitly.

The Python implementation focuses more heavily on algorithmic experimentation and cross-checking.

The JavaScript implementation adds application-style behavior and asynchronous interfaces.

---

## Testing strategy

Palindrome algorithms benefit from several categories of tests.

### Deterministic examples

Use known inputs such as:

- `racecar`
- `hello`
- `abba`
- `cbbd`
- `abca`
- `abc`

### Boundary tests

Use:

- empty input
- one-character input
- two-character input
- very short non-palindromes
- numbers such as `0`, `10`, `11`, and `121`

### Cross-implementation tests

The Python program compares:

- center expansion
- dynamic programming
- Manacher's algorithm

The JavaScript program similarly tests multiple implementations.

The C++ program validates the major algorithms with explicit assertions.

Independent implementations are useful because an algorithm can agree with itself while still containing a systematic error.

---

## Real-world applications

Palindrome techniques are useful beyond interview exercises.

### Text processing

Palindrome checks can be used as a component of string-analysis systems.

### Data validation

Some identifiers and structured values have symmetry constraints.

### Search systems

Longest-substring algorithms can identify symmetric regions within text.

### Bioinformatics

DNA and RNA sequence analysis can involve symmetry and reverse-complement patterns. Biological sequence analysis requires domain-specific definitions beyond ordinary character palindromes.

### Pattern analysis

Palindrome detection provides a compact example of algorithms that compare mirrored regions.

### Algorithm education

Palindrome problems demonstrate several foundational algorithmic ideas:

- two pointers
- string indexing
- normalization
- recursion
- backtracking
- dynamic programming
- center expansion
- linear-time preprocessing

---

## Python, JavaScript, and C++ comparison

### Python

Python is particularly concise for experimenting with algorithms.

The implementation demonstrates:

- slicing
- sets
- dictionaries through `Counter`
- nested functions
- dataclasses
- type annotations
- randomized testing
- algorithm comparison

It is suitable for quickly validating algorithmic ideas.

### JavaScript

JavaScript demonstrates:

- string processing
- Unicode-aware regular expressions
- `Map`
- `Set`
- Promises
- asynchronous application structure
- safe-integer validation

It is useful when palindrome logic is part of browser or JavaScript application code.

### C++

C++ demonstrates:

- explicit memory considerations
- `std::string_view`
- standard containers
- class-based architecture
- exceptions
- input validation
- performance measurement
- low-level character classification
- algorithmic trade-offs

It is useful when the algorithm is part of a performance-sensitive native application.

---

## Production-oriented design

A production palindrome service should not expose every algorithm to every input size without considering resource cost.

A practical policy can be:

- Use two pointers for direct palindrome validation.
- Use the remove-one-character algorithm for one-deletion validation.
- Use center expansion for moderate longest-substring workloads.
- Use Manacher's algorithm when strict linear-time behavior is required.
- Avoid collecting all palindromic substrings unless the caller explicitly needs them.
- Apply input-size limits before quadratic operations.
- Define Unicode normalization rules explicitly.
- Separate algorithmic code from API and presentation layers.
- Test edge cases and large inputs.
- Measure real workloads before optimizing.

The C++ case study models these concerns through a validation layer, algorithm layer, service layer, and reporting layer.
