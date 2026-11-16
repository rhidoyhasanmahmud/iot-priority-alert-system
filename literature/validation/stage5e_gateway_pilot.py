#!/usr/bin/env python3
"""Stage 5E two-class, finite-K *measurement feasibility* gateway.

This is a synthetic CPU-handler laboratory probe, NOT a real device, security
enrichment system or research algorithm. FIFO only. The optional MQTT mode
requires a separately running broker and Eclipse Paho MQTT client 2.x.

Examples:
  python3 stage5e_gateway_pilot.py --self-test
  python3 stage5e_gateway_pilot.py --shape burst --output pilot.jsonl
  python3 stage5e_gateway_pilot.py --transport mqtt --host 127.0.0.1 --output mqtt.jsonl
"""

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import statistics
import threading
import time
import uuid

from stage5d_lifecycle_audit import audit


def now():
    return time.monotonic_ns()


def payloads(n):
    """Same ordered class and work-intensity sequence for every traffic shape."""
    records = []
    for i in range(n):
        records.append({"event_id": f"evt_{i:05d}",
                        "kind": "tamper" if i % 4 == 0 else "health",
                        "cpu_iterations": (4_000, 8_000, 16_000)[i % 3]})
    return records


def scheduled_gaps_ns(n, shape):
    # Every run starts with the same 0-gap first event. Units are SOURCE schedule
    # targets, not guaranteed receiver/offered times.
    gaps = [0] + [8_000_000] * (n - 1)
    if shape == "base":
        return gaps
    if shape == "overload":
        return [0] * n  # INTENSITY CHANGE: the source horizon shrinks.
    if shape != "burst":
        raise ValueError("shape must be base/burst/overload")
    lo, hi = n // 3, 2 * n // 3
    removed = sum(gaps[lo:hi])
    for i in range(lo, hi):
        gaps[i] = 0
    # Identical source horizon and work/class sequence as base, not identical
    # actually-offered gateway timestamps (threading, MQTT, OS can add drift).
    outside = [i for i in range(1, n) if not lo <= i < hi]
    if not outside:
        raise ValueError("need source gaps outside the burst window")
    q, rem = divmod(removed, len(outside))
    for j, i in enumerate(outside):
        gaps[i] += q + (j < rem)
    assert sum(gaps) == 8_000_000 * (n - 1)
    return gaps


class PilotGateway:
    """Nonpreemptive FIFO worker with K waiting and one reserved/running slot."""

    def __init__(self, *, run_id, K, tau_ns, urgent_deadline_offset_ns):
        self.run_id = run_id
        self.K = K
        self.tau_ns = tau_ns
        self.urgent_offset = urgent_deadline_offset_ns
        self.condition = threading.Condition()
        self.waiting = deque()
        self.active = None
        self.seen = set()  # scoped to this freshly constructed run
        self.attempts = []
        self.offers = []
        self.closed = False
        self.worker_errors = []
        self.worker = threading.Thread(target=self._serve, name="stage5e-fifo-worker", daemon=True)
        self.worker.start()

    def receive(self, raw):
        # This timestamp is outside the modeled scheduling queue. In MQTT mode
        # it is captured at the FIRST line of the Paho on_message callback.
        callback = now()
        attempt_id = f"attempt_{uuid.uuid4().hex}"
        try:
            doc = json.loads(raw)
            if not isinstance(doc, dict) or set(doc) != {"event_id", "kind", "cpu_iterations"}:
                raise ValueError("unexpected payload shape")
            eid, kind, work = doc["event_id"], doc["kind"], doc["cpu_iterations"]
            if not isinstance(eid, str) or not eid or kind not in ("tamper", "health"):
                raise ValueError("invalid ID/kind")
            if type(work) is not int or not 1 <= work <= 100_000:
                raise ValueError("unsafe synthetic work amount")
        except (ValueError, TypeError, UnicodeDecodeError):
            with self.condition:
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": None,
                                      "callback_ns": callback,
                                      "validation_end_ns": now(), "disposition": "INVALID"})
                self.condition.notify_all()
            return

        # Trusted class is derived AFTER validation in this fictional laboratory
        # mapping. It is NOT an authenticated field/security classifier.
        cls = "URGENT" if kind == "tamper" else "ROUTINE"
        with self.condition:
            require_open = not self.closed
            if not require_open:
                raise RuntimeError("callback after gateway closed")
            if eid in self.seen:
                disposition = "DUPLICATE"
                validation_end = now()
                self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                      "attempt_id": attempt_id, "event_id": eid,
                                      "callback_ns": callback, "validation_end_ns": validation_end,
                                      "disposition": disposition})
                self.condition.notify_all()
                return
            self.seen.add(eid)
            validation_end = now()
            offered = now()  # after validation + dedup, before capacity decision
            busy, waiting = self.active is not None, len(self.waiting)
            rejected = busy and waiting >= self.K
            row = {"type": "offer", "run_id": self.run_id,
                   "event_id": eid, "attempt_id": attempt_id, "trusted_class": cls,
                   "offer_ns": offered, "waiting_at_offer": waiting,
                   "running_at_offer": busy,
                   "urgent_deadline_ns": (offered + self.urgent_offset if cls == "URGENT" else None),
                   "terminal": "REJECTED" if rejected else "UNRESOLVED",
                   "start_ns": None, "complete_ns": None}
            self.attempts.append({"type": "attempt", "run_id": self.run_id,
                                  "attempt_id": attempt_id, "event_id": eid,
                                  "callback_ns": callback, "validation_end_ns": validation_end,
                                  "disposition": "OFFERED"})
            self.offers.append(row)
            if not rejected:
                job = (row, work)
                if self.active is None:
                    # This slot counts as running/reserved for admission, even
                    # if worker thread has not yet entered the handler.
                    self.active = job
                else:
                    self.waiting.append(job)
            self.condition.notify_all()

    @staticmethod
    def _synthetic_cpu_handler(row, work):
        # Actual CPU computation, rather than time.sleep(service_ms).
        # This does NOT represent measured real IoT enrichment/rule/I/O time.
        digest = hashlib.pbkdf2_hmac("sha256", row["event_id"].encode(),
                                     b"stage5e-lab-only", work)
        # Deterministic tiny surrogate rule and in-memory result serialization.
        return json.dumps({"id": row["event_id"], "flag": digest[0] % 2 == 0})

    def _serve(self):
        try:
            while True:
                with self.condition:
                    while self.active is None:
                        if self.closed:
                            return
                        self.condition.wait()
                    row, work = self.active
                    row["start_ns"] = now()
                self._synthetic_cpu_handler(row, work)
                with self.condition:
                    row["complete_ns"] = now()
                    row["terminal"] = "COMPLETED"
                    self.active = self.waiting.popleft() if self.waiting else None
                    self.condition.notify_all()
        except Exception as exc:  # An incomplete run must never be silently reported successful.
            with self.condition:
                self.worker_errors.append(repr(exc))
                self.closed = True
                self.condition.notify_all()

    def callback_count(self):
        with self.condition:
            return len(self.attempts)

    def shutdown_and_drain(self, timeout_s=30.0):
        deadline = time.monotonic() + timeout_s
        with self.condition:
            self.closed = True
            self.condition.notify_all()
            while (self.active is not None or self.waiting) and not self.worker_errors:
                left = deadline - time.monotonic()
                if left <= 0:
                    break
                self.condition.wait(timeout=left)
        self.worker.join(timeout=1)
        if self.worker_errors:
            raise RuntimeError(f"synthetic worker failed: {self.worker_errors}")
        with self.condition:
            return (self.active is None and not self.waiting and not self.worker.is_alive(),
                    list(self.attempts), list(self.offers), now())


def publish_schedule(gateway, events, gaps, *, deliver, duplicate_every=13, add_invalid=True):
    assert len(events) == len(gaps)
    published = []
    deadline = time.monotonic_ns()
    for i, (ev, gap) in enumerate(zip(events, gaps)):
        deadline += gap
        while (remaining := (deadline - now()) / 1e9) > 0:
            time.sleep(min(remaining, .02))  # SOURCE pacing ONLY; not handler service
        raw = json.dumps(ev, sort_keys=True).encode()
        deliver(raw)
        published.append({"type": "published", "run_id": gateway.run_id,
                          "event_id": ev["event_id"],
                          "publisher_clock_note": "logical source; do not subtract source timestamp"})
        if duplicate_every and (i + 1) % duplicate_every == 0:
            deliver(raw)
    if add_invalid:
        deliver(b"{not-json")
    return published


def mqtt_publisher_and_receiver(gateway, events, gaps, host, port, timeout_s):
    # Import on demand: local tests require zero third-party libraries.
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("MQTT mode requires Eclipse paho-mqtt 2.x and a running broker") from exc
    topic = "research/stage5e/" + gateway.run_id
    subscribed = threading.Event()
    failures = []
    sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                      client_id="stage5e-subscriber-" + gateway.run_id)

    def on_connect(client, userdata, flags, reason_code, properties):
        if getattr(reason_code, "is_failure", False):
            failures.append("subscriber connection refused")
        else:
            client.subscribe(topic, qos=1)

    def on_subscribe(client, userdata, mid, reason_codes, properties):
        if any(getattr(r, "is_failure", False) for r in reason_codes):
            failures.append("subscription failed")
        else:
            subscribed.set()

    sub.on_connect = on_connect
    sub.on_subscribe = on_subscribe
    sub.on_message = lambda client, userdata, message: gateway.receive(message.payload)
    pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                      client_id="stage5e-publisher-" + gateway.run_id)
    publisher_connected = threading.Event()

    def publisher_on_connect(client, userdata, flags, reason_code, properties):
        if getattr(reason_code, "is_failure", False):
            failures.append("publisher connection refused")
        else:
            publisher_connected.set()

    pub.on_connect = publisher_on_connect
    started_sub = started_pub = False
    publish_infos = []
    try:
        sub.connect(host, port, keepalive=30)
        sub.loop_start()
        started_sub = True
        if not subscribed.wait(timeout_s) or failures:
            raise RuntimeError(f"subscriber did not subscribe within timeout: {failures}")
        pub.connect(host, port, keepalive=30)
        pub.loop_start()
        started_pub = True
        if not publisher_connected.wait(timeout_s) or failures:
            raise RuntimeError(f"publisher did not connect within timeout: {failures}")

        def deliver(raw):
            info = pub.publish(topic, raw, qos=1)
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"publisher enqueue failed with rc={info.rc}")
            # Do NOT block the publisher after every event: that would change
            # the source burst shape into an ACK-paced closed-loop workload.
            publish_infos.append(info)

        published = publish_schedule(gateway, events, gaps, deliver=deliver)
        for info in publish_infos:
            info.wait_for_publish(timeout=timeout_s)
            if not info.is_published():
                raise RuntimeError("publisher QoS1 confirmation missing")
        expected_callbacks = len(events) + len(events) // 13 + 1
        until = time.monotonic() + timeout_s
        while gateway.callback_count() < expected_callbacks and time.monotonic() < until:
            time.sleep(.01)
        # QoS1 broker/network retries may produce extra callbacks. The Stage 5F
        # gate independently verifies that every intended logical ID was offered;
        # an exact attempt-count equality would reject legitimate redeliveries.
        captured_all_intended = gateway.callback_count() >= expected_callbacks
        # Full ACK'd source list does not prove broker-to-subscriber delivery.
        return published, captured_all_intended, expected_callbacks
    finally:
        if started_pub:
            pub.disconnect()
            pub.loop_stop()
        if started_sub:
            sub.disconnect()
            sub.loop_stop()


def run_pilot(*, transport, shape, event_count, K, urgent_deadline_ms,
              routine_tau_ms, host="127.0.0.1", port=1883, timeout_s=15):
    if not (6 <= event_count <= 10_000) or not (0 <= K <= 10_000) or urgent_deadline_ms <= 0 or routine_tau_ms <= 0:
        raise ValueError("6<=event_count<=10000, 0<=K<=10000, positive timing budgets required")
    run_id = "s5e-" + uuid.uuid4().hex[:14]
    events = payloads(event_count)
    gaps = scheduled_gaps_ns(event_count, shape)
    provenance = hashlib.sha256(json.dumps({"events": events, "gaps_ns": gaps},
                                           sort_keys=True).encode()).hexdigest()
    gateway = PilotGateway(run_id=run_id, K=K,
                           tau_ns=int(routine_tau_ms * 1e6),
                           urgent_deadline_offset_ns=int(urgent_deadline_ms * 1e6))
    try:
        if transport == "inproc":
            published = publish_schedule(gateway, events, gaps, deliver=gateway.receive)
            captured_all, expected = True, event_count + event_count // 13 + 1
        elif transport == "mqtt":
            published, captured_all, expected = mqtt_publisher_and_receiver(
                gateway, events, gaps, host, port, timeout_s)
        else:
            raise ValueError("transport must be inproc/mqtt")
    finally:
        drained, attempts, offers, cutoff = gateway.shutdown_and_drain(timeout_s=timeout_s)

    manifest = {"type": "manifest", "run_id": run_id,
                "policy_id": "fifo", "scenario_id": f"stage5e_{transport}_{shape}",
                "trace_provenance": "deterministic_synthetic_lab_trace_sha256=" + provenance,
                "K": K, "routine_tau_ns": int(routine_tau_ms * 1e6),
                "observation_end_ns": cutoff,
                "clock_domain": "single_gateway_process_monotonic_ns",
                "dedup_cache_reset": True, "publisher_log_complete": True,
                "receiver_capture_complete": captured_all}
    rows = [manifest, *published, *attempts, *offers]
    summary = audit(rows)
    summary.update({"transport": transport, "source_shape": shape,
                    "trace_sha256": provenance, "drained": drained,
                    "callback_expected": expected, "callback_observed": len(attempts),
                    "meaning": "synthetic CPU work; no real IoT/service requirement calibration"})
    return rows, summary


def self_test():
    results = []
    for K in (0, 3):
        for shape in ("base", "burst", "overload"):
            rows, result = run_pilot(transport="inproc", shape=shape, event_count=36,
                                     K=K, urgent_deadline_ms=50, routine_tau_ms=50)
            assert result["drained"] and result["offered_unique"] == 36
            assert result["delivery_attempts"] == 36 + 36 // 13 + 1
            assert result["duplicates"] == 36 // 13
            assert result["invalid_attempts"] == 1
            assert result["admitted"] + result["rejected"] == 36
            assert result["urgent_failure_U_bounds"]["exact"] is not None
            assert result["routine_timely_start_R_bounds"]["exact"] is not None
            assert all(row["terminal"] in ("COMPLETED", "REJECTED")
                       for row in rows if row["type"] == "offer")
            results.append((K, shape, result))
            print(f"PASS in-process K={K} shape={shape}: "
                  f"offers=36 rejected={result['rejected']} "
                  f"completed={result['measured_completed_service_n']}")
    # Paired source traces preserve class/work order; burst preserves source
    # horizon, but the overload intervention intentionally does not.
    assert sum(scheduled_gaps_ns(36, "base")) == sum(scheduled_gaps_ns(36, "burst"))
    assert sum(scheduled_gaps_ns(36, "overload")) == 0
    print("PASS paired source-horizon and overload-confound checks")
    print("PASS 6/6 in-process gateway ledger audits; MQTT NOT EXECUTED")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--transport", choices=("inproc", "mqtt"), default="inproc")
    p.add_argument("--shape", choices=("base", "burst", "overload"), default="burst")
    p.add_argument("--events", type=int, default=60)
    p.add_argument("--queue-capacity", type=int, default=3)
    p.add_argument("--urgent-deadline-ms", type=float, default=50.0)
    p.add_argument("--routine-tau-ms", type=float, default=50.0)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--timeout-s", type=float, default=15.0)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    if args.timeout_s <= 0 or not 1 <= args.port <= 65535:
        p.error("positive --timeout-s and a valid --port are required")
    if args.self_test:
        self_test()
        return
    if args.output is None:
        p.error("--output required for a recorded pilot")
    rows, summary = run_pilot(transport=args.transport, shape=args.shape,
                              event_count=args.events, K=args.queue_capacity,
                              urgent_deadline_ms=args.urgent_deadline_ms,
                              routine_tau_ms=args.routine_tau_ms,
                              host=args.host, port=args.port, timeout_s=args.timeout_s)
    args.output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                           encoding="utf-8")
    print(json.dumps({"ledger": str(args.output), **summary}, indent=2, sort_keys=True))
    if not summary["drained"] or (args.transport == "mqtt" and not summary["receiver_capture_complete"]):
        p.exit(2, "INCOMPLETE pilot: diagnostic ledger saved; do not use as a fully reconciled run\n")


if __name__ == "__main__":
    main()
