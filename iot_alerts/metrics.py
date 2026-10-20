"""Loss-aware summaries for fully drained simulation runs.

Latency/waiting distributions describe completions only. Deadline failure also
includes drops with a configured deadline, using all deadline-bearing arrivals.
"""
import math
import statistics


def fraction(numerator, denominator):
    return None if denominator == 0 else numerator / denominator


def deadline_status(event, finish_s=None):
    if event.absolute_deadline_s is None:
        return 'not_set'
    if finish_s is None:
        return 'dropped'
    return 'met' if finish_s <= event.absolute_deadline_s else 'missed'


def _distribution(values, prefix):
    ordered = sorted(values)
    def percentile(p):
        return ordered[math.ceil(len(ordered)*p)-1] if ordered else None
    return {
        f'{prefix}_samples': len(ordered),
        f'mean_{prefix}_ms': statistics.fmean(ordered)*1000 if ordered else None,
        f'p95_{prefix}_ms': percentile(.95)*1000 if ordered else None,
        f'p99_{prefix}_ms': percentile(.99)*1000 if ordered else None,
        f'max_{prefix}_ms': ordered[-1]*1000 if ordered else None,
    }


def summarize(result):
    """Return overall plus high/medium/low rows with explicit denominators.

    None means undefined, never zero. All groups share one observation window:
    first generated arrival to last completion/rejection, including idle and drain.
    """
    events = [c.event for c in result.completions] + [r.event for r in result.rejections]
    if len(events) != result.generated or len({e.id for e in events}) != len(events):
        raise ValueError('Result must account for every generated event exactly once')
    start = min((e.arrival for e in events), default=None)
    end = max([c.finish_s for c in result.completions] +
              [r.rejected_at_s for r in result.rejections], default=None)
    duration = None if start is None else end-start
    rows = []
    for priority in (None, 0, 1, 2):
        completions = [c for c in result.completions if priority is None or c.event.priority == priority]
        rejections = [r for r in result.rejections if priority is None or r.event.priority == priority]
        deadline_completions = [c for c in completions if c.event.deadline_s is not None]
        deadline_drops = sum(r.event.deadline_s is not None for r in rejections)
        misses = sum(deadline_status(c.event, c.finish_s) == 'missed' for c in deadline_completions)
        completed, dropped = len(completions), len(rejections)
        generated = completed+dropped
        deadline_generated = len(deadline_completions)+deadline_drops
        row = dict(policy=result.policy, priority='all' if priority is None else priority,
            generated=generated, admitted=completed, completed=completed, dropped=dropped,
            unfinished=0, drop_fraction=fraction(dropped, generated),
            deadline_generated=deadline_generated, deadline_admitted=len(deadline_completions),
            deadline_completed=len(deadline_completions), deadline_dropped=deadline_drops,
            without_deadline=generated-deadline_generated,
            deadline_met=len(deadline_completions)-misses, deadline_missed_completed=misses,
            deadline_failed=misses+deadline_drops,
            admitted_deadline_miss_fraction=fraction(misses, len(deadline_completions)),
            deadline_failure_fraction=fraction(misses+deadline_drops, deadline_generated),
            observation_start_s=start, observation_end_s=end, observation_duration_s=duration,
            throughput_per_s=None if duration is None or duration <= 0 else completed/duration)
        row.update(_distribution([c.latency_s for c in completions], 'latency'))
        row.update(_distribution([c.wait_s for c in completions], 'wait'))
        rows.append(row)
    return rows
