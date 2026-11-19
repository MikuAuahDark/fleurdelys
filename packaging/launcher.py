"""Absolute-import entry point for PyInstaller."""
from fleurdelys.__main__ import main
import os
import sys

if __name__ == "__main__":
    try:
        main()
    finally:
        # pygls closes the stdio writer on LSP exit. PyInstaller flushes
        # sys.stdout afterwards, so provide a valid stream for that final flush.
        if sys.stdout.closed:
            sys.stdout = open(os.devnull, "w")
            sys.__stdout__ = sys.stdout
