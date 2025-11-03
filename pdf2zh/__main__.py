"""
Make pdf2zh package executable as a module.
Usage: python -m pdf2zh [options]
"""

from pdf2zh.pdf2zh import main
import sys

if __name__ == "__main__":
    sys.exit(main())
