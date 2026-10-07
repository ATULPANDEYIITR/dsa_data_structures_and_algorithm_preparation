import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/*
 * Fast and Slow Pointers
 *
 * Enterprise-oriented scenario:
 * A repository-style event processing pipeline stores processing stages as a
 * linked chain. A corrupted pipeline can point backward, creating a cycle.
 *
 * This program models:
 * - midpoint discovery,
 * - Floyd cycle detection,
 * - cycle-entry discovery,
 * - cycle-length measurement,
 * - explicit validation,
 * - state-oriented diagnostic results,
 * - an application service that reports chain integrity.
 *
 * Java 17+.
 */
public class FastSlowPointers {

    enum ChainStatus {
        ACYCLIC,
        CYCLIC,
        EMPTY
    }

    static final class Stage {
        private final String name;
        private final int sequence;
        private Stage next;

        Stage(int sequence, String name) {
            if (sequence <= 0) {
                throw new IllegalArgumentException(
                    "Stage sequence must be positive."
                );
            }

            if (name == null || name.isBlank()) {
                throw new IllegalArgumentException(
                    "Stage name must not be blank."
                );
            }

            this.sequence = sequence;
            this.name = name;
        }

        String name() {
            return name;
        }

        int sequence() {
            return sequence;
        }

        Stage next() {
            return next;
        }

        void connectTo(Stage target) {
            this.next = Objects.requireNonNull(
                target,
                "A stage connection cannot target null."
            );
        }

        @Override
        public String toString() {
            return sequence + ":" + name;
        }
    }

    static final class Pipeline {
        private final List<Stage> ownedStages = new ArrayList<>();
        private Stage head;

        Stage addStage(String name) {
            Stage stage = new Stage(ownedStages.size() + 1, name);

            if (head == null) {
                head = stage;
            } else {
                ownedStages.get(ownedStages.size() - 1).connectTo(stage);
            }

            ownedStages.add(stage);
            return stage;
        }

        Stage head() {
            return head;
        }

        Stage stageAt(int zeroBasedIndex) {
            if (zeroBasedIndex < 0 || zeroBasedIndex >= ownedStages.size()) {
                throw new IndexOutOfBoundsException(
                    "Stage index is outside the pipeline."
                );
            }

            return ownedStages.get(zeroBasedIndex);
        }

        int size() {
            return ownedStages.size();
        }

        void createCycleAt(int zeroBasedIndex) {
            if (head == null) {
                throw new IllegalStateException(
                    "Cannot create a cycle in an empty pipeline."
                );
            }

            Stage target = stageAt(zeroBasedIndex);
            Stage tail = ownedStages.get(ownedStages.size() - 1);
            tail.connectTo(target);
        }

        String preview(int limit) {
            if (head == null) {
                return "empty";
            }

            StringBuilder result = new StringBuilder();
            Stage current = head;

            for (int count = 0; count < limit && current != null; count++) {
                if (result.length() > 0) {
                    result.append(" -> ");
                }

                result.append(current);
                current = current.next();
            }

            if (current != null) {
                result.append(" -> ...");
            }

            return result.toString();
        }
    }

    static final class CycleReport {
        private final ChainStatus status;
        private final Stage meetingStage;
        private final Stage entryStage;
        private final int cycleLength;
        private final int distanceToEntry;

        private CycleReport(
            ChainStatus status,
            Stage meetingStage,
            Stage entryStage,
            int cycleLength,
            int distanceToEntry
        ) {
            this.status = status;
            this.meetingStage = meetingStage;
            this.entryStage = entryStage;
            this.cycleLength = cycleLength;
            this.distanceToEntry = distanceToEntry;
        }

        static CycleReport empty() {
            return new CycleReport(
                ChainStatus.EMPTY,
                null,
                null,
                0,
                0
            );
        }

        static CycleReport acyclic() {
            return new CycleReport(
                ChainStatus.ACYCLIC,
                null,
                null,
                0,
                0
            );
        }

        static CycleReport cyclic(
            Stage meetingStage,
            Stage entryStage,
            int cycleLength,
            int distanceToEntry
        ) {
            return new CycleReport(
                ChainStatus.CYCLIC,
                meetingStage,
                entryStage,
                cycleLength,
                distanceToEntry
            );
        }

        ChainStatus status() {
            return status;
        }

        Stage meetingStage() {
            return meetingStage;
        }

        Stage entryStage() {
            return entryStage;
        }

        int cycleLength() {
            return cycleLength;
        }

        int distanceToEntry() {
            return distanceToEntry;
        }

        @Override
        public String toString() {
            if (status == ChainStatus.EMPTY) {
                return "EMPTY";
            }

            if (status == ChainStatus.ACYCLIC) {
                return "ACYCLIC";
            }

            return "CYCLIC{meeting=" + meetingStage
                + ", entry=" + entryStage
                + ", length=" + cycleLength
                + ", distanceToEntry=" + distanceToEntry
                + "}";
        }
    }

    static final class PipelineIntegrityService {

        Stage findSecondMiddle(Stage head) {
            Stage slow = head;
            Stage fast = head;

            while (fast != null && fast.next() != null) {
                slow = slow.next();
                fast = fast.next().next();
            }

            return slow;
        }

        Stage findFirstMiddle(Stage head) {
            if (head == null) {
                return null;
            }

            Stage slow = head;
            Stage fast = head;

            while (fast.next() != null && fast.next().next() != null) {
                slow = slow.next();
                fast = fast.next().next();
            }

            return slow;
        }

        Stage findMeetingStage(Stage head) {
            Stage slow = head;
            Stage fast = head;

            while (fast != null && fast.next() != null) {
                slow = slow.next();
                fast = fast.next().next();

                if (slow == fast) {
                    return slow;
                }
            }

            return null;
        }

        CycleReport inspect(Stage head) {
            if (head == null) {
                return CycleReport.empty();
            }

            Stage meeting = findMeetingStage(head);

            if (meeting == null) {
                return CycleReport.acyclic();
            }

            Stage entry = findCycleEntry(head, meeting);
            int length = calculateCycleLength(entry);
            int distance = calculateDistanceToEntry(head, entry);

            return CycleReport.cyclic(
                meeting,
                entry,
                length,
                distance
            );
        }

        /*
         * The first pointer starts at the pipeline head while the second
         * starts at Floyd's meeting point. Equal-speed movement finds the
         * cycle entry without retaining every visited node.
         */
        private Stage findCycleEntry(Stage head, Stage meeting) {
            Stage left = head;
            Stage right = meeting;

            while (left != right) {
                left = left.next();
                right = right.next();
            }

            return left;
        }

        private int calculateCycleLength(Stage entry) {
            int length = 1;
            Stage current = entry.next();

            while (current != entry) {
                current = current.next();
                length++;
            }

            return length;
        }

        private int calculateDistanceToEntry(Stage head, Stage entry) {
            int distance = 0;
            Stage current = head;

            while (current != entry) {
                current = current.next();
                distance++;
            }

            return distance;
        }

        boolean isMergeSafe(Stage head) {
            /*
             * A cyclic processing pipeline cannot be treated as a finite
             * sequence because traversal would never reach a terminal stage.
             */
            return inspect(head).status() != ChainStatus.CYCLIC;
        }
    }

    static void demonstrateMiddleDetection(
        PipelineIntegrityService service
    ) {
        System.out.println("\n=== Middle Detection ===");

        Pipeline pipeline = new Pipeline();

        pipeline.addStage("ingest");
        pipeline.addStage("validate");
        pipeline.addStage("normalize");
        pipeline.addStage("persist");
        pipeline.addStage("audit");
        pipeline.addStage("publish");

        Stage first = service.findFirstMiddle(pipeline.head());
        Stage second = service.findSecondMiddle(pipeline.head());

        System.out.println("Pipeline: " + pipeline.preview(10));
        System.out.println("First middle: " + first);
        System.out.println("Second middle: " + second);
    }

    static void demonstrateEnterpriseInspection(
        PipelineIntegrityService service
    ) {
        System.out.println("\n=== Pipeline Integrity Inspection ===");

        Pipeline healthy = new Pipeline();
        healthy.addStage("ingest");
        healthy.addStage("validate");
        healthy.addStage("transform");
        healthy.addStage("persist");
        healthy.addStage("audit");

        CycleReport healthyReport = service.inspect(healthy.head());

        System.out.println("Healthy pipeline: " + healthy.preview(10));
        System.out.println("Integrity report: " + healthyReport);
        System.out.println(
            "Merge-safe workflow: "
                + service.isMergeSafe(healthy.head())
        );

        Pipeline corrupted = new Pipeline();
        corrupted.addStage("ingest");
        corrupted.addStage("validate");
        corrupted.addStage("transform");
        corrupted.addStage("publish");
        corrupted.addStage("audit");
        corrupted.addStage("notify");

        corrupted.createCycleAt(2);

        CycleReport corruptedReport = service.inspect(corrupted.head());

        System.out.println("Corrupted pipeline: " + corrupted.preview(10));
        System.out.println("Integrity report: " + corruptedReport);
        System.out.println(
            "Merge-safe workflow: "
                + service.isMergeSafe(corrupted.head())
        );
    }

    static void demonstrateDuplicatePayloads(
        PipelineIntegrityService service
    ) {
        System.out.println("\n=== Identity Versus Equal Payload ===");

        Stage first = new Stage(1, "validate");
        Stage second = new Stage(2, "validate");

        first.connectTo(second);
        second.connectTo(first);

        /*
         * Both nodes have the same business label, but they represent
         * different objects. Floyd must compare object identity using ==.
         */
        System.out.println(
            "Names equal: "
                + first.name().equals(second.name())
        );

        System.out.println(
            "Objects identical: "
                + (first == second)
        );

        CycleReport report = service.inspect(first);

        System.out.println("Cycle report: " + report);
    }

    static void demonstrateSelfCycle(
        PipelineIntegrityService service
    ) {
        System.out.println("\n=== Self-Cycle ===");

        Stage retry = new Stage(1, "retry");
        retry.connectTo(retry);

        CycleReport report = service.inspect(retry);

        System.out.println("Report: " + report);
    }

    static void demonstrateOptionalMiddle(
        PipelineIntegrityService service
    ) {
        System.out.println("\n=== Empty and Single-Stage Pipelines ===");

        Stage empty = null;
        System.out.println(
            "Empty middle: "
                + service.findSecondMiddle(empty)
        );

        Pipeline single = new Pipeline();
        single.addStage("commit");

        System.out.println(
            "Single-stage middle: "
                + service.findSecondMiddle(single.head())
        );
    }

    static void runAssertions(PipelineIntegrityService service) {
        Pipeline pipeline = new Pipeline();

        pipeline.addStage("A");
        pipeline.addStage("B");
        pipeline.addStage("C");
        pipeline.addStage("D");

        assert service.findFirstMiddle(pipeline.head())
            .name().equals("B");

        assert service.findSecondMiddle(pipeline.head())
            .name().equals("C");

        assert service.inspect(pipeline.head()).status()
            == ChainStatus.ACYCLIC;

        pipeline.createCycleAt(2);

        CycleReport report = service.inspect(pipeline.head());

        assert report.status() == ChainStatus.CYCLIC;
        assert report.entryStage().name().equals("C");
        assert report.cycleLength() == 2;
        assert report.distanceToEntry() == 2;

        Stage self = new Stage(1, "self");
        self.connectTo(self);

        CycleReport selfReport = service.inspect(self);

        assert selfReport.status() == ChainStatus.CYCLIC;
        assert selfReport.cycleLength() == 1;
        assert selfReport.distanceToEntry() == 0;

        System.out.println("\nAll Java assertions passed.");
    }

    public static void main(String[] args) {
        System.out.println("FAST AND SLOW POINTERS");
        System.out.println("=====================");

        PipelineIntegrityService service =
            new PipelineIntegrityService();

        demonstrateMiddleDetection(service);
        demonstrateEnterpriseInspection(service);
        demonstrateDuplicatePayloads(service);
        demonstrateSelfCycle(service);
        demonstrateOptionalMiddle(service);
        runAssertions(service);

        System.out.println("\n=== Complexity ===");
        System.out.println(
            "Middle detection: O(n) time and O(1) auxiliary space."
        );
        System.out.println(
            "Floyd detection: O(n) time and O(1) auxiliary space."
        );
        System.out.println(
            "Cycle-entry detection: O(n) time and O(1) auxiliary space."
        );
    }
}
