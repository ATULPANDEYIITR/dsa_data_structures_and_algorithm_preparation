#include <algorithm>
#include <array>
#include <cstddef>
#include <exception>
#include <iostream>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

struct Position {
    int row{};
    int col{};

    bool operator==(const Position& other) const {
        return row == other.row && col == other.col;
    }

    bool operator<(const Position& other) const {
        return std::tie(row, col) < std::tie(other.row, other.col);
    }
};

class NQueensSolver {
private:
    int n_;
    std::vector<std::vector<int>> solutions_;

    void search(
        int row,
        std::vector<int>& placement,
        std::vector<bool>& columns,
        std::vector<bool>& descending,
        std::vector<bool>& ascending
    ) {
        if (row == n_) {
            solutions_.push_back(placement);
            return;
        }

        for (int col = 0; col < n_; ++col) {
            const int d1 = row - col + n_ - 1;
            const int d2 = row + col;

            if (columns[col] || descending[d1] || ascending[d2]) {
                continue;
            }

            placement[row] = col;
            columns[col] = true;
            descending[d1] = true;
            ascending[d2] = true;

            search(
                row + 1,
                placement,
                columns,
                descending,
                ascending
            );

            placement[row] = -1;
            columns[col] = false;
            descending[d1] = false;
            ascending[d2] = false;
        }
    }

public:
    explicit NQueensSolver(int n) : n_(n) {
        if (n < 1 || n > 14) {
            throw std::invalid_argument("n must be between 1 and 14");
        }
    }

    const std::vector<std::vector<int>>& solve() {
        solutions_.clear();

        std::vector<int> placement(n_, -1);
        std::vector<bool> columns(n_, false);
        std::vector<bool> descending(2 * n_ - 1, false);
        std::vector<bool> ascending(2 * n_ - 1, false);

        search(
            0,
            placement,
            columns,
            descending,
            ascending
        );

        return solutions_;
    }

    static bool validSolution(const std::vector<int>& solution) {
        const int n = static_cast<int>(solution.size());
        if (n == 0) {
            return false;
        }

        std::set<int> columns;
        std::set<int> down;
        std::set<int> up;

        for (int row = 0; row < n; ++row) {
            const int col = solution[row];

            if (col < 0 || col >= n) {
                return false;
            }

            if (!columns.insert(col).second) {
                return false;
            }

            if (!down.insert(row - col).second) {
                return false;
            }

            if (!up.insert(row + col).second) {
                return false;
            }
        }

        return true;
    }

    std::string render(const std::vector<int>& solution) const {
        if (static_cast<int>(solution.size()) != n_) {
            throw std::invalid_argument("solution has wrong size");
        }

        std::string output;

        for (int row = 0; row < n_; ++row) {
            for (int col = 0; col < n_; ++col) {
                output += (solution[row] == col ? 'Q' : '.');
                if (col + 1 < n_) {
                    output += ' ';
                }
            }
            if (row + 1 < n_) {
                output += '\n';
            }
        }

        return output;
    }
};

class Maze {
private:
    std::vector<std::string> grid_;
    int rows_;
    int cols_;

    static constexpr std::array<Position, 4> directions_{
        Position{-1, 0},
        Position{1, 0},
        Position{0, -1},
        Position{0, 1}
    };

    bool valid(const Position& p) const {
        return p.row >= 0 &&
               p.row < rows_ &&
               p.col >= 0 &&
               p.col < cols_ &&
               grid_[p.row][p.col] == '.';
    }

    void generate(
        const Position& current,
        const Position& target,
        std::set<Position>& visited,
        std::vector<Position>& currentPath,
        std::vector<std::vector<Position>>& paths,
        std::size_t maxPaths
    ) const {
        if (paths.size() >= maxPaths) {
            return;
        }

        if (current == target) {
            paths.push_back(currentPath);
            return;
        }

        for (const auto& direction : directions_) {
            Position next{
                current.row + direction.row,
                current.col + direction.col
            };

            if (!valid(next) || visited.contains(next)) {
                continue;
            }

            visited.insert(next);
            currentPath.push_back(next);

            generate(
                next,
                target,
                visited,
                currentPath,
                paths,
                maxPaths
            );

            currentPath.pop_back();
            visited.erase(next);
        }
    }

public:
    explicit Maze(std::vector<std::string> grid)
        : grid_(std::move(grid)),
          rows_(static_cast<int>(grid_.size())),
          cols_(grid_.empty() ? 0 : static_cast<int>(grid_[0].size())) {
        if (grid_.empty() || cols_ == 0) {
            throw std::invalid_argument("maze cannot be empty");
        }

        for (const auto& row : grid_) {
            if (static_cast<int>(row.size()) != cols_) {
                throw std::invalid_argument("maze must be rectangular");
            }

            if (row.find_first_not_of(".#") != std::string::npos) {
                throw std::invalid_argument("maze contains invalid cell");
            }
        }
    }

    std::vector<std::vector<Position>> allPaths(
        Position start,
        Position target,
        std::size_t maxPaths = 10000
    ) const {
        if (maxPaths == 0) {
            throw std::invalid_argument("maxPaths must be positive");
        }

        if (!valid(start) || !valid(target)) {
            return {};
        }

        std::set<Position> visited{start};
        std::vector<Position> currentPath{start};
        std::vector<std::vector<Position>> paths;

        generate(
            start,
            target,
            visited,
            currentPath,
            paths,
            maxPaths
        );

        return paths;
    }

    std::optional<std::vector<Position>> shortestPath(
        Position start,
        Position target
    ) const {
        if (!valid(start) || !valid(target)) {
            return std::nullopt;
        }

        // BFS is used here because every legal move has equal cost.
        std::vector<Position> queue;
        queue.push_back(start);

        std::set<Position> visited{start};
        std::map<Position, Position> previous;

        std::size_t head = 0;

        while (head < queue.size()) {
            Position current = queue[head++];

            if (current == target) {
                std::vector<Position> path;
                Position node = target;

                path.push_back(node);

                while (!(node == start)) {
                    node = previous.at(node);
                    path.push_back(node);
                }

                std::reverse(path.begin(), path.end());
                return path;
            }

            for (const auto& direction : directions_) {
                Position next{
                    current.row + direction.row,
                    current.col + direction.col
                };

                if (!valid(next) || visited.contains(next)) {
                    continue;
                }

                visited.insert(next);
                previous[next] = current;
                queue.push_back(next);
            }
        }

        return std::nullopt;
    }

    std::string renderPath(const std::vector<Position>& path) const {
        std::set<Position> cells(path.begin(), path.end());
        std::string output;

        for (int row = 0; row < rows_; ++row) {
            for (int col = 0; col < cols_; ++col) {
                Position p{row, col};
                output += cells.contains(p) ? '*' : grid_[row][col];

                if (col + 1 < cols_) {
                    output += ' ';
                }
            }

            if (row + 1 < rows_) {
                output += '\n';
            }
        }

        return output;
    }
};

int main() {
    try {
        std::cout << "=== N-Queens ===\n";

        NQueensSolver queens(4);
        const auto& solutions = queens.solve();

        if (solutions.size() != 2) {
            throw std::runtime_error("4-Queens must have exactly 2 solutions");
        }

        for (std::size_t i = 0; i < solutions.size(); ++i) {
            if (!NQueensSolver::validSolution(solutions[i])) {
                throw std::runtime_error("invalid N-Queens solution");
            }

            std::cout << "\nSolution " << i + 1 << "\n";
            std::cout << queens.render(solutions[i]) << '\n';
        }

        std::cout << "\n=== Maze Governance ===\n";

        Maze maze({
            "...#.",
            ".#...",
            "...#.",
            "#....",
            "....."
        });

        Position start{0, 0};
        Position target{4, 4};

        const auto paths = maze.allPaths(start, target, 5);

        std::cout << "Generated paths: " << paths.size() << '\n';

        for (std::size_t i = 0; i < paths.size(); ++i) {
            std::cout << "\nPath " << i + 1
                      << ", length=" << paths[i].size() << '\n';
            std::cout << maze.renderPath(paths[i]) << '\n';
        }

        const auto shortest = maze.shortestPath(start, target);

        if (!shortest.has_value()) {
            throw std::runtime_error("expected a reachable target");
        }

        std::cout << "\nShortest path length: "
                  << shortest->size() << '\n';
        std::cout << maze.renderPath(*shortest) << '\n';

        NQueensSolver one(1);
        NQueensSolver two(2);
        NQueensSolver three(3);

        if (one.solve().size() != 1 ||
            !two.solve().empty() ||
            !three.solve().empty()) {
            throw std::runtime_error("N-Queens edge-case validation failed");
        }

        Maze blocked({
            ".#",
            "#."
        });

        if (!blocked.allPaths({0, 0}, {1, 1}).empty()) {
            throw std::runtime_error("blocked-maze validation failed");
        }

        std::cout << "\nAll validation checks passed.\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Failure: " << ex.what() << '\n';
        return 1;
    }
}
