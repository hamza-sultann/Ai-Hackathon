"""Deterministic cosmetic labels for assets the CSVs only identify by code."""
from __future__ import annotations

import hashlib

_AREAS = [
    "Faisalabad West Division", "Lahore Central", "Lahore East", "Lahore South",
    "Multan Cantt Division", "Gujranwala City", "Rawalpindi Urban", "Sialkot Division",
    "Sargodha Region", "Bahawalpur Division", "Sheikhupura Rural", "Kasur District",
]
_SUBSTATIONS = [
    "GS-132KV Nishatabad", "GS-132KV Egerton Road", "GS-132KV Gulberg", "GS-132KV Samanabad",
    "GS-132KV New Multan", "GS-132KV Model Town", "GS-66KV Township", "GS-132KV Shalimar",
]
_LOCALITIES = [
    "Sector C-2, Industrial Estate", "Block B, Township", "Main Boulevard Commercial",
    "Green Town Residential", "Mughalpura Line", "Peoples Colony", "Satellite Town",
    "Ghala Mandi Bazaar", "Cantt Housing Scheme", "Riverside Colony", "Old City Quarter",
]
_TARIFF = {
    "residential": "A-1 Residential",
    "commercial": "A-2 Commercial",
    "industrial": "B-2 Industrial",
}
_STD_KVA = [100, 200, 315, 400, 630, 1000]


def _pick(pool: list[str], key: str) -> str:
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return pool[h % len(pool)]


def feeder_name(feeder_id: str) -> str:
    return f"{_pick(_LOCALITIES, feeder_id)} Feeder {feeder_id.split('-')[-1]}"


def service_area(feeder_id: str) -> str:
    return _pick(_AREAS, feeder_id)


def substation(feeder_id: str) -> str:
    return _pick(_SUBSTATIONS, feeder_id)


def pmt_location(pmt_id: str) -> str:
    return f"{_pick(_LOCALITIES, pmt_id)} ({pmt_id})"


def tariff_category(consumer_type: str) -> str:
    return _TARIFF.get(str(consumer_type).lower(), "A-1 Residential")


def meter_id(consumer_id: str) -> str:
    suffix = consumer_id.split("-")[-1] if "-" in consumer_id else consumer_id
    return f"MTR-{suffix}"


def consumer_address(consumer_id: str, pmt_id: str, feeder_id: str) -> str:
    n = (int(hashlib.md5(consumer_id.encode()).hexdigest(), 16) % 400) + 1
    return f"House/Plot {n}, {_pick(_LOCALITIES, pmt_id)}, {_pick(_AREAS, feeder_id)}"


def capacity_kva(total_sanctioned_load_kw: float) -> float:
    # crude: transformer sized ~1.4x aggregate sanctioned load, snapped to a standard rating
    target = max(total_sanctioned_load_kw * 1.4, 50)
    for kva in _STD_KVA:
        if kva >= target:
            return float(kva)
    return float(_STD_KVA[-1])
