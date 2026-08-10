# Unauthenticated Personality Injection in Embodied AI

**Proof-of-Concept Code and Research Artefacts**

> Stanley Akingbola, Dan, Yan Lin Aung  
> University of Derby, Derby, UK  
> *Proceedings of the 16th International Conference on the Internet of Things (IoT 2026)*  
> Newcastle upon Tyne, UK, November 2026

---

## Overview

This repository contains the proof-of-concept code, pipeline modification,
and evidence artefacts for the paper:

> **"Unauthenticated Personality Injection in Embodied AI:
> A Configuration-Layer Attack on LLM-Controlled Social Robots"**

We demonstrate that the Pollen Robotics Reachy Mini Lite exposes two
entirely unauthenticated API endpoints controlling the robot's AI system
prompt on a management interface bound to all network interfaces (0.0.0.0:7860).
Any device on the same WiFi network can replace the robot's AI instructions
in under two seconds, with no credentials and no LLM interaction.

**Vulnerability:**
- CWE-306: Missing Authentication for a Critical Function
- CWE-1327: Binding to an Unrestricted IP Address
- CVSS v3.1 Base Score: 7.1 HIGH

**Responsible Disclosure:**  
Disclosed to Pollen Robotics via private GitHub Security Advisory before
publication. Secondary notification sent to contact@pollen-robotics.com
and security@huggingface.co.

---

## Repository Structure

```
├── exploit.py                    # Proof-of-concept exploit (all 3 vectors)
├── pipeline_patch/
│   └── text_to_text.py           # Text-to-text pipeline modification for Phase 1 testing
├── phase1_prompts.json           # All 11 Phase 1 prompt injection prompts + results
├── logs/
│   ├── vector2_server_log.txt    # Server log from Vector 2 (remote Python)
│   ├── csrf_test_log.txt         # Server log from partial CSRF test (Vector 3b)
│   └── vector3_browser_console.txt  # Browser console output from Vector 3
└── docs/
    └── reproduction_checklist.md # Step-by-step reproduction guide
```

---

## Target System

- **Robot:** Pollen Robotics Reachy Mini Lite
- **App:** reachy-mini-conversation-app v0.8.0 (commit 81dfd7c)
- **Host:** Windows 11 PC
- **Vulnerable endpoints:**
  - `POST /api/v1/personalities/save`
  - `POST /api/v1/personalities/apply`
- **Management interface:** Gradio on 0.0.0.0:7860 (all interfaces)

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

All 11 prompt injection attempts failed. See `phase1_prompts.json` for
full details. The HuggingFace-hosted LLM resisted all attempts across:

| Category | Prompts | Result |
|---|---|---|
| False identity acceptance | 3 | All REJECTED |
| System prompt extraction | 3 | All REJECTED |
| Safety override | 3 | All REJECTED |
| Memory corruption | 2 | REJECTED / PARTIAL (session-bounded) |

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

```bibtex
@inproceedings{akingbola2026personality,
  title     = {Unauthenticated Personality Injection in Embodied AI:
               A Configuration-Layer Attack on LLM-Controlled Social Robots},
  author    = {Akingbola, Stanley and Dan and Aung, Yan Lin},
  booktitle = {Proceedings of the 16th International Conference on
               the Internet of Things (IoT 2026)},
  year      = {2026},
  address   = {Newcastle upon Tyne, UK},
  publisher = {ACM}
}
```

---

## License

The code in this repository is released for research and educational
purposes only, consistent with ACM's policy on responsible disclosure
and reproducible research.
