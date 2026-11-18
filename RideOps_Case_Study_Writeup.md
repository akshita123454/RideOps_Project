# 📑 RIDEOPS OPERATIONS DIAGNOSIS & INTELLIGENCE SYSTEM
## Executive Submission: Forward Deployed Engineer (FDE) Case Study
**Candidate:** FDE / Product & Technical Solutions Candidate  
**Target:** MoveInSync Leadership Review  
**Data Scope:** 1,444 Enterprise Mobility Support Records (July 2 – September 30, 2026)  
**Deliverable:** 4-Page Comprehensive Case Study Write-Up

---

# SECTION 1: DIAGNOSIS & EMPIRICAL FINDINGS

### 1.1 The Symptom vs. The Root Cause
RideOps leadership reported an approximate **60% surge in open support complaints** between July and September 2026 without the budget to hire additional personnel. While internal stakeholders engaged in cross-departmental finger-pointing, an empirical audit of the 1,444 support tickets reveals that the crisis is **structural rather than attributable to staff inertia**.

```
       [JULY]                           [AUGUST]                         [SEPTEMBER]
390 Inflow / 360 Outflow          462 Inflow / 469 Outflow          592 Inflow / 567 Outflow
Net Backlog: +30                  Net Backlog: -7                   Net Backlog: +25
Workload: 11.3 tix/agent/wk       Workload: 13.3 tix/agent/wk       Workload: 17.1 tix/agent/wk (+51.8%)
```

The support operation hit an unyielding **throughput ceiling**. In September, weekly volume surged to 17.1 tickets per agent per week. Because the operational capacity was capped, any friction in ticket handling compounded into open backlog.

---

### 1.2 The Three Stakeholder Claims Evaluated Against Data

| Stakeholder | Internal Perception | Data Verdict | Quantitative Finding |
|---|---|---|---|
| **Meera** *(Support Lead)* | "Support is working hard; Engineering takes too long to resolve escalated tickets." | **Partially True** | Escalated tickets take a median of **86.8 hours** (vs. **12.6 hours** for L1). However, her team caused over half of this delay by escalating tickets that never belonged in Engineering. |
| **Sandeep** *(Eng Manager)* | "L1 escalates blindly without basic checks, dumping triaged work onto engineers." | **Strongly Supported** | **56.6% of escalations (275 out of 486) were wasteful** (89 insufficient info, 84 config issues, 56 known duplicates, 24 how-to queries, 22 non-reproducible). |
| **Ritika** *(Head of Ops)* | "Stop blaming each other. Reduce backlog and improve client experience without hiring." | **Correct Strategic Frame** | The solution is neither hiring nor blame; it is **intercepting preventable escalations at L1** and **eliminating repeat bugs upstream**. |

---

### 1.3 The Four Empirical Bottlenecks Discovered

#### Bottleneck 1: The 56.6% Wasteful Escalation Tax
486 of 1,444 tickets (33.7%) were escalated to Engineering. Of these, **275 were rejected or resolved as non-bugs**. Escalating a ticket increases its resolution time by **689% (from 12.6h to 86.8h)**. Every wasteful escalation robs ~75 hours of customer response time while consuming costly developer hours.

#### Bottleneck 2: The "Ping-Pong" Multi-Handoff Multiplier
**229 tickets bounced between L1 and Engineering 2 or more times** (accounting for 47.1% of all escalations).
* 1 handoff: Median resolution = **58.7 hours**
* 2 handoffs: Median resolution = **110.4 hours**
* 3 handoffs: Median resolution = **169.9 hours (7.1 days)**
* **89 of the 229 bouncing tickets** were rejected because L1 failed to provide basic diagnostic information ("Insufficient info - returned to L1").

#### Bottleneck 3: Individual Execution Variances
Aggregated team averages masked stark individual behavioral extremes across the 8 L1 agents:
* **Rahul T (The Over-Escalator):** Escalated **61.6% of his assigned tickets** (93 out of 151; team average: 31.8%). Crucially, **75.3% of his escalations (70 tickets) were wasteful**. Rahul alone generated ~25% of all wasted engineering tickets.
* **Karan B (The Premature Closer):** Boasted the lowest escalation rate (16.1%) but suffered a catastrophic **29.5% reopen rate** (64 reopened tickets; team average: 8.5%). When clients reopened Karan’s tickets, their **average CSAT plummeted to 2.00** (vs. 3.46 on non-reopened). Karan cleared his queue by closing tickets before the root issue was resolved.

#### Bottleneck 4: 183 Tickets Masking Just 3 Software Defects
Support volume was artificially inflated by unresolved core software defects:
1. `Booking cutoff changed but roster still uses old cutoff` — **66 tickets across 34 enterprise clients**
2. `Ad-hoc booking done by admin not reflecting for employee` — **60 tickets across 29 enterprise clients**
3. `Cancelled bookings still appearing in tomorrow's roster` — **57 tickets across 27 enterprise clients**

**183 tickets (12.7% of all company volume)** were caused by these three roster-sync issues. Engineering repeatedly closed these tickets as *Duplicate of known issue* or *Config issue* without patching the underlying race condition.

---

# SECTION 2: DEFINING SUCCESS (THE KPI FRAMEWORK)

To guarantee sustainable progress without headcount expansion, RideOps must track an operational balance sheet. Improving speed must not degrade quality (reopen rate), and reducing escalations must not leave tickets abandoned.

### 2.1 The Operational Scorecard & Measurable Targets

| Metric | Baseline (Sep 2026) | Target (Week 4) | Measurement Cadence | Strategic Intent |
|---|---|---|---|---|
| **Wasteful Escalation Rate (North Star)** | **56.6%** (275/486) | **≤ 25.0%** | Weekly | Primary lever to reclaim 8,000+ engineering hours and collapse cycle times. |
| **Total Open Backlog** | **48 tickets** | **≤ 20 tickets** | Daily / Real-time | Restore buffer capacity against inflow spikes. |
| **Median Resolution Time** | **22.4 hours** | **≤ 14.0 hours** | Weekly | Shrink cycle time across all categories. |
| **Multi-Handoff Rate (≥2 handoffs)** | **47.1%** of esc. | **≤ 15.0%** of esc. | Weekly | Eliminate the back-and-forth ping-pong between teams. |
| **Agent Escalation Disparity** | 16% to 62% range | **≤ 15% delta across agents** | Weekly | Standardize agent capability via guided playbooks. |
| **Reopen Rate** | **11.5%** (Sep) | **≤ 5.0%** | Weekly | Stop premature ticket closures (specifically Karan B pattern). |
| **Enterprise CSAT** | **3.65 / 5.0** | **≥ 4.20 / 5.0** | Monthly | Directly correlated with resolution times < 24 hours. |

### 2.2 The Correlation that Governs CSAT
Analysis of CSAT scores across resolution duration confirms a steep cliff:
* `< 6 hours`: **4.16 CSAT** (89 ratings)
* `6 – 12 hours`: **4.32 CSAT** (128 ratings)
* `12 – 24 hours`: **4.17 CSAT** (111 ratings)
* `24 – 48 hours`: **3.78 CSAT** (108 ratings)
* `48 – 96 hours`: **3.35 CSAT** (103 ratings)
* `> 96 hours`: **2.39 CSAT** (109 ratings)

Tickets exceeding 48 hours (virtually all multi-handoff escalations) inevitably destroy client satisfaction. Intercepting escalations directly elevates CSAT.

---

# SECTION 3: THE SOLUTION (NERVECENTER v0)

Rather than building a passive BI dashboard, we engineered **NerveCenter**, a working internal system that embeds automated decision-making and operational guardrails into daily support and product workflows.

```
+-----------------------------------------------------------------------------------+
|                                  NERVECENTER                                      |
+--------------------------+------------------------------+-------------------------+
|    1. AGENT COCKPIT      |       2. OPS COMMAND         |      3. BUG RADAR       |
|  * Personal Benchmarks   |  * Backlog Pressure Index    |  * 2-Pass NLP Clusters  |
|  * TF-IDF Ticket DNA     |  * Inflow vs. Outflow Flow   |  * Radius of Impact     |
|  * Escalation Calculator |  * What-If Simulator         |  * Auto-Generated Specs |
|  * Pre-Flight Checklists |  * Outlier Agent Heatmap     |  * Upstream Root Cause  |
+--------------------------+------------------------------+-------------------------+
```

### 3.1 Primary Persona Selected: L1 Support Agent (The Front-Line Gatekeeper)
We selected the L1 Support Agent as our core user because **56.6% of the system’s failure originates at the point of initial triage**. If the front-line agent makes a more informed triage decision, engineering hours are conserved, ping-pong bounces are averted, and cycle time drops from 87h to 12h.

### 3.2 Key Technical Capabilities Built into NerveCenter

#### 1. "Ticket DNA" Similarity Engine (`engine/ticket_dna.py`)
Utilizes a sublinear TF-IDF vectorizer trained on historical ticket descriptions with cosine similarity scoring. When an agent opens a ticket, NerveCenter instantly extracts the **top 5 most similar closed tickets from company history**, displaying:
* Whether past tickets were successfully resolved by L1 or escalated.
* The exact engineering verdict if escalated (`Config issue`, `Fixed`, `Not a bug`).
* The historical resolution playbook, giving the agent a blueprint to resolve the issue in minutes.

#### 2. The Escalation Payoff Calculator
Prior to escalating, the agent is presented with a dynamically computed risk profile:
$$\text{Waste Risk} = \frac{\text{Similar Past Wasteful Escalations}}{\text{Total Similar Past Escalations}}$$
The calculator explicitly displays:
* *Expected Resolution Time if Escalated:* **~87 Hours**
* *Expected Resolution Time if Handled at L1:* **~12 Hours**
This behavioral nudge forces agents to reconsider unnecessary escalations.

#### 3. Category-Specific Pre-Escalation Checklists (`engine/data_loader.py`)
Dynamic checklists customized for all 10 ticket categories. For example, on a *Roster / booking not syncing* complaint, the agent must verify:
* [x] Admin booking cutoff time configuration
* [x] 15-minute sync propagation window
* [x] Mobile app version alignment
* [x] Screenshot attachment comparing roster vs. booking screen
This directly eliminates the **89 tickets rejected for "Insufficient Info"**.

#### 4. The What-If Backlog Simulator (`engine/metrics.py`)
Empowers Ritika to simulate the downstream impact of operational improvements. Intercepting 40% of wasteful escalations reclaims **8,250 hours of engineering time**, which equals over **15 full-time engineer-months** of capacity reallocated from ticket triage to product innovation.

#### 5. Product Defect Radar (`engine/bug_cluster.py`)
A two-pass clustering engine (exact match + fuzzy cosine similarity at 0.75 threshold) that scans across tickets to isolate product defects. It auto-generates Markdown engineering tickets complete with impacted client lists, sample ticket IDs, and technical hypotheses.

---

# SECTION 4: FOUR-WEEK EXECUTION PLAN

```
WEEK 1: Triage Guardrails      WEEK 2: Pilot & Coaching       WEEK 3: Upstream Bug Fixes     WEEK 4: Hand-Off & Runbook
* Deploy Agent Cockpit         * Rahul T targeted coaching    * Sandeep patches top 3 bugs   * Full SOP documentation
* Enforce pre-flight checklist * Karan B premature-close audit* Release self-serve admin tools* Automated Monday digest
* Launch Known-Issues KB       * Weekly Ops Review launch     * Smart skill-based routing    * Final leadership audit
```

### Week 1: Gatekeeping & Immediate Waste Interception
* **Deploy Agent Cockpit v0:** Onboard all 8 L1 agents to use the pre-escalation checklist for the top 3 problem categories (Roster Sync, Live Tracking, Report Export).
* **Engineering Escalation Gate:** Sandeep institutes an SLA agreement: Engineering rejects any escalation that lacks a completed NerveCenter diagnostic checklist.
* **Publish Known-Issues KB:** Convert the 56 known duplicate issues into instant canned macros inside the Cockpit.
* *Explicit Non-Goal:* No product re-architecture or external client-facing modifications.

### Week 2: Targeted Behavioral Coaching & Operations Rhythm
* **Individual Intervention (Rahul T):** Pair Rahul T with a senior agent for 5 days. Mandate that all his escalations receive secondary sign-off until his escalation rate drops under 35%.
* **Audit Premature Closures (Karan B):** Introduce a 48-hour customer verification window before tickets can be marked permanently closed, preventing Karan’s high reopen rate.
* **Launch Monday Ops Briefing:** Ritika uses NerveCenter’s 1-click Executive Digest for weekly alignment meetings between Meera and Sandeep.
* *Explicit Non-Goal:* No changes to the underlying Jira/ticketing database schema.

### Week 3: Upstream Defect Elimination & Routing Optimization
* **Engineering Bug Sprint:** Sandeep’s team prioritizes the top 3 defect clusters identified by the Bug Radar (`Booking cutoff delay`, `Ad-hoc sync race condition`, `Export timeout`), permanently eradicating **~60 incoming tickets per month**.
* **Skill-Based Routing Engine:** Direct complex Roster tickets to top-performing agents (Priya D, Neha P) while routing How-To and Login queries to newer agents.
* *Explicit Non-Goal:* No complex machine learning model training; continue relying on fast, explainable TF-IDF algorithms.

### Week 4: Institutionalization, SOPs & Transition
* **Formalize Operating Runbooks:** Document standard operating procedures for maintaining ticket checklists and updating the Bug Radar.
* **Automate Leadership Digest:** Schedule the Backlog Pressure Index and weekly KPI summary to email Ritika, Meera, and Sandeep every Monday at 08:00 IST.
* **Audit Against Targets:** Present the 30-day transformation metrics against the baseline, demonstrating a ≥50% reduction in wasteful escalations and stabilization of open tickets below 20.
* *Explicit Non-Goal:* Do not expand tool scope to non-support departments.

---

### Conclusion
By analyzing the empirical reality behind RideOps' ticket data, **NerveCenter bridges the gap between Support, Operations, and Engineering**. It proves that solving enterprise support backlogs does not require expanding headcount—it requires arming front-line engineers with intelligent, data-driven systems.
