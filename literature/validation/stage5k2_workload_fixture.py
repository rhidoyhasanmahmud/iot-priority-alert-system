#!/usr/bin/env python3
"""Deterministic *fictional* offer/work fixtures for an unapproved Stage 5K.2 pilot.

This is NOT an IoT deployment trace, measured handler calibration, simulator of
MQTT/SQLite timing, algorithm benchmark, or evidence of scheduler superiority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


GENERATOR_VERSION = "stage5k2-artificial-candidate-v1"
DEFAULT_HORIZON_NS = 1_000_000_000  # illustrative, NOT an operational target


def canonical_bytes(data: object) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rank(seed: int, channel: str, index: int) -> bytes:
    return hashlib.sha256(f"{GENERATOR_VERSION}|{seed}|{channel}|{index}".encode()).digest()


def rank_order(seed: int, channel: str, count: int) -> list[int]:
    return sorted(range(count), key=lambda i: (rank(seed, channel, i), i))


def offer_offset(index: int, count: int, horizon_ns: int, shape: str) -> int:
    """Same first/last offer time, with changed concentration only.

    Mapping uses integer arithmetic for stable reproducibility. For the
    clustered shape, 80% of event indices fall in the middle 20% of time.
    """
    u = index / (count - 1)
    if shape == "smooth":
        x = u
    elif shape == "clustered":
        if u <= 0.1:
            x = 4.0 * u
        elif u <= 0.9:
            x = 0.4 + 0.25 * (u - 0.1)
        else:
            x = 0.6 + 4.0 * (u - 0.9)
    else:
        raise ValueError(f"unknown shape: {shape}")
    return round(horizon_ns * x)


def build_fixture(
    *, seed: int, count: int, urgent_count: int, horizon_ns: int, shape: str, dispersion: str
) -> tuple[list[dict], list[dict], dict]:
    if seed < 0 or count < 4 or count % 2 != 0 or not (0 < urgent_count < count):
        raise ValueError("Require seed >= 0, even count >= 4, and 0 < urgent_count < count")
    if horizon_ns < 100 * (count - 1):
        raise ValueError("Horizon too short to distinguish planned offer instants")
    if shape not in {"smooth", "clustered"} or dispersion not in {"flat", "variable"}:
        raise ValueError("Unknown shape or work dispersion")

    urgent_ids = set(rank_order(seed, "class", count)[:urgent_count])
    low_work_ids = set(rank_order(seed, "work", count)[: count // 2])
    fixture_id = f"{GENERATOR_VERSION}-s{seed}-n{count}-u{urgent_count}-{shape}-{dispersion}-h{horizon_ns}"
    offers: list[dict] = []
    hidden: list[dict] = []

    for index in range(count):
        event_id = f"synthetic-s{seed:06d}-e{index:06d}"
        offers.append(
            {
                "fixture_id": fixture_id,
                "event_id": event_id,
                "trusted_class": "urgent" if index in urgent_ids else "routine",
                "planned_offer_offset_ns": offer_offset(index, count, horizon_ns, shape),
            }
        )
        hidden.append(
            {
                "event_id": event_id,
                "synthetic_required_work_units": (
                    4 if dispersion == "flat" else (1 if index in low_work_ids else 7)
                ),
            }
        )

    offsets = [row["planned_offer_offset_ns"] for row in offers]
    if offsets[0] != 0 or offsets[-1] != horizon_ns or offsets != sorted(set(offsets)):
        raise AssertionError("Invalid or colliding synthetic source offsets")

    offer_bytes = b"".join(map(canonical_bytes, offers))
    hidden_bytes = b"".join(map(canonical_bytes, hidden))
    manifest = {
        "generator_version": GENERATOR_VERSION,
        "fixture_id": fixture_id,
        "purpose": "synthetic_fixture_integrity_only_NOT_CALIBRATED_OR_SCIENTIFIC_RESULTS",
        "seed": seed,
        "count": count,
        "urgent_count": urgent_count,
        "routine_count": count - urgent_count,
        "shape": shape,
        "work_dispersion": dispersion,
        "planned_horizon_ns": horizon_ns,
        "first_offer_offset_ns": offsets[0],
        "last_offer_offset_ns": offsets[-1],
        "total_offered_synthetic_work_units": sum(row["synthetic_required_work_units"] for row in hidden),
        "mean_offered_synthetic_work_units": 4,
        "offer_sha256": digest(offer_bytes),
        "hidden_work_sha256": digest(hidden_bytes),
        "visibility": {
            "online_policy_input": "offers.jsonl: arrived jobs only, never future rows",
            "execution_model_only": "hidden_work.jsonl; not visible to dispatcher before service",
            "not_included": "real timestamps, measured service duration, device SLA, output outcomes",
        },
    }
    return offers, hidden, manifest


def save_fixture(output_dir: Path, *, seed: int, count: int, urgent_count: int,
                 horizon_ns: int, shape: str, dispersion: str) -> dict:
    offers, hidden, manifest = build_fixture(
        seed=seed, count=count, urgent_count=urgent_count, horizon_ns=horizon_ns,
        shape=shape, dispersion=dispersion,
    )
    output_dir.mkdir(parents=True, exist_ok=False)  # never overwrite someone else's fixture
    (output_dir / "offers.jsonl").write_bytes(b"".join(map(canonical_bytes, offers)))
    (output_dir / "hidden_work.jsonl").write_bytes(b"".join(map(canonical_bytes, hidden)))
    (output_dir / "manifest.json").write_bytes(canonical_bytes(manifest))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--count", type=int, default=60)
    parser.add_argument("--urgent-count", type=int, default=15)
    parser.add_argument("--horizon-ns", type=int, default=DEFAULT_HORIZON_NS)
    parser.add_argument("--shape", choices=["smooth", "clustered"], default="smooth")
    parser.add_argument("--dispersion", choices=["flat", "variable"], default="flat")
    args = parser.parse_args()
    result = save_fixture(
        args.out_dir, seed=args.seed, count=args.count, urgent_count=args.urgent_count,
        horizon_ns=args.horizon_ns, shape=args.shape, dispersion=args.dispersion,
    )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
