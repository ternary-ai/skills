# Ternary Capital — Skills

**Agent-native finance. Build for markets.**

A library of cognitive agent skills for agentic financial intelligence. Skills are step-by-step playbooks loaded on demand — covering research, portfolio management, risk, and crisis protocols.

---

## What is a Skill?

A skill is a structured playbook the agent loads via `read_skill("<name>")`. It defines which tools to call, in what order, and what defaults to apply. The agent never improvises tool sequences — it follows the loaded skill exactly.

Skills are organized into two tiers:

| Tier | Description |
|---|---|
| `basic/` | Utilities and data primitives: charting, tables, calculators, data sourcing |
| `advanced/` | Full investment workflows: underwriting, portfolio construction, risk, crisis |

---

## Skill Categories

- **Research & Analysis** — equity research reports, quick screens, deep fundamental underwriting, variant perception detection, thesis integrity audits
- **Portfolio & Position Management** — sizing, conviction calibration, construction optimization, daily monitoring, exit discipline, performance attribution
- **Risk & Crisis** — capital preservation, crisis capital allocation, activist feasibility analysis
- **Charting & Visualization** — bar/line charts, network graphs, markdown tables
- **Utilities** — calculator, Anthropic SDK reference, data sourcing, news ingest

Full skill index and documentation: [skills/README.md](skills/README.md)

---

## Adding a Skill

1. Create `skills/basic/<name>/SKILL.md` or `skills/advanced/<name>/SKILL.md`
2. Add YAML frontmatter: `name`, `description` (one-line trigger for the agent)
3. Write: Purpose · Trigger · Inputs · Process · Tools · Output
4. Register it in the Skill Index in [skills/README.md](skills/README.md)

---

Part of [github.com/ternary-ai](https://github.com/ternary-ai) — open-source agents, models, synthetic data, prompt engineering, and scaffolding.

[contact@ternary.capital](mailto:contact@ternary.capital) · US · Japan · Est. 2020
