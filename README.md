<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RideOps — The Second Desk</title>
<style>
  :root {
    --ink: #0F172A;
    --body: #1E293B;
    --muted: #475569;
    --faint: #64748B;
    --border: #E2E8F0;
    --navy: #1E40AF;
    --green: #047857;
    --red: #B91C1C;
    --amber: #B45309;
  }
  * { box-sizing: border-box; }
  html, body { background: #FFFFFF; }
  body {
    margin: 0;
    color: var(--ink);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.55;
  }
  .wrap { max-width: 960px; margin: 0 auto; padding: 40px 32px 72px; }
  h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 4px; color: #0F172A; }
  .subtitle { color: var(--muted); font-size: 1rem; margin: 0 0 28px; }
  h2 {
    font-size: 1.15rem; font-weight: 600; color: #1E3A8A;
    letter-spacing: -0.01em; margin: 34px 0 10px;
    padding-bottom: 8px; border-bottom: 1px solid var(--border);
  }
  p { margin: 10px 0; color: #1E293B; }
  li { margin: 5px 0; color: #1E293B; }
  strong { color: #0F172A; }
  code {
    background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 4px;
    padding: 1px 5px; font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    font-size: 0.86em; color: #0F172A;
  }
  pre {
    background: #0F172A; color: #E2E8F0; padding: 16px 18px; border-radius: 6px;
    overflow-x: auto; font-size: 0.85rem; line-height: 1.6;
    font-family: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
    white-space: pre;
  }
  pre code { background: none; border: none; padding: 0; color: #E2E8F0; }
  table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 0.9rem; }
  th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }
  th { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }
  td { color: #1E293B; }
  tr:hover td { background: #F8FAFC; }
  .card {
    background: #FFFFFF; border: 1px solid var(--border); border-radius: 6px;
    padding: 16px 20px; margin: 14px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  }
  .card-header {
    font-size: 0.75rem; font-weight: 700; color: var(--navy);
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;
  }
  .loops { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 14px 0; }
  @media (max-width: 680px) { .loops { grid-template-columns: 1fr; } }
  .loop { border: 1px solid var(--border); border-radius: 6px; padding: 16px 18px; color: #1E293B; }
  .loop-visible { border-left: 4px solid var(--amber); }
  .loop-hidden { border-left: 4px solid var(--red); }
  .loop strong { display: block; font-size: 0.9rem; margin-bottom: 6px; color: #0F172A; }
  .muted { color: var(--faint); }
  ul, ol { margin: 8px 0; padding-left: 22px; }
</style>
</head>
<body>
<div class="wrap">

  <h1>RideOps — The Second Desk</h1>
  <p class="subtitle">An L1 decision-gate tool for a corporate employee-transportation provider.</p>

  <p>
    The support operation was treated as a queue to clear. It is actually a rework factory
    with two broken decisions — <strong>escalate to engineering</strong> and
    <strong>close as resolved</strong>. This application quantifies both failure modes and
    gates them before they happen.
  </p>

  <h2>Problem</h2>
  <p>
    Open support tickets rose approximately 60% between July and September 2026 across
    1,444 tickets and 200 corporate clients. Hiring is not an option. Leadership needs the
    backlog reduced with the existing headcount.
  </p>

  <h2>Diagnosis</h2>
  <p>
    The backlog is decomposed with Little's Law (<code>L = λ × W</code>, open tickets =
    arrival rate × cycle time):
  </p>
  <table>
    <thead>
      <tr><th>Driver</th><th>Finding</th></tr>
    </thead>
    <tbody>
      <tr><td>Arrival rate (λ)</td><td>+51.8% inflow (390 → 592/month). A hiring problem, off the table.</td></tr>
      <tr><td>Cycle time (W)</td><td>L1 resolves in 12.6h; escalated tickets take 86.8h (7× slower).</td></tr>
      <tr><td>Escalation loop</td><td>56.6% of escalations (275/486) return as non-bugs; 229 tickets ping-pong at a 128.5h median.</td></tr>
      <tr><td>Reopen loop</td><td>11.5% of tickets reopen; one agent (Karan B) reopens 29.5% at CSAT 2.0.</td></tr>
      <tr><td>Structural defects</td><td>183 tickets (13%) trace to three upstream roster/export bugs.</td></tr>
    </tbody>
  </table>

  <div class="loops">
    <div class="loop loop-visible">
      <strong>Loop 1 — Escalation (visible)</strong>
      56.6% of escalations bounce back as non-bugs. 229 tickets ping-pong 2+ times at a
      128.5h median. Escalated tickets take 86.8h versus 12.6h at L1.
    </div>
    <div class="loop loop-hidden">
      <strong>Loop 2 — Reopen (nobody named it)</strong>
      11.5% of tickets reopen after closure. Karan B closes 29.5% too early at CSAT 2.0.
      Three internal perspectives blame each other; none names premature closure.
    </div>
  </div>

  <p>
    The backlog is driven by two unverified decisions, each spinning tickets through a
    rework loop. The escalation loop is visible; the reopen loop is the second,
    unacknowledged one.
  </p>

  <h2>Solution</h2>
  <p>"The Second Desk" is a decision gate for L1 agents. For every open ticket it shows,
  before the agent acts:</p>
  <ul>
    <li><strong>Escalation Gate</strong> — calibrated probability the escalation will bounce back as a non-bug, a recommendation, and the three most similar past tickets as evidence.</li>
    <li><strong>Closure Gate</strong> — calibrated probability the closure will reopen, with the agent's own track record as evidence.</li>
    <li><strong>Known-defect short-circuit</strong> — if the ticket matches a recurring defect cluster, escalation is blocked and a documented workaround is shown.</li>
  </ul>
  <p>
    Risk scores are a weighted blend of three inspectable rates (category base rate, agent
    history, TF-IDF similarity), shrunk toward stable category rates with Laplace smoothing.
    No black-box model.
  </p>

  <h2>Success Metrics</h2>
  <table>
    <thead>
      <tr><th>KPI</th><th>Baseline</th><th>Target</th></tr>
    </thead>
    <tbody>
      <tr><td>Open backlog</td><td>48 and climbing</td><td>−40%</td></tr>
      <tr><td>Escalation waste rate</td><td>56.6%</td><td>&lt; 30%</td></tr>
      <tr><td>Reopen rate</td><td>11.5%</td><td>&lt; 6%</td></tr>
      <tr><td>Escalated median cycle time</td><td>86.8h</td><td>−40%</td></tr>
      <tr><td>CSAT on resolved</td><td>declining to 2.4 with delay</td><td>≥ 4.0</td></tr>
    </tbody>
  </table>

  <h2>Application Structure</h2>
  <pre><code>.
├── app.py                      # Landing: Little's Law decomposition, two-loop finding, KPIs
├── pages/
│   ├── 1_Agent_Cockpit.py      # The Second Desk (L1 decision gate)
│   ├── 2_Ops_Command.py        # Weekly KPI monitoring, burn-down simulation
│   └── 3_Bug_Radar.py          # Upstream defect clustering
├── engine/
│   ├── data_loader.py          # Parsing and derived columns
│   ├── decision_gate.py        # Escalation and closure risk models
│   ├── ticket_dna.py           # TF-IDF similarity (one input signal)
│   ├── bug_cluster.py          # Recurring defect detection
│   ├── metrics.py              # KPIs, Little's Law decomposition, simulator
│   └── ui_layout.py            # Styling and navigation
├── rideops_support_tickets.csv # 1,444 tickets (Jul 2 – Sep 30, 2026)
└── requirements.txt</code></pre>

  <h2>Prerequisites</h2>
  <ul>
    <li>Python 3.10+</li>
    <li>Virtual environment (<code>venv</code>)</li>
  </ul>

  <h2>Setup</h2>
  <pre><code>cd MoveInSync
.\venv\Scripts\activate
pip install -r requirements.txt</code></pre>

  <h2>Run</h2>
  <pre><code>streamlit run app.py --server.headless true</code></pre>
  <p>Open <code>http://localhost:8501</code>.</p>

  <h2>Verification</h2>
  <ul>
    <li>Landing page renders the Little's Law decomposition and the two-loop finding.</li>
    <li>The Second Desk shows both gates with a 0–100% risk score, recommendation, and evidence.</li>
    <li>A ticket matching a known defect cluster blocks escalation and shows the workaround.</li>
    <li>Rahul T's escalation risk scores higher than team average; Karan B's closure risk scores higher than team average.</li>
  </ul>

  <h2>Next Four Weeks</h2>
  <ol>
    <li><strong>Calibrate and instrument</strong> — log agent decisions to re-tune risk scores against real outcomes.</li>
    <li><strong>Roll out the gate</strong> — coach the two outliers (Rahul T: over-escalation; Karan B: premature closure).</li>
    <li><strong>Fix the top three defects</strong> — remove 183 recurring tickets at the source.</li>
    <li><strong>Client self-service</strong> — deflect how-to and duplicate tickets before they enter the queue.</li>
  </ol>

  <p class="muted">Deliberately out of scope: additional hiring, an LLM chatbot, and large process reorganization.</p>

</div>
</body>
</html>
