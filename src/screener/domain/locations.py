"""Deterministic service-area matching.

Rules first, LLM second: a known alias is matched by code (fast, testable, explainable);
only text the rules cannot place is left to the model's world knowledge, and the model's
answer is accepted only if it names a configured city.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Literal

from pydantic import BaseModel, Field

from screener.config import ServiceArea
from screener.domain.text import contains_phrase, normalize


class LocationMatch(BaseModel):
    status: Literal["resolved", "ambiguous", "no_match"]
    city_id: str | None = None
    zone: str | None = None
    options: list[str] = Field(default_factory=list)  # for clarifying questions
    option_city_ids: list[str] = Field(default_factory=list)
    source: Literal["rules", "fuzzy"] | None = None


class LocationMatcher:
    FUZZY_THRESHOLD = 0.8  # 'madriz' vs 'madrid' = 0.83; no two configured cities are this close

    def __init__(self, areas: list[ServiceArea]):
        self.areas = areas

    def match(self, text: str | None) -> LocationMatch:
        if not text or not normalize(text):
            return LocationMatch(status="no_match")
        norm = normalize(text)

        city_hits = [a for a in self.areas if any(contains_phrase(norm, al) for al in a.aliases)]
        zone_hits = self._zone_hits(norm)

        if len(city_hits) == 1:
            city = city_hits[0]
            zone = next((z for (a, z, _) in zone_hits if a.id == city.id), None)
            return LocationMatch(status="resolved", city_id=city.id, zone=zone, source="rules")
        if len(city_hits) > 1:
            return LocationMatch(
                status="ambiguous",
                options=[a.name for a in city_hits],
                option_city_ids=[a.id for a in city_hits],
            )

        cities = {a.id for (a, _, _) in zone_hits}
        if len(cities) == 1:
            area, zone, _ = zone_hits[0]
            return LocationMatch(status="resolved", city_id=area.id, zone=zone, source="rules")
        if len(cities) > 1:
            return LocationMatch(
                status="ambiguous",
                options=[f"{zone} ({area.name})" for (area, zone, _) in zone_hits],
                option_city_ids=[area.id for (area, _, _) in zone_hits],
            )

        fuzzy = self._fuzzy_city(norm)
        if fuzzy:
            return LocationMatch(status="resolved", city_id=fuzzy.id, source="fuzzy")
        return LocationMatch(status="no_match")

    def zone_in_city(self, city_id: str, text: str | None) -> str | None:
        """Canonical zone name if `text` names a zone of that city."""
        if not text:
            return None
        norm = normalize(text)
        for area, zone, _ in self._zone_hits(norm):
            if area.id == city_id:
                return zone
        return None

    def _zone_hits(self, norm: str) -> list[tuple[ServiceArea, str, str]]:
        hits = [
            (area, zone.name, alias)
            for area in self.areas
            for zone in area.zones
            for alias in zone.aliases
            if contains_phrase(norm, alias)
        ]
        # Keep the most specific matches: "centro histórico" (CDMX) beats "centro" (4 cities).
        hits.sort(key=lambda h: len(h[2]), reverse=True)
        kept: list[tuple[ServiceArea, str, str]] = []
        for hit in hits:
            if any(normalize(hit[2]) in normalize(k[2]) and hit[2] != k[2] for k in kept):
                continue
            if any(k[0].id == hit[0].id and k[1] == hit[1] for k in kept):
                continue
            kept.append(hit)
        return kept

    def _fuzzy_city(self, norm: str) -> ServiceArea | None:
        """Typos like 'Madriz' or 'Barcelna'. Only for aliases long enough to be safe."""
        tokens = norm.split()
        grams = tokens + [" ".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]
        best: tuple[float, ServiceArea] | None = None
        for area in self.areas:
            for alias in area.aliases:
                alias_n = normalize(alias)
                if len(alias_n) < 5:
                    continue
                for gram in grams:
                    score = SequenceMatcher(None, alias_n, gram).ratio()
                    if score >= self.FUZZY_THRESHOLD and (best is None or score > best[0]):
                        best = (score, area)
        return best[1] if best else None
