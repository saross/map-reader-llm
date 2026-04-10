#!/usr/bin/env python3
"""
55-Map Cleanup Analysis
========================

Characterises the results of scripts/55maps-cleanup-stragglers.sh by
diffing before/after snapshots per pass, and cross-referencing with
per-pass logs to determine:

1. Which pass (A/B/C) recovered each straggler tile
2. How many passes were needed per tile
3. Which tiles required safe-mode (Pass C) to recover
4. Which tiles remain persistently failed after all 3 passes
5. Final coverage per run

Usage:
    python3 scripts/55maps-cleanup-analysis.py
    python3 scripts/55maps-cleanup-analysis.py --output results/55maps-cleanup-report.json
"""
import json
import argparse
from pathlib import Path
from collections import Counter

DEFAULT_RECORDS = Path('outputs/55maps-generalisation/cleanup-records')
DEFAULT_OUTPUT = Path('results/55maps-cleanup-report.json')
PASSES = ['A-standard', 'B-longer-backoff', 'C-safemode']


def load_snapshot(records_dir: Path, run: int, tag: str) -> set[str]:
    """Load the processed_tiles set from a snapshot file. Empty set if missing."""
    path = records_dir / f'run_{run}' / f'{tag}.json'
    if not path.exists():
        return set()
    with open(path) as f:
        data = json.load(f)
    return set(data.get('processed_tiles', []))


def analyse_run(records_dir: Path, run: int) -> dict:
    """Analyse cleanup passes for a single run."""
    # Load all snapshots
    snapshots = {}
    for tag in ['initial', 'final']:
        snapshots[tag] = load_snapshot(records_dir, run, tag)
    for pass_name in PASSES:
        snapshots[f'before-{pass_name}'] = load_snapshot(records_dir, run, f'before-{pass_name}')
        snapshots[f'after-{pass_name}'] = load_snapshot(records_dir, run, f'after-{pass_name}')

    initial = snapshots['initial']
    final = snapshots['final']

    # Per-pass recovery: tiles added during each pass
    recovered_by_pass = {}
    for pass_name in PASSES:
        before = snapshots[f'before-{pass_name}']
        after = snapshots[f'after-{pass_name}']
        recovered = after - before
        recovered_by_pass[pass_name] = sorted(recovered)

    # Straggler pool = anything missing at the start
    total_target = 8541
    initial_missing = total_target - len(initial)
    final_missing = total_target - len(final)
    total_recovered = len(final) - len(initial)

    # Still missing after all passes
    from_manifest = None
    try:
        with open('inputs/tiles_384_55maps/full_evaluation_manifest.json') as f:
            from_manifest = set(json.load(f))
    except FileNotFoundError:
        from_manifest = set()

    still_missing = sorted(from_manifest - final)

    return {
        'run': run,
        'initial_processed': len(initial),
        'initial_missing': initial_missing,
        'final_processed': len(final),
        'final_missing': final_missing,
        'total_recovered': total_recovered,
        'recovery_rate': total_recovered / max(initial_missing, 1),
        'recovered_by_pass': {k: len(v) for k, v in recovered_by_pass.items()},
        'recovered_tiles_by_pass': recovered_by_pass,
        'still_missing_tiles': still_missing,
        'safe_mode_required_count': len(recovered_by_pass.get('C-safemode', [])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyse 55-map cleanup results')
    parser.add_argument('--records-dir', type=Path, default=DEFAULT_RECORDS)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.records_dir.exists():
        print(f'Records directory not found: {args.records_dir}')
        print('Run scripts/55maps-cleanup-stragglers.sh first.')
        return

    per_run = []
    for run in range(1, 6):
        per_run.append(analyse_run(args.records_dir, run))

    # Cross-run analysis: per-tile recovery
    tile_recovery_pass: dict[str, dict[int, str]] = {}  # tile -> {run: pass}
    for run_data in per_run:
        run = run_data['run']
        for pass_name, tiles in run_data['recovered_tiles_by_pass'].items():
            for tile in tiles:
                tile_recovery_pass.setdefault(tile, {})[run] = pass_name

    # Tile-level statistics: how many tiles needed safe-mode in AT LEAST one run
    tiles_needing_safemode = set()
    for tile, by_run in tile_recovery_pass.items():
        if any('C-safemode' in p for p in by_run.values()):
            tiles_needing_safemode.add(tile)

    # Consensus coverage after cleanup
    tile_success_count = Counter()
    for run_data in per_run:
        run = run_data['run']
        snap_path = args.records_dir / f'run_{run}' / 'final.json'
        if snap_path.exists():
            with open(snap_path) as f:
                data = json.load(f)
            for tile in data.get('processed_tiles', []):
                tile_success_count[tile] += 1

    dist = Counter()
    for n in tile_success_count.values():
        dist[n] += 1
    # Add tiles with 0 successes
    from_manifest = set(json.load(open('inputs/tiles_384_55maps/full_evaluation_manifest.json')))
    zero = len(from_manifest - set(tile_success_count.keys()))
    dist[0] = zero

    safe_for_4of5 = dist.get(4, 0) + dist.get(5, 0)
    at_risk_4of5 = sum(dist[n] for n in range(0, 4))

    report = {
        'per_run': [{k: v for k, v in r.items() if k != 'recovered_tiles_by_pass'} for r in per_run],
        'cross_run': {
            'tiles_needing_safemode_somewhere': len(tiles_needing_safemode),
            'tile_success_distribution': dict(sorted(dist.items())),
            'safe_for_4of5_consensus': safe_for_4of5,
            'at_risk_4of5_consensus': at_risk_4of5,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)

    # Pretty-print summary
    print('=' * 72)
    print('55-Map Cleanup Analysis')
    print('=' * 72)
    print()
    print('Per-run recovery:')
    print(f"{'Run':>3} | {'Initial':>7} | {'Final':>7} | {'Recovered':>9} | "
          f"{'Rate':>5} | {'A':>4} {'B':>4} {'C':>4} | {'Still missing':>13}")
    print('-' * 72)
    for r in per_run:
        pa = r['recovered_by_pass'].get('A-standard', 0)
        pb = r['recovered_by_pass'].get('B-longer-backoff', 0)
        pc = r['recovered_by_pass'].get('C-safemode', 0)
        print(f"{r['run']:>3} | "
              f"{r['initial_processed']:>7} | "
              f"{r['final_processed']:>7} | "
              f"{r['total_recovered']:>9} | "
              f"{r['recovery_rate']*100:>4.1f}% | "
              f"{pa:>4} {pb:>4} {pc:>4} | "
              f"{r['final_missing']:>13}")
    print()
    print(f"Safe-mode required somewhere: {len(tiles_needing_safemode)} unique tiles")
    print()
    print('Consensus coverage after cleanup:')
    for n in sorted(dist.keys()):
        mark = ''
        if n < 4:
            mark = ' ⚠ below 4-of-5 threshold'
        elif n == 4:
            mark = ' ← at threshold'
        elif n == 5:
            mark = ' ← full'
        print(f"  {n} successes: {dist[n]:>5} tiles{mark}")
    print()
    print(f"Safe for 4-of-5: {safe_for_4of5} / 8541 ({safe_for_4of5/8541*100:.1f}%)")
    print(f"At risk for 4-of-5: {at_risk_4of5}")
    print()
    print(f"Full report written: {args.output}")


if __name__ == '__main__':
    main()
