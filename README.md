# Financial Crime Intelligence System

A real-time financial crime intelligence and investigation platform for Bitcoin transaction networks, built using the Elliptic++ dataset.

The system combines machine learning, temporal anomaly detection, graph analysis, and interactive network visualization to identify suspicious transaction activity and provide analysts with explainable risk assessments.

> **Note:** This project simulates real-time detection by replaying the temporally ordered Elliptic++ dataset. It does not connect to the live Bitcoin blockchain.

---

## Overview

Financial crime rarely appears as a single suspicious transaction.

Suspicious behavior can emerge from:

- unusual transaction activity
- sudden changes in transaction frequency
- highly connected entities
- dense transaction communities
- coordinated activity across multiple wallets
- combinations of individually weak signals

This project approaches the problem as a **financial crime intelligence problem** rather than simply classifying individual transactions.

The system continuously replays transaction activity from the Elliptic++ dataset, analyzes incoming activity, updates a transaction graph, calculates multiple risk signals, and presents the results through an analyst-oriented investigation dashboard.

---

## Key Features

### Machine Learning Detection

An XGBoost classifier analyzes transaction and behavioral features to estimate the likelihood of illicit activity.

### Temporal Anomaly Detection

The system analyzes transaction behavior over time to identify unusual changes in activity, velocity, and frequency.

### Graph-Based Intelligence

The evolving Bitcoin transaction network is represented as a graph using NetworkX.

Graph analysis is used to identify:

- highly connected entities
- suspicious network structures
- important nodes
- dense communities
- relationships between suspicious entities

### Community Detection

Louvain community detection is used to identify groups of closely connected entities within the transaction network.

### Explainable Risk Scoring

Machine learning, graph, and temporal signals are combined into a single risk score ranging from 0–100.

Risk levels:

| Score | Risk Level |
|------:|------------|
| 0–29 | LOW |
| 30–59 | MEDIUM |
| 60–79 | HIGH |
| 80–100 | CRITICAL |

The system also provides evidence explaining why an entity or transaction received its risk score.

### Simulated Real-Time Monitoring

The Elliptic++ temporal sequence is replayed as a simulated transaction stream.

The analyst can observe:

- incoming transactions
- newly generated alerts
- changing risk levels
- evolving network activity
- suspicious communities

### Interactive Network Investigation

Analysts can investigate suspicious entities through an interactive network visualization.

The interface focuses on relevant local neighborhoods rather than attempting to render the entire Elliptic++ graph.

---

## System Architecture

```text
                    ELLIPTIC++ DATASET
                           │
                           ▼
                  TEMPORAL STREAM
                     SIMULATOR
                           │
                           ▼
                  INCOMING ACTIVITY
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       ML / TEMPORAL              GRAPH UPDATE
          ANALYSIS                      │
              │                   NetworkX Graph
              │                         │
              │                  Graph Features
              │                  Community Detection
              │                         │
              └────────────┬────────────┘
                           ▼
                    RISK FUSION ENGINE
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           ALERT        EVIDENCE      ACTION
                           │
                           ▼
                   FASTAPI / WEBSOCKET
                           │
                           ▼
                   REACT ANALYST UI