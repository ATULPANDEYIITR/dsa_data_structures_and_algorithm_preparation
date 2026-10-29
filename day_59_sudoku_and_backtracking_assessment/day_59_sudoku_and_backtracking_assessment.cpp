#include <algorithm>
#include <array>
#include <chrono>
#include <exception>
#include <iostream>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

class SudokuError : public std::runtime_error {
public:
    explicit SudokuError(const std::string& message)
        : std::runtime_error(message) {}
};

class Sudoku {
public:
    using Grid = std::array<std::array<int, 9>, 9>;

    struct Statistics {
        std::size_t decisions{0};
        std::size_t backtracks{0};
        double elapsedMs{0.0};
    };

private:
    Grid grid_;
    std::array<std::set<int>, 9> rows_;
    std::array<std::set<int>, 9> columns_;
    std::array<std::set<int>, 9> boxes_;
    Statistics statistics_;

    static int boxIndex(int row, int column) {
        return (row / 3) * 3 + column / 3;
    }

    void validateInput() const {
        for (const auto& row : grid_) {
            for (int value : row) {
                if (value < 0 || value > 9) {
                    throw SudokuError("Every cell must contain a value from 0 through 9.");
                }
            }
        }
    }

    void initializeConstraints() {
        for (int row = 0; row < 9; ++row) {
            for (int column = 0; column < 9; ++column) {
                int value = grid_[row][column];
                if (value == 0) {
                    continue;
                }

                const int box = boxIndex(row, column);

                if (rows_[row].count(value) ||
                    columns_[column].count(value) ||
                    boxes_[box].count(value)) {
                    throw SudokuError("Initial Sudoku violates a row, column, or box constraint.");
                }

                rows_[row].insert(value);
                columns_[column].insert(value);
                boxes_[box].insert(value);
            }
        }
    }

    std::set<int> candidates(int row, int column) const {
        std::set<int> result;

        if (grid_[row][column] != 0) {
            return result;
        }

        for (int value = 1; value <= 9; ++value) {
            const int box = boxIndex(row, column);

            if (!rows_[row].count(value) &&
                !columns_[column].count(value) &&
                !boxes_[box].count(value)) {
                result.insert(value);
            }
        }

        return result;
    }

    struct Choice {
        int row;
        int column;
        std::set<int> candidates;
    };

    std::optional<Choice> selectCell() const {
        std::optional<Choice> best;

        for (int row = 0; row < 9; ++row) {
            for (int column = 0; column < 9; ++column) {
                if (grid_[row][column] != 0) {
                    continue;
                }

                auto options = candidates(row, column);

                if (options.empty()) {
                    return Choice{row, column, {}};
                }

                if (!best || options.size() < best->candidates.size()) {
                    best = Choice{row, column, std::move(options)};
                }

                if (best->candidates.size() == 1) {
                    return best;
                }
            }
        }

        return best;
    }

    void place(int row, int column, int value) {
        const int box = boxIndex(row, column);
        grid_[row][column] = value;
        rows_[row].insert(value);
        columns_[column].insert(value);
        boxes_[box].insert(value);
    }

    void undo(int row, int column, int value) {
        const int box = boxIndex(row, column);
        grid_[row][column] = 0;
        rows_[row].erase(value);
        columns_[column].erase(value);
        boxes_[box].erase(value);
    }

    bool search() {
        auto choice = selectCell();

        if (!choice) {
            return true;
        }

        if (choice->candidates.empty()) {
            return false;
        }

        // The search explicitly follows:
        // Choice -> Constraint -> Recursive call -> Undo choice.
        for (int value : choice->candidates) {
            ++statistics_.decisions;
            place(choice->row, choice->column, value);

            if (search()) {
                return true;
            }

            undo(choice->row, choice->column, value);
            ++statistics_.backtracks;
        }

        return false;
    }

public:
    explicit Sudoku(const Grid& grid)
        : grid_(grid) {
        validateInput();
        initializeConstraints();
    }

    bool solve() {
        const auto started = std::chrono::steady_clock::now();
        const bool solved = search();
        const auto finished = std::chrono::steady_clock::now();

        statistics_.elapsedMs =
            std::chrono::duration<double, std::milli>(finished - started).count();

        return solved;
    }

    const Grid& grid() const {
        return grid_;
    }

    const Statistics& statistics() const {
        return statistics_;
    }
};

void printGrid(const Sudoku::Grid& grid) {
    for (int row = 0; row < 9; ++row) {
        if (row > 0 && row % 3 == 0) {
            std::cout << "------+-------+------\n";
        }

        for (int column = 0; column < 9; ++column) {
            if (column > 0 && column % 3 == 0) {
                std::cout << "| ";
            }

            std::cout << (grid[row][column] == 0 ? '.' : char('0' + grid[row][column]));

            if (column != 8) {
                std::cout << ' ';
            }
        }
        std::cout << '\n';
    }
}

std::vector<std::vector<int>> combinationSum(
    std::vector<int> values,
    int target
) {
    if (target < 0) {
        throw std::invalid_argument("Target cannot be negative.");
    }

    std::sort(values.begin(), values.end());
    std::vector<std::vector<int>> result;
    std::vector<int> path;

    std::function<void(std::size_t, int)> search =
        [&](std::size_t start, int remaining) {
            if (remaining == 0) {
                result.push_back(path);
                return;
            }

            for (std::size_t i = start; i < values.size(); ++i) {
                if (i > start && values[i] == values[i - 1]) {
                    continue;
                }

                if (values[i] > remaining) {
                    break;
                }

                path.push_back(values[i]);
                search(i + 1, remaining - values[i]);
                path.pop_back();
            }
        };

    search(0, target);
    return result;
}

int main() {
    try {
        const Sudoku::Grid puzzle{{
            {{5, 3, 0, 0, 7, 0, 0, 0, 0}},
            {{6, 0, 0, 1, 9, 5, 0, 0, 0}},
            {{0, 9, 8, 0, 0, 0, 0, 6, 0}},
            {{8, 0, 0, 0, 6, 0, 0, 0, 3}},
            {{4, 0, 0, 8, 0, 3, 0, 0, 1}},
            {{7, 0, 0, 0, 2, 0, 0, 0, 6}},
            {{0, 6, 0, 0, 0, 0, 2, 8, 0}},
            {{0, 0, 0, 4, 1, 9, 0, 0, 5}},
            {{0, 0, 0, 0, 8, 0, 0, 7, 9}}
        }};

        Sudoku sudoku(puzzle);

        std::cout << "Original Sudoku:\n";
        printGrid(sudoku.grid());

        if (!sudoku.solve()) {
            std::cout << "\nThe puzzle has no solution.\n";
            return 0;
        }

        std::cout << "\nSolved Sudoku:\n";
        printGrid(sudoku.grid());

        const auto& stats = sudoku.statistics();
        std::cout << "\nDecisions: " << stats.decisions
                  << "\nBacktracks: " << stats.backtracks
                  << "\nElapsed: " << stats.elapsedMs << " ms\n";

        const auto combinations = combinationSum({2, 3, 5, 6, 8}, 10);

        std::cout << "\nSubset-sum backtracking:\n";
        for (const auto& combination : combinations) {
            std::cout << "[";
            for (std::size_t i = 0; i < combination.size(); ++i) {
                if (i) std::cout << ", ";
                std::cout << combination[i];
            }
            std::cout << "]\n";
        }
    } catch (const SudokuError& error) {
        std::cerr << "Sudoku validation error: " << error.what() << '\n';
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "Execution error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
