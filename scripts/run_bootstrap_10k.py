#!/usr/bin/env python3
"""
Bootstrap-CI N=10000 upgrade runner.

Reads /tmp/bootstrap-10k-jobs.csv and re-runs evaluate_detections.py for
each queued cell with --bootstrap 10000, preserving every other parameter
(buffers, ground truth, bounds, seed, label, MCC flag).

Designed for parallel execution via xargs -P or GNU parallel; also supports
single-cell invocation.

Usage:
    # Run a single cell by index (0-based):
    python3 /tmp/run_bootstrap_10k.py --index 17

    # List queued cells:
    python3 /tmp/run_bootstrap_10k.py --list

    # Status counts:
    python3 /tmp/run_bootstrap_10k.py --status

Author: Claude Code (Opus 4.7) for Shawn Ross's overnight bootstrap-10K sweep.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).parent == Path('/tmp') else Path('/home/shawn/Code/map-reader-llm')
QUEUE_CSV = Path('/tmp/bootstrap-10k-jobs.csv')
LOG_DIR = Path('/tmp/bootstrap-10k-logs')
LOG_DIR.mkdir(exist_ok=True)


def load_queue() -> list[dict]:
    """Load the CSV queue of jobs to run."""
    rows = []
    with open(QUEUE_CSV) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows


def run_cell(row: dict, dry_run: bool = False) -> dict:
    """Run evaluate_detections.py with --bootstrap 10000 for a single cell.

    Args:
        row: Manifest row with detections, bounds, ground_truth, etc.
        dry_run: If True, print command but do not execute.

    Returns:
        Result dict with status, wall_time_s, exit_code, stderr_tail.
    """
    eval_path = Path(row['eval_path'])
    output_dir = Path(row['output_dir'])
    cmd = [
        str(REPO_ROOT / '.venv' / 'bin' / 'python3'),
        str(REPO_ROOT / 'scripts' / 'evaluate_detections.py'),
    ]
    if row.get('detections'):
        for d in row['detections'].split('|'):
            cmd += ['--detections', d]
    if row.get('detections_dir'):
        cmd += ['--detections-dir', row['detections_dir']]
    if row.get('glob'):
        cmd += ['--glob', row['glob']]
    if row.get('batch'):
        cmd += ['--batch', row['batch']]
    cmd += ['--ground-truth', row['ground_truth']]
    cmd += ['--bounds', row['bounds']]
    cmd += ['--buffers'] + row['buffers'].split()
    cmd += ['--bootstrap', '10000']
    cmd += ['--seed', row.get('seed') or '42']
    cmd += ['--label', row['label']]
    cmd += ['--output-dir', str(output_dir)]
    if row.get('mcc') == '1':
        cmd += ['--mcc']

    if dry_run:
        print(' '.join(cmd))
        return {'status': 'dry_run', 'wall_time_s': 0.0, 'exit_code': 0, 'cmd': ' '.join(cmd)}

    log_file = LOG_DIR / (eval_path.parent.name + '__' + str(abs(hash(str(eval_path)))) + '.log')
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=3600,  # 1 hr per cell ceiling
        )
        wall = time.time() - t0
        with open(log_file, 'w') as f:
            f.write(' '.join(cmd) + '\n\n')
            f.write(proc.stdout)
        if proc.returncode != 0:
            return {
                'status': 'error',
                'wall_time_s': wall,
                'exit_code': proc.returncode,
                'log_file': str(log_file),
                'stderr_tail': proc.stdout[-500:],
            }
        # Verify the file was written and now reports n=10000
        try:
            with open(eval_path) as f:
                d = json.load(f)
            md = d.get('_metadata') or {}
            cli = md.get('cli_args') or {}
            new_n = cli.get('bootstrap')
            if new_n != 10000:
                return {
                    'status': 'verify_failed',
                    'wall_time_s': wall,
                    'exit_code': 0,
                    'log_file': str(log_file),
                    'observed_n': new_n,
                }
        except Exception as e:
            return {
                'status': 'verify_failed',
                'wall_time_s': wall,
                'exit_code': 0,
                'log_file': str(log_file),
                'error': str(e),
            }
        return {
            'status': 'ok',
            'wall_time_s': wall,
            'exit_code': 0,
            'log_file': str(log_file),
        }
    except subprocess.TimeoutExpired as e:
        wall = time.time() - t0
        return {
            'status': 'timeout',
            'wall_time_s': wall,
            'exit_code': -1,
            'log_file': str(log_file),
        }
    except Exception as e:
        wall = time.time() - t0
        return {
            'status': 'exception',
            'wall_time_s': wall,
            'exit_code': -1,
            'error': str(e),
        }


def main() -> int:
    """CLI entry point."""
    p = argparse.ArgumentParser()
    p.add_argument('--index', type=int, help='Run cell at this 0-based index from the queue')
    p.add_argument('--list', action='store_true', help='List queued cells')
    p.add_argument('--status', action='store_true', help='Show status summary')
    p.add_argument('--dry-run', action='store_true', help='Print command, do not execute')
    args = p.parse_args()
    rows = load_queue()
    if args.list:
        for i, r in enumerate(rows):
            print(f'  {i:4d}  {r["status"]:6s}  {r["eval_path"]}')
        return 0
    if args.status:
        from collections import Counter
        c = Counter(r['status'] for r in rows)
        for k, v in c.most_common():
            print(f'  {k:8s}  {v}')
        return 0
    if args.index is None:
        print('error: --index required (or --list, --status)', file=sys.stderr)
        return 2
    if args.index < 0 or args.index >= len(rows):
        print(f'error: index {args.index} out of range [0,{len(rows)})', file=sys.stderr)
        return 2
    row = rows[args.index]
    result = run_cell(row, dry_run=args.dry_run)
    eval_short = row['eval_path'].replace('results/', '')
    print(f'[{args.index:4d}] {result["status"]:8s}  '
          f'wall={result.get("wall_time_s", 0):.1f}s  '
          f'{eval_short}')
    if result['status'] != 'ok' and result['status'] != 'dry_run':
        print(f'  log: {result.get("log_file", "n/a")}', file=sys.stderr)
        print(f'  details: {result}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
