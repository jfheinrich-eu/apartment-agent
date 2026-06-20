from __future__ import annotations

from wohnung_agent.models import Apartment, ApartmentMatch, SearchProfile, InternetStatus
from wohnung_agent.i18n import tr

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

    def __init__(self, profile: SearchProfile, language: str = "en") -> None:
        """Cache normalized regions for faster matching."""
        self.profile = profile
        self.language = language
        self.normalized_regions = {region.casefold() for region in profile.regions}

    def evaluate(self, apartment: Apartment) -> ApartmentMatch:
        """Return a scored match result for a single apartment."""
        reasons: list[str] = []
        score = 0
        rejected = False

        if apartment.city.casefold() not in self.normalized_regions:
            rejected = True
            reasons.append(tr(self.language, "filter.city_mismatch", city=apartment.city))
        else:
            score += REGION_MATCH_SCORE
            reasons.append(tr(self.language, "filter.city_match", city=apartment.city))

        if apartment.warm_rent_eur is None:
            score -= RENT_MISSING_PENALTY
            reasons.append(tr(self.language, "filter.rent_missing"))
        elif apartment.warm_rent_eur <= self.profile.max_warm_rent:
            score += RENT_MATCH_SCORE
            reasons.append(tr(self.language, "filter.rent_match", rent=apartment.warm_rent_eur))
        else:
            rejected = True
            reasons.append(tr(self.language, "filter.rent_too_high", rent=apartment.warm_rent_eur))

        if apartment.rooms is None:
            score -= ROOMS_MISSING_PENALTY
            reasons.append(tr(self.language, "filter.rooms_missing"))
        elif apartment.rooms >= self.profile.min_rooms:
            score += ROOM_MATCH_SCORE
            reasons.append(tr(self.language, "filter.rooms_match", rooms=apartment.rooms))
        else:
            rejected = True
            reasons.append(tr(self.language, "filter.rooms_too_few", rooms=apartment.rooms))

        if self.profile.kitchen_required:
            if apartment.has_kitchen is True:
                score += KITCHEN_MATCH_SCORE
                reasons.append(tr(self.language, "filter.kitchen_yes"))
            elif apartment.has_kitchen is False:
                rejected = True
                reasons.append(tr(self.language, "filter.kitchen_no"))
            else:
                score -= KITCHEN_UNKNOWN_PENALTY
                reasons.append(tr(self.language, "filter.kitchen_unknown"))

        if apartment.address:
            score += ADDRESS_MATCH_SCORE
            reasons.append(tr(self.language, "filter.address_available"))
        else:
            reasons.append(tr(self.language, "filter.address_missing"))

        if apartment.internet_status == InternetStatus.AVAILABLE_1000:
            score += INTERNET_AVAILABLE_SCORE
            reasons.append(tr(self.language, "filter.internet_yes"))
        elif apartment.internet_status == InternetStatus.NOT_AVAILABLE_1000:
            score -= INTERNET_NOT_AVAILABLE_PENALTY
            reasons.append(tr(self.language, "filter.internet_no"))
        else:
            reasons.append(tr(self.language, "filter.internet_unknown"))

        return ApartmentMatch(
            apartment=apartment,
            score=max(0, min(score, 100)),
            reasons=reasons,
            rejected=rejected,
        )
