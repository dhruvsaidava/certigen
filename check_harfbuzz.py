#!/usr/bin/env python3
"""Check if HarfBuzz is installed"""
try:
    import harfbuzz
    import freetype
    print("✓ HarfBuzz is installed and available")
    print("  Gujarati text rendering will use advanced text shaping")
except ImportError as e:
    print("✗ HarfBuzz is not installed")
    print("\nTo install, run:")
    print("  pip install harfbuzz freetype-py")
    print("\nWithout HarfBuzz, Gujarati ligatures may render incorrectly.")

