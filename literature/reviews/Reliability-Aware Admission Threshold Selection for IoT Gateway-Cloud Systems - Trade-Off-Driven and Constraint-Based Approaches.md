# Reliability-Aware Admission Threshold Selection for IoT Gateway–Cloud Systems: Trade-Off-Driven and Constraint-Based Approaches

## 1. Bibliographic record and source

- **Review 17 · R26 · core-related finite-buffer admission mechanism.** Reliability is a model condition; this paper does not differentiate urgent/routine classes.
- **Author:** Shensheng Tang.
- **Publication:** IoT, 7(3), article 60, 2026. Publisher: MDPI. Published 31 July 2026.
- **DOI:** [10.3390/iot7030060](https://doi.org/10.3390/iot7030060). [Official article](https://www.mdpi.com/2624-831X/7/3/60), author/title/venue/DOI verified on 15 November 2026.
- The publication title uses a gateway-cloud en dash; the filename uses a plain hyphen for portability. Identity is anchored by DOI, not punctuation.
- **Read source:** supplied `Reliability-Aware_Admission_Threshold_Selection_fo.pdf`, 23 pages; PDF page = printed article page. `IoT-07-00060.pdf` and `b878b67cab2aea10857190bd6320c96b465e.pdf` are byte-identical copies, not separate papers. All share SHA-256 `e6eafa8059d3be71c8dc8840a083ef55059055e501b78c8194d11c47842f4d6d`.
- Full-text critical review with visually checked generator/results. A limited independent baseline stationary calculation is described in Section 7; the entire numerical study and deployment performance were not replicated. PDF not redistributed. No quartile/indexing claim.

## 2. Research problem

A finite-buffer gateway admits offered tasks while gateway/cloud failures suspend service. Permissive admission can improve delivered work but reduce free buffer space and increase saturation. The design decision is a threshold controlling when admission becomes probabilistic, chosen either by weighted utility or explicit saturation/headroom constraints (Sections 2-5).

This contributes directly to overload/admission reasoning. It does not choose which queued urgent or routine task runs next.

## 3. Authors' claimed contribution

The paper combines a finite level-dependent quasi-birth-and-death (LD-QBD) model, failure/repair states, four stationary metrics, and two threshold-selection paradigms. It contrasts a weighted optimum with a largest-feasible threshold and examines sensitivity to load, buffer size and reliability.

The word adaptation describes thresholds recalculated across stationary parameter settings. The author explicitly distinguishes this from online learning or real-time control (Section 6.5, pp. 18-19). General bursts, service differentiation and online threshold adaptation are future work (pp. 21-22).

## 4. Model and assumptions

- Offered arrivals are Poisson with state-independent rate lambda; the finite occupancy n ranges from 0 through K. Rejected tasks leave immediately. Admission changes accepted traffic, not the source-offered process (p. 5).
- Gateway and cloud are independent two-state Markov failure/repair processes. Phase `(g,c)` uses 0 for up, 1 for down. Admitted tasks are retained through outages; departures occur only in phase `(0,0)` at rate mu_g. The CTMC departure-rate abstraction implies memoryless service while available, rather than a general service-time distribution (pp. 6-8).
- Admissions are possible when the gateway is up, including while the cloud is down; a gateway-down arrival is not admitted. Thus both failures suspend service, but the arrival matrix does not treat their admission consequences identically.
- State space has `4*(K+1)` states. Upward transitions use `lambda*p(n)*diag(1,1,0,0)`; downward transitions use `mu_g*diag(1,0,0,0)`; phase transitions encode failures/repairs (Equations 2-10, pp. 7-8).
- No class labels, deadlines, expiry, size-dependent service or routine quota. A task may eventually complete after a long outage without being timely for an alert application.
- Baseline: K=20, lambda=8, mu_g=10, gateway failure/repair 0.05/0.5 and cloud failure/repair 0.04/0.4; weights alpha=0.5, beta=2; constraints saturation <=0.05 and normalized headroom >=0.3 (p. 16).

## 5. Method and decision mechanism

For an up gateway, Equation 1 (p. 6) uses:

`p(n) = 1` when `n < Nth`; `p(n) = (K-n)/(K-Nth)` when `Nth <= n < K`; `p(K)=0`.

A smaller threshold begins rejection earlier. For each integer `Nth` from 1 to K-1, solve the stationary balance equations `pi*Q=0`, `sum(pi)=1` and compute:

- `D_eff = throughput/lambda`: completion rate divided by **offered** rate (Equation 11).
- `P_CR = Pr(N>=Nth)`: fraction of time within the policy's throttling region (Equation 12).
- `P_sat = Pr(N=K)`: full-buffer probability at a fixed physical boundary (Equation 13).
- `H_soft = E[K-N]/K`: average normalized free space (Equation 14).

Weighted selection maximizes `J = D_eff - alpha*P_CR - beta*P_sat` over the threshold grid (Equations 15-16, Algorithm 1). Constraint-based selection maximizes deliverability under the saturation/headroom limits, implemented by taking the largest feasible threshold (Equations 17-18, Algorithm 2). Unimodality and monotonic/contiguous feasibility are adopted structural assumptions supported numerically in the examined ranges, not universally proved properties (pp. 12-14).

The enumeration requires O(K) stationary solves. That is not a claim that total arithmetic cost is O(K): each solve has a K-dependent state dimension. Empty feasible sets, tie rules, parameter estimation, monitoring cadence and transient reconfiguration require additional operational decisions.

## 6. Evidence ledger

| Claim examined | Source location | Actual evidence | Interpretation boundary |
| --- | --- | --- | --- |
| Admission controls a measurable deliverability/buffer trade-off | Equations 1, 11-14, pp. 6-9; Figure 1, p. 16 | Threshold changes admission while offered rate and service/failure processes stay fixed; reported deliverability rises, headroom falls and saturation rises. | Poisson stationary model, not a measured alarm-burst recovery experiment. |
| Less congestion-control activity can coexist with worse saturation | Section 3.2, p. 10; Figure 1, p. 16 | P_CR falls as its boundary moves with Nth, while P_sat rises. The author explicitly explains the policy-dependent metric. | Falling P_CR does not mean less physical congestion at the same queue level. |
| The two design objectives choose different thresholds | Figures 2-3, pp. 17-18; Section 6.3 | Baseline weighted threshold is 15; largest feasible threshold is 18. Limited independent stationary recalculation matches both. | These values depend on the stated rates, weights and constraints; they are not transferable default settings. |
| Reliability-aware adaptation is demonstrated | Figures 4-6, pp. 18-19 | Numerical sweeps vary capacity, failure intensity and offered load; selected thresholds generally become more conservative with degradation. | Parameter-sweep sensitivity, not an implemented online controller; no measured response to changing conditions or estimation errors. |
| Constraint selection supplies operational protection | Equations 17-18; Algorithms 1-2, pp. 12-14 | The selected stationary model point satisfies prescribed P_sat/H_soft inequalities when feasible. | Stationary probabilities and average headroom do not impose a sample-path queue bound, deadline bound or class-fairness guarantee. |

## 7. Critical appraisal

**Useful evidence.** Separating offered from admitted work prevents a common misleading comparison: lower queueing pressure can result from rejecting more tasks. The moving P_CR boundary is disclosed rather than treated as a fixed congestion measure. The generator and metrics are sufficiently explicit for a small baseline consistency check.

**Limited independent numerical check.** Construct the 84-state CTMC for K=20 with phase index `2*g+c`, add the admission/service/failure/repair rates from Equations 4-7, set each diagonal to minus its off-diagonal row sum, then solve normalized stationary balance for Nth=1,...,19. This review used a dense double-precision linear solve; it is a check of the stated baseline, not a reproduction of all figures or an experimental validation of the model.

| Threshold | D_eff | P_CR | P_sat | H_soft | J |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 14 | 0.851767 | 0.121918 | 0.030385 | 0.719420 | 0.730038 |
| 15 | 0.853447 | 0.110383 | 0.034076 | 0.713454 | 0.730104 |
| 18 | 0.857493 | 0.079939 | 0.048578 | 0.697882 | 0.720369 |
| 19 | 0.858432 | 0.069938 | 0.055725 | 0.694047 | 0.712014 |

The maximizing weighted threshold is 15; 19 violates the 0.05 saturation limit, leaving 18 as the largest feasible threshold. Normalization and stationarity residuals were checked at floating-point tolerance. J(15)-J(14) is only about 0.000066: the exact maximizing integer is less consequential than its sensitivity/near-optimal neighborhood, which should be reported before calling the configuration robust.

**Construct limits.** With no post-admission discards and stationary flow conservation, completion rate equals accepted rate. D_eff therefore captures rejection/loss relative to offered work, not a probability of completing before an alert deadline. P_sat is not total rejection probability: probabilistic throttling and gateway-down rejection occur away from a full buffer. P_CR is a control-activity measure with a moving threshold.

**External and theoretical limits.** Poisson arrivals, independent exponential outages and the single aggregate service abstraction exclude correlated bursts/failures, heterogeneous service and urgency classes. The finite state space permits stationary calculation but does not establish timeliness. Numerical monotonicity does not prove all parameter cases; early termination of feasibility searches relies on that structure. Explicit rejection outcomes during both failure states and feasibility checks under parameter uncertainty would be needed for deployment.

**Research use:** retain as a clear analytical admission study with a successful limited baseline check. Do not adopt its parameter values or claim it is an online, deadline-aware or starvation-protecting alert scheduler.

## 8. Synthesis contribution and open question

Compare RAAC with [finite-buffer network control](Optimal%20Control%20of%20Wireless%20Networks%20With%20Finite%20Buffers.md): RAAC immediately rejects non-admitted tasks; the older network model retains source traffic in unlimited reservoirs. Their claims about internal saturation and delivered work use different boundaries. Compare class-neutral admission here with TRIAGE/4's semantic admission/priority handling.

**Open reading question:** which class-aware admission methods jointly account for offered-task urgent failures, routine rejection/waiting, and recovery after correlated bursts/outages? The present paper provides a stationary reference case, not evidence that this broader question is unanswered.

**Bangla note:** কম buffer pressure দেখলেই ভালো system বলা যাবে না; কত offered task reject হয়েছে এবং accepted task সময়মতো শেষ হয়েছে কি না, আলাদা করে দেখতে হবে।

[Register](../README.md) · [Comparison](../synthesis/comparison.csv) · [Synthesis](../synthesis/findings.md)
