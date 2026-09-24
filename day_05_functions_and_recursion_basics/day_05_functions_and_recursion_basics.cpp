/*
 * Day 5 — Functions and Recursion Basics
 *
 * C++17 case study:
 * A Recursive File-System Analysis Engine
 *
 * The program demonstrates:
 * - Function declarations and definitions
 * - Parameters and return values
 * - Local scope
 * - Function composition
 * - Iteration versus recursion
 * - Base cases
 * - Recursive calls
 * - Call-stack behavior
 * - Recursive tree traversal
 * - Searching
 * - Aggregation
 * - Validation
 * - Error handling
 * - Complexity analysis
 * - Memoization
 * - Industry-style data modeling
 *
 * The simulated file system is represented as a tree:
 *
 * Directory
 *   ├── File
 *   ├── File
 *   └── Directory
 *         ├── File
 *         └── File
 *
 * This is a realistic use of recursion because every directory can contain
 * directories that contain more directories.
 */

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;


// ============================================================================
// 1. BASIC FUNCTIONS
// ============================================================================

int add(int first, int second) {
    return first + second;
}

int multiply(int first, int second) {
    return first * second;
}

double divide(double dividend, double divisor) {
    if (divisor == 0.0) {
        throw invalid_argument("Division by zero is not allowed.");
    }

    return dividend / divisor;
}


// ============================================================================
// 2. RECURSIVE FUNDAMENTALS
// ============================================================================

long long factorialRecursive(int number) {
    if (number < 0) {
        throw invalid_argument(
            "Factorial requires a non-negative integer."
        );
    }

    // Base case: recursion must stop at zero.
    if (number == 0) {
        return 1;
    }

    // Recursive case: reduce the problem toward zero.
    return static_cast<long long>(number) *
           factorialRecursive(number - 1);
}

long long factorialIterative(int number) {
    if (number < 0) {
        throw invalid_argument(
            "Factorial requires a non-negative integer."
        );
    }

    long long result = 1;

    for (int current = 2; current <= number; ++current) {
        result *= current;
    }

    return result;
}


// ============================================================================
// 3. RECURSIVE POWER
// ============================================================================

long long powerRecursive(long long base, int exponent) {
    if (exponent < 0) {
        throw invalid_argument(
            "This integer implementation requires a non-negative exponent."
        );
    }

    if (exponent == 0) {
        return 1;
    }

    // Divide the exponent by two to reduce recursion depth.
    long long half = powerRecursive(base, exponent / 2);

    if (exponent % 2 == 0) {
        return half * half;
    }

    return base * half * half;
}


// ============================================================================
// 4. EUCLID'S ALGORITHM
// ============================================================================

long long gcdRecursive(long long first, long long second) {
    first = llabs(first);
    second = llabs(second);

    // gcd(a, 0) = |a|
    if (second == 0) {
        return first;
    }

    return gcdRecursive(second, first % second);
}


// ============================================================================
// 5. SUM OF DIGITS
// ============================================================================

long long sumOfDigits(long long number) {
    number = llabs(number);

    // A single digit is the simplest possible case.
    if (number < 10) {
        return number;
    }

    return (number % 10) +
           sumOfDigits(number / 10);
}


// ============================================================================
// 6. FIBONACCI
// ============================================================================

long long fibonacciRecursive(int number) {
    if (number < 0) {
        throw invalid_argument(
            "Fibonacci requires a non-negative integer."
        );
    }

    if (number <= 1) {
        return number;
    }

    return fibonacciRecursive(number - 1) +
           fibonacciRecursive(number - 2);
}

long long fibonacciIterative(int number) {
    if (number < 0) {
        throw invalid_argument(
            "Fibonacci requires a non-negative integer."
        );
    }

    long long first = 0;
    long long second = 1;

    for (int index = 0; index < number; ++index) {
        long long next = first + second;
        first = second;
        second = next;
    }

    return first;
}


// ============================================================================
// 7. MEMOIZED FIBONACCI
// ============================================================================

long long fibonacciMemoized(
    int number,
    unordered_map<int, long long>& cache
) {
    if (number < 0) {
        throw invalid_argument(
            "Fibonacci requires a non-negative integer."
        );
    }

    if (number <= 1) {
        return number;
    }

    auto cached = cache.find(number);

    if (cached != cache.end()) {
        return cached->second;
    }

    long long result =
        fibonacciMemoized(number - 1, cache) +
        fibonacciMemoized(number - 2, cache);

    cache[number] = result;

    return result;
}


// ============================================================================
// 8. FILE-SYSTEM DATA MODEL
// ============================================================================

enum class NodeType {
    File,
    Directory
};

struct FileNode {
    string name;
    NodeType type;
    size_t sizeBytes;
    bool hidden;
    vector<unique_ptr<FileNode>> children;

    FileNode(
        string nodeName,
        NodeType nodeType,
        size_t nodeSizeBytes = 0,
        bool isHidden = false
    )
        : name(std::move(nodeName)),
          type(nodeType),
          sizeBytes(nodeSizeBytes),
          hidden(isHidden) {
    }

    bool isFile() const {
        return type == NodeType::File;
    }

    bool isDirectory() const {
        return type == NodeType::Directory;
    }

    void addChild(unique_ptr<FileNode> child) {
        if (!isDirectory()) {
            throw logic_error(
                "A file cannot contain child nodes."
            );
        }

        children.push_back(std::move(child));
    }
};


// ============================================================================
// 9. FILE-SYSTEM ANALYSIS FUNCTIONS
// ============================================================================

struct AnalysisResult {
    size_t fileCount = 0;
    size_t directoryCount = 0;
    size_t totalBytes = 0;
    size_t hiddenFileCount = 0;
    size_t maximumDepth = 0;
};


// Recursive traversal:
//
// The current node is processed first.
// If it is a directory, every child is recursively analyzed.
//
// Base case:
// A file has no children, so processing ends at that node.
//
// Recursive case:
// A directory delegates analysis to each child.
//
// Time complexity: O(N), where N is the number of nodes.
// Space complexity: O(H) call-stack usage, where H is tree height.
void analyzeTree(
    const FileNode& node,
    size_t currentDepth,
    AnalysisResult& result
) {
    result.maximumDepth =
        max(result.maximumDepth, currentDepth);

    if (node.isFile()) {
        ++result.fileCount;
        result.totalBytes += node.sizeBytes;

        if (node.hidden) {
            ++result.hiddenFileCount;
        }

        // Base case: files do not contain children.
        return;
    }

    ++result.directoryCount;

    // Recursive case: analyze every child.
    for (const auto& child : node.children) {
        analyzeTree(
            *child,
            currentDepth + 1,
            result
        );
    }
}


// ============================================================================
// 10. RECURSIVE TREE PRINTING
// ============================================================================

void printTree(
    const FileNode& node,
    size_t depth = 0
) {
    // Indentation makes the recursive hierarchy visible.
    cout << string(depth * 2, ' ')
         << (node.isDirectory() ? "[DIR] " : "[FILE] ")
         << node.name;

    if (node.isFile()) {
        cout << " (" << node.sizeBytes << " bytes)";

        if (node.hidden) {
            cout << " [hidden]";
        }
    }

    cout << '\n';

    // Base case:
    // A file has no children, so this loop executes zero times.
    for (const auto& child : node.children) {
        printTree(*child, depth + 1);
    }
}


// ============================================================================
// 11. RECURSIVE FILE SEARCH
// ============================================================================

void findFilesByExtension(
    const FileNode& node,
    const string& extension,
    vector<const FileNode*>& matches
) {
    if (node.isFile()) {
        if (
            node.name.size() >= extension.size() &&
            node.name.compare(
                node.name.size() - extension.size(),
                extension.size(),
                extension
            ) == 0
        ) {
            matches.push_back(&node);
        }

        return;
    }

    for (const auto& child : node.children) {
        findFilesByExtension(
            *child,
            extension,
            matches
        );
    }
}


// ============================================================================
// 12. RECURSIVE SEARCH BY NAME
// ============================================================================

const FileNode* findNodeByName(
    const FileNode& node,
    const string& targetName
) {
    if (node.name == targetName) {
        return &node;
    }

    if (node.isFile()) {
        return nullptr;
    }

    for (const auto& child : node.children) {
        const FileNode* result =
            findNodeByName(*child, targetName);

        if (result != nullptr) {
            return result;
        }
    }

    return nullptr;
}


// ============================================================================
// 13. RECURSIVE SIZE FILTER
// ============================================================================

void findLargeFiles(
    const FileNode& node,
    size_t minimumBytes,
    vector<const FileNode*>& matches
) {
    if (node.isFile()) {
        if (node.sizeBytes >= minimumBytes) {
            matches.push_back(&node);
        }

        return;
    }

    for (const auto& child : node.children) {
        findLargeFiles(
            *child,
            minimumBytes,
            matches
        );
    }
}


// ============================================================================
// 14. RECURSIVE DIRECTORY SIZE
// ============================================================================

size_t calculateDirectorySize(
    const FileNode& node
) {
    if (node.isFile()) {
        return node.sizeBytes;
    }

    size_t total = 0;

    for (const auto& child : node.children) {
        total += calculateDirectorySize(*child);
    }

    return total;
}


// ============================================================================
// 15. BUILD A REALISTIC SAMPLE FILE SYSTEM
// ============================================================================

unique_ptr<FileNode> buildSampleFileSystem() {
    auto root = make_unique<FileNode>(
        "project",
        NodeType::Directory
    );

    auto source = make_unique<FileNode>(
        "src",
        NodeType::Directory
    );

    source->addChild(
        make_unique<FileNode>(
            "main.cpp",
            NodeType::File,
            8500
        )
    );

    source->addChild(
        make_unique<FileNode>(
            "calculator.cpp",
            NodeType::File,
            12500
        )
    );

    source->addChild(
        make_unique<FileNode>(
            "calculator.h",
            NodeType::File,
            4200
        )
    );

    auto tests = make_unique<FileNode>(
        "tests",
        NodeType::Directory
    );

    tests->addChild(
        make_unique<FileNode>(
            "test_calculator.cpp",
            NodeType::File,
            7200
        )
    );

    tests->addChild(
        make_unique<FileNode>(
            "test_data.cpp",
            NodeType::File,
            6400
        )
    );

    auto docs = make_unique<FileNode>(
        "docs",
        NodeType::Directory
    );

    docs->addChild(
        make_unique<FileNode>(
            "README.md",
            NodeType::File,
            5500
        )
    );

    docs->addChild(
        make_unique<FileNode>(
            "architecture.md",
            NodeType::File,
            15000
        )
    );

    auto configuration = make_unique<FileNode>(
        ".config",
        NodeType::Directory
    );

    configuration->addChild(
        make_unique<FileNode>(
            ".env",
            NodeType::File,
            300,
            true
        )
    );

    auto assets = make_unique<FileNode>(
        "assets",
        NodeType::Directory
    );

    assets->addChild(
        make_unique<FileNode>(
            "logo.png",
            NodeType::File,
            55000
        )
    );

    assets->addChild(
        make_unique<FileNode>(
            "diagram.png",
            NodeType::File,
            125000
        )
    );

    root->addChild(std::move(source));
    root->addChild(std::move(tests));
    root->addChild(std::move(docs));
    root->addChild(std::move(configuration));
    root->addChild(std::move(assets));

    root->addChild(
        make_unique<FileNode>(
            "LICENSE",
            NodeType::File,
            1800
        )
    );

    return root;
}


// ============================================================================
// 16. VALIDATION FUNCTIONS
// ============================================================================

bool isValidExtension(const string& extension) {
    return !extension.empty() &&
           extension.front() == '.' &&
           extension.size() > 1;
}

size_t parsePositiveSize(const string& text) {
    if (text.empty()) {
        throw invalid_argument(
            "Size input cannot be empty."
        );
    }

    size_t position = 0;
    unsigned long long value =
        stoull(text, &position);

    if (position != text.size()) {
        throw invalid_argument(
            "Size input contains invalid characters."
        );
    }

    if (value == 0) {
        throw invalid_argument(
            "Size must be greater than zero."
        );
    }

    if (value >
        static_cast<unsigned long long>(
            numeric_limits<size_t>::max()
        )) {
        throw out_of_range(
            "Size is too large for this platform."
        );
    }

    return static_cast<size_t>(value);
}


// ============================================================================
// 17. FORMAT HELPERS
// ============================================================================

string formatBytes(size_t bytes) {
    const double value = static_cast<double>(bytes);

    if (bytes < 1024) {
        return to_string(bytes) + " B";
    }

    if (bytes < 1024 * 1024) {
        ostringstream output;
        output << fixed << setprecision(2)
               << value / 1024.0 << " KB";
        return output.str();
    }

    ostringstream output;
    output << fixed << setprecision(2)
           << value / (1024.0 * 1024.0) << " MB";

    return output.str();
}


// ============================================================================
// 18. RUN ANALYSIS
// ============================================================================

void runFileSystemCaseStudy() {
    cout << "\n========================================\n";
    cout << "RECURSIVE FILE-SYSTEM ANALYSIS ENGINE\n";
    cout << "========================================\n\n";

    auto root = buildSampleFileSystem();

    cout << "File-system structure:\n\n";
    printTree(*root);

    AnalysisResult result;

    analyzeTree(
        *root,
        0,
        result
    );

    cout << "\nAnalysis:\n";
    cout << "Files: "
         << result.fileCount << '\n';

    cout << "Directories: "
         << result.directoryCount << '\n';

    cout << "Total file storage: "
         << formatBytes(result.totalBytes) << '\n';

    cout << "Hidden files: "
         << result.hiddenFileCount << '\n';

    cout << "Maximum depth: "
         << result.maximumDepth << '\n';

    cout << "Calculated root size: "
         << formatBytes(
                calculateDirectorySize(*root)
            )
         << '\n';

    cout << "\nC++ files:\n";

    vector<const FileNode*> cppFiles;

    findFilesByExtension(
        *root,
        ".cpp",
        cppFiles
    );

    for (const FileNode* file : cppFiles) {
        cout << "  " << file->name
             << " -> "
             << formatBytes(file->sizeBytes)
             << '\n';
    }

    cout << "\nFiles >= 10 KB:\n";

    vector<const FileNode*> largeFiles;

    findLargeFiles(
        *root,
        10 * 1024,
        largeFiles
    );

    for (const FileNode* file : largeFiles) {
        cout << "  " << file->name
             << " -> "
             << formatBytes(file->sizeBytes)
             << '\n';
    }

    cout << "\nSearching for architecture.md:\n";

    const FileNode* found =
        findNodeByName(
            *root,
            "architecture.md"
        );

    if (found != nullptr) {
        cout << "  Found: "
             << found->name
             << " (" << formatBytes(found->sizeBytes)
             << ")\n";
    } else {
        cout << "  Not found.\n";
    }
}


// ============================================================================
// 19. BASIC ALGORITHM TESTS
// ============================================================================

void runTests() {
    cout << "\n========================================\n";
    cout << "TESTS\n";
    cout << "========================================\n";

    assert(add(2, 3) == 5);
    assert(multiply(4, 5) == 20);

    assert(factorialRecursive(0) == 1);
    assert(factorialRecursive(5) == 120);

    assert(factorialIterative(5) == 120);

    assert(powerRecursive(2, 10) == 1024);

    assert(gcdRecursive(48, 18) == 6);
    assert(gcdRecursive(0, 15) == 15);

    assert(sumOfDigits(12345) == 15);

    assert(fibonacciRecursive(10) == 55);
    assert(fibonacciIterative(10) == 55);

    unordered_map<int, long long> cache;

    assert(
        fibonacciMemoized(10, cache) == 55
    );

    auto root = buildSampleFileSystem();

    AnalysisResult result;

    analyzeTree(
        *root,
        0,
        result
    );

    assert(result.fileCount == 10);
    assert(result.directoryCount == 6);
    assert(result.hiddenFileCount == 1);

    assert(
        calculateDirectorySize(*root) ==
        result.totalBytes
    );

    vector<const FileNode*> cppFiles;

    findFilesByExtension(
        *root,
        ".cpp",
        cppFiles
    );

    assert(cppFiles.size() == 4);

    vector<const FileNode*> largeFiles;

    findLargeFiles(
        *root,
        10 * 1024,
        largeFiles
    );

    assert(largeFiles.size() == 5);

    assert(
        findNodeByName(*root, "README.md") != nullptr
    );

    assert(
        findNodeByName(*root, "missing.txt") == nullptr
    );

    cout << "All tests passed.\n";
}


// ============================================================================
// 20. EDGE-CASE DEMONSTRATION
// ============================================================================

void demonstrateEdgeCases() {
    cout << "\n========================================\n";
    cout << "EDGE CASES\n";
    cout << "========================================\n";

    try {
        factorialRecursive(-1);
    } catch (const exception& error) {
        cout << "Negative factorial: "
             << error.what() << '\n';
    }

    try {
        divide(10.0, 0.0);
    } catch (const exception& error) {
        cout << "Division by zero: "
             << error.what() << '\n';
    }

    try {
        parsePositiveSize("abc");
    } catch (const exception& error) {
        cout << "Invalid size: "
             << error.what() << '\n';
    }

    try {
        FileNode file(
            "example.txt",
            NodeType::File,
            100
        );

        file.addChild(
            make_unique<FileNode>(
                "invalid.txt",
                NodeType::File,
                20
            )
        );
    } catch (const exception& error) {
        cout << "Invalid tree operation: "
             << error.what() << '\n';
    }
}


// ============================================================================
// 21. MAIN
// ============================================================================

int main() {
    cout << "========================================\n";
    cout << "DAY 5 — FUNCTIONS AND RECURSION BASICS\n";
    cout << "========================================\n";

    cout << "\nBasic functions:\n";
    cout << "2 + 3 = " << add(2, 3) << '\n';
    cout << "4 × 5 = " << multiply(4, 5) << '\n';
    cout << "20 / 4 = " << divide(20, 4) << '\n';

    cout << "\nFactorial:\n";

    for (int number = 0; number <= 6; ++number) {
        cout << number << "! = "
             << factorialRecursive(number)
             << '\n';
    }

    cout << "\nPower:\n";
    cout << "2^10 = "
         << powerRecursive(2, 10)
         << '\n';

    cout << "\nGCD:\n";
    cout << "gcd(48, 18) = "
         << gcdRecursive(48, 18)
         << '\n';

    cout << "\nSum of digits:\n";
    cout << "sumOfDigits(9876) = "
         << sumOfDigits(9876)
         << '\n';

    cout << "\nFibonacci comparison:\n";

    for (int number = 0; number <= 10; ++number) {
        cout << "F(" << number << ") = "
             << fibonacciIterative(number)
             << '\n';
    }

    unordered_map<int, long long> cache;

    cout << "\nMemoized F(40) = "
         << fibonacciMemoized(40, cache)
         << '\n';

    runFileSystemCaseStudy();
    runTests();
    demonstrateEdgeCases();

    cout << "\n========================================\n";
    cout << "DAY 5 CASE STUDY COMPLETED\n";
    cout << "========================================\n";

    return 0;
}
