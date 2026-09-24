/*
    Day 13 — Array Insertion and Deletion

    Technical case study:
    An inventory reservation system backed by a contiguous dynamic array.

    The program demonstrates:
    - insertion at beginning
    - insertion at end
    - insertion at a position
    - deletion from beginning
    - deletion from end
    - deletion by index
    - deletion by value
    - stable deletion
    - unordered deletion
    - element shifting
    - dynamic-array capacity
    - validation and exceptions
    - duplicate values
    - realistic domain modeling
    - complexity considerations
    - performance measurement

    Compile:
        g++ -std=c++17 -O2 -Wall -Wextra -pedantic day13.cpp -o day13

    Run:
        ./day13
*/

#include <algorithm>
#include <chrono>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// ---------------------------------------------------------------------------
// PRODUCT MODEL
// ---------------------------------------------------------------------------

struct Product {
    int id{};
    std::string name;
    int quantity{};
    double price{};

    Product() = default;

    Product(int productId, std::string productName, int productQuantity, double productPrice)
        : id(productId),
          name(std::move(productName)),
          quantity(productQuantity),
          price(productPrice) {
        if (productId <= 0) {
            throw std::invalid_argument("Product ID must be positive.");
        }

        if (productQuantity < 0) {
            throw std::invalid_argument("Quantity cannot be negative.");
        }

        if (productPrice < 0.0) {
            throw std::invalid_argument("Price cannot be negative.");
        }
    }
};

std::ostream& operator<<(std::ostream& output, const Product& product) {
    output << "ID=" << product.id
           << ", Name=" << product.name
           << ", Quantity=" << product.quantity
           << ", Price=" << std::fixed << std::setprecision(2)
           << product.price;

    return output;
}

// ---------------------------------------------------------------------------
// EDUCATIONAL DYNAMIC ARRAY
// ---------------------------------------------------------------------------

template <typename T>
class DynamicArray {
private:
    T* data_;
    std::size_t size_;
    std::size_t capacity_;

    void resize(std::size_t newCapacity) {
        if (newCapacity < size_) {
            throw std::invalid_argument(
                "New capacity cannot be smaller than current size."
            );
        }

        T* newData = new T[newCapacity];

        for (std::size_t index = 0; index < size_; ++index) {
            newData[index] = data_[index];
        }

        delete[] data_;
        data_ = newData;
        capacity_ = newCapacity;
    }

    void ensureCapacity() {
        if (size_ == capacity_) {
            const std::size_t newCapacity =
                capacity_ == 0 ? 1 : capacity_ * 2;

            resize(newCapacity);
        }
    }

    void validateInsertionIndex(std::size_t index) const {
        if (index > size_) {
            throw std::out_of_range("Insertion index is outside the array.");
        }
    }

    void validateElementIndex(std::size_t index) const {
        if (index >= size_) {
            throw std::out_of_range("Element index is outside the array.");
        }
    }

public:
    explicit DynamicArray(std::size_t initialCapacity = 4)
        : data_(new T[initialCapacity]),
          size_(0),
          capacity_(initialCapacity) {
        if (initialCapacity == 0) {
            delete[] data_;
            data_ = nullptr;
            capacity_ = 0;
        }
    }

    ~DynamicArray() {
        delete[] data_;
    }

    DynamicArray(const DynamicArray& other)
        : data_(new T[other.capacity_]),
          size_(other.size_),
          capacity_(other.capacity_) {
        for (std::size_t index = 0; index < size_; ++index) {
            data_[index] = other.data_[index];
        }
    }

    DynamicArray& operator=(const DynamicArray& other) {
        if (this == &other) {
            return *this;
        }

        DynamicArray temporary(other);
        swap(temporary);

        return *this;
    }

    DynamicArray(DynamicArray&& other) noexcept
        : data_(other.data_),
          size_(other.size_),
          capacity_(other.capacity_) {
        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;
    }

    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this == &other) {
            return *this;
        }

        delete[] data_;

        data_ = other.data_;
        size_ = other.size_;
        capacity_ = other.capacity_;

        other.data_ = nullptr;
        other.size_ = 0;
        other.capacity_ = 0;

        return *this;
    }

    void swap(DynamicArray& other) noexcept {
        std::swap(data_, other.data_);
        std::swap(size_, other.size_);
        std::swap(capacity_, other.capacity_);
    }

    std::size_t size() const {
        return size_;
    }

    std::size_t capacity() const {
        return capacity_;
    }

    bool empty() const {
        return size_ == 0;
    }

    T& operator[](std::size_t index) {
        validateElementIndex(index);
        return data_[index];
    }

    const T& operator[](std::size_t index) const {
        validateElementIndex(index);
        return data_[index];
    }

    // O(1) amortized append.
    void pushBack(const T& value) {
        ensureCapacity();

        data_[size_] = value;
        ++size_;
    }

    // O(n) worst case because elements at and after index shift right.
    void insert(std::size_t index, const T& value) {
        validateInsertionIndex(index);
        ensureCapacity();

        for (std::size_t current = size_; current > index; --current) {
            data_[current] = std::move(data_[current - 1]);
        }

        data_[index] = value;
        ++size_;
    }

    // O(n) worst case, O(1) when removing the final element.
    T popBack() {
        if (empty()) {
            throw std::out_of_range("Cannot remove from an empty array.");
        }

        --size_;
        return std::move(data_[size_]);
    }

    // Stable deletion: preserve relative order.
    T erase(std::size_t index) {
        validateElementIndex(index);

        T removed = std::move(data_[index]);

        for (std::size_t current = index + 1; current < size_; ++current) {
            data_[current - 1] = std::move(data_[current]);
        }

        --size_;

        return removed;
    }

    // O(1) deletion when order is irrelevant.
    T eraseUnordered(std::size_t index) {
        validateElementIndex(index);

        T removed = std::move(data_[index]);

        if (index != size_ - 1) {
            data_[index] = std::move(data_[size_ - 1]);
        }

        --size_;
        return removed;
    }

    // Linear search followed by stable deletion.
    bool eraseFirstById(int productId) {
        for (std::size_t index = 0; index < size_; ++index) {
            if (data_[index].id == productId) {
                erase(index);
                return true;
            }
        }

        return false;
    }

    // Delete every matching item while preserving order.
    std::size_t eraseAllById(int productId) {
        std::size_t writeIndex = 0;
        std::size_t removedCount = 0;

        for (std::size_t readIndex = 0; readIndex < size_; ++readIndex) {
            if (data_[readIndex].id == productId) {
                ++removedCount;
            } else {
                if (writeIndex != readIndex) {
                    data_[writeIndex] = std::move(data_[readIndex]);
                }

                ++writeIndex;
            }
        }

        size_ = writeIndex;
        return removedCount;
    }

    void print(const std::string& label) const {
        std::cout << label
                  << " | size=" << size_
                  << ", capacity=" << capacity_
                  << '\n';

        for (std::size_t index = 0; index < size_; ++index) {
            std::cout << "  [" << index << "] " << data_[index] << '\n';
        }

        if (empty()) {
            std::cout << "  <empty>\n";
        }
    }
};

// ---------------------------------------------------------------------------
// INVENTORY RESERVATION SYSTEM
// ---------------------------------------------------------------------------

class InventorySystem {
private:
    DynamicArray<Product> products_;

    static void validateProduct(const Product& product) {
        if (product.quantity <= 0) {
            throw std::invalid_argument(
                "A product must have positive available quantity."
            );
        }
    }

public:
    void addProductAtEnd(const Product& product) {
        validateProduct(product);
        products_.pushBack(product);
    }

    void addPriorityProduct(std::size_t index, const Product& product) {
        validateProduct(product);
        products_.insert(index, product);
    }

    Product removeFirstProduct() {
        if (products_.empty()) {
            throw std::out_of_range("Inventory is empty.");
        }

        return products_.erase(0);
    }

    Product removeLastProduct() {
        return products_.popBack();
    }

    Product removeProductByIndex(std::size_t index) {
        return products_.erase(index);
    }

    bool removeProductById(int productId) {
        return products_.eraseFirstById(productId);
    }

    std::size_t removeAllProductsById(int productId) {
        return products_.eraseAllById(productId);
    }

    void removeWithoutPreservingOrder(std::size_t index) {
        products_.eraseUnordered(index);
    }

    void print() const {
        products_.print("Inventory");
    }

    std::size_t size() const {
        return products_.size();
    }
};

// ---------------------------------------------------------------------------
// SHIFT-COST CALCULATIONS
// ---------------------------------------------------------------------------

std::size_t insertionShiftCount(
    std::size_t size,
    std::size_t index
) {
    if (index > size) {
        throw std::out_of_range("Invalid insertion index.");
    }

    return size - index;
}

std::size_t deletionShiftCount(
    std::size_t size,
    std::size_t index
) {
    if (index >= size) {
        throw std::out_of_range("Invalid deletion index.");
    }

    return size - index - 1;
}

void demonstrateShiftCosts(std::size_t size) {
    std::cout << "\nShift-cost analysis for size " << size << '\n';
    std::cout << "Index | Insert shifts | Delete shifts\n";
    std::cout << "---------------------------------------\n";

    for (std::size_t index = 0; index < size; ++index) {
        std::cout
            << std::setw(5) << index << " | "
            << std::setw(13) << insertionShiftCount(size, index) << " | "
            << std::setw(13) << deletionShiftCount(size, index)
            << '\n';
    }

    std::cout
        << std::setw(5) << size << " | "
        << std::setw(13) << 0 << " | "
        << std::setw(13) << "N/A"
        << "  <- insertion at end\n";
}

// ---------------------------------------------------------------------------
// ARRAY-BACKED QUEUE
// ---------------------------------------------------------------------------

class NaiveQueue {
private:
    DynamicArray<int> data_;

public:
    void enqueue(int value) {
        data_.pushBack(value);
    }

    int dequeue() {
        if (data_.empty()) {
            throw std::out_of_range("Queue is empty.");
        }

        // Removing index 0 requires shifting every remaining element.
        return data_.erase(0);
    }

    bool empty() const {
        return data_.empty();
    }
};

class CircularQueue {
private:
    std::vector<int> data_;
    std::size_t front_{0};
    std::size_t size_{0};

public:
    explicit CircularQueue(std::size_t capacity)
        : data_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument(
                "Circular queue capacity must be positive."
            );
        }
    }

    bool empty() const {
        return size_ == 0;
    }

    bool full() const {
        return size_ == data_.size();
    }

    void enqueue(int value) {
        if (full()) {
            throw std::overflow_error("Circular queue is full.");
        }

        const std::size_t position =
            (front_ + size_) % data_.size();

        data_[position] = value;
        ++size_;
    }

    int dequeue() {
        if (empty()) {
            throw std::out_of_range("Circular queue is empty.");
        }

        const int value = data_[front_];

        front_ = (front_ + 1) % data_.size();
        --size_;

        return value;
    }
};

// ---------------------------------------------------------------------------
// PERFORMANCE BENCHMARK
// ---------------------------------------------------------------------------

template <typename Operation>
double benchmark(Operation operation, int repetitions) {
    const auto start = std::chrono::high_resolution_clock::now();

    for (int iteration = 0; iteration < repetitions; ++iteration) {
        operation();
    }

    const auto end = std::chrono::high_resolution_clock::now();

    const std::chrono::duration<double, std::milli> elapsed = end - start;
    return elapsed.count();
}

void runBenchmark() {
    constexpr std::size_t size = 10000;
    constexpr int repetitions = 50;

    const double beginningInsertion = benchmark(
        [] {
            DynamicArray<int> values(size);
            for (std::size_t index = 0; index < size; ++index) {
                values.pushBack(static_cast<int>(index));
            }

            values.insert(0, -1);
        },
        repetitions
    );

    const double endingInsertion = benchmark(
        [] {
            DynamicArray<int> values(size);
            for (std::size_t index = 0; index < size; ++index) {
                values.pushBack(static_cast<int>(index));
            }

            values.pushBack(-1);
        },
        repetitions
    );

    std::cout << "\nPerformance experiment\n";
    std::cout << "Beginning insertion: "
              << beginningInsertion << " ms\n";
    std::cout << "End insertion:       "
              << endingInsertion << " ms\n";
    std::cout
        << "Measurements depend on compiler, optimization level, hardware, "
           "and system load.\n";
}

// ---------------------------------------------------------------------------
// TESTS
// ---------------------------------------------------------------------------

void runTests() {
    DynamicArray<int> values;

    values.pushBack(10);
    values.pushBack(20);
    values.pushBack(30);

    values.insert(0, 5);

    if (values[0] != 5) {
        throw std::runtime_error("Beginning insertion test failed.");
    }

    values.insert(2, 15);

    if (values[2] != 15) {
        throw std::runtime_error("Position insertion test failed.");
    }

    values.pushBack(40);

    if (values[values.size() - 1] != 40) {
        throw std::runtime_error("End insertion test failed.");
    }

    if (values.erase(0) != 5) {
        throw std::runtime_error("Beginning deletion test failed.");
    }

    if (values.popBack() != 40) {
        throw std::runtime_error("End deletion test failed.");
    }

    if (values.erase(1) != 15) {
        throw std::runtime_error("Index deletion test failed.");
    }

    DynamicArray<Product> products;

    products.pushBack(Product(1, "Keyboard", 10, 50.0));
    products.pushBack(Product(2, "Mouse", 20, 25.0));
    products.pushBack(Product(3, "Monitor", 5, 200.0));

    products.insert(
        1,
        Product(4, "Webcam", 7, 75.0)
    );

    if (products[1].id != 4) {
        throw std::runtime_error("Product insertion failed.");
    }

    if (!products.eraseFirstById(4)) {
        throw std::runtime_error("Product deletion by ID failed.");
    }

    if (products.size() != 3) {
        throw std::runtime_error("Unexpected product count.");
    }

    CircularQueue queue(3);
    queue.enqueue(10);
    queue.enqueue(20);

    if (queue.dequeue() != 10) {
        throw std::runtime_error("Circular queue dequeue failed.");
    }

    queue.enqueue(30);
    queue.enqueue(40);

    if (queue.dequeue() != 20 ||
        queue.dequeue() != 30 ||
        queue.dequeue() != 40) {
        throw std::runtime_error("Circular queue wrap-around failed.");
    }

    bool caughtException = false;

    try {
        values.erase(100);
    } catch (const std::out_of_range&) {
        caughtException = true;
    }

    if (!caughtException) {
        throw std::runtime_error(
            "Bounds validation test failed."
        );
    }

    std::cout << "\nAll tests passed.\n";
}

// ---------------------------------------------------------------------------
// MAIN CASE STUDY
// ---------------------------------------------------------------------------

int main() {
    try {
        std::cout
            << "DAY 13 — ARRAY INSERTION AND DELETION\n"
            << "Industry-style case study: Inventory Reservation System\n";

        // -------------------------------------------------------------------
        // Stage 1: basic dynamic-array behavior
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 1: Dynamic array basics ---\n";

        DynamicArray<int> numbers(2);

        numbers.pushBack(10);
        numbers.pushBack(20);
        numbers.pushBack(30);

        numbers.print("After appending three values");

        // Insert in the middle.
        numbers.insert(1, 15);
        numbers.print("After inserting 15 at index 1");

        // Delete from the middle.
        numbers.erase(2);
        numbers.print("After deleting index 2");

        // -------------------------------------------------------------------
        // Stage 2: inventory model
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 2: Inventory system ---\n";

        InventorySystem inventory;

        inventory.addProductAtEnd(
            Product(101, "Keyboard", 15, 49.99)
        );

        inventory.addProductAtEnd(
            Product(102, "Mouse", 30, 24.99)
        );

        inventory.addProductAtEnd(
            Product(103, "Monitor", 8, 199.99)
        );

        inventory.print();

        // A high-priority product is inserted near the beginning.
        inventory.addPriorityProduct(
            1,
            Product(104, "Webcam", 12, 79.99)
        );

        inventory.print();

        // Delete by ID.
        if (inventory.removeProductById(102)) {
            std::cout << "\nProduct 102 was removed.\n";
        }

        inventory.print();

        // Delete the first product.
        const Product first = inventory.removeFirstProduct();
        std::cout << "\nRemoved first product: " << first << '\n';

        inventory.print();

        // Add a duplicate ID deliberately to demonstrate delete-all behavior.
        inventory.addProductAtEnd(
            Product(105, "USB Hub", 20, 29.99)
        );

        inventory.addProductAtEnd(
            Product(105, "USB Hub Replacement", 10, 34.99)
        );

        inventory.print();

        const std::size_t removedDuplicates =
            inventory.removeAllProductsById(105);

        std::cout
            << "\nRemoved " << removedDuplicates
            << " products with ID 105.\n";

        inventory.print();

        // -------------------------------------------------------------------
        // Stage 3: stable versus unordered deletion
        // -------------------------------------------------------------------

        std::cout
            << "\n--- Stage 3: Stable versus unordered deletion ---\n";

        DynamicArray<int> stableValues;

        for (int value : {10, 20, 30, 40, 50}) {
            stableValues.pushBack(value);
        }

        stableValues.erase(1);
        stableValues.print("Stable deletion");

        DynamicArray<int> unorderedValues;

        for (int value : {10, 20, 30, 40, 50}) {
            unorderedValues.pushBack(value);
        }

        unorderedValues.eraseUnordered(1);
        unorderedValues.print("Unordered deletion");

        // -------------------------------------------------------------------
        // Stage 4: shift-cost analysis
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 4: Shift cost ---\n";
        demonstrateShiftCosts(8);

        // -------------------------------------------------------------------
        // Stage 5: queue design
        // -------------------------------------------------------------------

        std::cout
            << "\n--- Stage 5: Queue and the cost of front deletion ---\n";

        NaiveQueue naiveQueue;

        naiveQueue.enqueue(100);
        naiveQueue.enqueue(200);
        naiveQueue.enqueue(300);

        std::cout
            << "Naive queue first dequeue: "
            << naiveQueue.dequeue()
            << '\n';

        std::cout
            << "The naive queue shifts remaining elements after each dequeue.\n";

        CircularQueue efficientQueue(4);

        efficientQueue.enqueue(100);
        efficientQueue.enqueue(200);
        efficientQueue.enqueue(300);

        std::cout
            << "Circular queue first dequeue: "
            << efficientQueue.dequeue()
            << '\n';

        efficientQueue.enqueue(400);
        efficientQueue.enqueue(500);

        std::cout
            << "Circular buffering reuses released positions without "
               "shifting every element.\n";

        // -------------------------------------------------------------------
        // Stage 6: validation and failure conditions
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 6: Error handling ---\n";

        try {
            DynamicArray<int> empty;
            empty.popBack();
        } catch (const std::out_of_range& error) {
            std::cout
                << "Handled empty-array deletion: "
                << error.what()
                << '\n';
        }

        try {
            DynamicArray<int> values;
            values.pushBack(1);
            values.insert(5, 10);
        } catch (const std::out_of_range& error) {
            std::cout
                << "Handled invalid insertion index: "
                << error.what()
                << '\n';
        }

        try {
            Product invalidProduct(999, "Invalid", -5, 10.0);
            (void)invalidProduct;
        } catch (const std::invalid_argument& error) {
            std::cout
                << "Handled invalid product: "
                << error.what()
                << '\n';
        }

        // -------------------------------------------------------------------
        // Stage 7: tests
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 7: Automated tests ---\n";
        runTests();

        // -------------------------------------------------------------------
        // Stage 8: performance
        // -------------------------------------------------------------------

        std::cout << "\n--- Stage 8: Performance experiment ---\n";
        runBenchmark();

        // -------------------------------------------------------------------
        // Complexity reference
        // -------------------------------------------------------------------

        std::cout << R"(
Complexity reference
---------------------------------------------------------------
Operation                         Typical complexity
---------------------------------------------------------------
Access by index                  O(1)
Search by value                 O(n)
Insert at beginning             O(n)
Insert in middle                O(n)
Insert at end                   O(1) amortized
Delete from beginning           O(n)
Delete from middle              O(n)
Delete from end                 O(1)
Delete by index                 O(n) worst case
Delete by value                 O(n)
Unordered deletion by index     O(1)
Dynamic-array resize            O(n)
---------------------------------------------------------------

The key cost comes from preserving order.

For insertion at index i in an array of size n:
    shifted elements = n - i

For deletion at index i:
    shifted elements = n - i - 1

Insertion and deletion are therefore not inherently expensive at every
position. The cost depends on how many elements must move.
)";

        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "\nFatal error: "
            << error.what()
            << '\n';

        return 1;
    }
}
