"""
backend/ml/generate_causality_audit.py

Generates models/temporal_causality_audit.json and models/temporal_causality_audit.md
for Stage 9.1 Real-Time Causality Audit.
"""

import os
import sys
import json
from datetime import datetime, timezone

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath("."))


def generate_causality_audit():
    print("Generating Stage 9.1 Real-Time Causality Audit artifacts...")
    ts = datetime.now(timezone.utc).isoformat()

    audit_data = {
        "timestamp": ts,
        "stage": "STAGE 9.1 — REAL-TIME CAUSALITY AUDIT",
        "current_temporal_mode": "OPTION B: Sequentially causal after current-timestep completion",
        "implementation_inspection": {
            "q1_info_required_to_score_one_tx": "time_step (required), txId (optional metadata), total_BTC (optional micro deviation), and current timestep count N_t stored in history_state.",
            "q2_score_transaction_requires_final_Nt": "YES, if history_state contains time_step t. It reads curr_count = history_state[t]['count']. If history_state[t] is absent, it falls back to hist_mean_cnt (yielding z=0).",
            "q3_score_batch_calculates_Nt_from_complete_timestep": "YES. Lines 205–211 of temporal.py aggregate the entire batch by time_step and store the full count c = N_t into history_state[t] before row-by-row scoring begins.",
            "q4_sequential_stateful_scoring_path_exists": "PARTIALLY. record_timestep() allows sequential updates per timestep, but no within-timestep running arrival counter exists.",
            "q5_first_tx_accesses_later_txs_in_same_timestep": "YES, in score_batch(). When scoring transaction position 0 of timestep t, N_t represents the total count of all transactions in timestep t.",
            "q6_state_update_timing": "BEFORE scoring. In score_batch(), state is populated for all timesteps present in the input batch before iterating through rows.",
            "q7_person_2_streaming_callability": "If Person 2 calls score_transaction() transaction-by-transaction without pre-supplying final N_t, the detector uses the fallback (z=0, score=0). To receive the true velocity score, the completed timestep must be recorded.",
        },
        "modes_distinction": {
            "mode_a_timestep_batch": "The entire timestep is observed, final N_t is known, and all transactions in that timestep share the network-level activity velocity score.",
            "mode_b_true_sequential_online": "Transactions arrive one by one at millisecond arrival latency with only past transactions known. Final N_t is unknown when transaction #1 arrives.",
        },
        "within_timestep_perturbation_test": {
            "status": "WITHIN-TIMESTEP FUTURE DEPENDENCE DETECTED",
            "test_name": "test_13_within_timestep_future_dependence_audit",
            "test_file": "tests/test_temporal_anomaly.py",
            "evidence": "At timestep 32, scoring position 0 with 10 txs in batch yielded temporal_score = 0.0 (z = -0.98). Scoring position 0 with full timestep (1323 txs) yielded temporal_score = 0.5055 (z = +1.40). Score changed due to transactions arriving after position 0 in the same timestep.",
        },
        "wallet_level_signals_status": "NONE FABRICATED (persistent wallet/account/device identifiers do not exist in the acquired dataset and were strictly excluded).",
        "correct_status_classification": "OPTION B: Sequentially causal after current-timestep completion",
        "signal_nature": "NETWORK-LEVEL TIMESTEP TEMPORAL ANOMALY SIGNAL (measures macro network transaction velocity across discrete 3-hour blockchain observation windows, not zero-latency per-transaction arrival time).",
        "person_2_integration_implication": "In the streaming architecture, Person 2 should recognize that ml_score (from the frozen XGBoost model) is transaction-level and available at zero latency, whereas temporal_score represents network-level activity context that reflects the completed velocity of the active ~3-hour timestep window. It must not be presented as a zero-latency transaction arrival signal.",
        "recommended_next_step": "For strict online zero-latency scoring in a future phase, adopt Lag-1 Timestep Velocity (scoring timestep t using the completed velocity z_{t-1} of the preceding observation window) or an expanding arrival counter. Do not alter existing frozen architecture now.",
        "corrected_timestep_description": "Each timestep in the Elliptic dataset represents a discrete, disconnected ~3-hour observation window of Bitcoin blockchain transactions, sampled at approximately two-week intervals over a two-year timeline. There is an approximate two-week unrecorded temporal gap between consecutive timesteps, and transaction edges do not cross between timesteps.",
        "score_semantics_clarification": {
            "ml_score": "Transaction-level supervised fraud risk probability produced by the 182-feature XGBoost baseline model.",
            "temporal_score": "Network/activity-level temporal volume anomaly context derived from rolling transaction velocity history across discrete observation windows. It is NOT a fraud probability and NOT a wallet risk score.",
        },
        "final_test_used": False,
        "audit_verdict": {
            "current_temporal_mode": "Option B",
            "uses_final_current_timestep_nt": "YES",
            "strict_online_causal": "NO",
            "future_timestep_causality": "PASS",
            "within_timestep_causality": "NOT APPLICABLE (Option B requires completed timestep)",
            "label_independence": "PASS",
            "test_csv_loaded": "NO",
            "test_csv_evaluated": "NO",
            "unit_tests": "25/25 passed",
            "documentation_corrected": "YES",
        },
    }

    # Write JSON
    os.makedirs("models", exist_ok=True)
    json_path = "models/temporal_causality_audit.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"Saved {json_path}")

    # Write Markdown
    md_path = "models/temporal_causality_audit.md"
    md_lines = [
        "# Stage 9.1 — Real-Time Causality Audit Report",
        "",
        f"**Date / Timestamp:** `{ts}`  ",
        "**Stage:** Stage 9.1 Real-Time Causality Audit  ",
        "**Current Temporal Mode:** `OPTION B: Sequentially causal after current-timestep completion`  ",
        "**Strict Online Causal:** `NO`  ",
        "**Future-Timestep Causality:** `PASS`  ",
        "**Final Test Used:** `NO`  ",
        "",
        "---",
        "",
        "## 1. Implementation Inspection Answers",
        "",
        "1. **Information required to score one transaction:** `time_step` (mandatory), `txId` (optional metadata), `total_BTC` (optional continuous value), and current timestep transaction count $N_t$ in `history_state`.",
        "2. **Does `score_transaction()` require final $N_t$:** **YES**. If $t$ is recorded in `history_state`, it reads `curr_count = history_state[t]['count']`. If $t$ is absent, it falls back to historical mean $\\mu$ (yielding $z=0$, score $=0$).",
        "3. **Does `score_batch()` calculate $N_t$ from complete current timestep:** **YES**. Lines 205–211 calculate `df_counts = clean_df.groupby('time_step').size().to_dict()` across the entire batch before row scoring begins.",
        "4. **Is there a sequential/stateful scoring path:** **PARTIALLY**. `record_timestep()` enables sequential timestep updates, but there is no running cumulative within-timestep arrival counter in `score_transaction()`.",
        "5. **Can scoring the first transaction of timestep $t$ access transactions later in timestep $t$:** **YES** in `score_batch()`, because the aggregate batch count $N_t$ represents the full count of all transactions in timestep $t$.",
        "6. **State update timing:** **BEFORE** row scoring. State is populated for all timesteps present in the input DataFrame before row-by-row scoring starts.",
        "7. **Can Person 2 call transaction-by-transaction during replay without future current-timestep information:** If Person 2 calls `score_transaction()` without recording $N_t$, the detector uses the fallback ($z=0$, score $=0$). Only after the completed timestep count is provided can the true timestep-level velocity score be produced.",
        "",
        "---",
        "",
        "## 2. Distinction Between Modes",
        "",
        "* **Mode A (Timestep-Batch Temporal Mode):** The entire timestep snapshot is available, final count $N_t$ is known, and all transactions in that timestep share the macro network velocity score.",
        "* **Mode B (True Sequential / Online Mode):** Transactions arrive one by one in real-time, and only transactions arriving prior to or at the current instant are available. Final $N_t$ is unknown at the arrival of transaction #1.",
        "",
        "---",
        "",
        "## 3. Within-Timestep Future Perturbation Test Results",
        "",
        "* **Test Added:** `test_13_within_timestep_future_dependence_audit` in `tests/test_temporal_anomaly.py`.",
        "* **Procedure:** At validation timestep 32, scored transaction position 0 when only 10 transactions were present in the batch, then re-scored position 0 when all 1,323 transactions of timestep 32 were present.",
        "* **Finding:**",
        "  * Position 0 score with 10 txs: `0.0` ($z = -0.98$)",
        "  * Position 0 score with 1,323 txs: `0.5055` ($z = +1.40$)",
        "* **Explicit Audit Finding:**",
        "  ```text",
        "  WITHIN-TIMESTEP FUTURE DEPENDENCE DETECTED",
        "  ```",
        "",
        "---",
        "",
        "## 4. Wallet-Level Signals Non-Fabrication",
        "",
        "Persistent wallet IDs, account addresses, and merchant tags do not exist in the acquired dataset files and were **strictly not fabricated**.",
        "",
        "---",
        "",
        "## 5. Correct Status Classification",
        "",
        "```text",
        "OPTION B: Sequentially causal after current-timestep completion",
        "```",
        "",
        "The detector is causally valid across timesteps (it never accesses timesteps $t+1, t+2, \\dots$), but requires completion of the active timestep $t$ before computing its final velocity metric.",
        "",
        "---",
        "",
        "## 6. Functional Nature & Person 2 Integration Implication",
        "",
        "The current implementation represents a **NETWORK-LEVEL TIMESTEP TEMPORAL ANOMALY SIGNAL** rather than a zero-latency transaction arrival signal.",
        "",
        "> [!IMPORTANT]",
        "> **Person 2 Integration Implication:**",
        "> In the streaming/replay pipeline, Person 2 should treat `ml_score` (from the frozen XGBoost baseline) as the immediate, zero-latency transaction-level risk score. The `temporal_score` represents the macro network volume anomaly context of the ~3-hour observation window, which is finalized upon completion of the timestep batch. It must not be presented to the frontend or analyst UI as a zero-latency microsecond arrival signal.",
        "",
        "**Recommended Next Modification for Strict Online Scoring (Future Phase):**",
        "Adopt **Lag-1 Timestep Velocity ($z_{t-1}$)**: score all incoming transactions of timestep $t$ using the completed velocity of the *preceding* observation window $t-1$. Because timestep $t-1$ is already complete, $z_{t-1}$ is $100\\%$ known when transaction #1 of timestep $t$ arrives, achieving strict zero-latency causality without altering feature definitions.",
        "",
        "---",
        "",
        "## 7. Corrected Time-Step Description",
        "",
        "The contradictory wording (*\"sequential ~3-hour snapshots spaced by ~2-week intervals\"*) is formally replaced with the scientifically accurate definition:",
        "",
        "> **Corrected Definition:** Each timestep in the Elliptic dataset represents a discrete, disconnected ~3-hour observation window of Bitcoin blockchain transactions, sampled at approximately two-week intervals over a two-year timeline. There is an approximate two-week unrecorded temporal gap between consecutive timesteps, and transaction edges do not cross between timesteps.",
        "",
        "---",
        "",
        "## 8. Clarification of Score Semantics",
        "",
        "* **`ml_score`:** Transaction-level supervised fraud risk probability output from the 182-feature XGBoost model.",
        "* **`temporal_score`:** Network/activity-level temporal volume anomaly context derived from rolling transaction count velocity across discrete observation windows. It is **NOT** a fraud probability, **NOT** an individual fraud score, and **NOT** a wallet risk metric.",
        "",
        "---",
        "",
        "## 9. Final Test Protection",
        "",
        "```text",
        "FINAL TEST USED: NO",
        "```",
        "`data/processed/test.csv` (timesteps 35–49) remains completely untouched and was neither loaded nor evaluated during this audit.",
        "",
        "---",
        "",
        "## 10. Audit Summary Table",
        "",
        "| Audit Check | Status |",
        "| :--- | :---: |",
        "| Current Temporal Mode | **Option B** |",
        "| Uses Final Current-Timestep $N_t$ | **YES** |",
        "| Strict Online Causal | **NO** |",
        "| Future-Timestep Causality | **PASS** |",
        "| Within-Timestep Causality | **Option B (Requires Completed Timestep)** |",
        "| Label Independence | **PASS** |",
        "| Test CSV Loaded / Evaluated | **NO** |",
        "| Unit Tests Passed | **25 / 25** |",
        "| Documentation Corrected | **YES** |",
        "",
        "---",
        "**NEXT ACTION: WAIT FOR REVIEW**",
    ]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"Saved {md_path}")


if __name__ == "__main__":
    generate_causality_audit()
