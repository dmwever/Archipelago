from dataclasses import dataclass
from random import Random
from typing import Dict, List, Union

from .Options import NumberOfChecks, NumberOfLocks, SpeedRequirement


@dataclass(frozen=True)
class Trip:
    distance_tier: int
    speed_tier: int
    key_needed: int

    def get_name(self) -> str:
        name = f"Trip Distance {self.distance_tier}"
        if self.key_needed > 0:
            name += f" (Area {self.key_needed})"
        if self.speed_tier > 0:
            name += f" (Speed {self.speed_tier})"
        return name

    def get_name_unique(self, unique_identifier: int) -> str:
        return f"{self.get_name()} #{unique_identifier}"

    def as_dict_with_amount(self, amount: int) -> Dict[str, int]:
        dict_without_amount = self.as_dict()
        dict_without_amount["amount"] = amount
        return dict_without_amount

    def as_dict(self) -> Dict[str, int]:
        return {
            "distance_tier": self.distance_tier,
            "key_needed": self.key_needed,
            "speed_tier": self.speed_tier,
        }


all_trips = []

max_per_category = 10
for distance in range(1, max_per_category + 1):
    for speed in range(0, max_per_category + 1):
        for key in range(0, max_per_category + 1):
            all_trips.append(Trip(distance, speed, key))


def generate_trips(options: Dict[str, int], random: Random) -> Dict[Trip, int]:
    valid_trips = []
    enable_speed = options[SpeedRequirement.internal_name] > 0
    number_of_keys = options[NumberOfLocks.internal_name]
    for trip in all_trips:
        has_speed = trip.speed_tier > 0
        if enable_speed != has_speed:
            continue
        if trip.key_needed > number_of_keys:
            continue
        valid_trips.append(trip)
    chosen_trips = random.choices(valid_trips, k=options[NumberOfChecks.internal_name])

    make_sure_all_key_tiers_have_one_trip(chosen_trips, number_of_keys)

    trip_counts = dict()
    for trip in chosen_trips:
        if trip not in trip_counts:
            trip_counts[trip] = 0
        trip_counts[trip] += 1
    return trip_counts


def make_sure_all_key_tiers_have_one_trip(chosen_trips: List[Trip], number_of_keys: int) -> None:
    if number_of_keys <= 0:
        return
    for missing_key_tier in range(0, number_of_keys + 1):
        if find_trip_with_key_tier(chosen_trips, missing_key_tier):
            continue
        for higher_key_tier in range(number_of_keys, missing_key_tier - 1, -1):
            if missing_key_tier == higher_key_tier:
                return
            trip_to_downgrade = find_trip_with_key_tier(chosen_trips, higher_key_tier)
            if trip_to_downgrade is None:
                continue
            chosen_trips.remove(trip_to_downgrade)
            chosen_trips.append(Trip(trip_to_downgrade.distance_tier, trip_to_downgrade.speed_tier, missing_key_tier))
            break


def find_trip_with_key_tier(trips: List[Trip], tier: int) -> Union[Trip, None]:
    for trip in trips:
        if trip.key_needed == tier:
            return trip

    return None
