import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;

public class Main {

    enum Environment {
        DEVELOPMENT,
        STAGING,
        PRODUCTION
    }

    enum DeploymentState {
        REGISTERED,
        HEALTHY,
        DEGRADED,
        RETIRED
    }

    record ServiceKey(String service, Environment environment) {
        ServiceKey {
            if (service == null || service.isBlank()) {
                throw new IllegalArgumentException(
                    "Service name must not be blank"
                );
            }
            Objects.requireNonNull(environment, "Environment is required");
            service = service.trim().toLowerCase();
        }
    }

    static final class Deployment {
        private final ServiceKey key;
        private String version;
        private DeploymentState state;
        private long revision;

        Deployment(
            ServiceKey key,
            String version,
            DeploymentState state,
            long revision
        ) {
            this.key = Objects.requireNonNull(key);
            if (version == null || version.isBlank()) {
                throw new IllegalArgumentException(
                    "Version must not be blank"
                );
            }
            if (revision < 0) {
                throw new IllegalArgumentException(
                    "Revision cannot be negative"
                );
            }

            this.version = version;
            this.state = Objects.requireNonNull(state);
            this.revision = revision;
        }

        ServiceKey key() {
            return key;
        }

        String version() {
            return version;
        }

        DeploymentState state() {
            return state;
        }

        long revision() {
            return revision;
        }

        void upgrade(String newVersion, long expectedRevision) {
            if (state == DeploymentState.RETIRED) {
                throw new IllegalStateException(
                    "A retired deployment cannot be upgraded"
                );
            }
            if (revision != expectedRevision) {
                throw new IllegalStateException(
                    "Stale revision: expected " + expectedRevision
                    + ", current " + revision
                );
            }
            if (newVersion == null || newVersion.isBlank()) {
                throw new IllegalArgumentException(
                    "Version must not be blank"
                );
            }

            version = newVersion;
            revision++;
            state = DeploymentState.REGISTERED;
        }

        void transitionTo(DeploymentState nextState) {
            Objects.requireNonNull(nextState);

            if (state == DeploymentState.RETIRED
                && nextState != DeploymentState.RETIRED) {
                throw new IllegalStateException(
                    "Retired deployments cannot be reactivated"
                );
            }

            if (state == DeploymentState.REGISTERED
                && nextState != DeploymentState.HEALTHY
                && nextState != DeploymentState.DEGRADED
                && nextState != DeploymentState.RETIRED) {
                throw new IllegalStateException(
                    "Invalid transition from REGISTERED"
                );
            }

            state = nextState;
            revision++;
        }

        @Override
        public String toString() {
            return key + " version=" + version
                + " state=" + state + " revision=" + revision;
        }
    }

    static final class DeploymentRegistry {
        private final Map<ServiceKey, Deployment> deployments =
            new HashMap<>();

        void register(Deployment deployment) {
            Objects.requireNonNull(deployment);
            Deployment existing = deployments.putIfAbsent(
                deployment.key(), deployment
            );

            if (existing != null) {
                throw new IllegalStateException(
                    "Deployment already exists: " + deployment.key()
                );
            }
        }

        Optional<Deployment> find(ServiceKey key) {
            return Optional.ofNullable(deployments.get(key));
        }

        boolean remove(ServiceKey key) {
            return deployments.remove(key) != null;
        }

        Map<ServiceKey, Deployment> snapshot() {
            // The map structure is immutable in the returned snapshot.
            // Deployment objects remain mutable, so callers should not
            // treat this as a deep immutable snapshot.
            return Collections.unmodifiableMap(
                new HashMap<>(deployments)
            );
        }

        int size() {
            return deployments.size();
        }
    }

    static final class DeploymentMetrics {
        private final Map<Environment, Integer> stateCounts =
            new HashMap<>();

        void record(Deployment deployment) {
            stateCounts.merge(
                deployment.key().environment(), 1, Integer::sum
            );
        }

        Map<Environment, Integer> counts() {
            return Collections.unmodifiableMap(stateCounts);
        }
    }

    private static void demonstrateKeyValueOperations() {
        System.out.println("=== Enterprise deployment registry ===");

        DeploymentRegistry registry = new DeploymentRegistry();

        ServiceKey paymentsKey = new ServiceKey(
            "Payments", Environment.PRODUCTION
        );
        ServiceKey identityKey = new ServiceKey(
            "Identity", Environment.PRODUCTION
        );
        ServiceKey searchKey = new ServiceKey(
            "Search", Environment.STAGING
        );

        registry.register(new Deployment(
            paymentsKey, "3.4.1", DeploymentState.REGISTERED, 0
        ));
        registry.register(new Deployment(
            identityKey, "2.8.0", DeploymentState.REGISTERED, 0
        ));
        registry.register(new Deployment(
            searchKey, "1.9.2", DeploymentState.REGISTERED, 0
        ));

        // Records are used as composite keys because their generated
        // equals() and hashCode() methods use the component values.
        ServiceKey equivalentPaymentsKey = new ServiceKey(
            "payments", Environment.PRODUCTION
        );

        Deployment payments = registry.find(equivalentPaymentsKey)
            .orElseThrow();

        System.out.println("Found deployment: " + payments);
        payments.transitionTo(DeploymentState.HEALTHY);
        payments.upgrade("3.4.2", payments.revision());

        System.out.println("Updated deployment: " + payments);
        System.out.println("Registry size: " + registry.size());

        try {
            registry.register(new Deployment(
                equivalentPaymentsKey,
                "9.9.9",
                DeploymentState.REGISTERED,
                0
            ));
        } catch (IllegalStateException exception) {
            System.out.println(
                "Duplicate rejected: " + exception.getMessage()
            );
        }

        try {
            payments.upgrade("3.4.3", 0);
        } catch (IllegalStateException exception) {
            System.out.println(
                "Stale update rejected: " + exception.getMessage()
            );
        }

        try {
            payments.transitionTo(DeploymentState.RETIRED);
            payments.transitionTo(DeploymentState.HEALTHY);
        } catch (IllegalStateException exception) {
            System.out.println(
                "Invalid state transition: " + exception.getMessage()
            );
        }

        System.out.println(
            "Search removed: " + registry.remove(searchKey)
        );
        System.out.println(
            "Search still present: " + registry.find(searchKey).isPresent()
        );
    }

    private static void demonstrateFrequencyIndex() {
        System.out.println("\n=== Environment frequency index ===");

        List<String> deploymentEvents = List.of(
            "production", "staging", "production",
            "development", "production", "staging"
        );

        Map<String, Integer> frequency = new HashMap<>();

        for (String environment : deploymentEvents) {
            frequency.merge(environment, 1, Integer::sum);
        }

        // Sorting is used for deterministic presentation; HashMap itself
        // does not guarantee iteration order.
        Map<String, Integer> sorted = new TreeMap<>(frequency);
        System.out.println("Deployment counts: " + sorted);

        int productionCount = frequency.getOrDefault("production", 0);
        System.out.println("Production events: " + productionCount);
    }

    private static void demonstrateCollisionAndEquality() {
        System.out.println("\n=== Equality and collision behavior ===");

        Map<ServiceKey, String> map = new HashMap<>();

        ServiceKey first = new ServiceKey(
            "billing", Environment.PRODUCTION
        );
        ServiceKey equivalent = new ServiceKey(
            "BILLING", Environment.PRODUCTION
        );

        map.put(first, "version-4.1");
        map.put(equivalent, "version-4.2");

        System.out.println("Map size after equivalent-key update: " + map.size());
        System.out.println("Latest value: " + map.get(first));

        Set<Integer> distinctHashes = new HashSet<>();
        distinctHashes.add(first.hashCode());
        distinctHashes.add(equivalent.hashCode());

        if (distinctHashes.size() != 1) {
            throw new AssertionError("Equal keys must have equal hash codes");
        }

        // Unequal keys can still have the same hash code. HashMap resolves
        // collisions internally and verifies key equality before a match.
        Map<Integer, String> numericLookup = new HashMap<>();
        numericLookup.put(1, "service-A");
        numericLookup.put(17, "service-B");

        System.out.println("Numeric lookup: " + numericLookup.get(17));
    }

    private static void demonstrateMetrics() {
        System.out.println("\n=== Registry aggregation ===");

        List<Deployment> deployments = new ArrayList<>();
        deployments.add(new Deployment(
            new ServiceKey("api", Environment.PRODUCTION),
            "2.0", DeploymentState.HEALTHY, 1
        ));
        deployments.add(new Deployment(
            new ServiceKey("worker", Environment.PRODUCTION),
            "5.1", DeploymentState.DEGRADED, 2
        ));
        deployments.add(new Deployment(
            new ServiceKey("search", Environment.STAGING),
            "1.4", DeploymentState.HEALTHY, 3
        ));

        DeploymentMetrics metrics = new DeploymentMetrics();
        deployments.forEach(metrics::record);

        System.out.println("Environment counts: " + metrics.counts());
    }

    public static void main(String[] args) {
        demonstrateKeyValueOperations();
        demonstrateFrequencyIndex();
        demonstrateCollisionAndEquality();
        demonstrateMetrics();

        System.out.println("\nAll Java hash-table demonstrations completed.");
    }
}
