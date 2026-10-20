import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/**
 * Enterprise cache registry illustrating collision management, workload policies,
 * metrics, and correctness checks with Java 17 domain modeling.
 */
public class CollisionConcepts {

    enum ResolutionStrategy {
        SEPARATE_CHAINING,
        LINEAR_PROBING
    }

    record CachePolicy(
            ResolutionStrategy strategy,
            double maximumLoadFactor,
            int initialCapacity
    ) {
        CachePolicy {
            Objects.requireNonNull(strategy, "strategy");
            if (initialCapacity < 4) {
                throw new IllegalArgumentException("Capacity must be at least four");
            }
            if (!(maximumLoadFactor > 0.0 && maximumLoadFactor < 1.0)) {
                throw new IllegalArgumentException("Load factor threshold must be in (0, 1)");
            }
        }
    }

    record CacheMetrics(long probes, long collisions, long resizes) {}

    record CacheEntry(String key, String value) {
        CacheEntry {
            if (key == null || key.isBlank()) {
                throw new IllegalArgumentException("Key cannot be blank");
            }
            Objects.requireNonNull(value, "value");
        }
    }

    interface CacheStore {
        void put(String key, String value);
        Optional<String> get(String key);
        boolean remove(String key);
        double loadFactor();
        CacheMetrics metrics();
        int size();
    }

    static final class ChainedStore implements CacheStore {
        private List<List<CacheEntry>> buckets;
        private int size;
        private long probes;
        private long collisions;
        private long resizes;
        private final double threshold;

        ChainedStore(CachePolicy policy) {
            buckets = newBuckets(policy.initialCapacity());
            threshold = policy.maximumLoadFactor();
        }

        private static List<List<CacheEntry>> newBuckets(int capacity) {
            List<List<CacheEntry>> result = new ArrayList<>(capacity);
            for (int i = 0; i < capacity; i++) {
                result.add(new ArrayList<>());
            }
            return result;
        }

        private int index(String key) {
            return Math.floorMod(key.hashCode(), buckets.size());
        }

        @Override
        public void put(String key, String value) {
            validateKey(key);
            Objects.requireNonNull(value, "value");
            List<CacheEntry> bucket = buckets.get(index(key));

            for (int i = 0; i < bucket.size(); i++) {
                probes++;
                CacheEntry entry = bucket.get(i);
                if (entry.key().equals(key)) {
                    bucket.set(i, new CacheEntry(key, value));
                    return;
                }
                collisions++;
            }

            if (!bucket.isEmpty()) collisions++;
            bucket.add(new CacheEntry(key, value));
            size++;

            if (loadFactor() > threshold) {
                resize(buckets.size() * 2);
            }
        }

        @Override
        public Optional<String> get(String key) {
            validateKey(key);
            for (CacheEntry entry : buckets.get(index(key))) {
                probes++;
                if (entry.key().equals(key)) return Optional.of(entry.value());
            }
            return Optional.empty();
        }

        @Override
        public boolean remove(String key) {
            validateKey(key);
            List<CacheEntry> bucket = buckets.get(index(key));
            for (int i = 0; i < bucket.size(); i++) {
                probes++;
                if (bucket.get(i).key().equals(key)) {
                    bucket.remove(i);
                    size--;
                    return true;
                }
            }
            return false;
        }

        private void resize(int capacity) {
            List<CacheEntry> entries = buckets.stream()
                    .flatMap(List::stream)
                    .toList();
            buckets = newBuckets(capacity);
            size = 0;

            for (CacheEntry entry : entries) {
                buckets.get(index(entry.key())).add(entry);
                size++;
            }
            resizes++;
        }

        @Override
        public double loadFactor() {
            return (double) size / buckets.size();
        }

        @Override
        public CacheMetrics metrics() {
            return new CacheMetrics(probes, collisions, resizes);
        }

        @Override
        public int size() {
            return size;
        }
    }

    static final class ProbingStore implements CacheStore {
        private enum SlotState { EMPTY, OCCUPIED, DELETED }

        private static final class Slot {
            SlotState state = SlotState.EMPTY;
            String key;
            String value;
        }

        private Slot[] slots;
        private int size;
        private int deleted;
        private long probes;
        private long collisions;
        private long resizes;
        private final double threshold;

        ProbingStore(CachePolicy policy) {
            slots = new Slot[policy.initialCapacity()];
            for (int i = 0; i < slots.length; i++) slots[i] = new Slot();
            threshold = Math.min(policy.maximumLoadFactor(), 0.65);
        }

        private int index(String key) {
            return Math.floorMod(key.hashCode(), slots.length);
        }

        private int[] locate(String key) {
            int position = index(key);
            int firstDeleted = -1;

            for (int count = 0; count < slots.length; count++) {
                probes++;
                Slot slot = slots[position];

                if (slot.state == SlotState.EMPTY) {
                    return new int[] {
                        firstDeleted >= 0 ? firstDeleted : position, 0
                    };
                }

                if (slot.state == SlotState.DELETED) {
                    if (firstDeleted < 0) firstDeleted = position;
                } else if (slot.key.equals(key)) {
                    return new int[] { position, 1 };
                } else {
                    collisions++;
                }

                position = (position + 1) % slots.length;
            }

            if (firstDeleted >= 0) return new int[] { firstDeleted, 0 };
            throw new IllegalStateException("No available slot");
        }

        @Override
        public void put(String key, String value) {
            validateKey(key);
            Objects.requireNonNull(value, "value");

            if ((double) (size + deleted + 1) / slots.length > threshold) {
                resize(slots.length * 2);
            }

            int[] result = locate(key);
            Slot slot = slots[result[0]];
            if (result[1] == 1) {
                slot.value = value;
                return;
            }

            if (slot.state == SlotState.DELETED) deleted--;
            slot.state = SlotState.OCCUPIED;
            slot.key = key;
            slot.value = value;
            size++;
        }

        @Override
        public Optional<String> get(String key) {
            validateKey(key);
            int[] result = locate(key);
            return result[1] == 1
                    ? Optional.of(slots[result[0]].value)
                    : Optional.empty();
        }

        @Override
        public boolean remove(String key) {
            validateKey(key);
            int[] result = locate(key);
            if (result[1] == 0) return false;

            Slot slot = slots[result[0]];
            slot.state = SlotState.DELETED;
            slot.key = null;
            slot.value = null;
            size--;
            deleted++;

            if (deleted > size && deleted > 8) resize(slots.length);
            return true;
        }

        private void resize(int capacity) {
            List<CacheEntry> entries = new ArrayList<>();
            for (Slot slot : slots) {
                if (slot.state == SlotState.OCCUPIED) {
                    entries.add(new CacheEntry(slot.key, slot.value));
                }
            }

            slots = new Slot[capacity];
            for (int i = 0; i < capacity; i++) slots[i] = new Slot();
            size = 0;
            deleted = 0;

            for (CacheEntry entry : entries) {
                int[] result = locate(entry.key());
                Slot slot = slots[result[0]];
                slot.state = SlotState.OCCUPIED;
                slot.key = entry.key();
                slot.value = entry.value();
                size++;
            }
            resizes++;
        }

        @Override
        public double loadFactor() {
            return (double) size / slots.length;
        }

        @Override
        public CacheMetrics metrics() {
            return new CacheMetrics(probes, collisions, resizes);
        }

        @Override
        public int size() {
            return size;
        }
    }

    private static void validateKey(String key) {
        if (key == null || key.isBlank()) {
            throw new IllegalArgumentException("Key cannot be blank");
        }
    }

    private static void verify(CacheStore store) {
        store.put("tenant-1", "profile-A");
        store.put("tenant-17", "profile-B");
        store.put("tenant-33", "profile-C");
        store.put("tenant-1", "profile-A-updated");

        if (!store.get("tenant-1").orElseThrow().equals("profile-A-updated")) {
            throw new IllegalStateException("Update failed");
        }
        if (!store.remove("tenant-17")) {
            throw new IllegalStateException("Deletion failed");
        }
        if (store.get("tenant-17").isPresent()) {
            throw new IllegalStateException("Deleted key is still present");
        }
        if (store.get("tenant-33").isEmpty()) {
            throw new IllegalStateException("Collision lookup failed");
        }

        for (int i = 0; i < 200; i++) {
            store.put("customer-" + i, "record-" + i);
        }
        for (int i = 0; i < 200; i++) {
            if (!store.get("customer-" + i).orElseThrow().equals("record-" + i)) {
                throw new IllegalStateException("Resizing validation failed");
            }
        }
    }

    private static void report(String name, CacheStore store) {
        System.out.printf(
                "%s: size=%d, loadFactor=%.3f, metrics=%s%n",
                name, store.size(), store.loadFactor(), store.metrics()
        );
    }

    public static void main(String[] args) {
        CachePolicy chainPolicy = new CachePolicy(
                ResolutionStrategy.SEPARATE_CHAINING, 0.75, 8);
        CachePolicy probePolicy = new CachePolicy(
                ResolutionStrategy.LINEAR_PROBING, 0.65, 8);

        Map<ResolutionStrategy, CacheStore> stores = new HashMap<>();
        stores.put(chainPolicy.strategy(), new ChainedStore(chainPolicy));
        stores.put(probePolicy.strategy(), new ProbingStore(probePolicy));

        Set<ResolutionStrategy> verified = new HashSet<>();
        for (var entry : stores.entrySet()) {
            verify(entry.getValue());
            verified.add(entry.getKey());
            report(entry.getKey().name(), entry.getValue());
        }

        if (verified.size() != ResolutionStrategy.values().length) {
            throw new IllegalStateException("A collision strategy was not verified");
        }

        try {
            stores.get(ResolutionStrategy.SEPARATE_CHAINING).put(" ", "invalid");
            throw new IllegalStateException("Blank key was accepted");
        } catch (IllegalArgumentException expected) {
            System.out.println("Invalid-key validation passed.");
        }

        System.out.println("All enterprise cache checks passed.");
    }
}
