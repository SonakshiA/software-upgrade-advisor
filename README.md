# Upgrade Decision Model

Decide whether a software package needs upgrading.

An agent searches trusted sources for release notes and security advisories. A decision model then reads that evidence and says whether to upgrade, why, and how urgently. If the evidence is too thin to decide, it says so instead of guessing.

## How it works

1. **Research agent** ([create_agent.py](create_agent.py)): an Azure AI Foundry agent that uses Bing Custom Search to find official release notes, advisories, and support information. It returns JSON with `package`, `installed_version`, `summary`, and `source_urls`.
2. **Decision model** ([model.py](model.py)): takes the agent's summary as evidence and answers three questions:
   - `upgrade_needed`: a probability-style signal that an upgrade is needed.
   - `reason`: `security-fix`, `end-of-support`, `compatibility`, `routine-update`, `no-upgrade-needed`, or `insufficient-evidence`.
   - `urgency`: a score from 0 (Routine) to 3 (Immediate). The score is an expected value, so it can fall between whole numbers.
3. **Action**: `print_upgrade_decision` maps the answers to one of `gather more evidence`, `monitor`, `schedule upgrade review`, or `prioritize upgrade review`. If the reason is `insufficient-evidence`, urgency is ignored.
4. **Pipeline** ([fetch_news.py](fetch_news.py)): runs the agent for a package and passes its summary to the decision model.

Missing evidence is never treated as proof that a version is safe.

## Prerequisites

- Python 3.11+
- An Azure AI Foundry project with:
  - a Bing Custom Search connection
  - a `gpt-4.1` model deployment for the agent
  - a decision model deployment

## Setup

```powershell
pip install -r requirements.txt
Copy-Item .env.template .env
```

Edit `.env`:

| Variable | Description |
|----------|-------------|
| `ENDPOINT` | Decision model endpoint, ending at `/providers/microsoft`. Do not add `/v1/systemone`; the SDK appends it. |
| `PROJECT_ENDPOINT` | Foundry project endpoint. |
| `DEPLOYMENT_NAME` | Decision model deployment name. |
| `CONN_ID` | Resource ID of the Bing Custom Search connection. |
| `DOMAIN_NAME` | Bing Custom Search instance name. |

`.env` is git-ignored. Do not commit it.

## Usage

Create the agent once:

```powershell
python create_agent.py
```

Run the pipeline:

```powershell
python fetch_news.py
```

By default, [fetch_news.py](fetch_news.py) checks Django 4.2.0. Change `user_message` to check another package and version.

Example output:

```text
{ "package": "...", "installed_version": "...", "summary": "...", "source_urls": [...] }
Upgrade-needed signal: ...
Reason: ... (confidence: ...)
Urgency: ... of 3
Action: ...
```