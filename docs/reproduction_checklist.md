# Reproduction Checklist

| Step | Action | Expected Result |
|---|---|---|
| 1 | Install reachy-mini-conversation-app v0.8.0 (commit 81dfd7c) | App installed; robot connected via USB |
| 2 | Start: `reachy-mini-conversation-app.exe --ui` | Console: `Uvicorn running on http://0.0.0.0:7860` |
| 3 | From attacker device: `curl http://TARGET:7860/api/v1/status` | HTTP 200 — no credentials required |
| 4 | Run: `python exploit.py --target TARGET --lang Spanish` | Both endpoints return HTTP 200; ATTACK COMPLETE printed |
| 5 | Ask robot: "Hello, how are you today?" | Robot responds in Spanish |
| 6 | Stop and restart the application | Robot still responds in Spanish (persist=True) |
| 7 | Run: `python exploit.py --target TARGET --restore` | Robot returns to English default |
| 8 | Check host server logs during step 4 | Source IP of attacker machine appears on POST requests |

Replace TARGET with the robot host IP (e.g. 192.168.0.23).
For Vector 1: use --target localhost.
For Vector 3: paste commands from logs/vector3_browser_console.txt into browser F12 console.
