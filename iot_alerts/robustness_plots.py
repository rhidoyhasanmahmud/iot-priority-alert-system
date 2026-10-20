"""Facet robustness effects using precise numeric scientific plots."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy
from .analysis import COMPARISONS
from .study import scenarios


def render(intervals, plan, kind, output):
    output = Path(output)
    output.mkdir()
    scenario_map = {s['id']: s for s in scenarios(plan)}
    effects = sorted({r['effect'] for r in intervals})
    for effect in effects:
        for traffic in plan['traffic']:
            for service in plan['service_distributions']:
                for capacity in plan['capacities']:
                    group = [r for r in intervals if r['effect'] == effect and
                        (scenario_map[r['scenario_id']]['traffic'], scenario_map[r['scenario_id']]['service_distribution'],
                         scenario_map[r['scenario_id']]['queue_capacity']) == (traffic, service, capacity)]
                    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained')
                    for ax, metric in zip(axes.flat, COMPARISONS):
                        rows = sorted([r for r in group if r['metric_id'] == metric['id']],
                                      key=lambda r: scenario_map[r['scenario_id']]['rate'])
                        scale = 100 if metric['unit'] == 'fraction' else 1
                        ax.axvline(0, color='#64748b', linestyle=':')
                        for index, row in enumerate(rows):
                            if row['interval_status'] == 'available':
                                ax.plot([row['ci_low']*scale, row['ci_high']*scale], [index, index], color='#2563eb', linewidth=2)
                                ax.plot(row['mean_difference']*scale, index, 'o', color='#1e40af')
                            else:
                                ax.text(.03, index, 'Undefined interval', transform=ax.get_yaxis_transform())
                        ax.set_yticks(range(len(rows)), [f'{scenario_map[r["scenario_id"]]["rate"]:g}/s ({r["scenario_id"]})' for r in rows])
                        ax.set_ylim(len(rows)-.5, -.5)
                        titles = dict(routine_wait='Routine p95 waiting', urgent_failure='Urgent deadline failure',
                                      routine_drop='Routine drop fraction', routine_failure='Routine deadline failure')
                        ax.set_title(titles[metric['id']])
                        ax.set_xlabel('Difference (percentage points)' if scale == 100 else 'Difference (ms)')
                        ax.grid(axis='x', alpha=.15)
                    label = 'ENGINEERING SMOKE — NOT PAPER EVIDENCE' if plan['profile'] == 'smoke' else 'SECONDARY EXPLORATORY — UNADJUSTED'
                    fig.suptitle(f'{label}\n{kind}: {effect} | {traffic}, {service}, capacity {capacity}\nMean paired effect; marginal 95% bootstrap intervals', fontsize=11)
                    for extension in ('png', 'svg', 'pdf'):
                        fig.savefig(output/f'{effect}-{traffic}-{service}-{capacity}.{extension}', dpi=180)
                    plt.close(fig)
    return dict(matplotlib=matplotlib.__version__, numpy=numpy.__version__)
