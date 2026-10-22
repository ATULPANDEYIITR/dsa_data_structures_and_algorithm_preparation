#include <algorithm>
#include <cstdint>
#include <functional>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

class RecursionLab {
public:
    static std::uint64_t factorial(unsigned int n) {
        if (n > 20) {
            throw std::invalid_argument("Factorial exceeds uint64_t range");
        }
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }

    static std::uint64_t fibonacci(unsigned int n) {
        if (n > 93) {
            throw std::invalid_argument("Fibonacci exceeds uint64_t range");
        }
        std::unordered_map<unsigned int, std::uint64_t> memo;
        return fibonacciMemo(n, memo);
    }

    static std::uint64_t power(std::uint64_t base, unsigned int exponent) {
        if (exponent == 0) return 1;
        const std::uint64_t half = power(base, exponent / 2);
        if (half != 0 &&
            half > std::numeric_limits<std::uint64_t>::max() / half) {
            throw std::overflow_error("Power result overflows uint64_t");
        }
        const std::uint64_t squared = half * half;
        if (exponent % 2 == 0) return squared;
        if (base != 0 &&
            squared > std::numeric_limits<std::uint64_t>::max() / base) {
            throw std::overflow_error("Power result overflows uint64_t");
        }
        return base * squared;
    }

    static std::int64_t sumTo(unsigned int n) {
        if (n > 100000) {
            throw std::invalid_argument("Input exceeds the recursive sum limit");
        }
        if (n == 0) return 0;
        return static_cast<std::int64_t>(n) + sumTo(n - 1);
    }

    static std::string reverseString(const std::string& value) {
        return reverseStringAt(value, 0);
    }

    static std::vector<int> reverseArray(std::vector<int> values) {
        reverseRange(values, 0, values.empty() ? 0 : values.size() - 1);
        return values;
    }

    static std::int64_t sumArray(const std::vector<int>& values,
                                 std::size_t index = 0) {
        if (index > values.size()) {
            throw std::out_of_range("Array index is outside the sequence");
        }
        if (index == values.size()) return 0;
        return static_cast<std::int64_t>(values[index]) +
               sumArray(values, index + 1);
    }

    static int binarySearch(const std::vector<int>& values, int target) {
        if (!std::is_sorted(values.begin(), values.end())) {
            throw std::invalid_argument("Binary search requires sorted input");
        }
        return binarySearchRange(values, target, 0,
                                 static_cast<int>(values.size()) - 1);
    }

    static void printCallStack(unsigned int n, unsigned int depth = 0) {
        std::cout << std::string(depth * 2, ' ')
                  << "factorial(" << n << ")\n";
        if (n > 1) printCallStack(n - 1, depth + 1);
        std::cout << std::string(depth * 2, ' ')
                  << "return from factorial(" << n << ")\n";
    }

private:
    static std::uint64_t fibonacciMemo(
        unsigned int n,
        std::unordered_map<unsigned int, std::uint64_t>& memo) {
        if (n <= 1) return n;
        const auto found = memo.find(n);
        if (found != memo.end()) return found->second;
        const std::uint64_t result =
            fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
        memo.emplace(n, result);
        return result;
    }

    static std::string reverseStringAt(const std::string& value,
                                       std::size_t index) {
        if (index == value.size()) return "";
        return reverseStringAt(value, index + 1) + value[index];
    }

    static void reverseRange(std::vector<int>& values,
                             std::size_t left, std::size_t right) {
        if (values.empty() || left >= right) return;
        std::swap(values[left], values[right]);
        reverseRange(values, left + 1, right - 1);
    }

    static int binarySearchRange(const std::vector<int>& values,
                                 int target, int left, int right) {
        if (left > right) return -1;
        const int middle = left + (right - left) / 2;
        if (values[middle] == target) return middle;
        if (target < values[middle]) {
            return binarySearchRange(values, target, left, middle - 1);
        }
        return binarySearchRange(values, target, middle + 1, right);
    }
};

void runTests() {
    if (RecursionLab::factorial(0) != 1 ||
        RecursionLab::factorial(5) != 120) {
        throw std::runtime_error("Factorial test failed");
    }
    if (RecursionLab::fibonacci(10) != 55) {
        throw std::runtime_error("Fibonacci test failed");
    }
    if (RecursionLab::power(2, 10) != 1024 ||
        RecursionLab::power(9, 0) != 1) {
        throw std::runtime_error("Power test failed");
    }
    if (RecursionLab::sumTo(10) != 55) {
        throw std::runtime_error("Sum test failed");
    }
    if (RecursionLab::reverseString("stack") != "kcats") {
        throw std::runtime_error("String reversal test failed");
    }
    if (RecursionLab::reverseArray({1, 2, 3}) !=
        std::vector<int>({3, 2, 1})) {
        throw std::runtime_error("Array reversal test failed");
    }
    if (RecursionLab::sumArray({2, 4, 6}) != 12 ||
        RecursionLab::sumArray({}) != 0) {
        throw std::runtime_error("Array sum test failed");
    }
    if (RecursionLab::binarySearch({1, 3, 5, 7}, 5) != 2 ||
        RecursionLab::binarySearch({}, 5) != -1) {
        throw std::runtime_error("Binary search test failed");
    }
    bool rejected = false;
    try {
        RecursionLab::factorial(21);
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    if (!rejected) throw std::runtime_error("Factorial limit test failed");

    rejected = false;
    try {
        RecursionLab::power(2, 64);
    } catch (const std::overflow_error&) {
        rejected = true;
    }
    if (!rejected) throw std::runtime_error("Power overflow test failed");

    std::cout << "All C++ recursion tests passed.\n";
}

int main() {
    try {
        runTests();

        std::cout << "factorial(5): " << RecursionLab::factorial(5) << '\n';
        std::cout << "fibonacci(10): " << RecursionLab::fibonacci(10) << '\n';
        std::cout << "power(2, 10): " << RecursionLab::power(2, 10) << '\n';
        std::cout << "sumTo(10): " << RecursionLab::sumTo(10) << '\n';
        std::cout << "reverseString(\"recursion\"): "
                  << RecursionLab::reverseString("recursion") << '\n';

        const std::vector<int> values{7, 2, 9, 4, 1};
        const auto reversed = RecursionLab::reverseArray(values);
        std::cout << "Reversed array: ";
        for (int value : reversed) std::cout << value << ' ';
        std::cout << "\nArray sum: " << RecursionLab::sumArray(values) << '\n';

        std::cout << "Binary search for 5: "
                  << RecursionLab::binarySearch({1, 3, 5, 7}, 5) << '\n';
        std::cout << "Call stack for factorial(4):\n";
        RecursionLab::printCallStack(4);
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
