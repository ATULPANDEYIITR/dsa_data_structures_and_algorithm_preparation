# Day 21 — Character Frequency

## Topic introduction

Character frequency is the process of counting how many times each character occurs in a string. It is one of the most useful introductory applications of hash tables, dictionaries, maps, arrays, and counting techniques.

Given the string `banana`, the frequency distribution is:

- `b` → 1
- `a` → 3
- `n` → 2

The basic operation is simple:

1. Read one character.
2. Locate its current count.
3. Increment that count.
4. Continue until the input is exhausted.

This pattern appears in anagram detection, duplicate detection, text analysis, data validation, compression-related algorithms, search problems, cryptographic preprocessing, log analysis, and many interview-style data-structure problems.

The three implementations approach the same subject from different perspectives:

- Python emphasizes dictionaries, `Counter`, arrays, validation, testing, and progressively advanced algorithms.
- JavaScript emphasizes `Map`, objects, arrays, Unicode iteration, application-level processing, and executable data transformations.
- C++ develops an industry-style text analytics engine using classes, `unordered_map`, fixed arrays, algorithms, validation, exception handling, and deterministic reporting.

---

## Fundamental concepts

### Character

A character is an individual element of textual data.

For example, the string `hello` contains:

`h`, `e`, `l`, `l`, `o`

The character `l` occurs twice.

A character can be:

- a letter
- a digit
- whitespace
- punctuation
- a symbol
- a Unicode code point

The exact definition of a character depends on the programming language and the problem requirements.

### Frequency

Frequency is the number of occurrences of an item.

For `banana`:

`a` has frequency `3`.

A frequency table therefore maps an item to the number of times it occurs.

### Distinct character

A distinct character is a character that appears at least once, regardless of how many times it occurs.

`banana` has three distinct characters:

`b`, `a`, and `n`.

### Duplicate character

A duplicate character appears more than once.

In `banana`:

- `a` appears 3 times
- `n` appears 2 times

Therefore both are duplicates.

### Unique character

A unique character appears exactly once.

In `banana`, `b` is unique.

### Frequency distribution

A frequency distribution records the count associated with every distinct character.

Two strings may have different ordering but identical frequency distributions.

For example:

`aabbcc`

and

`ccbbaa`

have the same distribution.

---

## The fundamental counting algorithm

The general algorithm is:

1. Create an empty frequency structure.
2. Iterate through the string.
3. For each character, retrieve its current count.
4. Increment the count.
5. Return the frequency structure.

For `banana`:

| Character | Count |
|---|---:|
| `b` | 1 |
| `a` | 3 |
| `n` | 2 |

If the input contains `n` characters and there are `k` distinct characters, dictionary-based counting normally requires:

- Time: `O(n)`
- Space: `O(k)`

The algorithm is linear because every input character is processed once.

---

## Frequency arrays

A frequency array is appropriate when the possible character set is known and small.

For lowercase English letters there are exactly 26 possible values.

The mapping is:

| Character | Index |
|---|---:|
| `a` | 0 |
| `b` | 1 |
| `c` | 2 |
| ... | ... |
| `z` | 25 |

The mathematical mapping is:

`index = ord(character) - ord('a')`

The Python implementation uses `lowercase_frequency_array()`. The JavaScript implementation uses `lowercaseFrequencyArray()`. The C++ implementation uses `lowercaseLetterArray()`.

A frequency array has predictable memory usage:

`O(A)`

where `A` is the alphabet size.

For the lowercase English alphabet, `A = 26`.

### Advantages

- Very fast indexing
- Small fixed memory footprint
- No hash-table overhead
- Predictable behavior
- Simple implementation

### Limitations

A fixed array becomes inconvenient when:

- the alphabet is large
- arbitrary Unicode characters are allowed
- the character domain is unknown
- the input is sparse across a large domain

For these cases, a dictionary or map is usually more appropriate.

---

## Dictionaries, maps, and hash tables

A dictionary associates keys with values.

Conceptually:

`character → frequency`

Python provides several suitable structures:

- `dict`
- `collections.defaultdict`
- `collections.Counter`

JavaScript provides:

- objects
- `Map`

C++ provides:

- `std::unordered_map`
- `std::map`

The implementations primarily use hash-based structures because character frequencies usually require efficient lookup.

### Hash-table complexity

Expected lookup and insertion are generally:

`O(1)`

Therefore character counting is normally:

`O(n)`

expected time.

Strict worst-case hash-table behavior can be worse than `O(1)`, depending on the implementation and collision behavior.

---

## Python implementation

The Python file begins with a basic dictionary implementation:

`count_characters_basic(text)`

The central operation is equivalent to:

`frequency[character] = frequency.get(character, 0) + 1`

This avoids a separate existence test.

### `defaultdict`

`count_characters_defaultdict()` uses `defaultdict(int)`.

An unseen character automatically receives the default integer value `0`.

The operation becomes:

`frequency[character] += 1`

### `Counter`

Python's `Counter` is specifically designed for frequency counting.

The implementation demonstrates:

`Counter(text)`

This is concise and useful when the frequency problem is the central operation.

The educational script still implements manual counting because understanding the underlying algorithm is more important than hiding it behind a library abstraction.

---

## JavaScript implementation

The JavaScript version demonstrates both objects and `Map`.

### Object-based counting

`countCharactersObject()` creates an object without a prototype using:

`Object.create(null)`

This is useful for frequency tables because arbitrary string keys are being treated as data rather than object properties.

### `Map`

`countCharactersMap()` uses:

`Map`

The important operations are:

- `get()`
- `set()`
- `has()`

A `Map` makes the key-value relationship explicit and avoids many object-property concerns.

### Frequency arrays

`lowercaseFrequencyArray()` demonstrates the same fixed-alphabet strategy as Python and C++.

JavaScript obtains the alphabet position using:

`character.charCodeAt(0) - 97`

because lowercase ASCII `a` begins at code point 97.

---

## C++ case study

The C++ implementation develops a text analytics engine instead of presenting only isolated frequency examples.

The central class is:

`TextAnalyticsEngine`

It provides operations for:

- input validation
- character counting
- fixed-array letter counting
- frequency sorting
- most frequent character detection
- duplicate detection
- first non-repeating character detection
- frequency comparison
- anagram detection
- character grouping
- longest unique substring detection
- minimum-window search
- frequency signatures
- anagram grouping
- document analysis

This design separates the analytical logic from the reporting logic.

---

## C++ problem being modeled

The case study represents a basic document-processing service.

Several documents are processed:

- `DOC-001`
- `DOC-002`
- `DOC-003`

For each document, the system calculates:

- document length
- number of distinct characters
- most frequent character
- first non-repeating character
- duplicate characters
- complete frequency information

The design resembles a small text-analysis component that could form part of a larger processing pipeline.

---

## C++ data structures

### `unordered_map`

The primary frequency structure is:

`unordered_map<char, int>`

It provides expected constant-time lookup and insertion.

### `array<int, 26>`

The fixed English-letter frequency operation uses:

`array<int, 26>`

This is appropriate because the domain is known exactly.

### `vector<CharacterStat>`

A vector is used when frequency results need to be sorted or returned as an ordered collection.

### `optional`

`optional` represents values that may not exist.

For example, an empty string has no most frequent character and no first non-repeating character.

---

## Most frequent character

The most frequent-character problem requires a frequency table first.

A second pass or iteration over the frequency table can determine the largest count.

There is an important design decision when multiple characters have the same maximum frequency.

Possible policies include:

- first character encountered
- smallest character
- largest character
- arbitrary character
- all tied characters

The Python implementation demonstrates first-occurrence tie-breaking in `most_frequent_character()` and alphabetical tie-breaking in `most_frequent_character_alphabetical_tie_break()`.

The C++ case study explicitly chooses the smallest character for deterministic output.

A production system should document its tie-breaking rule rather than leaving it accidental.

---

## Duplicate characters

A duplicate is any character whose count is greater than one.

The basic procedure is:

1. Count every character.
2. Iterate through the frequency table.
3. Select counts greater than one.

The result for `banana` is:

- `a` → 3
- `n` → 2

The important condition is:

`frequency > 1`

---

## Unique characters

A unique character has exactly one occurrence.

The condition is:

`frequency == 1`

For `banana`, the unique character is:

`b`

The concept is closely related to the first non-repeating-character problem.

---

## First non-repeating character

The first non-repeating character is different from simply finding any unique character.

The algorithm is:

1. Build the frequency table.
2. Scan the original string from left to right.
3. Return the first character whose frequency equals one.

For:

`swiss`

the frequencies are:

- `s` → 3
- `w` → 1
- `i` → 1

The first character with frequency one is:

`w`

A frequency map alone does not preserve the required positional decision. The original string must also be considered.

---

## First repeating character

The first repeating character can be solved using a set.

For every character:

1. Check whether it has already been seen.
2. If yes, return it.
3. Otherwise insert it into the set.

This can be performed in one pass.

Expected complexity:

- Time: `O(n)`
- Space: `O(k)`

This demonstrates that not every frequency-related problem requires an explicit frequency count.

---

## Frequency comparison

Two strings have the same character frequencies if every character occurs the same number of times in both strings.

For example:

`aabbcc`

and

`ccbbaa`

have equal frequency distributions.

Order does not matter.

This is the fundamental idea behind many anagram problems.

The Python implementation uses:

`Counter(text_a) == Counter(text_b)`

The JavaScript implementation explicitly compares two `Map` structures.

The C++ implementation compares two `unordered_map` objects.

---

## Anagrams

Two strings are anagrams when they contain the same characters with the same frequencies after applying the problem's normalization rules.

For example:

`listen`

and

`silent`

have the same distribution.

A practical application often requires normalization.

The Python implementation's `can_form_anagram()`:

- converts letters to lowercase
- removes non-English alphabetic characters
- compares frequencies

Therefore:

`Dormitory`

and

`Dirty room`

are treated as equivalent by that function.

The exact normalization rule is part of the problem definition. Anagram comparison should not silently assume that spaces, punctuation, case, accents, or Unicode normalization are irrelevant.

---

## Frequency difference

A frequency difference compares two distributions.

If:

`text_a = aab`

and

`text_b = ab`

then:

`a → +1`

The positive count indicates that the first input contains one additional `a`.

A negative value indicates that the second input contains more occurrences.

This technique is useful when a program needs to identify exactly what character counts differ rather than returning only `true` or `false`.

---

## Character grouping

Characters can be grouped according to their frequency.

For `banana`:

- frequency 1 → `b`
- frequency 2 → `n`
- frequency 3 → `a`

The Python function is:

`group_characters_by_frequency()`

The JavaScript equivalent is:

`groupCharactersByFrequency()`

The C++ equivalent is:

`groupByFrequency()`

This transforms a character-to-count relationship into a count-to-characters relationship.

That is a useful example of changing the direction of an association.

---

## Sorting by frequency

A frequency map does not inherently provide a frequency-sorted result.

If the application needs:

`character → frequency`

ordered by decreasing frequency, the distinct characters must be sorted.

If there are `k` distinct characters:

- counting costs `O(n)`
- sorting costs `O(k log k)`

Total:

`O(n + k log k)`

When `k` is bounded by a small alphabet, the sorting cost may be insignificant.

---

## Unicode considerations

Character frequency becomes more subtle when Unicode is involved.

ASCII-based frequency arrays assume a small fixed character domain.

Unicode has a much larger character space.

Python strings provide Unicode-aware text processing. JavaScript's `for...of` iterates Unicode code points rather than individual UTF-16 code units. C++ `std::string`, by contrast, is fundamentally a sequence of bytes and does not automatically provide full Unicode character semantics.

There is an additional distinction between:

- bytes
- Unicode code units
- Unicode code points
- grapheme clusters

A visible human-perceived character may consist of multiple code points.

Therefore, a statement such as "count characters" is incomplete for advanced internationalized software unless the intended unit is specified.

---

## Case sensitivity

These are different:

`A`

and

`a`

in a case-sensitive frequency calculation.

A case-insensitive algorithm should normalize them to a common representation.

The implementations demonstrate both approaches.

Case conversion itself can have language-specific and Unicode-specific behavior, so production systems dealing with international text should define their normalization requirements precisely.

---

## Whitespace and punctuation

Whitespace is still a character.

For:

`a b`

the space has a frequency of one.

Possible application rules include:

- count spaces
- ignore spaces
- count all whitespace together
- distinguish spaces from tabs
- remove punctuation
- preserve punctuation

There is no universally correct choice.

The algorithm must follow the requirements of the problem being solved.

---

## Edge cases

Important edge cases include:

### Empty string

Input:

`""`

Frequency:

`{}`

There is no most frequent character and no first non-repeating character.

### One character

Input:

`"a"`

Frequency:

`a → 1`

The character is both unique and the most frequent character.

### All characters identical

Input:

`"aaaa"`

Frequency:

`a → 4`

There is no unique character.

### Case differences

Input:

`"AaAa"`

A case-sensitive algorithm sees two characters.

A case-insensitive algorithm sees one character with frequency four.

### Whitespace

Input:

`"a a"`

The space has frequency one.

### Punctuation

Input:

`"!!!"`

The exclamation mark has frequency three.

### Digits

Input:

`"112233"`

Digits can be treated exactly like other characters if the problem definition permits them.

### Unicode

Input may contain characters outside ASCII. A fixed 26-element English-letter array cannot represent those characters.

---

## Validation

The Python implementation validates that the input is a string.

The JavaScript implementation uses `typeof value !== "string"`.

The C++ implementation enforces a document-size limit.

Input validation is important because a frequency algorithm can otherwise receive:

- null-like values
- numbers
- arrays
- oversized input
- malformed external data

The appropriate validation policy depends on the application.

---

## Common mistakes

### Using nested loops unnecessarily

A slow approach might compare every character against every other character.

That can lead to:

`O(n²)`

time.

A frequency table normally reduces the counting operation to:

`O(n)`

expected time.

### Forgetting case sensitivity

Counting `A` and `a` separately may be correct or incorrect depending on the requirement.

The rule should be explicit.

### Ignoring whitespace accidentally

Spaces are characters unless the specification says otherwise.

### Using a fixed array for an unknown alphabet

A 26-element array is not a general Unicode frequency structure.

### Losing original order

A frequency table does not by itself answer positional questions such as "first non-repeating character."

The original string must be scanned when order matters.

### Assuming dictionary ordering solves frequency ordering

Frequency structures and sorted frequency reports are different concepts.

Sorting requires an additional operation.

### Using an ambiguous tie-breaking rule

If several characters have the same maximum frequency, the program should define which result is expected.

### Confusing code points with visible characters

Unicode text can contain multiple code points representing one perceived character.

---

## Advanced sliding-window application

Character frequency is not limited to simple counting.

The Python, JavaScript, and C++ implementations also demonstrate sliding-window algorithms.

### Longest substring without repeating characters

For:

`abcabcbb`

the longest substring without a repeated character is:

`abc`

The algorithm maintains a moving window and records the most recent position of each character.

When a duplicate appears inside the active window, the left boundary moves forward.

Complexity:

- Time: `O(n)`
- Space: `O(k)`

The critical property is that the left boundary never moves backward.

---

## Minimum window containing required characters

The minimum-window problem asks for the smallest substring containing all required characters with their required frequencies.

For:

`ADOBECODEBANC`

and required characters:

`ABC`

the result is:

`BANC`

The algorithm maintains:

- required frequencies
- current window frequencies
- number of requirements currently satisfied
- left and right window boundaries

This demonstrates how a simple frequency table becomes part of a more advanced linear-time algorithm.

---

## Frequency signatures

A frequency signature is a canonical representation of a character distribution.

For example, the words:

`eat`

and

`tea`

have the same frequency signature because each contains:

- `a` → 1
- `e` → 1
- `t` → 1

The Python implementation represents a signature as a sorted tuple of character-count pairs.

The JavaScript implementation constructs a deterministic string signature.

The C++ implementation uses a fixed 256-entry frequency representation.

A signature can be used as a key for grouping anagrams.

---

## Grouping anagrams

The input:

`eat, tea, tan, ate, nat, bat`

can be partitioned into groups whose members have identical character-frequency distributions.

Conceptually:

- `eat`, `tea`, `ate`
- `tan`, `nat`
- `bat`

The important algorithmic idea is:

1. Generate a canonical frequency signature.
2. Use the signature as a group key.
3. Append each word to the corresponding group.

If there are `n` words and each word has length approximately `m`, generating frequency signatures is approximately `O(nm)` for fixed-alphabet counting, with additional costs depending on the representation and sorting strategy.

---

## Performance considerations

### Dictionary or hash map

Expected:

`O(n)` counting time

Memory:

`O(k)`

This is the most general approach.

### Fixed frequency array

Time:

`O(n)`

Memory:

`O(A)`

where `A` is the fixed alphabet size.

This is particularly effective for ASCII or lowercase English letters.

### Sorting frequency results

If there are `k` distinct characters:

`O(k log k)`

sorting is required after counting.

### Nested-loop counting

A direct comparison approach may require:

`O(n²)`

time.

This is generally unnecessary when a frequency table can be used.

---

## Data-structure comparison

| Structure | Best use | Typical lookup | Memory model |
|---|---|---:|---|
| Fixed array | Small known alphabet | O(1) | Fixed |
| Python `dict` | General character keys | Expected O(1) | Dynamic |
| Python `Counter` | Frequency-specific operations | Expected O(1) | Dynamic |
| JavaScript `Map` | Explicit key-value frequency table | Expected O(1) | Dynamic |
| C++ `unordered_map` | General hash-based counting | Expected O(1) | Dynamic |
| C++ `map` | Ordered keys | O(log k) | Dynamic |

The best structure depends on the domain rather than on a universal rule.

---

## Security considerations

Character-frequency processing can be computationally simple but still appear in systems that process untrusted input.

Relevant considerations include:

- imposing input-size limits
- avoiding unbounded memory allocation
- validating external data
- avoiding assumptions about encoding
- handling malformed text safely
- defining Unicode normalization requirements
- preventing denial-of-service conditions caused by extremely large inputs
- avoiding accidental exposure of sensitive document contents in diagnostic logs

Frequency distributions themselves can reveal information about source text. Applications handling confidential documents should treat analytical results according to the sensitivity of the original data.

---

## Implementation considerations

A production implementation should define:

1. What constitutes a character.
2. Whether comparison is case-sensitive.
3. Whether whitespace matters.
4. Whether punctuation matters.
5. Whether digits matter.
6. Which encoding is expected.
7. Whether Unicode normalization is required.
8. How ties are resolved.
9. Maximum input size.
10. Whether deterministic output is required.

These decisions are part of the algorithm's specification.

---

## Python, JavaScript, and C++ distinctions

### Python

Python is particularly convenient for frequency problems because dictionaries and `Counter` provide high-level abstractions.

The Python implementation is useful for:

- learning the counting algorithm
- experimenting with different data structures
- rapid testing
- building frequency-based utilities
- demonstrating advanced algorithms concisely

### JavaScript

JavaScript provides a useful perspective because character-frequency logic can be implemented with:

- objects
- `Map`
- arrays
- `Set`

The implementation also demonstrates modern Unicode-aware iteration and application-oriented processing.

This is relevant to browser and Node.js applications that analyze user-provided text.

### C++

C++ exposes more implementation details.

The case study demonstrates:

- explicit data structures
- classes
- deterministic sorting
- fixed-size arrays
- hash tables
- exception handling
- memory-conscious design
- algorithmic complexity
- system-style reporting

C++ is therefore useful when the goal is to understand how frequency analysis fits into a larger performance-sensitive system.

---

## Real-world applications

Character frequency techniques appear in many systems.

### Text analytics

Frequency tables can identify common symbols and structural properties of documents.

### Data validation

Expected character distributions can be compared against received data.

### Anagram detection

Frequency equality provides a direct mathematical basis for anagram comparison.

### Duplicate detection

Frequency counts identify repeated symbols.

### Search algorithms

Sliding-window techniques use frequency tables to identify substrings satisfying character constraints.

### Log processing

Character-level analysis can be part of preprocessing pipelines.

### Data compression

Frequency information is fundamental to several compression strategies, although a frequency table alone is not a complete compression algorithm.

### Pattern analysis

Frequency distributions can serve as compact structural representations of textual data.

### Grouping

Frequency signatures can group strings with equivalent character distributions.

---

## Important distinctions

### Frequency versus presence

A set answers:

"Does this character exist?"

A frequency map answers:

"How many times does this character exist?"

### Unique versus distinct

Distinct means the character appears at least once.

Unique means it appears exactly once.

### Most frequent versus first frequent

Most frequent depends on the highest count.

First occurrence depends on position.

When counts tie, an explicit tie-breaking rule is required.

### Counting versus sorting

Counting establishes frequencies.

Sorting establishes an order for displaying or processing those frequencies.

They are separate operations.

### ASCII versus Unicode

An ASCII-oriented fixed array is efficient for a restricted domain.

It is not a complete Unicode text-processing solution.

---

## Testing strategy

The implementations include tests for:

- ordinary strings
- empty strings
- repeated characters
- unique characters
- duplicate characters
- anagrams
- frequency differences
- sliding windows
- minimum windows
- anagram groups
- invalid input
- input-size limits

A good frequency implementation should not be tested only with simple examples such as `banana`.

Boundary cases often expose assumptions about:

- empty input
- ties
- case
- whitespace
- punctuation
- encoding
- missing results

---

## Complexity reference

| Operation | Typical time | Additional space |
|---|---:|---:|
| Character counting | O(n) | O(k) |
| Fixed alphabet counting | O(n) | O(A) |
| Most frequent character | O(n) | O(k) |
| Duplicate detection | O(n) | O(k) |
| Unique-character detection | O(n) | O(k) |
| Frequency comparison | O(n + m) | O(k) |
| Frequency sorting | O(n + k log k) | O(k) |
| First repeating character | O(n) expected | O(k) |
| Longest unique substring | O(n) | O(k) |
| Minimum required-character window | O(n) | O(k) |
| Anagram grouping | Depends on signature method | Depends on number of groups |

Here:

- `n` is the length of the first input.
- `m` is the length of the second input.
- `k` is the number of distinct characters.
- `A` is the fixed alphabet size.

---

## Files

The three executable implementations correspond to this topic:

- Python: comprehensive educational implementation from basic frequency counting through sliding-window and anagram-grouping algorithms.
- JavaScript: application-oriented implementation using objects, `Map`, arrays, sets, Unicode-aware iteration, and validation.
- C++: text analytics case study using `unordered_map`, fixed arrays, classes, sorting, sliding windows, document analysis, and tests.

All three implementations are self-contained and use no external dependencies.
