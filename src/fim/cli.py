"""Command Line Interface for File Integrity Monitor."""

import argparse
import sys
from pathlib import Path
from typing import List

from .baseline import build_baseline, save_baseline, load_baseline
from .storage import load_events, save_events
from .watcher import watch_directory
from .reporter import render_report
from .hasher import file_sha256
from .models import Event


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize baseline for directory."""
    root_path = Path(args.path).resolve()
    baseline_path = Path(args.baseline)
    
    if not root_path.exists():
        print(f"Error: Directory {root_path} does not exist")
        sys.exit(1)
    
    if not root_path.is_dir():
        print(f"Error: {root_path} is not a directory")
        sys.exit(1)
    
    print(f"Scanning {root_path}...")
    baseline = build_baseline(root_path)
    
    print(f"Found {len(baseline)} files")
    save_baseline(baseline, baseline_path)
    
    print(f"Baseline saved to {baseline_path}")


def cmd_watch(args: argparse.Namespace) -> None:
    """Watch directory for changes."""
    root_path = Path(args.path).resolve()
    baseline_path = Path(args.baseline)
    events_path = Path(args.events)
    
    if not root_path.exists():
        print(f"Error: Directory {root_path} does not exist")
        sys.exit(1)
    
    if not baseline_path.exists():
        print(f"Error: Baseline file {baseline_path} does not exist")
        sys.exit(1)
    
    try:
        baseline = load_baseline(baseline_path)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        sys.exit(1)
    
    # Load existing events if they exist
    existing_events = load_events(events_path)
    
    # Watch for changes
    updated_baseline, new_events = watch_directory(root_path, baseline)
    
    # Combine with existing events
    all_events = existing_events + new_events
    
    # Save updated baseline and events
    save_baseline(updated_baseline, baseline_path)
    save_events(all_events, events_path)
    
    print(f"Detected {len(new_events)} new events")
    print(f"Updated baseline saved to {baseline_path}")
    print(f"Events saved to {events_path}")
    
    # Generate report
    report_path = events_path.parent / "report.html"
    render_report(all_events, report_path)


def cmd_report(args: argparse.Namespace) -> None:
    """Generate HTML report from events."""
    events_path = Path(args.events)
    output_path = Path(args.out)
    
    if not events_path.exists():
        print(f"Error: Events file {events_path} does not exist")
        sys.exit(1)
    
    try:
        events = load_events(events_path)
    except Exception as e:
        print(f"Error loading events: {e}")
        sys.exit(1)
    
    render_report(events, output_path)


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify current files against baseline."""
    root_path = Path(args.path).resolve()
    baseline_path = Path(args.baseline)
    
    if not root_path.exists():
        print(f"Error: Directory {root_path} does not exist")
        sys.exit(1)
    
    if not baseline_path.exists():
        print(f"Error: Baseline file {baseline_path} does not exist")
        sys.exit(1)
    
    try:
        baseline = load_baseline(baseline_path)
    except Exception as e:
        print(f"Error loading baseline: {e}")
        sys.exit(1)
    
    print(f"Verifying {len(baseline)} files...")
    
    mismatches = []
    missing_files = []
    extra_files = []
    
    # Check files in baseline
    for rel_path, expected_hash in baseline.items():
        file_path = root_path / rel_path
        
        if not file_path.exists():
            missing_files.append(rel_path)
        else:
            actual_hash = file_sha256(file_path)
            if actual_hash != expected_hash:
                mismatches.append((rel_path, expected_hash, actual_hash))
    
    # Check for extra files
    current_baseline = build_baseline(root_path)
    for rel_path in current_baseline:
        if rel_path not in baseline:
            extra_files.append(rel_path)
    
    # Report results
    if mismatches:
        print(f"\nMODIFIED FILES ({len(mismatches)}):")
        for path, expected, actual in mismatches:
            print(f"  {path}")
            print(f"    Expected: {expected}")
            print(f"    Actual:   {actual}")
    
    if missing_files:
        print(f"\nMISSING FILES ({len(missing_files)}):")
        for path in missing_files:
            print(f"  {path}")
    
    if extra_files:
        print(f"\nEXTRA FILES ({len(extra_files)}):")
        for path in extra_files:
            print(f"  {path}")
    
    total_issues = len(mismatches) + len(missing_files) + len(extra_files)
    
    if total_issues == 0:
        print("\nAll files match baseline ✓")
        sys.exit(0)
    else:
        print(f"\nFound {total_issues} integrity issues")
        sys.exit(2)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="File Integrity Monitor - Monitor file integrity in directories"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Create baseline for directory')
    init_parser.add_argument('--path', required=True, help='Directory to scan')
    init_parser.add_argument('--baseline', required=True, help='Baseline file path')
    
    # Watch command
    watch_parser = subparsers.add_parser('watch', help='Watch directory for changes')
    watch_parser.add_argument('--path', required=True, help='Directory to watch')
    watch_parser.add_argument('--baseline', required=True, help='Baseline file path')
    watch_parser.add_argument('--events', required=True, help='Events file path')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate HTML report')
    report_parser.add_argument('--events', required=True, help='Events file path')
    report_parser.add_argument('--out', required=True, help='Output HTML file path')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify files against baseline')
    verify_parser.add_argument('--path', required=True, help='Directory to verify')
    verify_parser.add_argument('--baseline', required=True, help='Baseline file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'watch':
        cmd_watch(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'verify':
        cmd_verify(args)


if __name__ == '__main__':
    main()
