import smtplib
from unittest.mock import MagicMock, patch

import pytest
import requests

from wohnung_agent.models import Apartment, ApartmentMatch
from wohnung_agent.notifier import Notifier


def make_match() -> ApartmentMatch:
    apartment = Apartment(
        source="demo",
        external_id="1",
        title="Test apartment",
        url="https://example.com/1",
        city="Boizenburg",
        warm_rent_eur=750,
        rooms=2.5,
        has_kitchen=True,
    )
    return ApartmentMatch(apartment=apartment, score=90, reasons=["ok"], rejected=False)


def test_send_handles_telegram_request_exception():
    config = {
        "telegram": {"enabled": True, "bot_token": "abc", "chat_id": "123"},
        "email": {"enabled": False},
    }
    notifier = Notifier(config, language="en")

    with patch(
        "wohnung_agent.notifier.requests.post",
        side_effect=requests.RequestException("boom"),
    ):
        # No exception should bubble up from send()
        notifier.send(make_match())


@pytest.mark.parametrize(
    ("side_effect", "expected_fragment"),
    [
        (requests.Timeout("timeout"), "Telegram request timeout"),
        (requests.ConnectionError("offline"), "Telegram connection error"),
    ],
)
def test_send_handles_specific_telegram_request_failures(side_effect, expected_fragment, caplog):
    config = {
        "telegram": {"enabled": True, "bot_token": "abc", "chat_id": "123"},
        "email": {"enabled": False},
    }
    notifier = Notifier(config, language="en")

    with patch("wohnung_agent.notifier.requests.post", side_effect=side_effect):
        notifier.send(make_match())

    assert expected_fragment in caplog.text


def test_send_handles_smtp_exception():
    config = {
        "telegram": {"enabled": False},
        "email": {
            "enabled": True,
            "smtp_host": "smtp-test-host",
            "smtp_port": 587,
            "username": "u",
            "password": "p",
            "recipient": "r@example.com",
        },
    }
    notifier = Notifier(config, language="en")

    smtp_mock = MagicMock()
    smtp_mock.__enter__.return_value.starttls.side_effect = OSError("smtp down")

    with patch("wohnung_agent.notifier.smtplib.SMTP", return_value=smtp_mock):
        # No exception should bubble up from send()
        notifier.send(make_match())


def test_send_logs_smtp_authentication_error_with_endpoint(caplog):
    config = {
        "telegram": {"enabled": False},
        "email": {
            "enabled": True,
            "smtp_host": "smtp-test-host",
            "smtp_port": 587,
            "username": "u",
            "password": "p",
            "recipient": "r@example.com",
        },
    }
    notifier = Notifier(config, language="en")

    smtp_mock = MagicMock()
    smtp_session = smtp_mock.__enter__.return_value
    smtp_session.login.side_effect = smtplib.SMTPAuthenticationError(535, b"policy rejected")

    with patch("wohnung_agent.notifier.smtplib.SMTP", return_value=smtp_mock):
        notifier.send(make_match())

    assert "smtp-test-host:587" in caplog.text
    assert "policy rejected" in caplog.text


def test_send_with_all_channels_disabled_is_noop():
    config = {"telegram": {"enabled": False}, "email": {"enabled": False}}
    notifier = Notifier(config, language="en")
    notifier.send(make_match())