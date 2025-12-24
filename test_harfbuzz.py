#!/usr/bin/env python3
"""
Test HarfBuzz rendering for Gujarati text
"""
try:
    import harfbuzz
    import freetype
    HARFBUZZ_AVAILABLE = True
    print("HarfBuzz is available")
except ImportError:
    HARFBUZZ_AVAILABLE = False
    print("HarfBuzz not available - install with: pip install harfbuzz freetype-py")

if HARFBUZZ_AVAILABLE:
    from PIL import Image, ImageDraw
    import os
    
    def render_text_with_harfbuzz(text, font_path, font_size, width, height, text_color=(0, 0, 0)):
        """Render text using HarfBuzz for proper shaping"""
        # Load font with FreeType
        face = freetype.Face(font_path)
        face.set_char_size(font_size * 64)  # FreeType uses 26.6 fixed point
        
        # Create HarfBuzz buffer
        buf = harfbuzz.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        
        # Shape the text
        harfbuzz.shape(face, buf)
        
        # Create image
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Render glyphs
        x, y = 0, font_size
        glyph_infos = buf.glyph_infos
        glyph_positions = buf.glyph_positions
        
        for info, pos in zip(glyph_infos, glyph_positions):
            glyph_index = info.codepoint
            face.load_glyph(glyph_index)
            bitmap = face.glyph.bitmap
            glyph_image = Image.frombytes('L', (bitmap.width, bitmap.rows), bitmap.buffer)
            
            # Calculate position
            glyph_x = x + pos.x_offset // 64 + face.glyph.bitmap_left
            glyph_y = y - pos.y_offset // 64 - face.glyph.bitmap_top
            
            # Draw glyph
            mask = glyph_image
            draw.bitmap((glyph_x, glyph_y), mask, fill=text_color)
            
            # Advance position
            x += pos.x_advance // 64
            y -= pos.y_advance // 64
        
        return img, x  # Return image and text width
    
    # Test
    user_fonts_dir = os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/')
    font_path = os.path.join(user_fonts_dir, 'NotoSansGujarati-Regular.ttf')
    
    if os.path.exists(font_path):
        test_text = "ગોર શશીકાંત મહેન્દ્રભાઈ રાવલ"
        print(f"\nTesting text: {test_text}")
        img, text_width = render_text_with_harfbuzz(test_text, font_path, 48, 800, 200)
        img.save('test_harfbuzz_output.png')
        print(f"✓ Rendered image saved to: test_harfbuzz_output.png")
        print(f"Text width: {text_width}px")
    else:
        print(f"Font not found: {font_path}")

