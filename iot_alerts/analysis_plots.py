"""Optional scientific plots; the statistical analysis itself uses the stdlib."""
import itertools
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy


def render(comparisons, plan, directory):
    directory = Path(directory)
    directory.mkdir()
    definitions = (
        ('routine_wait', 'Routine p95 wait', 'Difference (ms)', 1, 0),
        ('urgent_failure', 'Urgent deadline failure', 'Difference (percentage points)', 100,
         plan['urgent_failure_budget']*100),
        ('routine_drop', 'Routine drop fraction', 'Difference (percentage points)', 100, 0),
        ('routine_failure', 'Routine deadline failure', 'Difference (percentage points)', 100, 0))
    for traffic, service, capacity in itertools.product(plan['traffic'], plan['service_distributions'], plan['capacities']):
        group = [r for r in comparisons if r['traffic'] == traffic and r['service_distribution'] == service
                 and r['queue_capacity'] == capacity]
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout='constrained')
        for ax, (comparison, title, xlabel, scale, threshold) in zip(axes.flat, definitions):
            rows = sorted((r for r in group if r['comparison'] == comparison), key=lambda r: r['rate'])
            ax.axvline(0, color='#64748b', linestyle=':', linewidth=1)
            if threshold != 0:
                ax.axvline(threshold, color='#b45309', linestyle='--', linewidth=1, label='Urgent budget')
            for index, row in enumerate(rows):
                if row['interval_status'] == 'available':
                    ax.plot([row['ci_low']*scale, row['ci_high']*scale], [index, index], color='#2563eb', linewidth=2)
                    ax.plot(row['mean_difference']*scale, index, 'o', color='#1e40af', markersize=5)
                else:
                    ax.text(.03, index, 'Undefined interval', transform=ax.get_yaxis_transform(), color='#b91c1c')
            ax.set_yticks(range(len(rows)), [f'{r["rate"]:g}/s ({r["scenario_id"]})' for r in rows])
            ax.set_ylim(len(rows)-.5, -.5)
            ax.set_xlabel(xlabel)
            ax.set_ylabel('Base arrival rate')
            reference = 'strict priority' if comparison == 'urgent_failure' else 'matched fixed guarded'
            ax.set_title(f'{title}\nCandidate minus {reference}', fontsize=11)
            ax.grid(axis='x', alpha=.15)
            if threshold:
                ax.legend(fontsize=8, loc='best')
        evidence = 'ENGINEERING SMOKE — NOT PAPER EVIDENCE' if plan['profile'] == 'smoke' else 'EXPLORATORY — NO MULTIPLICITY ADJUSTMENT'
        fig.suptitle(f'{evidence}\n{traffic} | {service} service | waiting capacity {capacity}\n'
                     'Mean paired seed difference; marginal 95% bootstrap intervals', fontsize=11)
        stem = directory/f'{traffic}-{service}-capacity{capacity}'
        for extension in ('png', 'svg', 'pdf'):
            fig.savefig(stem.with_suffix('.'+extension), dpi=180)
        plt.close(fig)
    return dict(matplotlib=matplotlib.__version__, numpy=numpy.__version__, backend=matplotlib.get_backend())
