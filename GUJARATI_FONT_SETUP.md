# Gujarati Font Setup Guide

## Problem
PIL/Pillow has limitations with complex Gujarati ligatures. For example, "મહેન્દ્રભાઈ" might render incorrectly as "મહેન્રભાઈ".

## Solution: HarfBuzz Text Shaping

We've implemented HarfBuzz support for proper Gujarati text rendering with correct ligature handling.

### Installation

1. **Install Required Dependencies:**
   ```bash
   pip install harfbuzz freetype-py
   ```

2. **Verify Installation:**
   ```bash
   python test_harfbuzz.py
   ```

### How It Works

- **Without HarfBuzz**: Uses PIL's basic text rendering (may have ligature issues)
- **With HarfBuzz**: Uses advanced text shaping engine for correct Gujarati ligature rendering

The script automatically detects if HarfBuzz is available and uses it for Gujarati text. If HarfBuzz is not installed, it falls back to PIL rendering.

### Testing

Test with the problematic text:
```
ગોર શશીકાંત મહેન્દ્રભાઈ રાવલ
```

With HarfBuzz, this should render correctly with proper ligatures.

### Note

The script uses **Noto Sans Gujarati** font which you've already installed. This font works best with HarfBuzz for Gujarati text rendering.

