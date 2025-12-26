#!/usr/bin/env python3
"""
Simple script to run linting tools on the codebase.
Usage: python lint.py [--fix]
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {description}: {e}")
        return False


def main():
    """Main linting function."""
    fix_mode = "--fix" in sys.argv or "-f" in sys.argv
    
    # Check if ruff is installed
    try:
        subprocess.run(["ruff", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: ruff is not installed. Please run: pip install ruff")
        return 1
    
    # Run ruff check
    ruff_cmd = "ruff check game/"
    if fix_mode:
        ruff_cmd += " --fix"
    
    ruff_success = run_command(ruff_cmd, "Ruff (linting)")
    
    # Run ruff format check
    format_cmd = "ruff format game/ --check"
    if fix_mode:
        format_cmd = "ruff format game/"
    
    format_success = run_command(format_cmd, "Ruff (formatting)")
    
    # Optional: Run mypy (if installed)
    try:
        subprocess.run(["mypy", "--version"], check=True, capture_output=True)
        mypy_cmd = "mypy game/ --ignore-missing-imports"
        mypy_success = run_command(mypy_cmd, "MyPy (type checking)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\nMyPy not installed. Skipping type checking.")
        print("Install with: pip install mypy")
        mypy_success = True
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Ruff (linting): {'✓ PASSED' if ruff_success else '✗ FAILED'}")
    print(f"Ruff (formatting): {'✓ PASSED' if format_success else '✗ FAILED'}")
    if mypy_success is not None:
        print(f"MyPy (type checking): {'✓ PASSED' if mypy_success else '✗ FAILED'}")
    
    if not (ruff_success and format_success and (mypy_success is None or mypy_success)):
        print("\nSome checks failed. Use --fix flag to auto-fix issues where possible.")
        return 1
    
    print("\nAll checks passed! ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())

