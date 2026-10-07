# Financial Crime Intelligence System

An explainable financial crime intelligence and investigation system for Bitcoin transaction networks.

The system replays the temporally ordered **Elliptic++** Bitcoin transaction dataset as a simulated real-time stream and combines:

- Machine learning
- Temporal anomaly detection
- Graph analysis
- Community detection
- Risk fusion
- Explainable evidence
- Interactive network visualization

to help analysts identify and investigate potentially suspicious activity.

> **Important:** This project does not connect to the live Bitcoin blockchain. "Real-time" refers to the simulated real-time replay of historically ordered Elliptic++ transaction data.

---

## Overview

Financial crime is rarely visible from a single transaction in isolation.

A transaction may appear normal when examined individually, but become more suspicious when considered alongside:

- the entity's recent behavior
- transaction velocity
- the structure of its surrounding network
- its connections to other entities
- its membership in a dense community
- other independent indicators of suspicious activity

This project approaches the problem as a **financial crime intelligence and investigation problem**, rather than simply classifying individual transactions as fraudulent or legitimate.

The system continuously replays the temporal progression of the Elliptic++ dataset, processes incoming activity, updates a transaction graph, calculates multiple intelligence signals, and presents the results through an analyst-focused investigation dashboard.

---

# System Architecture

```text
                         ELLIPTIC++ DATASET
                                  │
                                  ▼
                         TEMPORAL STREAM
                            SIMULATOR
                                  │
                                  ▼
                       INCOMING TRANSACTION
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ML / TEMPORAL                 GRAPH UPDATE
                ANALYSIS                        │
                    │                     NetworkX Graph
                    │                           │
                    │                     Graph Features
                    │                           │
                    │                  Community Detection
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                           RISK FUSION ENGINE
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                  SCORE        EVIDENCE       ACTION
                                  │
                                  ▼
                           FASTAPI BACKEND
                                  │
                              WebSocket
                                  │
                                  ▼
                         REACT ANALYST UI
                                  │
                                  ▼
                              ANALYST
