"""Initial command-line interface."""

import platform
import shutil
import sys


def main() -> None:
    """Run a lightweight environment diagnostic."""
    args = sys.argv[1:]

    if not args or args[0] in ("--help", "-h"):
        print("TaskWeave — Concurrent Task Scheduling & Performance Laboratory")
        print()
        print("Commands:")
        print("  doctor   Show Python and native toolchain availability")
        print("  demo     Show project foundation status")
        return

    if args[0] == "doctor":
        print(f"TaskWeave {__import__('taskweave').__version__}")
        print(f"Python: {platform.python_version()}")
        print(f"Platform: {platform.platform()}")
        for tool in ("git", "cmake", "g++", "clang++", "cl"):
            print(f"{tool}: {shutil.which(tool) or 'not found on PATH'}")
        return

    if args[0] == "demo":
        print("TaskWeave foundation is installed.")
        print("The full scheduler is implemented incrementally in subsequent phases.")
        return

    print(f"Unknown command: {args[0]}")
    print("Run 'python -m taskweave --help' for available commands.")
    raise SystemExit(2)