"""
Recommendation engine — rule-based scoring.

Scores every scholarship against a student profile and returns
a ranked list.  Keep this file pure logic — no Django ORM queries,
no HTTP concerns.  The caller provides the data.

Scoring weights
───────────────
  Field of study  40 %   (student's M2M fields vs scholarship's single FK)
  Degree level    25 %   (profile degree_level string vs study-level name)
  Funding type    20 %   (student's M2M preferences vs scholarship's FK)
  Country         15 %   (student's preferred countries vs scholarship's country)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


# ── Tunable weights ──────────────────────────────────────────

WEIGHTS = {
    "field_of_study": 0.40,
    "degree_level": 0.25,
    "funding_type": 0.20,
    "country": 0.15,
}

MIN_MATCH_SCORE = 50.0
MAX_RECOMMENDATIONS = 20


# ── Lightweight data shapes (decoupled from ORM) ─────────────

@dataclass(frozen=True)
class StudentProfile:
    degree_level: str                     # e.g. "masters"
    field_of_study_names: frozenset[str]  # e.g. frozenset({"Computer Science", "Engineering"})
    preferred_country_names: frozenset[str]  # e.g. frozenset({"Japan", "Germany"})
    funding_pref_names: frozenset[str]    # e.g. frozenset({"Fully Funded"})


@dataclass(frozen=True)
class ScholarshipStub:
    id: int
    degree_level_name: str    # e.g. "Masters"
    field_of_study_name: str  # e.g. "Computer Science"
    funding_type_name: str    # e.g. "Fully Funded"
    country_name: str         # e.g. "Japan"


@dataclass
class ScoredScholarship:
    scholarship_id: int
    total: float
    breakdown: dict[str, float]


# ── Normalisation helpers ─────────────────────────────────────

_DEGREE_ALIASES: dict[str, str] = {
    "undergraduate": "bachelors",
    "bachelors": "bachelors",
    "bachelor": "bachelors",
    "masters": "masters",
    "master": "masters",
    "phd": "phd",
    "doctorate": "phd",
    "doctoral": "phd",
    "diploma": "diploma",
}


def _norm_degree(value: str) -> str:
    return _DEGREE_ALIASES.get(value.strip().lower(), value.strip().lower())


def _norm(value: str) -> str:
    return value.strip().lower()


# ── Scoring functions (each returns 0.0 – 1.0) ──────────────

def _score_field(student: StudentProfile, scholarship: ScholarshipStub) -> float:
    """40 % weight — exact match on the scholarship's single field."""
    if not student.field_of_study_names:
        return 0.0
    return 1.0 if _norm(scholarship.field_of_study_name) in {_norm(f) for f in student.field_of_study_names} else 0.0


def _score_degree(student: StudentProfile, scholarship: ScholarshipStub) -> float:
    """25 % weight — degree-level name match."""
    return 1.0 if _norm_degree(student.degree_level) == _norm_degree(scholarship.degree_level_name) else 0.0


def _score_funding(student: StudentProfile, scholarship: ScholarshipStub) -> float:
    """20 % weight — scholarship funding type in student's preferences."""
    if not student.funding_pref_names:
        return 0.0
    return 1.0 if _norm(scholarship.funding_type_name) in {_norm(f) for f in student.funding_pref_names} else 0.0


def _score_country(student: StudentProfile, scholarship: ScholarshipStub) -> float:
    """15 % weight — scholarship country in student's preferred countries."""
    if not student.preferred_country_names:
        return 0.0
    return 1.0 if _norm(scholarship.country_name) in {_norm(c) for c in student.preferred_country_names} else 0.0


# ── Public API ───────────────────────────────────────────────

def score_scholarship(student: StudentProfile, scholarship: ScholarshipStub) -> ScoredScholarship:
    """Return weighted score (0 – 100) for one scholarship."""
    breakdown = {
        "field_of_study": _score_field(student, scholarship) * WEIGHTS["field_of_study"],
        "degree_level":   _score_degree(student, scholarship) * WEIGHTS["degree_level"],
        "funding_type":   _score_funding(student, scholarship) * WEIGHTS["funding_type"],
        "country":        _score_country(student, scholarship) * WEIGHTS["country"],
    }
    total = sum(breakdown.values()) * 100  # scale to 0 – 100
    return ScoredScholarship(
        scholarship_id=scholarship.id,
        total=round(total, 2),
        breakdown=breakdown,
    )


def rank_scholarships(
    student: StudentProfile,
    scholarships: Iterable[ScholarshipStub],
) -> list[ScoredScholarship]:
    """Return up to 20 scholarships with a match score above 50%."""
    scored = [score_scholarship(student, s) for s in scholarships]
    scored.sort(key=lambda s: s.total, reverse=True)
    return [
        scholarship
        for scholarship in scored
        if scholarship.total > MIN_MATCH_SCORE
    ][:MAX_RECOMMENDATIONS]
