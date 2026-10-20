"""Experimental aging selection; never reads actual service cost or future arrivals."""
import math
from dataclasses import dataclass

VARIANTS = ('adaptive_guarded', 'adaptive', 'fixed_guarded', 'fixed_deadline')


@dataclass(frozen=True)
class AgingConfig:
    minimum_s: float = .1
    maximum_s: float = 1.
    service_estimate_s: float = .01

    def __post_init__(self):
        from .simulator import positive
        for name, value in vars(self).items():
            positive(value, name)
        if self.minimum_s > self.maximum_s:
            raise ValueError('minimum_s must not exceed maximum_s')


def select_aging(events, clock, capacity, variant, config, fixed_interval):
    """Return (event, guard_activated). Caller supplies pending events only."""
    if not events:
        return None, False
    occupancy = min(1., max(0, len(events)-1)/capacity)
    interval = (config.maximum_s - occupancy*(config.maximum_s-config.minimum_s)
                if variant.startswith('adaptive') else fixed_interval)

    def deadline_key(event):
        return (event.absolute_deadline_s if event.deadline_s is not None else math.inf,
                event.arrival, event.id)

    def key(event):
        waited = max(0., clock-event.arrival)
        effective = (0 if waited >= event.priority*interval else
                     event.priority-math.floor(waited/interval))
        return (effective, *deadline_key(event))

    base = min(events, key=key)
    urgent = [event for event in events if event.priority == 0 and event.deadline_s is not None]
    if variant.endswith('_guarded') and urgent:
        reference = min(urgent, key=deadline_key)
        if base.id != reference.id and clock + 2*config.service_estimate_s > reference.absolute_deadline_s:
            return reference, True
    return base, False
