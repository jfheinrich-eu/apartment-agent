from __future__ import annotations

from wohnung_agent.models import Apartment, ApartmentMatch, SearchProfile, InternetStatus

REGION_MATCH_SCORE = 25
RENT_MATCH_SCORE = 30
ROOM_MATCH_SCORE = 25
KITCHEN_MATCH_SCORE = 15
ADDRESS_MATCH_SCORE = 5
INTERNET_AVAILABLE_SCORE = 15
RENT_MISSING_PENALTY = 10
ROOMS_MISSING_PENALTY = 10
KITCHEN_UNKNOWN_PENALTY = 5
INTERNET_NOT_AVAILABLE_PENALTY = 10


class FilterEngine:
    """Score apartments against the active search profile."""

    def __init__(self, profile: SearchProfile) -> None:
        """Cache normalized regions for faster matching."""
        self.profile = profile
        self.normalized_regions = {region.casefold() for region in profile.regions}

    def evaluate(self, apartment: Apartment) -> ApartmentMatch:
        """Return a scored match result for a single apartment."""
        reasons: list[str] = []
        score = 0
        rejected = False

        if apartment.city.casefold() not in self.normalized_regions:
            rejected = True
            reasons.append(f"Ort passt nicht: {apartment.city}")
        else:
            score += REGION_MATCH_SCORE
            reasons.append(f"Ort passt: {apartment.city}")

        if apartment.warm_rent_eur is None:
            score -= RENT_MISSING_PENALTY
            reasons.append("Warmmiete fehlt")
        elif apartment.warm_rent_eur <= self.profile.max_warm_rent:
            score += RENT_MATCH_SCORE
            reasons.append(f"Warmmiete passt: {apartment.warm_rent_eur:.0f} €")
        else:
            rejected = True
            reasons.append(f"Warmmiete zu hoch: {apartment.warm_rent_eur:.0f} €")

        if apartment.rooms is None:
            score -= ROOMS_MISSING_PENALTY
            reasons.append("Zimmerzahl fehlt")
        elif apartment.rooms >= self.profile.min_rooms:
            score += ROOM_MATCH_SCORE
            reasons.append(f"Zimmer passen: {apartment.rooms}")
        else:
            rejected = True
            reasons.append(f"Zu wenige Zimmer: {apartment.rooms}")

        if self.profile.kitchen_required:
            if apartment.has_kitchen is True:
                score += KITCHEN_MATCH_SCORE
                reasons.append("Einbauküche vorhanden")
            elif apartment.has_kitchen is False:
                rejected = True
                reasons.append("Keine Einbauküche")
            else:
                score -= KITCHEN_UNKNOWN_PENALTY
                reasons.append("Einbauküche ungeklärt")

        if apartment.address:
            score += ADDRESS_MATCH_SCORE
            reasons.append("Adresse vorhanden")
        else:
            reasons.append("Adresse fehlt; Internetprüfung nicht sicher möglich")

        if apartment.internet_status == InternetStatus.AVAILABLE_1000:
            score += INTERNET_AVAILABLE_SCORE
            reasons.append("Vodafone Kabel 1000 verfügbar")
        elif apartment.internet_status == InternetStatus.NOT_AVAILABLE_1000:
            score -= INTERNET_NOT_AVAILABLE_PENALTY
            reasons.append("Vodafone Kabel 1000 nicht verfügbar")
        else:
            reasons.append("Vodafone Kabel 1000 ungeprüft")

        return ApartmentMatch(
            apartment=apartment,
            score=max(0, min(score, 100)),
            reasons=reasons,
            rejected=rejected,
        )
