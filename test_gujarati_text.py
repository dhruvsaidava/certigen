#!/usr/bin/env python3
"""
Test script to check Gujarati text rendering with the specific text
"""
from PIL import Image, ImageDraw, ImageFont
import os
import unicodedata

def test_text_rendering():
    """Test rendering of the specific Gujarati text"""
    test_text = "ઉમેશકુમાર રતિલાલ પટેલ"
    
    # Find Noto Sans Gujarati font
    user_fonts_dir = os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/')
    font_path = os.path.join(user_fonts_dir, 'NotoSansGujarati-Regular.ttf')
    
    if not os.path.exists(font_path):
        print(f"Font not found: {font_path}")
        return
    
    print(f"Using font: {font_path}")
    print(f"Original text: {test_text}")
    print(f"Text length: {len(test_text)} characters")
    print(f"Unicode codes: {[hex(ord(c)) for c in test_text]}")
    
    # Normalize text
    normalized = unicodedata.normalize('NFC', test_text)
    print(f"\nNormalized text: {normalized}")
    print(f"Normalized length: {len(normalized)} characters")
    print(f"Normalized Unicode codes: {[hex(ord(c)) for c in normalized]}")
    
    if test_text != normalized:
        print("\n⚠️  Text changed after normalization!")
    else:
        print("\n✓ Text unchanged after normalization")
    
    # Create test image
    font = ImageFont.truetype(font_path, 48)
    img = Image.new('RGB', (800, 200), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw text
    draw.text((10, 10), normalized, fill='black', font=font)
    
    # Save
    output = 'test_gujarati_rendering.png'
    img.save(output)
    print(f"\n✓ Rendered image saved to: {output}")
    
    # Check each character
    print("\nCharacter analysis:")
    for i, char in enumerate(test_text):
        print(f"  {i}: {char} (U+{ord(char):04X}) {unicodedata.name(char, 'UNNAMED')}")

if __name__ == '__main__':
    test_text_rendering()


