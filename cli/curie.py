"""Shared CURIE prefix table and URI → CURIE shortener used by all projection paths."""
from __future__ import annotations

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
