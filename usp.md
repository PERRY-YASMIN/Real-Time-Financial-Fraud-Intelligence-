# TRACE: Threat Reconstruction and Attack Chain Evidence
**Product & System Specification**  
**Problem Statement:** HNX26PSI03 — AI-Powered Cyber Threat Intelligence  
**Institution:** Karunya Institute of Technology and Sciences — Internal Qualifier Hackathon  
**Target Delivery Window:** 24 Hours  

> **Core Product Vision:**  
> *"Don't just detect the attack. Reconstruct the story."*

---

## 1. Product Overview

Traditional security tools flood security analysts with disconnected, individual alerts. An isolated failed login, an unfamiliar device connection, or an elevated command are often flagged independently. Analysts are left to manually stitch these clues together across massive volumes of telemetry to understand what actually occurred.

**TRACE (Threat Reconstruction and Attack Chain Evidence)** is an AI-powered attack investigation system that ingests fragmented security logs across distributed enterprise entities, links them into a connected knowledge graph, filters out routine benign background noise, and reconstructs the full multi-stage attack story.

TRACE does not treat security events in isolation. Instead, it traces how an adversary moves from initial entry to ultimate impact across:
- **Users**
- **Devices**
- **IP addresses**
- **Applications and processes**
- **Files and resources**

Crucially, TRACE operates on an **evidence-first, deterministic foundation**. It avoids relying on generative language models to guess or hallucinate attack conclusions. Every attack stage surfaced by TRACE is backed by verifiable, inspectable raw event records.

---

## 2. Problem Statement Alignment (HNX26PSI03)

The following matrix maps the mandatory requirements and evaluation criteria of **HNX26PSI03** directly to TRACE's system architecture:

| Problem Statement Requirement | How TRACE Satisfies It | Implementation Component |
|---|---|---|
| **Connect events across Users** | Tracks user accounts across authentication, host sessions, and resource accesses. Links identities across disparate log sources. | `engine/entity_linker.py` |
| **Connect events across Devices** | Binds endpoint hostnames, machine IDs, and servers into the shared entity graph. | `engine/entity_linker.py` |
| **Connect events across IP Addresses** | Correlates internal IP addresses, external ingress IPs, and egress destinations. | `engine/entity_linker.py` |
| **Connect events across Applications/Processes** | Maps process execution hierarchies, command-line activity, and client applications. | `engine/graph_builder.py` |
| **Reconstruct attacker actions step-by-step** | Groups temporally correlated events into sequential kill-chain stages. | `engine/chain_correlator.py` |
| **Output: Attack Timeline** | Renders a chronological timeline showing how the attack developed over time. | `frontend/src/components/TimelineView.jsx` |
| **Output: People / Entities Involved** | Identifies compromised users, involved hosts, malicious IPs, and accessed sensitive assets. | `shared/schemas/responses.py` |
| **Output: Attack Stages** | Organizes related events into structured stages (e.g., Initial Access, Execution, Escalation, Collection, Exfiltration). | `engine/chain_correlator.py` |
| **Output: Proof / Evidence for Every Stage** | Every stage references concrete raw event IDs. Clicking a stage displays the raw log records. Rejects unsubstantiated claims. | `engine/evidence_verifier.py` |
| **Output: Risk Level** | Calculates explainable risk scores based on stage severity, asset criticality, and evidence density. | `engine/risk_scorer.py` |
| **Output: Recommended Action** | Provides actionable containment and remediation advice tailored to the observed attack path. | `engine/intervention_finder.py` |
| **False-Positive Control / Stay quiet on benign logs** | Requires multi-stage correlation and entity continuity before declaring an attack. Suppresses isolated benign anomalies. | `detection/filter.py` |
| **Timeline Accuracy** | Enforces temporal ordering ($t_1 \le t_2 \le \dots \le t_n$) within configurable correlation time windows. | `engine/chain_correlator.py` |
| **Explain why it is an attack** | Generates an explainable narrative linking entity transitions and causal steps. | `engine/story_generator.py` |

---

## 3. Minimum PS-Compliant Product vs. What Makes TRACE Different

To maintain crystal-clear focus during a 24-hour build, we strictly distinguish between the **mandatory baseline** required to solve the problem statement and our **additional differentiators**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        A. MANDATORY PROBLEM STATEMENT CORE                             │
│                                                                                        │
│   Raw Security Logs                                                                    │
│     └──► Normalization into common schema                                              │
│            └──► Entity Linking (User, Device, IP, App)                                 │
│                   └──► Suspicious / Anomalous Event Detection                          │
│                          └──► Multi-Event Temporal Correlation                         │
│                                 └──► Attack Chain Reconstruction                       │
│                                        └──► Evidence Binding for every Stage           │
│                                               └──► Timeline + Risk + Recommended Action│
│                                                      └──► Quiet on Benign Logs         │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        B. WHAT MAKES TRACE DIFFERENT (OUR USPs)                        │
│                                                                                        │
│   1. Attack Story & Interactive Replay: Step-by-step playback of how attack unfolded   │
│   2. Evidence-First Attack Graph: Interactive visual graph with zero ghost edges       │
│   3. Stage-Level Evidence & Confidence: Explainable arithmetic, not black-box scores   │
│   4. Earliest Intervention Point: Algorithmic identification of optimal cutoff point   │
│   5. Deep-Inspection Evidence Drawer: Immediate raw log provenance verification        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

The minimum PS core represents the pass/fail baseline for the hackathon. Our USPs elevate the project from a standard detection script to an intuitive, analyst-grade investigation platform.

---

## 4. What Makes TRACE Different (Our Core USPs)

### USP 1: Attack Story / Step-by-Step Attack Replay
* **What It Does:** Instead of presenting a static alert or a wall of security text, TRACE presents the incident as an unfolding chronological story. An interactive playback controller allows evaluators to step forward and backward through time.
* **Why It Matters:** In real security investigations, sequence matters. Evaluators can watch separate, seemingly innocuous events converge into a high-severity incident.
* **Evaluator Experience:** The evaluator clicks "Play" or steps forward:
  - The timeline highlights each stage in chronological sequence.
  - The attack graph animates, drawing new entities and edges as the adversary advances.
  - An accompanying narrative summarizes what just occurred: *"At 09:14, an unusual login was observed... 2 minutes later, a session attached from an unrecognised device..."*
* **Fallback If Needed:** If animation or playback state becomes difficult in frontend development, fall back to a simple tabbed or stepped stepper control (`[Previous Stage]`, `[Next Stage]`).

---

### USP 2: Evidence-First Attack Graph
* **What It Does:** Renders the attack as a directed entity graph where nodes represent real entities (`User`, `Device`, `IP`, `Process`, `File`) and edges represent observed interactions (`LOGGED_IN_FROM`, `USED_DEVICE`, `SPAWNED`, `ACCESSED`, `CONNECTED_TO`).
* **Why It Matters:** Most graph visualizers display arbitrary or decorative topologies. TRACE enforces a strict invariant: **Every single edge must hold one or more real event IDs as its backing evidence.**
* **Evaluator Experience:** The evaluator clicks on any node or edge in the graph:
  - An Evidence Drawer slides open.
  - The exact raw log entries that formed that edge are displayed with highlighted fields.
  - The evaluator sees that no connection was invented out of thin air.
* **Fallback If Needed:** If complex graph canvas libraries (e.g., Cytoscape) encounter styling or layout challenges, fall back to an interactive SVG node-link view or structured entity relationship cards.

---

### USP 3: Evidence-Backed Stage Confidence
* **What It Does:** Each attack stage displays an interpretable confidence and risk rating derived from observable evidence attributes, rather than a black-box percentage.
* **Why It Matters:** Evaluators and security analysts mistrust arbitrary numbers (e.g., "93% confident") when the system cannot justify where the number came from.
* **Evaluator Experience:** For each stage, TRACE displays:
  - The number of supporting log events found.
  - Which critical entities were shared with previous stages (entity continuity).
  - The severity weight of the observed action.
  - A brief, clear rationale: *"Confidence high: 2 distinct events confirm root command execution on the target finance server following session drift."*
* **Fallback If Needed:** Use a simple discrete rating scale (`Low`, `Medium`, `High`) based on the count and severity of supporting events.

---

### USP 4: Earliest Intervention Point (EIP)
* **What It Does:** Analyzes the full reconstructed chain and algorithmically identifies the earliest moment where security teams could have intervened to stop the attack before damage occurred.
* **Why It Matters:** Most tools focus purely on post-breach forensic reporting. TRACE bridges detection with incident response by answering: *"Where could we have stopped this with the least disruption?"*
* **Evaluator Experience:**
  - A prominent callout identifies the earliest intervention stage (e.g., after initial session drift, before privilege escalation or data access).
  - Explains the reasoning: *"Intervening here terminates the attacker's foothold before elevated commands or sensitive financial data are accessed."*
  - Recommends concrete actions: `REVOKE_SESSION`, `ISOLATE_HOST`, or `BLOCK_IP`.
* **Fallback If Needed:** If the dynamic bottleneck algorithm needs simplification, map predefined containment recommendations to the first confirmed post-authentication stage.

---

## 5. Core User Experience

TRACE is designed for intuitive interaction during an evaluation or investigation:

1. **Scenario Selection:** The evaluator selects an event feed from a dropdown:
   - *Clean / Benign Baseline Feed:* Evaluates noise suppression and false-positive resistance.
   - *Active Attack Feed:* Evaluates multi-stage reconstruction, entity linking, and timeline accuracy.
2. **Immediate Threat Summary:** A clear status header displays overall risk, attack status, affected identities, and incident duration.
3. **Dual Investigation Views:**
   - **Chronological Timeline:** Displays the sequence of stages, timestamps, and stage summaries.
   - **Interactive Attack Graph:** Displays how entities interlink and highlights the path taken by the attacker.
4. **Deep Evidence Inspection:** Clicking any stage card or graph edge reveals the raw underlying log events.
5. **Actionable Response:** An incident response card provides the recommended remediation step and earliest intervention guidance.

---

## 6. End-to-End System Flow (Representative Attack Scenario)

During development and testing, TRACE will use a representative multi-stage scenario. *(Note: This scenario is a representative design model; the team may simplify or adapt specific log attributes during implementation while preserving the core multi-stage requirements.)*

```
[Raw Log Ingestion]
        │
        ▼ (Stage 1: Initial Ingress)
Unusual Authentication: User j.doe logs in from an unrecognised external IP address
        │
        ▼ (Stage 2: Session / Device Drift)  <── [EARLIEST INTERVENTION POINT]
Session Attached: Session ID resumed from a host workstation never previously bound to j.doe
        │
        ▼ (Stage 3: Privilege Escalation)
Process Spawn: Elevated command execution (sudo / admin shell) initiated under the session
        │
        ▼ (Stage 4: Sensitive Resource Access)
File Read: Access to confidential financial reports or credential stores never previously touched
        │
        ▼ (Stage 5: Data Exfiltration)
Outbound Network Burst: High-volume egress connection to an external, untrusted destination IP
```

### Traceability Across the 10-Step Pipeline:
1. **Raw Log Ingestion:** Heterogeneous log entries (syslog, auth logs, process audits) are received.
2. **Normalization:** Extracted into uniform `NormalizedEvent` records.
3. **Entity Extraction:** Entities (`j.doe`, IP addresses, hostname, process name, file path) are indexed.
4. **Suspicious Event Detection:** Heuristics flag unusual characteristics (novel IP, elevated token, sensitive directory, outbound volume).
5. **Graph Construction:** Nodes and edges are established with raw event IDs attached to each relationship.
6. **Temporal Correlation:** Events occurring within a sliding correlation window are checked for entity continuity.
7. **Attack Stage Identification:** Consecutive correlated events are grouped into sequential kill-chain stages.
8. **Evidence Verification:** Every stage is checked to ensure it contains verifiable event IDs and raw log text.
9. **Risk & Intervention Calculation:** Overall risk is computed, and the earliest actionable intervention point is identified.
10. **UI Presentation:** The final timeline, graph, evidence drawer, and response recommendations are displayed.

---

## 7. Data and Event Model

All components communicate using standard data structures. The schema is defined cleanly and can be extended during development if needed:

```python
# Conceptual Event Schema (shared/schemas/events.py)
class NormalizedEvent:
    event_id: str               # Unique identifier for this log record (e.g., EVT-1001)
    timestamp: str              # ISO 8601 UTC timestamp
    event_type: str             # Category: AUTH, SESSION, PROCESS, FILE, NETWORK
    user: Optional[str]         # Associated username or account principal
    device: Optional[str]       # Hostname, workstation ID, or server label
    source_ip: Optional[str]    # Originating IP address
    destination_ip: Optional[str]# Destination IP address
    application: Optional[str]  # Application name or process binary
    resource: Optional[str]     # Target file path, resource URI, or database table
    action: str                 # Standardized action verb (LOGIN, SPAWN, READ, CONNECT)
    status: str                 # SUCCESS or FAILURE
    metadata: dict              # Flexible key-value store (bytes, PID, session_id, port)
    raw_log: str                # Original log line for evidence verification
```

### Purpose of Key Fields:
- `event_id`: Immutable audit key linking graph edges and timeline stages to raw data.
- `raw_log`: Preserves the exact original string to satisfy the problem statement requirement that every claim has proof.
- `metadata`: Accommodates format-specific details (e.g., transferred bytes, process IDs) without breaking normalization.

---

## 8. Entity Model

Entities are canonical security objects extracted from events:

| Entity Type | Example Values | Linking Role |
|---|---|---|
| **User** | `j.doe`, `admin` | Connects authentication attempts to subsequent process and resource activity. |
| **Device** | `srv-finance-01`, `ws-hr-04` | Connects host-level process execution to network ingress and egress. |
| **IP Address** | `198.51.100.42`, `10.0.4.12` | Connects external threat sources to internal hosts and exfiltration destinations. |
| **Application / Process** | `bash`, `powershell.exe`, `curl` | Connects user execution to file modifications and network connections. |
| **File / Resource** | `/confidential/q3_forecast.xlsx` | Identifies targeted sensitive assets. |

---

## 9. Attack Graph Topology

The attack graph represents observed interactions between entities:

```
[USER: j.doe]
    │
    ├── (LOGGED_IN_FROM) ────────► [IP: 198.51.100.42] (Source IP)
    │
    └── (USED_DEVICE) ───────────► [DEVICE: srv-finance-01]
                                        │
                                        ├── (SPAWNED_PROCESS) ──────► [PROCESS: bash]
                                        │                                    │
                                        │                                    └── (ACCESSED) ──► [FILE: q3_forecast.xlsx]
                                        │
                                        └── (CONNECTED_TO) ─────────► [IP: 203.0.113.88] (Destination IP)
```

### Graph Rules:
- **Evidence Requirement:** Every edge must hold an `evidence_event_ids` list containing $\ge 1$ raw event ID.
- **Zero Ghost Edges:** Edges cannot be created by heuristic inference alone; they must reflect an observed log event.
- **Compromise Highlighting:** Nodes involved in confirmed attack stages are visually highlighted to contrast with neutral context.

---

## 10. Attack Chain Reasoning & Temporal Correlation

To transform isolated alerts into a coherent attack chain, TRACE applies three core correlation principles:

1. **Temporal Ordering:** Events must respect temporal progression. An initial login must precede process spawning, which in turn must precede file access and egress.
2. **Entity Continuity:** For event $E_{i}$ to connect to event $E_{i+1}$, they must share at least one common entity (same user, same device, or same active session token):
   $$\text{Entities}(E_i) \cap \text{Entities}(E_{i+1}) \neq \emptyset$$
3. **Multi-Stage Thresholding:** Isolated anomalies that do not connect to a broader sequence are categorized as unlinked anomalies rather than an active attack chain.

---

## 11. False-Positive Strategy: "Quiet by Default"

The problem statement explicitly highlights false-positive resistance:
> *"False positives matter. Too many alerts on clean/benign logs can cap the score. More alerts does NOT mean a better system."*

TRACE avoids alert fatigue through a tiered filtering strategy:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. BENIGN BASELINE TRAFFIC                                             │
│    • Routine user logins, normal browsing, routine system tasks        │
│    • Outcome: Filtered out; dashboard remains calm and green           │
├────────────────────────────────────────────────────────────────────────┤
│ 2. ISOLATED ANOMALIES                                                  │
│    • Single mistyped password, isolated non-critical error log         │
│    • Outcome: Recorded as unlinked anomaly; no attack chain declared   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. COHESIVE MULTI-STAGE ATTACK                                         │
│    • Temporally correlated sequence sharing entity continuity (≥3 steps│
│    • Outcome: High-priority Attack Chain declared                      │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Principle:** The system stays quiet by default. An attack chain is only declared when multiple suspicious stages are linked across time and entities.

---

## 12. Evidence Model & Audit Trail

To satisfy the judging requirement that **every attack stage must have proof**, TRACE implements complete traceability:

- **Stage Record:** Contains `stage_name`, `timestamp_range`, `entities_involved`, and `evidence_event_ids`.
- **Evidence Audit:** Clicking any stage displays the raw log records corresponding to those IDs.
- **Integrity Guarantee:** If a stage cannot point to valid, ingested raw event IDs, it is rejected by the system.

---

## 13. Risk Scoring & Explanation Logic

TRACE calculates risk transparently:

- **Stage Risk:** Calculated based on the severity of the action (e.g., privilege escalation carries higher inherent risk than an unusual login) adjusted by asset criticality.
- **Overall Attack Risk:** Increases as the attack chain advances across more stages. A single anomaly produces a low score; a multi-stage sequence advancing to collection and exfiltration produces a critical score.
- **Explainability:** The UI explains the risk through concrete factors:
  - Progression across multiple kill-chain phases.
  - Presence of privileged command execution.
  - Involvement of high-value internal assets.

---

## 14. Recommended Response & Earliest Intervention Point

### Recommended Actions
Rather than generic advice, TRACE recommends concrete, context-aware remediation actions:
- `REVOKE_SESSION`: Terminate specific compromised session token.
- `ISOLATE_HOST`: Cut off network connectivity to the affected endpoint.
- `BLOCK_IP`: Add malicious source or destination IP to firewall blocklists.
- `AUDIT_RESOURCE`: Review accessed file paths for potential data exposure.

### Earliest Intervention Point (EIP)
TRACE identifies the earliest stage where containment would have prevented downstream damage:
- **Identification:** Pinpoints the transition point between initial access and subsequent exploitation.
- **Rationale:** Explains why intervening at this point stops the kill chain before privilege escalation, collection, or exfiltration occurs.

---

## 15. Frontend Dashboard Specification

The user interface delivers a clear, professional investigation experience:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TRACE ── Threat Reconstruction & Attack Chain Evidence              [Scenario: ▼]      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ THREAT SUMMARY: [ STATUS: ACTIVE ATTACK ]   Risk Level: CRITICAL   Duration: 13m 13s   │
│ Target Host: srv-finance-01  |  Compromised Account: j.doe  |  Threat IP: 198.51.100.42│
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ 1. CHRONOLOGICAL ATTACK TIMELINE          │ 2. INTERACTIVE ATTACK GRAPH                │
│ [▶ Play] [⏸ Pause] [⏮ Step] [⏭ Step]      │                                            │
│                                           │       [IP: 198.51.100.42]                  │
│ [Stage 1] 09:14 ── Unusual Login          │               │ (Logged in from)           │
│   Account j.doe from novel IP             │               ▼                            │
│                                           │       [USER: j.doe]                        │
│ [Stage 2] 09:16 ── Session Migration      │               │ (Used device)              │
│   * EARLIEST INTERVENTION POINT *         │               ▼                            │
│                                           │     [DEVICE: srv-finance-01]               │
│ [Stage 3] 09:19 ── Privilege Escalation   │         │               │                  │
│   Elevated command execution under session│         ▼ (Ran)         ▼ (Connected to)   │
│                                           │     [PROCESS: bash]   [IP: 203.0.113.88]   │
│ [Stage 4] 09:23 ── Sensitive File Read    │         │ (Accessed)                       │
│   Direct read of restricted finance file  │         ▼                                  │
│                                           │     [FILE: q3_forecast.xlsx]               │
│ [Stage 5] 09:27 ── Outbound Exfiltration  │                                            │
│   High-volume egress connection to dest IP│                                            │
├───────────────────────────────────────────┴────────────────────────────────────────────┤
│ 3. EARLIEST INTERVENTION PLAYBOOK:                                                     │
│ Recommended Action: REVOKE_SESSION(sess-8821) & ISOLATE_HOST(srv-finance-01)          │
│ Rationale: Terminating session at Stage 2 prevents privilege escalation & data leak    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. EVIDENCE DRAWER (Deep Inspection):                                                  │
│ Event ID: EVT-2004  |  Timestamp: 2026-10-07T09:23:30Z  | Verification: Confirmed      │
│ Raw Log: FILE_READ host="srv-finance-01" user="j.doe" path="/confidential/finance/..." │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 16. Live Demo Experience (3-Minute Script)

To present TRACE effectively, the team will walk through this clear 3-minute sequence:

1. **Step 1: Benign Baseline (0:00 – 0:45)**
   - Select the clean background dataset.
   - Show that the system stays calm and green, with zero attack chains declared.
   - *Message:* "Notice that TRACE does not raise false alarms on routine enterprise activity. It stays quiet on benign logs."
2. **Step 2: Attack Stream & Replay (0:45 – 1:45)**
   - Switch to the active attack dataset.
   - Trigger the Attack Replay to show events appearing step-by-step.
   - *Message:* "Here is the attack unfolding in chronological order. TRACE links the user, host, process, and external IPs into one cohesive attack chain."
3. **Step 3: Evidence Inspection (1:45 – 2:30)**
   - Click on a stage in the timeline and open the Evidence Drawer.
   - Show the exact underlying raw log record.
   - *Message:* "Every single attack stage has verifiable proof. Clicking any stage exposes the exact raw log entry that produced it."
4. **Step 4: Earliest Intervention Point (2:30 – 3:00)**
   - Highlight the Earliest Intervention Point badge and recommended action.
   - *Message:* "TRACE identifies Stage 2 as the earliest point to cut off the adversary, preventing privilege escalation and data exfiltration before damage occurred."

---

## 17. Scope Classification: MVP vs. USP vs. Stretch

| Feature | Category | Priority | Scope Rationale |
|---|---|---|---|
| **Log Normalization** | Core PS | **P0 (Must Have)** | Baseline requirement to handle heterogeneous security logs. |
| **Entity Linking** | Core PS | **P0 (Must Have)** | Connects users, devices, IPs, and processes into a shared graph. |
| **Temporal Correlation** | Core PS | **P0 (Must Have)** | Orders events chronologically within sliding time windows. |
| **Evidence Binding** | Core PS | **P0 (Must Have)** | Links every stage directly to raw log event IDs. |
| **Noise Suppression** | Core PS | **P0 (Must Have)** | Guarantees zero false alarm chains on benign traffic. |
| **Actionable Recommendations** | Core PS | **P0 (Must Have)** | Recommends practical containment actions. |
| **Interactive Graph Canvas** | UI / Judge | **P1 (Important)** | Visualizes entity relationships and attack paths. |
| **Timeline View** | UI / Judge | **P1 (Important)** | Displays chronological progression of stages. |
| **Evidence Drawer** | UI / Judge | **P1 (Important)** | Allows evaluators to drill down into raw log strings. |
| **Attack Replay Controller** | USP | **P2 (Differentiator)** | Interactive temporal playback of how the attack unfolded. |
| **Earliest Intervention Point** | USP | **P2 (Differentiator)** | Identifies optimal cutoff point to minimize breach damage. |
| *LLM Incident Summary Synthesis* | Stretch | *P3 (Stretch)* | Generates natural language summary (offline fallback if slow). |
| *Multi-Attacker Simultaneous Chains* | Stretch | *P3 (Stretch)* | Tracks two concurrent, independent attack chains. |
| *Unsupervised Clustering Layer* | Stretch | *P3 (Stretch)* | Additional anomaly scoring layer on top of heuristics. |

---

## 18. What We Are NOT Building (Explicit Scope Boundaries)

To avoid distractions and ensure high-quality delivery, the team will **not** attempt:

- **Not an Enterprise SIEM Replacement:** No support for hundreds of proprietary enterprise formats, syslog agents, or complex fleet management.
- **Not an LLM-Only Guesser:** We do not rely on generative models to invent attack logic. Detection is structured, deterministic, and evidence-bound.
- **Not a Production SOC Ticketing Tool:** No user login systems, ticket queues, or multi-tenant billing infrastructure.
- **Not an Overengineered Distributed Architecture:** No Kafka, no message brokers, no Kubernetes clusters, and no complex microservices. A clean, single-process FastAPI backend and React frontend ensure maximum reliability.

---

## 19. Technical Architecture

```
[ RAW SECURITY LOG FEEDS ]
            │
            ▼
┌─────────────────────────┐
│     Event Normalizer    │ ── Maps raw entries to NormalizedEvent schema
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│      Entity Linker      │ ── Resolves Users, Devices, IPs, Processes, Files
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│     Detection Engine    │ ── Heuristics, anomaly signals, and noise suppression
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ Attack Chain Correlator │ ── Enforces temporal windows and entity continuity
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│    Evidence Verifier    │ ── Validates event IDs and binds raw proof to stages
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│     Risk & Response     │ ── Computes risk score and Earliest Intervention Point
└─────────────────────────┘
            │ Emits AnalysisResponse schema
            ▼
┌─────────────────────────┐
│    FastAPI REST API     │ ── High-performance backend endpoints
└─────────────────────────┘
            │ JSON over HTTP
            ▼
┌─────────────────────────┐
│    React / Vite UI      │ ── Timeline, Entity Graph, Replay, Evidence Drawer
└─────────────────────────┘
```

---

## 20. Resource Declaration

In compliance with hackathon regulations:

* **Backend Libraries:**
  - `FastAPI` & `Uvicorn`: Lightweight, fast API service.
  - `NetworkX`: In-memory graph analytics and entity relationship modeling.
  - `Pydantic`: Strict schema validation and contract enforcement.
  - `Pytest`: Automated testing for detection and correlation logic.
  - `NumPy` / `Scikit-learn` *(optional)*: Baseline statistical calculations.

* **Frontend Libraries:**
  - `React` with `Vite`: High-performance UI framework and build tool.
  - `Tailwind CSS`: Rapid, clean component styling.
  - `Cytoscape.js` / `@xyflow/react` / SVG: Directed graph visualization.
  - `Lucide-React`: Icons for cybersecurity entities.

* **Datasets & Testing Telemetry:**
  - Synthetic enterprise log dataset (`data/generator.py`): Authored for this project to represent standard enterprise telemetry with both benign baseline traffic and a cohesive multi-stage attack modeled after MITRE ATT&CK techniques.

* **AI / Model Usage:**
  - Deterministic rules and graph analytics form the primary detection foundation. Any optional language model usage for narrative text generation is isolated with deterministic offline fallbacks.

---

## 21. Measurable Acceptance Criteria

The TRACE solution will be considered complete when it meets the following functional criteria:

1. **Entity Linking:** Disparate events sharing users, devices, IPs, or processes are linked into a queryable graph.
2. **Chronological Reconstruction:** Multiple related suspicious events form an ordered attack chain that preserves temporal ordering.
3. **Verifiable Proof:** Every displayed attack stage references at least one valid raw log event.
4. **Benign Log Quietness:** Ingesting benign background traffic results in a calm status with zero attack chains declared.
5. **Attack Detection:** Ingesting the multi-stage attack scenario reconstructs the full chain and triggers an active incident.
6. **Intervention Guidance:** The system identifies an actionable earliest intervention point and recommends appropriate containment.
7. **Interactive Visualization:** The frontend displays both the chronological timeline and the entity relationship graph.
8. **Live Demo Stability:** The entire flow runs reliably end-to-end locally without requiring external cloud services.
