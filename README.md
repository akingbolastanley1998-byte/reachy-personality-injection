# Network-Exposed Configuration Attacks on LLM-Controlled Social Robots

**Proof-of-Concept Code and Research Artefacts**

> Stanley Akingbola, Ugbede Ibrahim, Yan Lin Aung, Quang Dan Le, Hong Qing Yu
> University of Derby, Derby, UK
>
> Corresponding authors: Stanley Akingbola (akingbolastanley1998@gmail.com),
> Yan Lin Aung (y.aung@derby.ac.uk)

## Overview

This repository contains the proof-of-concept code, pipeline modification,
and evidence artefacts for the paper:

> **"Network-Exposed Configuration Attacks on LLM-Controlled Social Robots"**

We demonstrate that the Pollen Robotics Reachy Mini Lite exposes two
entirely unauthenticated API endpoints controlling the robot's AI system
prompt on a management interface bound to all network interfaces (0.0.0.0:7860).
Any device on the same WiFi network can replace the robot's AI instructions
in under two seconds, with no credentials and no LLM interaction.

**Vulnerability:**
- CWE-306: Missing Authentication for a Critical Function
- CWE-1327: Binding to an Unrestricted IP Address
- CVSS v3.1 Base Score: 6.5 MEDIUM (`CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N`)
- A second, distinct finding — cross-origin reachability of the `save`
  endpoint (CWE-352) — is scored separately, also 6.5 MEDIUM.

**Responsible Disclosure:**
Disclosed to Pollen Robotics via private GitHub Security Advisory before
publication. Secondary notification sent to contact@pollen-robotics.com
and security@huggingface.co.

---

## Repository Structure

```
├── exploit.py                    # Proof-of-concept exploit (V1/V2 vectors)
├── pipeline_patch/
│   └── text_to_text.py           # Text-to-text pipeline modification for Phase 1 testing
├── phase1_prompts.json           # All 11 Phase 1 prompt injection prompts + results
├── repository_survey.xlsx        # Full 59-repository classification (Section 8.1.2)
├── logs/
│   ├── vector2_server_log.txt    # Server log from Vector 2 (remote Python)
│   ├── csrf_test_log.txt         # Server log from the cross-origin CSRF test (Vector 3b)
│   └── vector3_browser_console.txt  # Browser console output from Vector 3
└── docs/
    └── reproduction_checklist.md # Step-by-step reproduction guide
```

> **Note:** `repository_survey.xlsx` is referenced by the paper (Section 7,
> Code Availability) but is not yet present in this repository. It needs to
> be added before the arXiv version is finalised — see the paper's Section
> 8.1.2 for what it must contain (the full 59-repository classification,
> genuine/false-positive justification for every repository, and the
> per-repository unauthenticated-endpoint finding for all 12 confirmed
> genuine applications).

---

## Target System

- **Robot:** Pollen Robotics Reachy Mini Lite
- **App:** reachy-mini-conversation-app v0.8.0 (commit 81dfd7c)
- **Host:** Windows 11 PC
- **Vulnerable endpoints:**
  - `POST /api/v1/personalities/save`
  - `POST /api/v1/personalities/apply`
- **Management interface:** Gradio on 0.0.0.0:7860 (all interfaces)

> The pinned commit and `/api/v1` path prefix used throughout the paper
> match this release exactly. The current public
> `reachy-mini-conversation-app` repository has since changed its route
> structure and no longer exposes this exact path or commit; the
> vulnerable request-parsing logic is unchanged in substance as of the
> v0.8.0 tag, but file and route layout should not be assumed identical.

---

## Quick Start

### Prerequisites
```bash
pip install requests websockets
```

### Vector 1 — Local (co-installed malware simulation)
```bash
python exploit.py --target localhost --lang French
```

### Vector 2 — Remote WiFi (any device on shared network)
```bash
python exploit.py --target <ROBOT_HOST_IP> --lang Spanish
```

### Vector 3 — Browser Console
Open F12 developer console on any device on the same WiFi and paste the
commands from `logs/vector3_browser_console.txt`.

### Restore Default Personality
```bash
python exploit.py --target <ROBOT_HOST_IP> --restore
```

### Enumerate Endpoints
```bash
python exploit.py --target <ROBOT_HOST_IP> --enumerate
```

---

## Text-to-Text Pipeline Modification

The `pipeline_patch/text_to_text.py` module adds a text input channel
to the Reachy Mini conversation app for systematic Phase 1 testing.

```bash
# From the reachy_mini_conversation_app root directory:
python pipeline_patch/text_to_text.py

# Then send prompts:
curl -X POST http://localhost:8765/chat \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, what is your name?"}'
```

---

## Phase 1 Results Summary

Eleven hand-written prompt-injection attempts were applied; none succeeded
in producing unauthorised behaviour. This is reported in the paper as a
**scoped manual control, not an automated adversarial evaluation** — see
Section 6.1 of the paper. Full prompts and recorded outputs are in
`phase1_prompts.json`.

| Category | Prompts | Result |
|---|---|---|
| False identity acceptance | 3 | All REJECTED |
| System prompt extraction | 3 | All REJECTED |
| Safety override | 3 | All REJECTED |
| Memory corruption (false operator-identity claim) | 2 | 1 REJECTED, 1 PARTIAL (claim stored in memory, no elevated behaviour in-session) |

> The paper's methodology (Section 5.5) describes five prompt-injection
> categories, including a distinct "unauthorised tool invocation (camera
> access, memory writes)" category. That category is not broken out as a
> separate top-level entry in `phase1_prompts.json` — worth checking
> against the paper text before the artefact is finalised.

---

## Evidence

Server logs and browser console outputs from all three attack vectors
are in the `logs/` directory.

---

## Reproduction Checklist

See `docs/reproduction_checklist.md` for the full step-by-step guide.

---

## Ethics Statement

All testing was conducted on researcher-owned hardware on private home
networks. No third-party systems, devices, or networks were targeted.
The university guest WiFi was used only to confirm the attack surface
was reachable in an institutional environment; no exploitation was
performed on it.

---

## Citation

A formal citation (venue, year, DOI) will be added once the paper is
assigned one. In the meantime:

```bibtex
@misc{akingbola2026networkexposed,
  title  = {Network-Exposed Configuration Attacks on LLM-Controlled Social Robots},
  author = {Akingbola, Stanley and Ibrahim, Ugbede and Aung, Yan Lin and Le, Quang Dan and Yu, Hong Qing},
  institution = {University of Derby},
  year   = {2026},
  note   = {Preprint}
}
```

---

## License

The code in this repository is released for research and educational
purposes only, consistent with ACM's policy on responsible disclosure
and reproducible research.
