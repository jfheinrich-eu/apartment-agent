from unittest.mock import MagicMock, patch

import requests

from wohnung_agent.models import Apartment, ApartmentMatch, AppConfig, TelegramConfig, EmailConfig
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
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        telegram=TelegramConfig(enabled=True, bot_token="abc", chat_id="123"),
        email=EmailConfig(enabled=False),
    )
    notifier = Notifier(config, language="en")

    with patch(
        "wohnung_agent.notifier.requests.post",
        side_effect=requests.RequestException("boom"),
    ):
        # No exception should bubble up from send()
        notifier.send(make_match())


def test_send_handles_smtp_exception():
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        telegram=TelegramConfig(enabled=False),
        email=EmailConfig(
            enabled=True,
            smtp_host="smtp.example.com",
            smtp_port=587,
            username="u",
            password="p",
            recipient="r@example.com",
        ),
    )
    notifier = Notifier(config, language="en")

    smtp_mock = MagicMock()
    smtp_mock.__enter__.return_value.starttls.side_effect = OSError("smtp down")

    with patch("wohnung_agent.notifier.smtplib.SMTP", return_value=smtp_mock):
        # No exception should bubble up from send()
        notifier.send(make_match())


def test_send_with_all_channels_disabled_is_noop():
    config = AppConfig(
        max_warm_rent=800,
        min_rooms=2.5,
        regions=["Boizenburg"],
        telegram=TelegramConfig(enabled=False),
        email=EmailConfig(enabled=False),
    )
    notifier = Notifier(config, language="en")
    notifier.send(make_match())