# Stage 9.1 — Real-Time Causality Audit Report

**Date / Timestamp:** `2026-10-07T08:33:28.861936+00:00`  
**Stage:** Stage 9.1 Real-Time Causality Audit  
**Current Temporal Mode:** `OPTION B: Sequentially causal after current-timestep completion`  
**Strict Online Causal:** `NO`  
**Future-Timestep Causality:** `PASS`  
**Final Test Used:** `NO`  

---

## 1. Implementation Inspection Answers

1. **Information required to score one transaction:** `time_step` (mandatory), `txId` (optional metadata), `total_BTC` (optional continuous value), and current timestep transaction count $N_t$ in `history_state`.
2. **Does `score_transaction()` require final $N_t$:** **YES**. If $t$ is recorded in `history_state`, it reads `curr_count = history_state[t]['count']`. If $t$ is absent, it falls back to historical mean $\mu$ (yielding $z=0$, score $=0$).
3. **Does `score_batch()` calculate $N_t$ from complete current timestep:** **YES**. Lines 205–211 calculate `df_counts = clean_df.groupby('time_step').size().to_dict()` across the entire batch before row scoring begins.
4. **Is there a sequential/stateful scoring path:** **PARTIALLY**. `record_timestep()` enables sequential timestep updates, but there is no running cumulative within-timestep arrival counter in `score_transaction()`.
5. **Can scoring the first transaction of timestep $t$ access transactions later in timestep $t$:** **YES** in `score_batch()`, because the aggregate batch count $N_t$ represents the full count of all transactions in timestep $t$.
6. **State update timing:** **BEFORE** row scoring. State is populated for all timesteps present in the input DataFrame before row-by-row scoring starts.
7. **Can Person 2 call transaction-by-transaction during replay without future current-timestep information:** If Person 2 calls `score_transaction()` without recording $N_t$, the detector uses the fallback ($z=0$, score $=0$). Only after the completed timestep count is provided can the true timestep-level velocity score be produced.

---

## 2. Distinction Between Modes

* **Mode A (Timestep-Batch Temporal Mode):** The entire timestep snapshot is available, final count $N_t$ is known, and all transactions in that timestep share the macro network velocity score.
* **Mode B (True Sequential / Online Mode):** Transactions arrive one by one in real-time, and only transactions arriving prior to or at the current instant are available. Final $N_t$ is unknown at the arrival of transaction #1.

---

## 3. Within-Timestep Future Perturbation Test Results

* **Test Added:** `test_13_within_timestep_future_dependence_audit` in `tests/test_temporal_anomaly.py`.
* **Procedure:** At validation timestep 32, scored transaction position 0 when only 10 transactions were present in the batch, then re-scored position 0 when all 1,323 transactions of timestep 32 were present.
* **Finding:**
  * Position 0 score with 10 txs: `0.0` ($z = -0.98$)
  * Position 0 score with 1,323 txs: `0.5055` ($z = +1.40$)
* **Explicit Audit Finding:**
  ```text
  WITHIN-TIMESTEP FUTURE DEPENDENCE DETECTED
  ```

---

## 4. Wallet-Level Signals Non-Fabrication

Persistent wallet IDs, account addresses, and merchant tags do not exist in the acquired dataset files and were **strictly not fabricated**.

---

## 5. Correct Status Classification

```text
OPTION B: Sequentially causal after current-timestep completion
```

The detector is causally valid across timesteps (it never accesses timesteps $t+1, t+2, \dots$), but requires completion of the active timestep $t$ before computing its final velocity metric.

---

## 6. Functional Nature & Person 2 Integration Implication

The current implementation represents a **NETWORK-LEVEL TIMESTEP TEMPORAL ANOMALY SIGNAL** rather than a zero-latency transaction arrival signal.

> [!IMPORTANT]
> **Person 2 Integration Implication:**
> In the streaming/replay pipeline, Person 2 should treat `ml_score` (from the frozen XGBoost baseline) as the immediate, zero-latency transaction-level risk score. The `temporal_score` represents the macro network volume anomaly context of the ~3-hour observation window, which is finalized upon completion of the timestep batch. It must not be presented to the frontend or analyst UI as a zero-latency microsecond arrival signal.

**Recommended Next Modification for Strict Online Scoring (Future Phase):**
Adopt **Lag-1 Timestep Velocity ($z_{t-1}$)**: score all incoming transactions of timestep $t$ using the completed velocity of the *preceding* observation window $t-1$. Because timestep $t-1$ is already complete, $z_{t-1}$ is $100\%$ known when transaction #1 of timestep $t$ arrives, achieving strict zero-latency causality without altering feature definitions.

---

## 7. Corrected Time-Step Description

The contradictory wording (*"sequential ~3-hour snapshots spaced by ~2-week intervals"*) is formally replaced with the scientifically accurate definition:

> **Corrected Definition:** Each timestep in the Elliptic dataset represents a discrete, disconnected ~3-hour observation window of Bitcoin blockchain transactions, sampled at approximately two-week intervals over a two-year timeline. There is an approximate two-week unrecorded temporal gap between consecutive timesteps, and transaction edges do not cross between timesteps.

---

## 8. Clarification of Score Semantics

* **`ml_score`:** Transaction-level supervised fraud risk probability output from the 182-feature XGBoost model.
* **`temporal_score`:** Network/activity-level temporal volume anomaly context derived from rolling transaction count velocity across discrete observation windows. It is **NOT** a fraud probability, **NOT** an individual fraud score, and **NOT** a wallet risk metric.

---

## 9. Final Test Protection

```text
FINAL TEST USED: NO
```
`data/processed/test.csv` (timesteps 35–49) remains completely untouched and was neither loaded nor evaluated during this audit.

---

## 10. Audit Summary Table

| Audit Check | Status |
| :--- | :---: |
| Current Temporal Mode | **Option B** |
| Uses Final Current-Timestep $N_t$ | **YES** |
| Strict Online Causal | **NO** |
| Future-Timestep Causality | **PASS** |
| Within-Timestep Causality | **Option B (Requires Completed Timestep)** |
| Label Independence | **PASS** |
| Test CSV Loaded / Evaluated | **NO** |
| Unit Tests Passed | **25 / 25** |
| Documentation Corrected | **YES** |

---
**NEXT ACTION: WAIT FOR REVIEW**
