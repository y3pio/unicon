"""Allow running unicon as a module: python -m cli"""
try:
    from cli import main
except ImportError:
    # Fallback if cli is a directory
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from cli import main

if __name__ == "__main__":
    main()

