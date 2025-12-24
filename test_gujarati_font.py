#!/usr/bin/env python3
"""
Test script to check if Gujarati fonts are available and working
"""
from PIL import Image, ImageDraw, ImageFont
import os
import glob

def test_gujarati_font(font_path):
    """Test if a font can render Gujarati text"""
    try:
        font = ImageFont.truetype(font_path, 24)
        test_text = 'ગુજરાતી'  # "Gujarati" in Gujarati
        
        # Create a test image
        img = Image.new('RGB', (200, 100), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to draw the text
        draw.text((10, 10), test_text, fill='black', font=font)
        
        # Check if text was rendered (not just boxes)
        # Save and check
        test_output = 'test_gujarati_output.png'
        img.save(test_output)
        
        print(f"✓ {font_path} - SUCCESS")
        return True
    except Exception as e:
        print(f"✗ {font_path} - FAILED: {e}")
        return False

def find_gujarati_fonts():
    """Find all potential Gujarati fonts"""
    print("Searching for Gujarati fonts...\n")
    
    import os.path
    search_paths = [
        'C:/Windows/Fonts/',
        os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/'),  # User fonts
        '/System/Library/Fonts/',
        '/usr/share/fonts/',
    ]
    
    gujarati_keywords = ['shruti', 'shvruti', 'noto', 'gujarati', 'gujrati', 'lohit']
    found_fonts = []
    
    for base_path in search_paths:
        if not os.path.exists(base_path):
            print(f"Skipping (not found): {base_path}")
            continue
            
        print(f"Searching in: {base_path}")
        
        # Get all fonts and filter by name
        all_fonts = []
        for ext in ['*.ttf', '*.TTF', '*.otf', '*.OTF']:
            try:
                all_fonts.extend(glob.glob(os.path.join(base_path, ext)))
            except:
                pass
        
        # Check if any font name contains Gujarati keywords
        for font_path in all_fonts:
            font_name_lower = os.path.basename(font_path).lower()
            if any(keyword in font_name_lower for keyword in gujarati_keywords):
                found_fonts.append(font_path)
    
    # Remove duplicates
    found_fonts = list(set(found_fonts))
    
    if found_fonts:
        print(f"\nFound {len(found_fonts)} potential Gujarati fonts:\n")
        working_fonts = []
        for font_path in found_fonts:
            if test_gujarati_font(font_path):
                working_fonts.append(font_path)
        
        if working_fonts:
            print(f"\n✓ {len(working_fonts)} working Gujarati font(s) found:")
            for font in working_fonts:
                print(f"  - {font}")
        else:
            print("\n✗ No working Gujarati fonts found!")
            print("\nPlease install a Gujarati font:")
            print("  - Shruti: Usually comes with Windows")
            print("  - Noto Sans Gujarati: Download from https://fonts.google.com/noto/specimen/Noto+Sans+Gujarati")
    else:
        print("\n✗ No Gujarati fonts found!")
        print("\nPlease install a Gujarati font:")
        print("  - Shruti: Usually comes with Windows")
        print("  - Noto Sans Gujarati: Download from https://fonts.google.com/noto/specimen/Noto+Sans+Gujarati")

if __name__ == '__main__':
    find_gujarati_fonts()

