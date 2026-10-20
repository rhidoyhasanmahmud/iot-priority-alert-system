# Application scenario and measurement boundary

The target is a gateway-side security event enrichment service for a building or small industrial site. Devices publish already-classified tampering alerts (high), repeated authentication-failure alerts (medium), and routine health events (low). The system does not detect intrusions or issue safety-critical control actions.

A receiver validates the message, deduplicates delivery IDs and enqueues work. A single worker enriches an alert with device context, applies a rule and records the outcome. That work can become slower than delivery during simultaneous reconnects or incident bursts. The current pilot models this service as a synthetic constant 10 ms cost; it does not benchmark actual enrichment or storage.

The research bottleneck is explicitly the application worker. Before using a real testbed result to support this assumption, measure broker forwarding time, receiver enqueue time, queue residence, dispatch cost and processing time separately. If network or broker delay dominates, the proposed scheduler cannot be credited for solving that bottleneck.

| Class | Example | Illustrative receiver-local deadline |
| --- | --- | --- |
| High | Device tampering alert | 100 ms |
| Medium | Repeated authentication-failure alert | 500 ms |
| Low | Routine device health record | 2000 ms |

These are experimental service budgets, not requirements from a real operator or a standard. Validate them with a deployment owner before making application claims; sweep the budgets in sensitivity tests. The pilot priorities are random synthetic class labels and are not real security detections.

Trust boundary: priority and deadlines come from a trusted local configuration. Priority spoofing, attack-detection accuracy, safety response, network reservation and availability under adversarial floods are outside the initial claim. Security-related event names do not make this a cybersecurity detection contribution.
