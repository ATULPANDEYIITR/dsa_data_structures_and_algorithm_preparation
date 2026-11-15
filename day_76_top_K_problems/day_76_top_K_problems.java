import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

/**
 * Top-K Selection and Enterprise Ranking Engine.
 *
 * Java 17, standard library only.
 *
 * Features:
 * - Kth largest and smallest
 * - Top-K frequent elements
 * - K closest elements
 * - Quickselect
 * - Immutable request and response records
 * - Policy-driven service layer
 * - Validation and typed exceptions
 * - Enterprise-style batch processing
 */
public class TopKEnterprise {

    enum Operation {
        KTH_LARGEST,
        KTH_SMALLEST,
        TOP_K_FREQUENT,
        K_CLOSEST
    }

    record SelectionRequest(
        Operation operation,
        List<Integer> values,
        int k,
        Integer target
    ) {
        SelectionRequest {
            Objects.requireNonNull(operation, "Operation is required");
            Objects.requireNonNull(values, "Values are required");

            values = List.copyOf(values);

            if (values.stream().anyMatch(Objects::isNull)) {
                throw new ValidationException("Null elements are prohibited");
            }

            if (operation == Operation.K_CLOSEST && target == null) {
                throw new ValidationException("Target is required");
            }
        }
    }

    record SelectionResponse(
        Operation operation,
        List<Integer> result,
        long executionTimeNanos
    ) {
        SelectionResponse {
            result = List.copyOf(result);
        }
    }

    record FrequencyEntry(int value, int frequency) {}

    static class ValidationException extends IllegalArgumentException {
        ValidationException(String message) {
            super(message);
        }
    }

    static class SelectionService {

        private void validateK(int k, int size, boolean allowZero) {
            int minimum = allowZero ? 0 : 1;

            if (k < minimum || k > size) {
                throw new ValidationException(
                    "k must be between " + minimum + " and " + size
                );
            }
        }

        public int kthLargest(List<Integer> values, int k) {
            validateK(k, values.size(), false);

            PriorityQueue<Integer> heap = new PriorityQueue<>();

            for (int value : values) {
                heap.offer(value);

                if (heap.size() > k) {
                    heap.poll();
                }
            }

            return heap.element();
        }

        public int kthSmallest(List<Integer> values, int k) {
            validateK(k, values.size(), false);

            PriorityQueue<Integer> heap =
                new PriorityQueue<>(Comparator.reverseOrder());

            for (int value : values) {
                heap.offer(value);

                if (heap.size() > k) {
                    heap.poll();
                }
            }

            return heap.element();
        }

        public int quickselectLargest(List<Integer> values, int k) {
            validateK(k, values.size(), false);

            int[] array = values.stream()
                .mapToInt(Integer::intValue)
                .toArray();

            int target = k - 1;
            int left = 0;
            int right = array.length - 1;

            Random random = new Random();

            while (left <= right) {
                int pivot = array[
                    left + random.nextInt(right - left + 1)
                ];

                int low = left;
                int current = left;
                int high = right;

                while (current <= high) {
                    if (array[current] > pivot) {
                        int temp = array[current];
                        array[current] = array[low];
                        array[low] = temp;
                        current++;
                        low++;
                    } else if (array[current] < pivot) {
                        int temp = array[current];
                        array[current] = array[high];
                        array[high] = temp;
                        high--;
                    } else {
                        current++;
                    }
                }

                if (target < low) {
                    right = low - 1;
                } else if (target > high) {
                    left = high + 1;
                } else {
                    return array[target];
                }
            }

            throw new IllegalStateException("Quickselect failed");
        }

        public List<Integer> topKFrequent(
            List<Integer> values,
            int k
        ) {
            Map<Integer, Long> frequencies = values.stream()
                .collect(Collectors.groupingBy(
                    Function.identity(),
                    Collectors.counting()
                ));

            validateK(k, frequencies.size(), true);

            Comparator<FrequencyEntry> ordering =
                Comparator.comparingInt(FrequencyEntry::frequency)
                    .thenComparing(
                        Comparator.comparingInt(FrequencyEntry::value)
                            .reversed()
                    );

            PriorityQueue<FrequencyEntry> heap =
                new PriorityQueue<>(ordering);

            frequencies.forEach((value, count) -> {
                heap.offer(new FrequencyEntry(
                    value,
                    Math.toIntExact(count)
                ));

                if (heap.size() > k) {
                    heap.poll();
                }
            });

            List<Integer> result = new ArrayList<>();

            while (!heap.isEmpty()) {
                result.add(heap.poll().value());
            }

            result.sort((a, b) -> {
                int comparison = Long.compare(
                    frequencies.get(b),
                    frequencies.get(a)
                );

                return comparison != 0
                    ? comparison
                    : Integer.compare(a, b);
            });

            return List.copyOf(result);
        }

        public List<Integer> kClosestElements(
            List<Integer> values,
            int k,
            int target
        ) {
            validateK(k, values.size(), true);

            for (int i = 1; i < values.size(); i++) {
                if (values.get(i - 1) > values.get(i)) {
                    throw new ValidationException(
                        "Input must be sorted"
                    );
                }
            }

            if (k == 0) {
                return List.of();
            }

            int left = 0;
            int right = values.size() - k;

            while (left < right) {
                int middle = left + (right - left) / 2;

                long leftDistance =
                    (long) target - values.get(middle);

                long rightDistance =
                    (long) values.get(middle + k) - target;

                if (leftDistance > rightDistance) {
                    left = middle + 1;
                } else {
                    right = middle;
                }
            }

            return List.copyOf(
                values.subList(left, left + k)
            );
        }

        public SelectionResponse execute(SelectionRequest request) {
            Objects.requireNonNull(request);

            long start = System.nanoTime();

            List<Integer> result = switch (request.operation()) {
                case KTH_LARGEST -> List.of(
                    kthLargest(request.values(), request.k())
                );

                case KTH_SMALLEST -> List.of(
                    kthSmallest(request.values(), request.k())
                );

                case TOP_K_FREQUENT -> topKFrequent(
                    request.values(),
                    request.k()
                );

                case K_CLOSEST -> kClosestElements(
                    request.values(),
                    request.k(),
                    request.target()
                );
            };

            return new SelectionResponse(
                request.operation(),
                result,
                System.nanoTime() - start
            );
        }

        public List<SelectionResponse> executeBatch(
            List<SelectionRequest> requests
        ) {
            return requests.stream()
                .map(this::execute)
                .toList();
        }
    }

    private static void runTests(SelectionService service) {
        List<Integer> values = List.of(3, 2, 1, 5, 6, 4);

        assert service.kthLargest(values, 2) == 5;
        assert service.kthSmallest(values, 2) == 2;
        assert service.quickselectLargest(values, 2) == 5;

        assert service.topKFrequent(
            List.of(1, 1, 1, 2, 2, 3),
            2
        ).equals(List.of(1, 2));

        assert service.kClosestElements(
            List.of(1, 2, 3, 4, 5),
            4,
            3
        ).equals(List.of(1, 2, 3, 4));

        assert service.topKFrequent(List.of(), 0).isEmpty();

        boolean rejected = false;

        try {
            service.kthLargest(values, 10);
        } catch (ValidationException exception) {
            rejected = true;
        }

        assert rejected;
    }

    public static void main(String[] args) {
        SelectionService service = new SelectionService();

        System.out.println("TOP-K ENTERPRISE SELECTION ENGINE");
        System.out.println("=================================");

        List<Integer> values = List.of(3, 2, 1, 5, 6, 4);

        System.out.println(
            "Second largest: " + service.kthLargest(values, 2)
        );

        System.out.println(
            "Third smallest: " + service.kthSmallest(values, 3)
        );

        System.out.println(
            "Quickselect: " + service.quickselectLargest(values, 2)
        );

        System.out.println(
            "Top frequent: " +
            service.topKFrequent(
                List.of(1, 1, 1, 2, 2, 3),
                2
            )
        );

        System.out.println(
            "Closest: " +
            service.kClosestElements(
                List.of(1, 2, 3, 4, 5),
                4,
                3
            )
        );

        List<SelectionRequest> requests = List.of(
            new SelectionRequest(
                Operation.KTH_LARGEST, values, 2, null
            ),
            new SelectionRequest(
                Operation.TOP_K_FREQUENT,
                List.of(4, 4, 3, 3, 2),
                2,
                null
            ),
            new SelectionRequest(
                Operation.K_CLOSEST,
                List.of(1, 2, 3, 4, 5),
                2,
                4
            )
        );

        System.out.println("\nEnterprise batch processing:");

        for (SelectionResponse response : service.executeBatch(requests)) {
            System.out.println(response);
        }

        runTests(service);

        System.out.println("\nAll assertions passed.");
    }
}
