# Stage 10 — Reserved development pilot (not a manuscript or frozen holdout)

**Status (17 November 2026):** Implementation and independently audited **in-process synthetic engineering pilot** completed. **No real MQTT run or Stage 10 held-out inference is claimed here.** Stage 8/9 frozen protocols and outcomes are unchanged. Manuscript writing and submission remain on hold pending the professor's decision.

## Problem and selected engineering candidate

Stage 9 urgent push-out protected urgent alerts but **cancelled already admitted routine alerts**, reducing eventual routine completion. A new **Stage 10 `pushout_deferred`** mode preserves a displaced *routine* alert in SQLite WAL/FULL **before** removing it from the main waiting queue. One original worker eventually executes the stored alert after its main queue empties; the resulting physical work and SQLite commit are independently audited. The main queue has `K=3` waiting positions; the new bounded **pending** spool allows `B=8` more jobs. B represents **additional, non-free capacity**. Historical completed spool rows accumulate; B does *not* cap cumulative database file bytes.

When B is full, an arriving urgent still displaces the youngest waiting routine but that routine is explicitly **CANCELLED**, preserving the Stage 9 urgent-admission behavior. No active service is interrupted, and routine arrivals are rejected at a full main queue: B is reserved for already-admitted victims. No restart/replay recovery after process crash is implemented or tested. This is a bounded durable *deferral within a live run*, not verified crash recovery.

## Pilot scope, comparators, and metrics

- 10 **development-only** seeds `9001..9010` and **two separate exploratory batches**; 120 + 105 = **225 source-matched, individually independently audited in-process trials**. `pushout_reserved_deferred` was added *after* the first batch; its 5-seed results are explicitly post-hoc exploratory. Stage 9 heldout seeds `220001..220030` were **never accessed or reused for Stage 10 tuning**.
- 60 fictional IoT offers per seed: 15 urgent, 45 routine; artificial PBKDF2 work of 1/4/7 units plus real SQLite WAL/FULL commit; single non-preemptive worker. Artificial urgent 50 ms deadline, routine 20 ms timely-start threshold. Arrivals are scheduled by the synthetic fixture, not measured real-device traces.
- **U** = percent of *all offered* urgent alerts rejected, cancelled, or completed after local 50ms deadline (lower is better). **R** = percent of *all offered* routine alerts whose service started within 20ms (higher is better). **C** = percent of *all offered* routine alerts eventually completed by the end-of-run drain (higher is better). **C is not a deadline metric**; run drain after all offers is included.
- Comparators: FIFO+B8, strict urgent-first+B8 (**equal added capacity**), Stage 9 pushout strict+B0 (**no added capacity**), slack-aware pushout+B0, pushout+slack+B8, pushout+B8, and later 50% reservation+B8. All B8 variants have the same number of **pending** spool slots, although policies use them differently and may incur different SQLite overhead.
- All 225 raw ledgers and main/spool SQLite backups passed independent source/capacity/order/physical-output audit. Four cells in the first batch: burst K3, smooth K3, overload K3, burst K0. Second batch: burst K3, overload K3, variable work K3. There is no statistical claim or publication-grade inference from these tuning data.

### Development-pilot results — K3 burst, 10 seeds

| Policy | Buffer B | U urgent failure ↓ | R routine timely start ↑ | C routine eventual completion ↑ |
|---|---:|---:|---:|---:|
| FIFO + bounded spill | 8 | 47.33% | 22.67% | 67.11% |
| Strict urgent-first + bounded spill | 8 | 42.00% | 22.44% | 67.56% |
| Stage 9 urgent pushout + strict dispatch | 0 | 2.00% | 22.22% | 42.00% |
| **Stage 10 pushout + bounded deferred recovery** | **8** | **0.00%** | **22.00%** | **54.67%** |
| Pushout + slack dispatch + deferred recovery | 8 | 32.00% | 23.11% | 47.56% |
| Pushout + slack dispatch, no recovery | 0 | 10.67% | 28.89% | 42.00% |

**Interpretation:** The B8 recovery candidate completed **12.67 percentage points more routine offers than Stage 9 B0** in these pilot runs, while urgent misses were 0% vs 2%. **This is not a same-resource comparison.** Against the **equal-B8 Strict baseline**, the candidate had much lower urgent failure (0% vs 42%) but **12.89pp fewer eventual routine completions** (54.67% vs 67.56%). It does **not dominate** the matched baseline. Routine timely start stayed around 22%, far below a potential operational target of 75%.

### Development-pilot results — K3 overload, 10 seeds

| Policy | B | U ↓ | R ↑ | C ↑ |
|---|---:|---:|---:|---:|
| FIFO + bounded spill | 8 | 64.00% | 4.44% | 51.78% |
| Strict urgent-first + bounded spill | 8 | 57.33% | 3.33% | 55.56% |
| Stage 9 urgent pushout | 0 | 10.00% | 3.11% | 22.89% |
| **Stage 10 pushout + bounded deferred recovery** | **8** | **4.00%** | **2.67%** | **40.44%** |
| Pushout + slack dispatch + deferred recovery | 8 | 14.67% | 10.22% | 41.11% |

**Interpretation:** Overload is not solved. The candidate's urgent failure is 4%, its routine eventual completion is **40.44%** (vs 22.89% Stage9 B0, and 55.56% equal-B8 Strict), and its timely routine starts are **only 2.67%**. With sustained overload or infinitely long arrivals, finite B cannot guarantee eventual service or timeliness.

### Other checks

1. **Smooth** K3 (first 5 seeds): nearly every offered job completed across policies; added B provides little benefit when queue pressure is low.
2. **Variable work** K3 (second 5 seeds): performance was mostly near saturation; no universal advantage can be inferred.
3. **K0 negative control** (first 5 seeds): pushout cannot evict without waiting positions. Recovery-only pushout modes did not use B. In contrast, FIFO/Strict+B8 can spool newly rejected work; this is a *different admission policy*.
4. **Reservation ablation**, later 5 burst seeds only: `pushout_reserved_deferred` B8 gave U=6.67%, C=57.78%, with **14 cancellations** across seeds; straightforward `pushout_deferred` on those seeds gave U=0%, C=53.78%, with **2 cancellations**. The reservation variant gains completion but hurts urgency and displaces more accepted routines. It is **not** selected as the primary candidate.
5. Slack-aware dispatch used previously measured class service (last-16, empirical P90) and a 3ms guard, never hidden future work. Its burst urgent performance was worse than simple strict-priority service; **do not claim it improves deadlines**.

## Verification and replication (no holdout)

```bash
python -m unittest discover -s literature/validation -p 'test_stage10_bounded_recovery.py' -v
python experiments/stage10_development_pilot.py \
  --seeds 9001 9002 9003 9004 9005 \
  --cells burst smooth overload burst_K0 \
  --B 8 --transport inproc --out-dir stage10-pilot-batch-1
python experiments/stage10_development_pilot.py \
  --seeds 9006 9007 9008 9009 9010 \
  --cells burst overload variable \
  --B 8 --transport inproc --out-dir stage10-pilot-batch-2
python experiments/stage10_reaudit_development.py \
  --pilot-dir stage10-pilot-batch-1 stage10-pilot-batch-2
```

These use a new process per policy+fixture, preserve raw JSONL and separate main/spool SQLite backups, check SHA-256 and exact queue replay, validate all original/duplicate/invalid source attempts, and **fail closed** on a mismatch. **All 225 trials were re-audited successfully after the implementation was finalized**, using `stage10_reaudit_development.py`. `test_stage10_bounded_recovery.py` includes 13 passing tests, including tamper rejection, B=1 overflow/cancellation fallback and B8 50%-reserved capacity behavior. A GitHub pull-request CI workflow also runs a **separate reserved-seed real-MQTT smoke pilot** when available; those results must be reviewed separately, never folded into the in-process summary.

## Next scientific gate — not yet performed

1. Supervisor to confirm whether the **U vs C tradeoff and extra B8 buffer** are an acceptable research question; the algorithm components have **not been established as novel**.
2. Obtain real device arrival/service measurements or candidly restrict any claims to the artificial model; validate a practical urgent deadline and routine SLO with stakeholders.
3. Before seeing **fresh Stage 10 heldout** seeds, freeze a separate versioned protocol: primary comparison against **equal-B FIFO and Strict**, separate no-extra-B Stage9 rescue comparison, randomization, 30-seed paired confidence intervals, explicit negative results, run-horizon semantics and fail-closed independent audits.
4. Run a **first, immutable** real-MQTT heldout experiment *only after* the protocol/runner/CI and professor research scope are approved. Do not adapt thresholds after examining heldout results.
5. **No manuscript or submission** before professor go/no-go. This pilot is evidence for discussion, not a best-paper or publication-quality claim.
