# Permutations

## Purpose

This project implements exhaustive permutation generation from four complementary perspectives:

- Recursive permutation generation
- Swap-based generation
- Used-array generation
- Duplicate-aware permutation generation

The five source files use the same mathematical problem while applying different programming and data-modeling techniques.

The central relationship is:

`Input sequence → recursion state → candidate selection → permutation → duplicate control → validation`

For `n` distinct elements, the number of permutations is `n!`.

When values repeat, the number of distinct permutations is:

`n! / (c1! × c2! × ... × ck!)`

where each `ci` is the frequency of one repeated value.

For example, `AAB` has three distinct permutations:

`AAB, ABA, BAA`

because `3! / 2! = 3`.

## Core Concepts

### Permutations

A permutation is an ordering of all elements of a sequence.

For `[A, B, C]`, the six permutations are:

`ABC`  
`ACB`  
`BAC`  
`BCA`  
`CAB`  
`CBA`

The ordering matters. This distinguishes permutations from combinations, where the selected elements are not ordered.

### Recursive Generation

Permutation generation naturally forms a search tree.

For `[A, B, C]`:

    []
    ├── A
    │   ├── AB → ABC
    │   └── AC → ACB
    ├── B
    │   ├── BA → BAC
    │   └── BC → BCA
    └── C
        ├── CA → CAB
        └── CB → CBA

Each recursion level selects the value that occupies the next position.

The recursion terminates when the current permutation has the same length as the input.

### Swap-Based Generation

The swap approach fixes one position at a time.

For a sequence beginning with `[A, B, C]`, the algorithm exchanges the first position with each possible candidate, recursively processes the remaining suffix, and restores the original arrangement after returning.

The essential state transition is:

`swap(start, candidate) → recurse(start + 1) → swap(start, candidate)`

Restoring the swap is important because sibling recursion branches must begin from the same state.

Duplicate values require an additional per-level set so that equal values are not placed into the same position through separate branches.

### Used-Array Generation

The used-array approach keeps the original values in stable positions.

A boolean array records whether an input position has already been selected:

`used[i] = true`

The recursive state contains:

- The current permutation
- The used-position array

At every depth, unused positions become candidates.

This approach makes selection state explicit and is useful when input positions have semantic meaning.

### Duplicate Handling

Duplicates cause the raw recursion tree to contain repeated results.

For `[A, A, B]`, selecting the first `A` and selecting the second `A` initially produce structurally different branches even though they produce identical value sequences.

Duplicate-aware generation prevents equivalent branches.

The implementations use a set of values selected at the current recursion depth.

This is different from the global `used` state.

The global state answers:

`Has this input position already been selected in the current permutation?`

The per-level set answers:

`Has this value already been used for this position?`

These two questions must not be conflated.

## Python Implementation

The Python file provides several implementations through functions and generators.

### Used-Array Generator

`permutations_used_array()` maintains:

- A sorted input list
- A Boolean `used` list
- A mutable current permutation
- A per-recursion-level duplicate set

It yields tuples instead of constructing one permanent collection of all results.

This allows callers to process results incrementally.

### Swap Generator

`permutations_swap()` modifies a working list in place.

The recursive function receives the index whose value is currently being fixed.

After recursion returns, the swap is reversed.

This restoration step prevents state leakage between sibling branches.

### Distinct-Input Generator

`permutations_distinct()` provides a stricter API for inputs known to contain unique values.

It rejects duplicate input rather than silently applying duplicate elimination.

This distinction is useful when duplicate values indicate invalid business input rather than a legitimate case.

### Validation

The Python implementation validates input size and reports invalid usage through `PermutationError`.

The exhaustive generator is deliberately restricted to small inputs because factorial growth makes large exhaustive searches impractical.

Assertions verify that:

- Both algorithms produce the expected number of results
- Duplicate-aware generation does not produce repeated permutations
- Different generation strategies produce equivalent result sets

## JavaScript Implementation

The JavaScript implementation uses generator functions and asynchronous iteration.

### Generator-Based Processing

`permutationsUsedArray()` and `permutationsSwap()` are synchronous generators.

A caller can consume one result at a time rather than immediately allocating the complete result set.

This is useful when a consumer needs to stop early.

For example, a caller can inspect the first matching permutation without generating every remaining result.

### Asynchronous Generation

`permutationsAsync()` provides an asynchronous interface.

The generator periodically yields control through `setImmediate`.

This does not reduce the mathematical number of permutations. It prevents a long synchronous computation from monopolizing the Node.js event loop for an extended interval.

### Maps and Sets

The JavaScript implementation uses `Map` for frequency counting and `Set` for duplicate suppression at a recursion depth.

The distinction between global used state and per-level duplicate state is preserved from the mathematical algorithm.

### Failure Handling

Invalid input is represented by `PermutationError`.

The top-level `main()` function catches failures and sets the Node.js process exit status.

## C++17 Implementation

The C++ implementation treats permutation generation as a reusable domain service through `PermutationEngine`.

The class owns the working sequence and exposes two generation strategies:

- `generateSwapBased()`
- `generateUsedArray()`

### Swap-Based State

The swap algorithm mutates a `vector<string>` in place.

A `set` records values already considered for the current recursion depth.

The original sequence is restored after every recursive call.

This gives the algorithm low auxiliary state while keeping the generated result collection separate from the recursion state.

### Used-Array State

The used-array implementation explicitly stores selection state in `vector<bool>`.

A current `vector<string>` represents the partial permutation.

The algorithm adds a value, recurses, removes the value, and marks the corresponding position unused.

### Verification

The program validates generated results by checking:

- Expected permutation count
- Actual result count
- Uniqueness of generated vectors

A `set<vector<string>>` is used for verification because vectors have lexicographical comparison support in the C++ standard library.

### Constraints

The implementation limits exhaustive generation to nine elements.

This is a practical safety boundary. Even though the algorithms are mathematically correct for larger inputs, materializing factorial-sized result collections quickly becomes expensive.

## Java 17 Implementation

The Java implementation models permutation generation through an explicit service and generator interface.

### Domain Types

`GenerationMethod` distinguishes:

- `USED_ARRAY`
- `SWAP`

`PermutationReport` is a Java record containing the measurable result of a generation operation.

`PermutationException` represents invalid domain operations.

### Generator Interface

`PermutationGenerator` provides a common abstraction for independent generation strategies.

`UsedArrayGenerator` and `SwapGenerator` implement the interface without exposing their internal recursion state.

This separates the permutation service from the algorithm used to produce results.

### Service Layer

`PermutationService` coordinates:

- Input validation
- Expected-count calculation
- Generator execution
- Result validation
- Reporting

This structure reflects an enterprise-style separation between domain behavior and orchestration.

### Immutable Results

Completed permutations are copied using `List.copyOf()`.

This prevents callers from accidentally modifying a permutation after it has been generated and validated.

## PostgreSQL Implementation

The PostgreSQL file represents permutation generation as relational data and recursive queries.

### Relational Model

The main tables are:

| Table | Purpose |
|---|---|
| `permutation_input` | Stores named input sequences |
| `permutation_result` | Stores generated permutations and their generation method |

`permutation_result.input_id` references `permutation_input.input_id` with a foreign key.

Deleting an input automatically deletes its generated results.

### Mathematical Counting

`unique_permutation_count()` calculates the number of distinct permutations using the factorial formula.

For an input with frequencies:

`A = 2, B = 1`

the function calculates:

`3! / (2! × 1!) = 3`

This provides an independent validation target for generated results.

### Used-Array SQL Model

`generate_used_array_permutations()` uses a recursive CTE.

The recursive state contains:

- The current permutation
- Positions already selected

`WITH ORDINALITY` gives each input value a stable position.

The query recursively adds positions that are not already present in the used-position array.

### Remaining-Value Model

`generate_remaining_value_permutations()` represents the same search problem through a different relational state.

Instead of a Boolean used array, each recursive row contains:

- The current prefix
- The remaining values

A candidate is removed from the remaining array and appended to the prefix.

This provides a relational counterpart to recursive permutation construction.

### Constraints and Indexes

The database applies:

- Primary keys
- Foreign keys
- Cardinality checks
- Method checks
- A composite index on input and method

The index supports queries that retrieve generated permutations for a particular input and generation strategy.

### Transactional Integrity

The script includes a transaction that inserts temporary permutation data and rolls it back.

This demonstrates that permutation generation can participate in normal PostgreSQL transaction semantics without leaving partially committed workflow data.

## Cross-Implementation Comparison

| Aspect | Python | JavaScript | C++17 | Java 17 | PostgreSQL |
|---|---|---|---|---|---|
| Main technique | Recursive generators | Generators and async iteration | Domain engine | Generator interface and service | Recursive CTEs |
| Swap generation | Yes | Yes | Yes | Yes | Relational counterpart |
| Used-array generation | Yes | Yes | Yes | Yes | Recursive position state |
| Duplicate handling | Per-level set | Per-level set | Per-level set | Per-level set | Distinct result validation |
| Lazy processing | Yes | Yes | No, materialized results | No, materialized results | Query-driven |
| Validation | Exceptions and assertions | Exceptions | Exceptions and verification | Custom exception and service validation | Constraints and validation queries |
| Primary strength | Concise recursion | Event-loop-compatible processing | Explicit memory and state control | Strong domain modeling | Persistent relational representation |

## Correctness Invariants

A valid permutation generator maintains several invariants.

### Length

Every generated permutation must have exactly the same number of elements as the input.

`length(permutation) = length(input)`

### Membership

Every input occurrence must be represented exactly once in a generated permutation.

For duplicate values, this is based on occurrence frequency rather than simple set membership.

### Uniqueness

A duplicate-aware generator must not return the same value sequence twice.

### Completeness

For an input containing `n` distinct values:

`generated_count = n!`

For repeated values:

`generated_count = n! / product(frequency!)`

### State Restoration

For swap-based recursion, every swap performed before recursive descent must be undone afterward.

Without restoration, one branch can corrupt the starting state of another branch.

## Edge Cases

### Empty Input

The empty sequence has exactly one permutation: the empty sequence.

This follows the mathematical definition of `0! = 1`.

The implementations therefore treat:

`[] → [[]]`

rather than returning zero permutations.

### One Element

A one-element sequence has one permutation containing that element.

`[A] → [A]`

### Repeated Elements

`[A, A, B]` produces three unique permutations rather than six raw recursion results.

### All Elements Equal

`[A, A, A]` has exactly one unique permutation:

`AAA`

### Excessively Large Input

Factorial growth makes exhaustive generation unsuitable for large inputs.

The implementations therefore impose practical input limits rather than attempting an unbounded search.

## Complexity

For `n` distinct values, there are `n!` output permutations.

Since every output contains `n` values, materializing all results requires at least:

`O(n × n!)`

output work.

The recursive working state is generally:

`O(n)`

excluding the stored result collection.

The total memory cost becomes much larger when all permutations are materialized.

The used-array method additionally stores the Boolean selection state.

The swap method primarily mutates the working sequence and uses per-level duplicate tracking.

The PostgreSQL implementation also incurs database storage and query-processing costs when generated permutations are persisted.

## Practical Design Decisions

The implementations deliberately separate four ideas:

**Generation**  
How candidate orderings are constructed.

**State**  
Which values or positions have already been selected.

**Duplicate handling**  
Which equivalent branches can be skipped.

**Validation**  
Whether the generated result set is complete and unique.

This separation makes it possible to change the generation strategy without changing the mathematical correctness criteria.

The most important distinction is between a duplicate input value and a duplicate generated permutation. Duplicate input values are valid. Duplicate output permutations are usually an error when the requested result is the set of distinct permutations.

## Failure Conditions

The implementations reject or constrain cases that would make exhaustive generation unsafe or invalid.

| Failure | Handling |
|---|---|
| Null or invalid input | Explicit validation |
| Excessive input size | Generation limit |
| Duplicate input for distinct-only API | Domain exception |
| Incorrect result count | Verification failure |
| Repeated generated result | Uniqueness validation failure |
| Factorial overflow risk | Range validation |
| Unrestored swap state | Prevented by explicit restoration |

## Security and Reliability Considerations

Permutation generation itself is not an authentication or authorization mechanism, but exhaustive search has an important resource-exhaustion risk.

An externally supplied sequence can cause factorial growth.

For this reason, production systems should enforce:

- Maximum input length
- Maximum result count
- Execution time limits
- Memory limits
- Pagination or streaming
- Cancellation for long-running jobs
- Database transaction boundaries

The provided implementations use small input limits because exhaustive generation is intentionally computationally expensive.

For application-facing APIs, input limits should be enforced before allocating large recursive structures or result collections.

## Repository Structure

A practical file layout is:

- `permutations.py`
- `permutations.js`
- `PermutationEngine.cpp`
- `PermutationPractice.java`
- `permutations.sql`
- `README.md`

Each source file is independently executable in its intended environment.

## Execution Requirements

### Python

Requires Python 3.10 or newer.

Run the script with:

`python permutations.py`

### JavaScript

Requires a modern Node.js runtime.

Run with:

`node permutations.js`

### C++17

Compile with a C++17-compatible compiler.

Example command:

`g++ -std=c++17 -O2 PermutationEngine.cpp -o permutations`

Run:

`./permutations`

On Windows, the resulting executable can be run as:

`permutations.exe`

### Java 17

Compile:

`javac PermutationPractice.java`

Run:

`java PermutationPractice`

### PostgreSQL

Execute the SQL script against a PostgreSQL database with permission to create schemas, tables, functions, and indexes.

The script creates its own `permutation_lab` schema and removes an existing schema of the same name before rebuilding it.

## Learning Progression

The implementations progress from direct recursive reasoning to increasingly explicit engineering models:

`Recursive search`  
→ `Used-array state`  
→ `Swap-based state mutation`  
→ `Duplicate-aware search`  
→ `Lazy/asynchronous consumption`  
→ `Domain-service validation`  
→ `Relational recursive state`

The underlying problem remains the same, while the representation of state, validation, execution model, and persistence changes across languages.
