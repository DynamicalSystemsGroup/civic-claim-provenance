"""Shared CURIE prefix table, URI → CURIE shortener, and graph/branch constants."""
from __future__ import annotations

# Named graph IRIs → Flexo branch names (last IRI segment, per ADCS convention).
# One branch per named graph; branch identity replaces the GRAPH clause.
GRAPH_IRI_PREFIX = "urn:nyccompost:graph:"
GRAPH_BRANCHES = ["judgments", "evidence", "provenance", "attestation"]

PREFIXES = {
    "urn:nyccompost:claim:": "cl:",
    "urn:nyccompost:evidence:": "ev:",
    "urn:nyccompost:assumption:": "am:",
    "urn:nyccompost:judgment:": "jd:",
    "urn:nyccompost:attestation:": "at:",
}


def _curie(uri):
    s = str(uri)
    for full, short in PREFIXES.items():
        if s.startswith(full):
            return short + s[len(full):]
    return s
