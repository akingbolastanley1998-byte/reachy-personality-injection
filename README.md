# Network-Exposed Configuration Attacks on LLM-Controlled Social Robots

Proof-of-concept code and research artefacts accompanying the paper of the same title.

**Authors:** Stanley Akingbola, Ugbede Ibrahim, Yan Lin Aung, Quang Dan Le, Hong Qing Yu
University of Derby, Derby, UK

Corresponding authors: Stanley Akingbola (akingbolastanley1998@gmail.com), Yan Lin Aung (y.aung@derby.ac.uk)

## Summary

Large language models are increasingly used as the reasoning layer behind physical, consumer-facing robots: they decide what the robot says, how it responds to a person, and in some cases what actions it takes. Almost all existing security research on these systems focuses on the conversational interface itself, treating the LLM's system prompt as fixed and asking whether adversarial input at inference time can override it. This project investigates a different and comparatively unexamined layer: the network-facing configuration interface that supplies that system prompt in the first place, before the model ever processes a single message.

Using the Pollen Robotics Reachy Mini Lite as a case study, we show that an attacker who never interacts with the robot's LLM at all can still take full control of what it says and how it behaves. The robot's personality management API, which defines the system prompt sent to the cloud-hosted LLM at the start of every session, is served over a Gradio interface bound to all network interfaces rather than restricted to the local host. Two endpoints on this interface, one that saves a new personality configuration and one that applies it, accept requests from any device on the network with no authentication, no session validation, and no caller verification of any kind. An attacker on the same WiFi network, whether a malicious guest, a compromised device, or another resident on a shared network in a home, school, or care setting, can submit two HTTP requests and silently replace the robot's operating instructions. The change takes effect in under two seconds, persists across application restarts, and produces an observable change in the robot's spoken behaviour on physical hardware, confirmed here by causing the robot to respond in a different language entirely of the attacker's choosing.

Because this attack chain never touches the model's conversational input or output, the robot's inference-time safety alignment is structurally irrelevant to it. Eleven direct prompt-injection attempts against the LLM itself were separately tested and all failed, which is reported here as evidence that the conversational layer was behaving as intended, not as evidence that the system as a whole is secure: the configuration-layer attack bypasses that layer entirely rather than defeating it. A further finding shows that one of the two endpoints is additionally reachable cross-origin, without a CORS preflight check, meaning a victim on the robot's network need only visit an ordinary web page for the same configuration-layer compromise to occur with no network tooling at all. A source-verified survey of 59 public repositories combining the same web frameworks with robotics or embodied-agent code found the identical missing-authentication pattern recurring in the large majority of genuine applications, indicating that this is not an isolated oversight in one product but a structural gap between how these frameworks are typically configured during development and what a consumer deployment actually requires. We refer to this gap, and the point in a product's lifecycle where it opens up, as the deployment gap.

The practical implication is that securing an LLM-controlled robot cannot rely on model-level defences alone. A robot can refuse every adversarial prompt a user sends it and still be fully compromised through the infrastructure that configures it, because the two problems sit at different layers of the system and neither compensates for a failure in the other.

| | |
|---|---|
| CWE-306 | Missing Authentication for a Critical Function |
| CWE-1327 | Binding to an Unrestricted IP Address |
| CVSS v3.1 (main finding) | 6.5 Medium — `AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N` |
| CWE-352 (cross-origin `save`) | 6.5 Medium — scored separately |

**Disclosure.** Reported to Pollen Robotics via private GitHub Security Advisory prior to publication, with secondary notice to contact@pollen-robotics.com and security@huggingface.co.

## Repository contents

```
exploit.py                   Proof-of-concept exploit (Vectors 1 and 2)
pipeline_patch/
  text_to_text.py            Text-to-text channel added for Phase 1 testing
phase1_prompts.json          All 11 Phase 1 prompts, categories, and recorded results
repository_survey.xlsx       Classification of 59 surveyed repositories (Section 8.1.2)
logs/
  vector2_server_log.txt     Server log, Vector 2 (remote attacker)
  csrf_test_log.txt          Server log, cross-origin CSRF test (Vector 3b)
  vector3_browser_console.txt  Browser console output, Vector 3
docs/
  reproduction_checklist.md  Step-by-step reproduction guide
```

`repository_survey.xlsx` currently records the genuine/false-positive classification of all 59 repositories (12 confirmed genuine) but not yet the per-repository unauthenticated-endpoint findings that the paper's 9/11 and 10/11 figures depend on. That column needs completing before the figures in Section 8.1.2 are fully supported by the released artefact.

## Target system

- Robot: Pollen Robotics Reachy Mini Lite
- Application: `reachy-mini-conversation-app` v0.8.0, commit `81dfd7c`
- Host: Windows 11 PC
- Vulnerable endpoints: `POST /api/v1/personalities/save`, `POST /api/v1/personalities/apply`
- Management interface: Gradio on `0.0.0.0:7860`

The pinned commit and `/api/v1` path prefix used throughout the paper match this release. The current public `reachy-mini-conversation-app` repository has since changed its route structure and no longer exposes this exact path or commit; the vulnerable request-parsing logic is unchanged in substance as of the v0.8.0 tag, but file and route layout should not be assumed identical.

## Usage

```bash
pip install requests websockets
```

Vector 1, local (co-installed malware simulation):
```bash
python exploit.py --target localhost --lang French
```

Vector 2, remote (any device on the same WiFi network):
```bash
python exploit.py --target <ROBOT_HOST_IP> --lang Spanish
```

Vector 3, browser console: open the F12 developer console on any device on the same WiFi network and paste the commands from `logs/vector3_browser_console.txt`.

Restore the default personality:
```bash
python exploit.py --target <ROBOT_HOST_IP> --restore
```

Enumerate endpoints:
```bash
python exploit.py --target <ROBOT_HOST_IP> --enumerate
```

### Text-to-text pipeline modification

`pipeline_patch/text_to_text.py` adds a text input channel to the conversation app so Phase 1 prompts can be sent and logged systematically, without touching the LLM, system prompt, tool descriptions, memory storage, or management API.

```bash
# from the reachy-mini-conversation-app root directory
python pipeline_patch/text_to_text.py

curl -X POST http://localhost:8765/chat \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, what is your name?"}'
```

## Phase 1 results

Eleven hand-written prompt-injection attempts were made against the cloud LLM, across the categories below. This is a scoped manual control, not an automated adversarial evaluation; see Section 6.1 of the paper for how the result should be read. Full prompts and recorded outputs are in `phase1_prompts.json`.

| Category | Prompts | Result |
|---|---|---|
| False identity acceptance | 3 | Rejected |
| System prompt extraction | 3 | Rejected |
| Safety override | 3 | Rejected |
| Memory corruption (false operator-identity claim) | 2 | 1 rejected, 1 partial — claim accepted and written to memory, no elevated behaviour observed in-session |

## Reproduction

See `docs/reproduction_checklist.md` for the full step-by-step guide. Server logs and browser console output for all three vectors are in `logs/`.

## Ethics

All testing was conducted on researcher-owned hardware on private home networks. No third-party system, account, or device was accessed. The university guest WiFi was used only to confirm the attack surface was reachable in an institutional environment; no exploitation was performed on it.

## Citation

```bibtex
@misc{akingbola2026networkexposed,
  title       = {Network-Exposed Configuration Attacks on LLM-Controlled Social Robots},
  author      = {Akingbola, Stanley and Ibrahim, Ugbede and Aung, Yan Lin and Le, Quang Dan and Yu, Hong Qing},
  institution = {University of Derby},
  year        = {2026},
  note        = {Preprint}
}
```

## License

Released for research and educational use, consistent with ACM's policy on responsible disclosure and reproducible research.
