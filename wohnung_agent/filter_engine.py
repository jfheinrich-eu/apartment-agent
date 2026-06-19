from __future__ import annotations

from wohnung_agent.models import Apartment, ApartmentMatch, SearchProfile, InternetStatus


class FilterEngine:
    def __init__(self, profile: SearchProfile) -> None:
        self.profile = profile
        self.normalized_regions = {region.casefold() for region in profile.regions}

    def evaluate(self, apartment: Apartment) -> ApartmentMatch:
        reasons: list[str] = []
        score = 0
        rejected = False

        if apartment.city.casefold() not in self.normalized_regions:
            rejected = True
            reasons.append(f"Ort passt nicht: {apartment.city}")
        else:
            score += 25
            reasons.append(f"Ort passt: {apartment.city}")

        if apartment.warm_rent_eur is None:
            score -= 10
            reasons.append("Warmmiete fehlt")
        elif apartment.warm_rent_eur <= self.profile.max_warm_rent:
            score += 30
            reasons.append(f"Warmmiete passt: {apartment.warm_rent_eur:.0f} €")
        else:
            rejected = True
            reasons.append(f"Warmmiete zu hoch: {apartment.warm_rent_eur:.0f} €")

        if apartment.rooms is None:
            score -= 10
            reasons.append("Zimmerzahl fehlt")
        elif apartment.rooms >= self.profile.min_rooms:
            score += 25
            reasons.append(f"Zimmer passen: {apartment.rooms}")
        else:
            rejected = True
            reasons.append(f"Zu wenige Zimmer: {apartment.rooms}")

        if self.profile.kitchen_required:
            if apartment.has_kitchen is True:
                score += 15
                reasons.append("Einbauküche vorhanden")
            elif apartment.has_kitchen is False:
                rejected = True
                reasons.append("Keine Einbauküche")
            else:
                score -= 5
                reasons.append("Einbauküche ungeklärt")

        if apartment.address:
            score += 5
            reasons.append("Adresse vorhanden")
        else:
            reasons.append("Adresse fehlt; Internetprüfung nicht sicher möglich")

        if apartment.internet_status == InternetStatus.AVAILABLE_1000:
            score += 15
            reasons.append("Vodafone Kabel 1000 verfügbar")
        elif apartment.internet_status == InternetStatus.NOT_AVAILABLE_1000:
            score -= 10
            reasons.append("Vodafone Kabel 1000 nicht verfügbar")
        else:
            reasons.append("Vodafone Kabel 1000 ungeprüft")

        return ApartmentMatch(
            apartment=apartment,
            score=max(0, min(score, 100)),
            reasons=reasons,
            rejected=rejected,
        )
