# Day 20 — String fundamentals

## Introduction

A string is a sequence of characters used to represent textual information. String processing is a fundamental part of data structures and algorithms because many practical problems involve searching, counting, validating, transforming, comparing, or organizing text.

The Day 20 study area covers:

- Characters
- Indexing
- Traversal
- Concatenation
- Comparison
- Conversion
- Case conversion
- Reverse string
- Character counting
- Space removal
- Case transformation
- Vowel counting
- First unique character
- Word counting

The three implementations approach these concepts differently:

- Python emphasizes readable string operations, Unicode-aware behavior, reusable functions, frequency analysis, validation, and a structured text-analysis model.
- JavaScript demonstrates string processing in an application-oriented language, including template literals, Unicode-aware iteration, maps, regular expressions, classes, and runtime validation.
- C++ develops an industry-style command-line text analyzer using `std::string`, standard-library algorithms, explicit data structures, validation, exception handling, and a modular class-based design.

---

## Fundamental concept: characters and strings

A character is a single textual element. A string is an ordered sequence of characters.

For example, the string `Python` contains six positions:

`P y t h o n`

The position of each element is represented by an index.

Most programming languages use zero-based indexing. This means the first element is at index `0`, the second at index `1`, and so on.

For a string of length `n`, valid zero-based indexes are:

`0` through `n - 1`

An empty string has length `0` and therefore has no valid character indexes.

### Character representation differs by language

Python does not have a separate built-in character type. A single character is a string of length one.

JavaScript also does not have a separate character type. A character is represented using a string.

C++ provides the `char` type for a single byte-sized character and `std::string` for a sequence of characters. A C++ `char` should not automatically be interpreted as a complete human-visible Unicode character.

This distinction becomes important when processing international text, emoji, combining characters, and multibyte encodings.

---

## Indexing

Indexing retrieves a character at a particular position.

Python uses:

`text[index]`

JavaScript commonly uses:

`text[index]`

or:

`text.at(index)`

C++ uses:

`text[index]`

and also provides:

`text.at(index)`

The two C++ access forms have different safety characteristics. `operator[]` does not perform bounds checking, while `at()` checks the index and throws `std::out_of_range` when the index is invalid.

Python raises `IndexError` for an invalid index.

JavaScript string indexing returns `undefined` for an index outside the available range.

### Negative indexing

Python supports negative indexing directly:

- `text[-1]` means the last element.
- `text[-2]` means the second-to-last element.

Modern JavaScript provides `at(-1)` for similar behavior.

C++ does not provide Python-style negative indexing. The equivalent must be calculated explicitly using the string length.

---

## Slicing

Slicing extracts part of a string.

Python has dedicated slicing syntax:

`text[start:stop:step]`

The stop position is excluded.

For example, if `text` is `PYTHON`:

- `text[:3]` produces `PYT`
- `text[2:]` produces `THON`
- `text[::2]` produces `PTO`
- `text[::-1]` produces the reverse string

JavaScript does not use Python's slicing syntax. Methods such as `slice()` perform similar extraction:

`text.slice(start, end)`

C++ uses operations such as `substr()` for substring extraction.

---

## Traversal

Traversal means visiting each character in sequence.

A basic traversal can be expressed conceptually as:

1. Start at the first character.
2. Process the current character.
3. Move to the next character.
4. Continue until the end of the string.

Python supports direct iteration:

`for character in text`

It also provides `enumerate()` when both the index and character are required.

JavaScript supports `for...of`, conventional index-based loops, and iteration over `Array.from(text)`.

C++ supports range-based `for` loops and index-based loops.

Traversal is the foundation for many string algorithms, including:

- Character counting
- Vowel counting
- Frequency analysis
- Validation
- Removing whitespace
- Detecting patterns
- Searching
- Building transformed strings

A single complete traversal normally takes O(n) time for a string containing n processed elements.

---

## String immutability

Python strings are immutable. JavaScript primitive strings are immutable. C++ `std::string` objects are mutable.

Immutability means that an existing string cannot have an individual character replaced directly.

For example, Python does not allow:

`text[0] = "H"`

Instead, a new string must be constructed.

JavaScript also does not mutate a primitive string through direct indexed assignment.

C++ differs because an existing `std::string` can be modified:

`text[0] = 'H';`

This difference has practical consequences.

Immutable strings make textual values predictable and prevent accidental modification of shared string values. Mutable strings can be convenient when repeatedly changing characters, but programmers must consider aliasing, state changes, and ownership.

---

## Concatenation

Concatenation means joining strings together.

Python uses:

`+`

and:

`"separator".join(collection)`

Python f-strings are useful when values need to be embedded into text.

JavaScript uses:

`+`

and template literals:

`${value}`

JavaScript also provides `join()` through arrays.

C++ supports `+` for `std::string` concatenation and `operator+=` for appending.

### Performance consideration

For a small number of strings, direct concatenation is normally sufficient.

For large collections of fragments, repeatedly creating temporary strings can increase allocation and copying costs.

Python commonly uses:

`"".join(parts)`

JavaScript commonly uses:

`parts.join("")`

C++ can use repeated `operator+=`, especially when the destination string has adequate capacity. Calling `reserve()` can reduce reallocations when the approximate required size is known.

The appropriate technique depends on the language, workload, implementation, and amount of text.

---

## String comparison

String comparison determines whether strings are equal or establishes an ordering.

Python uses operators such as:

- `==`
- `!=`
- `<`
- `>`
- `<=`
- `>=`

JavaScript uses strict equality:

`===`

and relational operators such as `<` and `>`.

C++ provides comparison operators for `std::string`.

String ordering is generally lexicographic. The exact ordering behavior depends on the language's character representation and comparison rules.

Case-sensitive comparison treats uppercase and lowercase characters as different values.

For example:

`"Python"` and `"python"`

are not equal under a normal case-sensitive comparison.

For case-insensitive comparisons, normalization is required. Python provides `casefold()` for robust caseless comparison. JavaScript can use lowercasing or locale-sensitive operations depending on the requirements. C++ examples in this project use ASCII-oriented case conversion.

---

## Conversion

Text frequently needs to be converted into other data types.

Python provides:

`str(value)`

for converting values to strings and functions such as:

`int(text)`

for integer conversion.

JavaScript provides:

`String(value)`

and:

`Number(text)`

C++ provides mechanisms such as `std::to_string()` for converting values to strings. Stream-based parsing can be used when more structured validation is required.

Conversion should be validated when input originates outside the program.

Examples of potentially unreliable input include:

- User-entered values
- Configuration files
- Network requests
- Command-line arguments
- Imported datasets

A robust program should not assume that every textual value is valid.

---

## Case conversion

Case conversion transforms alphabetic text.

Common operations include:

- Uppercase
- Lowercase
- Capitalization
- Title-style formatting
- Case-insensitive normalization

Python provides:

- `upper()`
- `lower()`
- `capitalize()`
- `title()`
- `swapcase()`
- `casefold()`

JavaScript provides:

- `toUpperCase()`
- `toLowerCase()`

The JavaScript implementation also demonstrates application-level capitalization and title-style processing.

C++ does not provide the same high-level collection of string case methods as Python. The case-study implementation uses standard character functions such as `tolower()` and `toupper()`.

### Important Unicode distinction

Simple ASCII case conversion is not sufficient for every language.

International text can contain characters whose case relationships depend on Unicode rules and locale. A production internationalization system should use appropriate Unicode and locale-aware facilities rather than assuming that every character behaves like English A-Z.

---

## Reverse string

Reversing a string is a common introductory algorithm.

For a string:

`hello`

the reversed string is:

`olleh`

Python can use slicing:

`text[::-1]`

The Python implementation also provides a manual implementation using indexes and a list.

JavaScript uses `Array.from(text).reverse().join("")`.

C++ copies the string and uses `std::reverse()`.

The normal complexity is:

- Time: O(n)
- Additional space: O(n)

because a new reversed string is produced.

A reversal operation becomes more complicated when the definition of "character" involves Unicode grapheme clusters rather than code points or bytes.

---

## Counting characters

Python's `len()` returns the number of Unicode code points represented by the Python string.

JavaScript's `.length` reports UTF-16 code units rather than Unicode code points.

The JavaScript implementation therefore demonstrates both:

- UTF-16 code-unit length
- `Array.from()` code-point-oriented length

C++ `std::string::size()` reports the number of stored bytes represented by the string.

This distinction is essential when comparing programs that process international text.

A statement such as "the string contains ten characters" can be ambiguous unless the representation being counted is specified.

Possible interpretations include:

- Bytes
- UTF-16 code units
- Unicode code points
- Unicode grapheme clusters

The correct interpretation depends on the application.

---

## Removing spaces

The practice implementation removes whitespace by traversing the input and retaining only non-whitespace characters.

Examples include:

`"a b c"` → `"abc"`

The Python implementation uses `str.isspace()`.

The JavaScript implementation uses a regular expression matching whitespace.

The C++ implementation uses `std::isspace()`.

Whitespace is broader than the ordinary ASCII space character. It can include tabs and line breaks.

This distinction matters when cleaning user input.

---

## Counting vowels

The implementations define English vowels as:

`a, e, i, o, u`

The algorithm traverses the input, normalizes alphabetic characters for comparison, and increments the count when a vowel is found.

For English text, this can be implemented in O(n) time.

The implementations also separate vowel and consonant counting from punctuation, digits, and whitespace.

This prevents values such as `7`, `!`, and spaces from incorrectly being treated as consonants.

---

## First unique character

The first unique character is the first character that appears exactly once.

For:

`swiss`

the character `w` is the first unique character.

A practical algorithm is:

1. Traverse the string and count the frequency of each character.
2. Traverse the string again.
3. Return the first character whose frequency equals one.
4. Return no result if every character repeats.

Using a hash-based frequency table gives expected O(n) time.

The Python implementation uses `Counter`.

The JavaScript implementation uses `Map`.

The C++ implementation uses `unordered_map`.

This two-pass pattern is useful because the first occurrence cannot be classified as unique until the total frequency information is known.

---

## Counting words

A simple definition of a word is a maximal sequence of non-whitespace characters.

For:

`one two three`

the result is three words.

For:

`  one   two    three  `

the result should also be three.

The implementations avoid treating repeated whitespace as multiple words.

Python can use:

`text.split()`

with no separator argument.

JavaScript uses trimming and a regular expression for repeated whitespace.

C++ uses either explicit traversal or `std::istringstream`.

The manual traversal demonstrates the underlying algorithm:

- Keep track of whether the current position is inside a word.
- Entering a non-whitespace region increments the count.
- Whitespace ends the current word.

The algorithm requires O(n) time.

---

## Character frequency

Frequency analysis records how many times each character appears.

For:

`banana`

the important frequencies include:

- `a` → 3
- `n` → 2
- `b` → 1

Frequency analysis is a fundamental technique in string problems.

It is useful for:

- Finding duplicate characters
- Finding unique characters
- Anagram detection
- Character statistics
- Text analytics
- Input validation
- Counting symbols
- Building histograms

Python uses `collections.Counter`.

JavaScript uses `Map`.

C++ uses `unordered_map`.

The expected time complexity is O(n), with O(k) additional storage where k is the number of distinct characters.

---

## Whitespace normalization

Removing all whitespace and normalizing whitespace are different operations.

Removing whitespace transforms:

`"Python is great"`

into:

`"Pythonisgreat"`

Whitespace normalization transforms:

`"  Python   is\tgreat  "`

into:

`"Python is great"`

Normalization is usually preferable when the semantic separation between words must be preserved.

It is useful in:

- Search systems
- Form processing
- Data cleaning
- Document processing
- Command parsing

---

## Palindrome detection

A palindrome reads the same forward and backward under a defined comparison rule.

Examples include:

`level`

and:

`A man, a plan, a canal: Panama`

The implementations normalize case and ignore non-alphanumeric characters for the palindrome example.

The general procedure is:

1. Normalize the input.
2. Reverse the normalized value.
3. Compare the original normalized value with its reverse.

The resulting algorithm is O(n) time and O(n) additional space when a cleaned string is constructed.

A two-pointer implementation can reduce temporary storage by comparing characters from both ends directly.

---

## Searching for occurrences

The implementations include a function that finds every starting position of a target substring.

For:

`banana`

searching for:

`ana`

produces positions:

`1, 3`

The implementation intentionally advances the search by one position after a match. This allows overlapping matches to be detected.

Substring searching is a fundamental building block for more advanced algorithms such as:

- Naive pattern matching
- Knuth-Morris-Pratt
- Boyer-Moore
- Rabin-Karp
- Search indexing

The built-in search functions in production code are normally preferable unless implementing an algorithm for educational or specialized purposes.

---

## Python implementation

The Python implementation is organized as a standalone study program.

### Basic demonstrations

The early functions demonstrate:

- Character and string creation
- Indexing
- Negative indexing
- Slicing
- Traversal
- Concatenation
- Comparison
- Conversion
- Case conversion

These examples establish the syntax needed before implementing algorithms.

### Practice algorithms

The Python program implements:

- `reverse_string()`
- `reverse_string_manually()`
- `count_characters()`
- `character_frequency()`
- `remove_spaces()`
- `change_case()`
- `count_vowels()`
- `count_vowels_and_consonants()`
- `first_unique_character()`
- `count_words()`

Each operation is independent, which makes the file useful for studying individual algorithms.

### Validation

The Python implementation demonstrates explicit validation using:

- `TypeError`
- `ValueError`
- `IndexError`

It also provides safe conversion through `safe_integer_from_string()`.

This separates valid program state from invalid input.

### Structured analysis

The `TextAnalysis` dataclass groups multiple results into one structured object.

The `analyze_text()` function combines:

- Character counts
- Word counts
- Vowel and consonant counts
- Unique-character analysis
- Longest-word analysis
- Frequency analysis
- Palindrome detection
- Whitespace normalization
- Character classification

This demonstrates how simple string algorithms can become components of a larger application.

---

## JavaScript implementation

The JavaScript implementation focuses on application-oriented string processing.

### Core syntax

The program demonstrates:

- Primitive strings
- Indexing
- `at()`
- `slice()`
- `for...of`
- Template literals
- `join()`
- `repeat()`
- Strict comparison
- Number conversion
- Case conversion

### Unicode behavior

JavaScript's `.length` counts UTF-16 code units.

This can produce results that differ from the number of visible or code-point-level characters.

`Array.from()` is used where code-point-oriented traversal is more appropriate.

The distinction is demonstrated explicitly with Unicode examples and emoji.

### Frequency maps

JavaScript's `Map` provides a useful data structure for frequency counting.

The pattern is:

1. Read one character.
2. Look up its existing count.
3. Increment the count.
4. Store the updated value.

This structure supports the first-unique-character algorithm.

### Regular expressions

Regular expressions are used for:

- Whitespace recognition
- Word separation
- Character classification
- Unicode-aware character tests

They are useful when the definition of a character class is more complex than a simple equality check.

### Class-based analyzer

The `TextAnalyzer` class demonstrates how individual string operations can be combined into a reusable object.

Its `analyze()` method returns a structured result containing multiple statistics.

This models a small application component rather than a collection of unrelated examples.

---

## C++ case study

The C++ program models a command-line text intelligence analyzer.

The system accepts a text value and produces structured information about it.

### Problem being solved

A text-processing component needs to answer questions such as:

- How many characters are present?
- How many words exist?
- How many vowels and consonants occur?
- What is the first unique character?
- What is the longest word?
- Is the text a palindrome?
- How frequently does each character occur?
- How much whitespace is present?
- How many letters, digits, and symbols exist?

These operations represent common low-level text-processing requirements.

### Architecture

The C++ implementation separates responsibilities into several layers.

#### Utility functions

Functions such as:

- `trim()`
- `toLowerASCII()`
- `toUpperASCII()`
- `isWhitespace()`
- `isVowel()`

provide reusable low-level operations.

#### Algorithms

The program then implements algorithms for:

- Reversal
- Character counting
- Space removal
- Case conversion
- Vowel counting
- Frequency analysis
- First unique character
- Word counting
- Longest word
- Palindrome detection
- Substring occurrence detection

#### Data structures

The case study uses:

- `std::string`
- `std::vector`
- `std::unordered_map`
- `std::map`
- `std::optional`
- `std::pair`
- `std::istringstream`
- `std::ostringstream`

Each structure is selected for a particular purpose.

`unordered_map` is useful for expected O(1) average frequency lookup.

`map` is useful when deterministic sorted character output is desirable.

`optional<char>` represents the possibility that no unique character exists without inventing a special sentinel character.

#### TextAnalyzer class

`TextAnalyzer` owns the input and exposes an `analyze()` operation.

This separates:

- Input validation
- Analysis
- Result representation
- Report generation

The design can be expanded without forcing the reporting code to perform the analysis itself.

---

## Complexity analysis

Let `n` represent the number of processed string elements and `k` represent the number of distinct characters.

| Operation | Typical time | Additional space |
|---|---:|---:|
| Index access | O(1) | O(1) |
| Full traversal | O(n) | O(1) |
| Reverse into new string | O(n) | O(n) |
| Remove spaces | O(n) | O(n) |
| Count vowels | O(n) | O(1) |
| Count words | O(n) | O(1) |
| Character frequency | O(n) expected | O(k) |
| First unique character | O(n) expected | O(k) |
| Longest word | O(n) | O(n) depending on parsing |
| Palindrome with normalization | O(n) | O(n) |
| Substring search using repeated basic search | Depends on implementation | O(m) result storage |

For ordinary educational string problems, O(n) solutions are usually appropriate because every character may need to be examined.

---

## Edge cases

String algorithms should explicitly consider boundary conditions.

Important cases include:

### Empty string

`""`

There are:

- Zero characters
- Zero words
- Zero vowels
- No unique character

Functions should avoid assuming that an element exists.

### Whitespace-only input

Examples:

`" "`

`"   "`

`"\t\n"`

Whitespace-only input may be syntactically non-empty but semantically empty for applications that require meaningful text.

The implementations demonstrate validation for this situation.

### Digits

A string such as:

`"12345"`

contains characters but no English vowels or consonants.

### Punctuation

A string such as:

`"!@#$%"`

contains symbols but no alphabetic characters.

### Mixed input

Example:

`"A1 B2 C3"`

contains letters, digits, whitespace, and potentially punctuation.

### Unicode text

Examples include:

`"café"`

`"भारत"`

`"日本"`

and emoji.

Unicode requires care because the meaning of "character" varies according to the representation and application requirements.

---

## Important distinction: bytes, code units, code points, and grapheme clusters

String processing becomes more subtle when Unicode is involved.

A byte is a unit of encoded storage.

A code unit is the basic unit used by a particular string encoding.

A Unicode code point represents a Unicode scalar value.

A grapheme cluster is closer to what a user perceives as one displayed character.

These are not always equivalent.

For example, an emoji or a letter with combining marks may occupy multiple storage units while appearing as one visual character.

The Python, JavaScript, and C++ implementations therefore should not be assumed to have identical character-count semantics.

Production applications that need precise user-visible character handling should define the required text model before implementing algorithms.

---

## Common mistakes

### Off-by-one errors

Incorrect:

`for index in range(len(text) + 1)`

The final index would be invalid.

The valid indexes range from `0` through `len(text) - 1`.

### Assuming indexing works for empty strings

Accessing the first character of an empty string is invalid.

### Treating whitespace as only `" "`

Tabs and line breaks are also whitespace.

### Forgetting case sensitivity

`"A"` and `"a"` are different in ordinary comparisons.

### Using the wrong conversion function

Text such as `"123abc"` should not automatically be accepted as a valid integer.

### Assuming `.length` has the same meaning in every language

Python, JavaScript, and C++ use different underlying string representations.

### Modifying immutable strings

Python and JavaScript primitive strings cannot be modified character-by-character.

### Ignoring Unicode

ASCII assumptions are unsuitable for many internationalized applications.

### Repeated inefficient concatenation

Constructing very large strings through repeated intermediate allocations can be inefficient.

### Confusing unique with first unique

A unique character must occur exactly once.

The first unique character is the first character in original order whose total frequency equals one.

---

## Exceptions and failure handling

The implementations intentionally demonstrate failures rather than silently ignoring them.

Python handles:

- Invalid indexes with `IndexError`
- Invalid case modes with `ValueError`
- Incorrect input types with `TypeError`
- Invalid numeric conversion through a safe conversion function

JavaScript handles:

- Invalid case modes with `Error`
- Invalid text through explicit type checks
- Empty search targets with exceptions

C++ handles:

- Invalid indexing through checked `at()`
- Invalid text using `std::invalid_argument`
- Unexpected application failures through the `main()` exception boundary

Good error handling makes the behavior of a string-processing component explicit.

---

## Performance considerations

String operations often require linear time because the program must inspect characters.

For example, counting vowels requires examining every character:

`O(n)`

Building a frequency table also requires reading every character:

`O(n)`

Finding the first unique character can be implemented with two linear passes:

`O(n)`

The additional frequency table requires storage proportional to the number of distinct characters:

`O(k)`

### Allocation behavior

Operations that create new strings require memory for their results.

Examples include:

- Reversal
- Case conversion
- Space removal
- Normalization
- Concatenation

When repeatedly building large text values, using a collection followed by `join()` in Python or JavaScript can be preferable.

In C++, reserving capacity can reduce reallocations when repeated appends are expected.

---

## Security considerations

String processing often occurs at application boundaries, so validation is important.

Potential sources of untrusted strings include:

- Web forms
- APIs
- Command-line input
- Configuration
- Database records
- Uploaded files
- Network messages

Important considerations include:

### Input size

Very large strings can consume substantial memory and CPU time.

Applications should impose appropriate limits when input size is externally controlled.

### Encoding

Invalid or unexpected encodings can cause incorrect processing.

### Normalization

Two visually similar strings may have different underlying representations.

Applications involving authentication, identifiers, filenames, or security-sensitive comparisons should define normalization rules carefully.

### Case-insensitive comparisons

A simple lowercase comparison may not be sufficient for every language or security-sensitive identifier.

### Injection

String concatenation should not be used to construct commands, SQL statements, HTML, or other executable formats from untrusted input without appropriate escaping, parameterization, or structured APIs.

The basic string techniques in this lesson are text-processing mechanisms, not complete security controls.

---

## Python, JavaScript, and C++ comparison

| Area | Python | JavaScript | C++ |
|---|---|---|---|
| Basic string type | `str` | Primitive `string` | `std::string` |
| Separate char type | No | No | Yes, `char` |
| Indexing | Direct | Direct / `at()` | `[]` / `at()` |
| Negative indexing | Yes | `at()` supports negative positions | No direct equivalent |
| Direct mutation | No | No for primitive strings | Yes |
| Frequency structure | `Counter` | `Map` | `unordered_map` |
| Case conversion | Rich built-in methods | Upper/lower methods | Character functions |
| Typical use | Data processing, scripting, algorithms | Web and application logic | Systems and performance-sensitive software |
| Unicode behavior | Unicode-oriented strings | UTF-16 code units | Depends strongly on encoding |
| Bounds behavior | Exception for invalid indexing | `undefined` for bracket access | `at()` throws, `[]` does not check |

The languages demonstrate the same algorithmic ideas while exposing different implementation concerns.

---

## Best practices

1. Define exactly what counts as a character before implementing a text algorithm.
2. Handle empty strings explicitly.
3. Validate externally supplied input.
4. Distinguish spaces from general whitespace.
5. Make case sensitivity explicit.
6. Use frequency maps for repeated counting problems.
7. Prefer linear-time algorithms when every character must be inspected.
8. Avoid unnecessary repeated allocations for large text.
9. Use language-appropriate Unicode handling when international text matters.
10. Keep validation, processing, and reporting responsibilities separate.
11. Use checked access when safety is more important than unchecked access.
12. Test edge cases rather than testing only normal input.
13. Document assumptions such as ASCII-only case conversion.
14. Use built-in search and transformation operations when they provide clearer and sufficiently efficient solutions.
15. Measure performance when processing very large strings instead of relying only on theoretical assumptions.

---

## Practical applications

String fundamentals are used throughout software engineering.

### Search

Search boxes, document search, command interpreters, and filtering systems all process strings.

### Data cleaning

Raw data frequently contains inconsistent spaces, capitalization, punctuation, and formatting.

### Validation

Email-like identifiers, usernames, product codes, dates, account references, and configuration values all require textual validation.

### Log analysis

Logs are strings containing timestamps, messages, identifiers, and status information.

### Compilers and interpreters

Source code begins as text and is transformed through lexical and syntactic processing.

### Natural-language processing

Text analysis requires tokenization, normalization, counting, searching, and Unicode handling.

### Web applications

Forms, URLs, headers, cookies, JSON fields, HTML content, and user-generated content all involve strings.

### Security systems

Authentication and authorization systems frequently compare and normalize textual identifiers.

---

## Relationship to data structures and algorithms

String problems are an important introduction to algorithmic thinking because they combine a simple data representation with many different computational tasks.

A string can be treated as:

- A sequence
- An indexed collection
- A searchable structure
- A frequency source
- A token stream
- A normalized value
- Input to a pattern-matching algorithm

The practice problems develop several reusable algorithmic patterns.

### One-pass traversal

Used for:

- Character counting
- Vowel counting
- Classification
- Word counting

### Frequency table

Used for:

- Duplicate detection
- Unique-character problems
- Anagram problems
- Statistical analysis

### Two-pass processing

Used by the first-unique-character algorithm.

### Two-pointer processing

Useful for:

- Palindrome checking
- In-place comparisons
- Reversal-related algorithms

### Transformation pipeline

Useful for:

- Normalization
- Cleaning
- Filtering
- Case conversion
- Validation

These patterns recur throughout more advanced data structures and algorithm problems.

---

## Implemented practice checklist

The three programs collectively implement the required Day 20 practice problems.

- [x] Reverse string
- [x] Count characters
- [x] Remove spaces
- [x] Change case
- [x] Count vowels
- [x] Find first unique character
- [x] Count words

The implementations also cover:

- [x] Characters
- [x] Indexing
- [x] Traversal
- [x] Concatenation
- [x] Comparison
- [x] Conversion
- [x] Case conversion
- [x] Character frequency
- [x] Whitespace normalization
- [x] Palindrome detection
- [x] Substring occurrence detection
- [x] Input validation
- [x] Exception handling
- [x] Edge-case testing
- [x] Complexity analysis
- [x] Unicode representation considerations
- [x] Modular text analysis
