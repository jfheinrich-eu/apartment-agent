from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any
import requests
from wohnung_agent.models import ApartmentMatch


def format_match(apartment_match: ApartmentMatch) -> str:
    apartment = apartment_match.apartment
    rent = "unbekannt" if apartment.warm_rent_eur is None else f"{apartment.warm_rent_eur:.0f} € warm"
    rooms = "unbekannt" if apartment.rooms is None else str(apartment.rooms)
    reasons = "\n".join(f"- {reason}" for reason in apartment_match.reasons)

    return (
        f"NEUER TREFFER: {apartment.city} – {apartment.title}\n"
        f"Miete: {rent}\n"
        f"Zimmer: {rooms}\n"
        f"Score: {apartment_match.score}/100\n"
        f"Link: {apartment.url}\n\n"
        f"Bewertung:\n{reasons}"
    )


class Notifier:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def send(self, apartment_match: ApartmentMatch) -> None:
        message = format_match(apartment_match)
        print("\n" + message + "\n")
        self._send_telegram(message)
        self._send_email(message)

    def _send_telegram(self, message: str) -> None:
        telegram_config = self.config.get("telegram", {})
        if not telegram_config.get("enabled"):
            return

        bot_token = telegram_config["bot_token"]
        chat_id = telegram_config["chat_id"]
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=20,
        )
        response.raise_for_status()

    def _send_email(self, message: str) -> None:
        email_config = self.config.get("email", {})
        if not email_config.get("enabled"):
            return

        email_message = EmailMessage()
        email_message["From"] = email_config["username"]
        email_message["To"] = email_config["recipient"]
        email_message["Subject"] = "Neuer Wohnungstreffer"
        email_message.set_content(message)

        with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as smtp:
            smtp.starttls()
            smtp.login(email_config["username"], email_config["password"])
            smtp.send_message(email_message)
