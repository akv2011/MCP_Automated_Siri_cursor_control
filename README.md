# SMS to Cursor over MCP

Text a phone number and an agent works in your editor. A Twilio webhook receives the SMS, Gemini turns it into a structured action, and the action reaches Cursor through an MCP server or, as a fallback, through UI automation. A summary goes back by SMS.

```
SMS -> Twilio -> /sms (Flask) -> Gemini -> action -> MCP bridge or UI bridge -> Cursor
                                                                         |
                                                     SMS summary <-------+
```

## Security model

Anything that turns a text message into actions on a machine is remote code execution unless every hop is checked. These are the checks, and `tests/test_guards.py` proves each one.

| Entry point | Check |
|---|---|
| `POST /sms` | Valid `X-Twilio-Signature` for the public URL Twilio called, and `From` must be in `ALLOWED_SENDERS` |
| Every other route (`/`, `/trigger`, `/logs`, `/send_sms`, ...) | `ADMIN_TOKEN` as `X-Admin-Token`, `?token=` once (then an HttpOnly, SameSite=Strict cookie). With no `ADMIN_TOKEN` set, these routes are closed |
| Any outgoing SMS, from a route or an MCP tool | The recipient must be in `ALLOWED_SENDERS`; all sends go through one function |
| MCP tool `run_command` | Parsed into argv and run without a shell. Only `ls`, `grep`, `find` (no `-exec`, `-delete`, `-fprint`) and read-only `git` (`status`, `log`, `diff`, `show`, list-only `branch`, no `--output` or external diff) |
| HTML responses | User text is escaped |
| Network binding | Flask app and UI bridge listen on 127.0.0.1; debug mode only with `FLASK_DEBUG=1` |

## Setup

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

| Variable | Meaning |
|---|---|
| `GEMINI_API_KEY` | Gemini key for turning SMS into actions |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Twilio account and the number people text |
| `ALLOWED_SENDERS` | Comma-separated E.164 numbers allowed to send commands and receive replies |
| `OWNER_PHONE` | Default recipient for the dashboard's test SMS; must also be in `ALLOWED_SENDERS` |
| `ADMIN_TOKEN` | Long random string for the dashboard and test routes |
| `PUBLIC_URL` | The https URL Twilio calls (your tunnel), used to verify signatures |
| `PROJECT_DIR` | Folder the MCP tools may read; defaults to the current directory |

## Run

```sh
python src/app.py                 # SMS app on 127.0.0.1:5000
python src/simple_ui_bridge.py    # UI automation fallback on 127.0.0.1:5002
ngrok http 5000                   # set PUBLIC_URL to the https URL it prints
```

Point the Twilio number's messaging webhook at `$PUBLIC_URL/sms`, then open `http://127.0.0.1:5000/?token=$ADMIN_TOKEN` for the dashboard.

## Connect the MCP bridge

`src/working_sms_mcp_bridge.py` is an MCP server over stdio (FastMCP 4, MCP 2026-07-28) with 11 tools: `sms_command`, `process_sms_request`, `cursor_automation`, `count_tests`, `find_large_files`, `analyze_codebase`, `run_command`, `send_sms_response`, `send_completion_summary`, `send_summary_message`, `complete_sms_task`. Replace `/path/to` with where you cloned this repo.

Claude Code:

```sh
claude mcp add sms-cursor-bridge -e PROJECT_DIR=/path/to/project -e ALLOWED_SENDERS=+15551234567 -- /path/to/MCP_Automated_Siri_cursor_control/.venv/bin/python /path/to/MCP_Automated_Siri_cursor_control/src/working_sms_mcp_bridge.py
```

Codex CLI:

```sh
codex mcp add sms-cursor-bridge --env PROJECT_DIR=/path/to/project -- /path/to/MCP_Automated_Siri_cursor_control/.venv/bin/python /path/to/MCP_Automated_Siri_cursor_control/src/working_sms_mcp_bridge.py
```

Gemini CLI (no `--` before the command):

```sh
gemini mcp add -s user -e PROJECT_DIR=/path/to/project sms-cursor-bridge /path/to/MCP_Automated_Siri_cursor_control/.venv/bin/python /path/to/MCP_Automated_Siri_cursor_control/src/working_sms_mcp_bridge.py
```

Cursor (`.cursor/mcp.json`) and Claude Desktop (`claude_desktop_config.json`): copy the `mcpServers` block from `mcp.json.example`. `python scripts/generate_mcp_link.py` prints a one-click Cursor install link for this checkout.

MCP Inspector:

```sh
npx @modelcontextprotocol/inspector /path/to/MCP_Automated_Siri_cursor_control/.venv/bin/python /path/to/MCP_Automated_Siri_cursor_control/src/working_sms_mcp_bridge.py
```

Checked on 2026-10-08: Claude Code 2.1.294 connects and MCP Inspector lists all 11 tools; Codex CLI 0.156.1 accepts the config; Gemini CLI 0.63.0 ran headless and called `count_tests`, which listed the repo's test file. Gemini CLI marks servers "Disabled" in a folder it does not trust; trust the folder or pass `--skip-trust`.

## Tests

```sh
pip install -r requirements-dev.txt
pytest
```

36 tests cover Gemini errors staying out of SMS replies, the webhook signature and sender checks, the admin token, the SMS allowlist on routes and MCP tools, HTML escaping, and the command parser, including that `ls ; touch pwned` creates nothing. Disabling the guards turns 24 of them red. `scripts/manual/` holds scripts that hit the live Twilio and Gemini APIs by hand.

## Notes

The UI automation fallback uses `pyautogui` keyboard shortcuts written for Cursor on Windows; the MCP bridge, webhook and guards run on any OS.

## Layout

```
src/app.py                      Twilio webhook, dashboard, Gemini planning, guards
src/working_sms_mcp_bridge.py   MCP server with the tools above
src/simple_ui_bridge.py         UI automation fallback for Cursor
src/schemas.py                  structured action the model must return
scripts/                        startup helper, Cursor link generator, manual checks
tests/test_guards.py            security tests
```
