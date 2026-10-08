import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from twilio.request_validator import RequestValidator

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

ALLOWED = "+15551230000"
STRANGER = "+15559990000"
AUTH_TOKEN = "twilio-auth-token-for-tests"
ADMIN = "admin-token-for-tests"
PUBLIC_URL = "https://bridge.example.test"

os.environ.update(
    GEMINI_API_KEY="test-key",
    TWILIO_ACCOUNT_SID="ACtest",
    TWILIO_AUTH_TOKEN=AUTH_TOKEN,
    TWILIO_PHONE_NUMBER="+15550001111",
    ALLOWED_SENDERS=ALLOWED,
    ADMIN_TOKEN=ADMIN,
    PUBLIC_URL=PUBLIC_URL,
)

import app as web  # noqa: E402
import working_sms_mcp_bridge as bridge  # noqa: E402


class FakeTwilio:
    def __init__(self):
        self.sent = []
        self.messages = SimpleNamespace(create=self.create)

    def create(self, body, from_, to):
        self.sent.append(to)
        return SimpleNamespace(sid="SM123")


@pytest.fixture
def client(monkeypatch):
    fake = FakeTwilio()
    monkeypatch.setattr(web, "twilio_client", fake)
    action = web.CursorAction(action=list(web.ActionType)[0], description="echo <b>hi</b>")
    monkeypatch.setattr(web, "process_with_gemini", lambda message: action)
    monkeypatch.setattr(web, "perform_cursor_action", lambda data: "✅ done <script>alert(1)</script>")
    web.app.config["TESTING"] = True
    with web.app.test_client() as c:
        c.fake = fake
        yield c


def signed_sms(client, sender, body="make a file", signature=None):
    form = {"From": sender, "Body": body}
    if signature is None:
        signature = RequestValidator(AUTH_TOKEN).compute_signature(PUBLIC_URL + "/sms", form)
    return client.post("/sms", data=form, headers={"X-Twilio-Signature": signature})


def test_sms_without_a_twilio_signature_is_refused(client):
    assert client.post("/sms", data={"From": ALLOWED, "Body": "hi"}).status_code == 403
    assert client.fake.sent == []


def test_sms_with_a_forged_signature_is_refused(client):
    assert signed_sms(client, ALLOWED, signature="forged").status_code == 403


def test_signed_sms_from_an_unknown_sender_is_refused(client):
    assert signed_sms(client, STRANGER).status_code == 403
    assert client.fake.sent == []


def test_signed_sms_from_an_allowed_sender_runs_and_replies_only_to_it(client):
    assert signed_sms(client, ALLOWED).status_code == 200
    assert client.fake.sent == [ALLOWED]


@pytest.mark.parametrize("path", ["/", "/logs", "/clear_logs", "/send_sms", "/test_bridge"])
def test_admin_routes_refuse_requests_without_the_token(client, path):
    assert client.get(path).status_code == 403


def test_trigger_refuses_requests_without_the_token(client):
    assert client.post("/trigger", data={"message": "rm -rf"}).status_code == 403


def test_admin_routes_are_closed_when_no_token_is_configured(client, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "")
    assert client.get("/logs", headers={"X-Admin-Token": ""}).status_code == 403


def test_a_token_in_the_url_signs_in_and_later_requests_use_the_cookie(client):
    assert client.get(f"/?token={ADMIN}").status_code == 200
    assert client.get("/logs").status_code == 200


def test_send_sms_refuses_numbers_outside_the_allowlist(client):
    page = client.get(f"/send_sms?token={ADMIN}&to={STRANGER}&message=hi").get_data(as_text=True)
    assert "not in ALLOWED_SENDERS" in page and client.fake.sent == []


def test_trigger_output_is_escaped(client):
    page = client.post(f"/trigger?token={ADMIN}", data={"message": "<img src=x onerror=alert(1)>"}).get_data(as_text=True)
    assert "<img src=x" not in page and "&lt;img src=x" in page
    assert "<script>alert(1)</script>" not in page


@pytest.mark.parametrize(
    "command",
    [
        "ls; touch pwned",
        "python -c 'print(1)'",
        "pip install anything",
        "git push origin main",
        "git -c core.pager=sh log",
        "git log --output=/tmp/x",
        "git diff --ext-diff",
        "git branch -D main",
        "find . -exec rm {} ;",
        "find . -delete",
        "curl https://example.com",
        "rm -rf /",
        "",
    ],
)
def test_run_command_refuses_anything_that_can_write_or_execute(command):
    with pytest.raises((PermissionError, ValueError)):
        bridge.parse_command(command)


@pytest.mark.parametrize("command", ["ls -la", "git status", "git log --oneline -5", "grep -rn TODO src", "find . -name '*.py'", "git branch -a"])
def test_run_command_allows_read_only_commands(command):
    assert bridge.parse_command(command)[0] in bridge.READ_ONLY


async def test_shell_metacharacters_reach_ls_as_arguments_not_as_a_second_command(tmp_path, monkeypatch):
    from fastmcp import Client as McpClient

    monkeypatch.setattr(bridge, "PROJECT_DIR", str(tmp_path))
    async with McpClient(bridge.mcp) as mcp:
        await mcp.call_tool("run_command", {"command": "ls ; touch pwned"}, raise_on_error=False)
    assert not (tmp_path / "pwned").exists()


async def test_sms_tools_refuse_numbers_outside_the_allowlist(monkeypatch):
    from fastmcp import Client as McpClient

    fake = FakeTwilio()
    monkeypatch.setattr(bridge, "Client", lambda sid, token: fake)
    async with McpClient(bridge.mcp) as mcp:
        refused = await mcp.call_tool("send_sms_response", {"phone_number": STRANGER, "message": "hi"}, raise_on_error=False)
        sent = await mcp.call_tool("send_sms_response", {"phone_number": ALLOWED, "message": "hi"}, raise_on_error=False)
    assert "not in ALLOWED_SENDERS" in refused.content[0].text
    assert fake.sent == [ALLOWED] and ALLOWED in sent.content[0].text
