from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
import json
import zipfile
import shutil
import uuid
from datetime import datetime
from pathlib import Path
import img2pdf
import pikepdf
import glob
import unicodedata

# Try to import HarfBuzz for proper text shaping (optional but recommended for Gujarati)
try:
    import harfbuzz
    import freetype
    HARFBUZZ_AVAILABLE = True
except ImportError:
    HARFBUZZ_AVAILABLE = False
    print("Warning: HarfBuzz not available. Install with: pip install harfbuzz freetype-py for better Gujarati text rendering")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def to_proper_case(name):
    """Convert name to proper case (First Letter Capital)"""
    return ' '.join(word.capitalize() for word in name.strip().lower().split())


def check_font_supports_gujarati(font_path):
    """Check if a font supports Gujarati characters"""
    try:
        test_font = ImageFont.truetype(font_path, 12)
        # Test with multiple Gujarati characters
        test_chars = ['અ', 'ક', 'ગ', 'જ', 'ન']  # Various Gujarati characters
        img = Image.new('RGB', (200, 50), 'white')
        draw = ImageDraw.Draw(img)
        
        for test_char in test_chars:
            try:
                bbox = draw.textbbox((0, 0), test_char, font=test_font)
                # If bbox is valid and has reasonable width, the font supports it
                if bbox and (bbox[2] - bbox[0]) > 0:
                    return True
            except:
                continue
    except Exception as e:
        # If we can't even load the font, it's not usable
        pass
    return False


def find_gujarati_font(font_size):
    """Find a font that supports Gujarati characters"""
    # Priority list of Gujarati font names (case-insensitive search)
    gujarati_font_names = [
        'shruti', 'shvruti', 'noto', 'gujarati', 'gujrati',
        'lohit-gujarati', 'lohit gujarati', 'mukta',
        'prabhki', 'rekha', 'kalapi'
    ]
    
    # Search paths (including user fonts directory)
    search_paths = [
        'C:/Windows/Fonts/',
        os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/'),  # User fonts
        '/System/Library/Fonts/',
        '/System/Library/Fonts/Supplemental/',
        '/usr/share/fonts/',
        '/usr/share/fonts/truetype/',
    ]
    
    # First, try exact matches with common names (prioritize Regular variant)
    user_fonts_dir = os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/')
    exact_matches = [
        # User fonts directory (where fonts are usually installed)
        os.path.join(user_fonts_dir, 'NotoSansGujarati-Regular.ttf'),
        os.path.join(user_fonts_dir, 'NotoSansGujarati-Bold.ttf'),
        os.path.join(user_fonts_dir, 'NotoSansGujarati-Medium.ttf'),
        # System fonts directory
        'C:/Windows/Fonts/NotoSansGujarati-Regular.ttf',
        'C:/Windows/Fonts/NotoSansGujarati-Bold.ttf',
        'C:/Windows/Fonts/NotoSansGujarati-Medium.ttf',
        'C:/Windows/Fonts/NotoSansGujarati-Regular.otf',
        'C:/Windows/Fonts/NotoSansGujarati-Bold.otf',
        'C:/Windows/Fonts/shvruti.ttf',
        'C:/Windows/Fonts/SHRUTI.TTF',
        'C:/Windows/Fonts/shruti.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf',
        '/usr/share/fonts/truetype/lohit-gujarati/Lohit-Gujarati.ttf',
        '/System/Library/Fonts/Supplemental/NotoSansGujarati-Regular.ttf',
    ]
    
    for font_path in exact_matches:
        if os.path.exists(font_path):
            try:
                if check_font_supports_gujarati(font_path):
                    print(f"Found Gujarati font: {font_path}")
                    return ImageFont.truetype(font_path, font_size)
            except Exception as e:
                print(f"Failed to load {font_path}: {e}")
                continue
    
    # Search in all font directories (case-insensitive)
    for font_dir in search_paths:
        if not os.path.exists(font_dir):
            continue
            
        # Get all font files
        all_fonts = []
        for ext in ['*.ttf', '*.TTF', '*.otf', '*.OTF']:
            try:
                all_fonts.extend(glob.glob(os.path.join(font_dir, ext)))
            except:
                continue
        
        # Search for fonts with Gujarati-related names (case-insensitive)
        for font_path in all_fonts:
            font_name_lower = os.path.basename(font_path).lower()
            # Check if font name contains any Gujarati-related keyword
            if any(keyword in font_name_lower for keyword in gujarati_font_names):
                try:
                    if check_font_supports_gujarati(font_path):
                        print(f"Found Gujarati font: {font_path}")
                        return ImageFont.truetype(font_path, font_size)
                except Exception as e:
                    continue
    
    # Search in other system font directories
    for base_path in search_paths:
        if os.path.exists(base_path):
            # Search for Noto fonts (most reliable for Gujarati)
            noto_patterns = [
                os.path.join(base_path, '**', '*Noto*Gujarati*.ttf'),
                os.path.join(base_path, '**', '*Noto*Gujarati*.otf'),
                os.path.join(base_path, '**', '*gujarati*.ttf'),
                os.path.join(base_path, '**', '*gujarati*.otf'),
            ]
            for pattern in noto_patterns:
                matches = glob.glob(pattern, recursive=True)
                for font_path in matches:
                    try:
                        if check_font_supports_gujarati(font_path):
                            return ImageFont.truetype(font_path, font_size)
                    except:
                        continue
    
    # Last resort: try Arial Unicode MS (if available, supports many scripts)
    arial_unicode_paths = [
        'C:/Windows/Fonts/ARIALUNI.TTF',
        'C:/Windows/Fonts/arialuni.ttf',
        'C:/Windows/Fonts/Arial Unicode MS.ttf',
    ]
    for font_path in arial_unicode_paths:
        if os.path.exists(font_path):
            try:
                if check_font_supports_gujarati(font_path):
                    return ImageFont.truetype(font_path, font_size)
            except:
                continue
    
    return None


def get_gujarati_font_path():
    """Get the path to the Gujarati font file"""
    user_fonts_dir = os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/')
    exact_matches = [
        os.path.join(user_fonts_dir, 'NotoSansGujarati-Regular.ttf'),
        'C:/Windows/Fonts/NotoSansGujarati-Regular.ttf',
        'C:/Windows/Fonts/shvruti.ttf',
        'C:/Windows/Fonts/SHRUTI.TTF',
    ]
    
    for font_path in exact_matches:
        if os.path.exists(font_path):
            return font_path
    
    # Search in user fonts directory
    if os.path.exists(user_fonts_dir):
        for font_file in os.listdir(user_fonts_dir):
            if 'noto' in font_file.lower() and 'gujarati' in font_file.lower() and 'regular' in font_file.lower():
                font_path = os.path.join(user_fonts_dir, font_file)
                if font_path.endswith('.ttf') or font_path.endswith('.otf'):
                    return font_path
    
    return None


def get_gujarati_font_path():
    """Get the path to the Gujarati font file"""
    user_fonts_dir = os.path.expanduser('~/AppData/Local/Microsoft/Windows/Fonts/')
    exact_matches = [
        os.path.join(user_fonts_dir, 'NotoSansGujarati-Regular.ttf'),
        'C:/Windows/Fonts/NotoSansGujarati-Regular.ttf',
        'C:/Windows/Fonts/shvruti.ttf',
        'C:/Windows/Fonts/SHRUTI.TTF',
    ]
    
    for font_path in exact_matches:
        if os.path.exists(font_path):
            return font_path
    
    # Search in user fonts directory
    if os.path.exists(user_fonts_dir):
        for font_file in os.listdir(user_fonts_dir):
            if 'noto' in font_file.lower() and 'gujarati' in font_file.lower() and 'regular' in font_file.lower():
                font_path = os.path.join(user_fonts_dir, font_file)
                if font_path.endswith('.ttf') or font_path.endswith('.otf'):
                    return font_path
    
    return None


def get_font_path(font_name, font_size):
    """Get font path based on selection"""
    font_map = {
        'arial': 'arial.ttf',
        'times': 'times.ttf',
        'cursive': None,  # Will use system cursive
        'mongolia': None,  # Will use system cursive
        'brush': None,  # Will use system cursive
        'lucida': None,  # Will use system cursive
        'gujarati': None,  # Will use Gujarati font
    }
    
    # For Gujarati font, use specialized search
    if font_name == 'gujarati':
        gujarati_font = find_gujarati_font(font_size)
        if gujarati_font:
            font_path = get_gujarati_font_path()
            print(f"Using Gujarati font: {font_path or 'PIL font object'}")
            # Store font path for HarfBuzz use
            if font_path:
                gujarati_font._font_path = font_path  # Store path for later use
            return gujarati_font
        # If no Gujarati font found, warn but continue with fallback
        print("Warning: No Gujarati-supporting font found. Using fallback font.")
        print("Please install a Gujarati font like Shruti or Noto Sans Gujarati.")
        font_file = 'arial.ttf'
    else:
        font_file = font_map.get(font_name, 'arial.ttf')
    
    # Try to find system fonts
    system_font_paths = [
        'C:/Windows/Fonts/',
        '/System/Library/Fonts/',
        '/usr/share/fonts/',
    ]
    
    if font_file:
        for base_path in system_font_paths:
            if os.path.exists(base_path):
                font_path = os.path.join(base_path, font_file)
                if os.path.exists(font_path):
                    try:
                        return ImageFont.truetype(font_path, font_size)
                    except:
                        continue
    
    # For cursive/handwriting fonts, try common system fonts
    if font_name in ['cursive', 'mongolia', 'brush', 'lucida']:
        cursive_fonts = [
            'C:/Windows/Fonts/BRUSHSCI.TTF',
            'C:/Windows/Fonts/BRUSHSC.ttf',
            'C:/Windows/Fonts/SCRIPTBL.TTF',
            'C:/Windows/Fonts/LHANDW.TTF',
        ]
        for font_path in cursive_fonts:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, font_size)
                except:
                    continue
    
    # Fallback to default font
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except:
        return ImageFont.load_default()


def render_gujarati_with_harfbuzz(draw, text, font_path, font_size, x, y, fill_color):
    """Render Gujarati text using HarfBuzz for proper ligature support"""
    if not HARFBUZZ_AVAILABLE:
        raise ImportError("HarfBuzz not available")
    
    # Load font with FreeType
    face = freetype.Face(font_path)
    face.set_char_size(font_size * 64)  # FreeType uses 26.6 fixed point
    
    # Create HarfBuzz buffer
    buf = harfbuzz.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    
    # Shape the text (this handles ligatures correctly)
    harfbuzz.shape(face, buf)
    
    # Get glyph information
    glyph_infos = buf.glyph_infos
    glyph_positions = buf.glyph_positions
    
    # Render each glyph
    current_x = x
    current_y = y
    
    for info, pos in zip(glyph_infos, glyph_positions):
        glyph_index = info.codepoint
        face.load_glyph(glyph_index)
        bitmap = face.glyph.bitmap
        
        if bitmap.width > 0 and bitmap.rows > 0:
            # Create glyph image
            glyph_image = Image.frombytes('L', (bitmap.width, bitmap.rows), bitmap.buffer)
            
            # Calculate position (FreeType coordinates: top-left origin)
            glyph_x = current_x + pos.x_offset // 64 + face.glyph.bitmap_left
            glyph_y = current_y - pos.y_offset // 64 - face.glyph.bitmap_top
            
            # Draw glyph using bitmap
            mask = glyph_image
            draw.bitmap((glyph_x, glyph_y), mask, fill=fill_color)
        
        # Advance position
        current_x += pos.x_advance // 64
        current_y -= pos.y_advance // 64
    
    # Return the width of rendered text
    return current_x - x


def generate_certificate_image(template_path, name, font_name, font_size, y_position, text_color, output_path):
    """Generate certificate image with name"""
    # Load template
    template = Image.open(template_path)
    template = template.convert('RGB')  # Ensure RGB mode
    
    # Get image dimensions
    width, height = template.size
    
    # Parse color
    color = text_color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Get font
    font = get_font_path(font_name, font_size)
    
    # Ensure name is properly encoded as Unicode string
    if isinstance(name, bytes):
        name = name.decode('utf-8')
    name = str(name)
    
    # Normalize Unicode for Gujarati (NFC normalization helps with ligatures)
    if font_name == 'gujarati':
        name = unicodedata.normalize('NFC', name)
    
    # Create drawing context
    draw = ImageDraw.Draw(template)
    
    # Calculate center X position
    center_x = width / 2
    
    # For Gujarati with HarfBuzz, calculate text width differently
    if font_name == 'gujarati' and HARFBUZZ_AVAILABLE:
        try:
            # Get font path for HarfBuzz
            font_path = getattr(font, '_font_path', None)  # Check stored path
            if not font_path:
                font_path = get_gujarati_font_path()  # Try to find it
            
            if font_path and os.path.exists(font_path):
                # Measure text width using HarfBuzz
                face = freetype.Face(font_path)
                face.set_char_size(font_size * 64)
                buf = harfbuzz.Buffer()
                buf.add_str(name)
                buf.guess_segment_properties()
                harfbuzz.shape(face, buf)
                
                # Calculate total width
                text_width = sum(pos.x_advance // 64 for pos in buf.glyph_positions)
                text_height = font_size
                
                # Center horizontally
                x_position = center_x - (text_width / 2)
                y_pos = y_position
                
                # Render with HarfBuzz
                render_gujarati_with_harfbuzz(draw, name, font_path, font_size, x_position, y_pos, rgb)
            else:
                # Fallback to PIL rendering if font path not found
                raise Exception("Font path not found for HarfBuzz")
                
        except Exception as e:
            print(f"Warning: HarfBuzz rendering failed ({e}), falling back to PIL")
            # Fallback to regular PIL rendering
            try:
                bbox = draw.textbbox((0, 0), name, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                text_width = len(name) * (font_size * 0.5)
                text_height = font_size
            
            x_position = center_x - (text_width / 2)
            y_pos = y_position
            draw.text((x_position, y_pos), name, fill=rgb, font=font)
    else:
        # Regular PIL rendering for non-Gujarati or when HarfBuzz not available
        try:
            bbox = draw.textbbox((0, 0), name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except Exception as e:
            # Fallback if bbox calculation fails
            print(f"Warning: Could not calculate text bbox: {e}")
            # Estimate width (rough approximation for Gujarati)
            if font_name == 'gujarati':
                text_width = len(name) * (font_size * 0.5)  # Gujarati characters are wider
            else:
                text_width = len(name) * (font_size * 0.6)
            text_height = font_size
        
        # Center horizontally
        x_position = center_x - (text_width / 2)
        
        # Y position is from top (PIL uses top-left as origin)
        y_pos = y_position
        
        # Draw text
        draw.text((x_position, y_pos), name, fill=rgb, font=font)
    
    # Save as JPG
    jpg_path = output_path.replace('.png', '.jpg')
    template.save(jpg_path, 'JPEG', quality=100)
    
    # Save as PNG
    template.save(output_path, 'PNG', optimize=True)
    
    return {'jpg': jpg_path, 'png': output_path}


def generate_pdf(image_path, pdf_path):
    """Generate PDF from image"""
    try:
        # Use img2pdf for high quality PDF generation
        with open(pdf_path, 'wb') as f:
            f.write(img2pdf.convert(image_path))
        return True
    except Exception as e:
        print(f"PDF generation error: {e}")
        return False


def combine_pdfs(pdf_files, output_path):
    """Combine multiple PDF files into one"""
    try:
        if not pdf_files:
            return False
        
        # Filter out non-existent files
        existing_pdfs = [pdf for pdf in pdf_files if os.path.exists(pdf)]
        if not existing_pdfs:
            return False
        
        # Create a new PDF and merge all pages
        merged_pdf = pikepdf.Pdf.new()
        
        for pdf_file in existing_pdfs:
            try:
                source_pdf = pikepdf.Pdf.open(pdf_file)
                merged_pdf.pages.extend(source_pdf.pages)
                source_pdf.close()
            except Exception as e:
                print(f"Error merging {pdf_file}: {e}")
                continue
        
        # Save the merged PDF
        merged_pdf.save(output_path)
        merged_pdf.close()
        
        return os.path.exists(output_path)
    except Exception as e:
        print(f"PDF combination error: {e}")
        return False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    """Process certificate generation"""
    try:
        # Check if template file is uploaded
        if 'template' not in request.files:
            return jsonify({'success': False, 'message': 'No template file uploaded'}), 400
        
        template_file = request.files['template']
        
        if template_file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Validate file type
        if not template_file.filename.lower().endswith('.png'):
            return jsonify({'success': False, 'message': 'Please upload a PNG image'}), 400
        
        # Save uploaded template
        template_filename = f'template_{int(datetime.now().timestamp())}.png'
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)
        template_file.save(template_path)
        
        # Verify it's a valid image
        try:
            img = Image.open(template_path)
            img.verify()
        except Exception as e:
            os.remove(template_path)
            return jsonify({'success': False, 'message': 'Invalid image file'}), 400
        
        # Get form data - ensure UTF-8 encoding is preserved
        font = request.form.get('font', 'arial')
        font_size = max(10, int(request.form.get('fontSize', 48)))  # Minimum font size is 10
        y_position = int(request.form.get('yPosition', 300))
        text_color = request.form.get('textColor', '#000000')
        names_text = request.form.get('names', '')
        generate_pdf_flag = request.form.get('generatePDF') == '1'
        
        if not names_text.strip():
            return jsonify({'success': False, 'message': 'Please provide at least one name'}), 400
        
        # Ensure names_text is a proper Unicode string (Flask should handle this, but ensure it)
        if isinstance(names_text, bytes):
            names_text = names_text.decode('utf-8')
        names_text = str(names_text)
        
        # Process names - preserve original case for Gujarati (don't convert to proper case)
        names = [line.strip() for line in names_text.split('\n') if line.strip()]
        # Only apply proper case conversion for non-Gujarati fonts
        if font == 'gujarati':
            proper_names = names  # Keep original text for Gujarati - no sorting to preserve order
        else:
            proper_names = [to_proper_case(name) for name in names]
            # Sort names alphabetically for easy sequential access (only for non-Gujarati)
            proper_names.sort()
        
        # Create session directory
        session_id = f'cert_{uuid.uuid4().hex[:16]}.{int(datetime.now().timestamp() * 1000000) % 100000000}'
        session_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, 'jpg'), exist_ok=True)
        os.makedirs(os.path.join(session_dir, 'pdf'), exist_ok=True)
        
        # Check if Gujarati font is available when Gujarati is selected
        if font == 'gujarati':
            test_font = find_gujarati_font(12)
            if not test_font:
                return jsonify({
                    'success': False,
                    'message': 'Gujarati font not found on your system. Please install a Gujarati font like Shruti or Noto Sans Gujarati. Common locations: C:/Windows/Fonts/'
                }), 400
        
        # Generate certificates
        generated_files = []
        for index, name in enumerate(proper_names):
            # Sanitize filename but preserve original name for display
            safe_name = ''.join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
            output_filename = f'cert_{index + 1}_{safe_name.replace(" ", "_")}.png'
            output_path = os.path.join(session_dir, output_filename)
            
            try:
                result = generate_certificate_image(
                    template_path, name, font, font_size, y_position, text_color, output_path
                )
            except Exception as e:
                error_msg = str(e)
                if font == 'gujarati' and 'font' in error_msg.lower():
                    return jsonify({
                        'success': False,
                        'message': f'Error rendering Gujarati text: {error_msg}. Please ensure a Gujarati font is installed.'
                    }), 500
                raise
            
            if result:
                # Copy JPG to jpg folder
                jpg_name = os.path.basename(result['jpg'])
                shutil.copy(result['jpg'], os.path.join(session_dir, 'jpg', jpg_name))
                
                file_info = {
                    'name': name,
                    'jpg': jpg_name,
                }
                
                # Generate PDF if requested
                if generate_pdf_flag:
                    pdf_path = os.path.join(session_dir, 'pdf', output_filename.replace('.png', '.pdf'))
                    pdf_generated = generate_pdf(result['png'], pdf_path)
                    if pdf_generated and os.path.exists(pdf_path):
                        file_info['pdf'] = os.path.basename(pdf_path)
                
                generated_files.append(file_info)
        
        # Generate combined PDF if PDFs were requested and generated
        combined_pdf_path = None
        has_combined_pdf = False
        if generate_pdf_flag:
            pdf_dir = os.path.join(session_dir, 'pdf')
            pdf_files = []
            for file_info in generated_files:
                if 'pdf' in file_info:
                    pdf_file_path = os.path.join(pdf_dir, file_info['pdf'])
                    if os.path.exists(pdf_file_path):
                        pdf_files.append(pdf_file_path)
            
            if pdf_files:
                combined_pdf_path = os.path.join(session_dir, 'combined_certificates.pdf')
                has_combined_pdf = combine_pdfs(pdf_files, combined_pdf_path)
        
        # Save session info
        info = {
            'session_id': session_id,
            'names': proper_names,
            'files': generated_files,
            'has_pdf': generate_pdf_flag,
            'has_combined_pdf': has_combined_pdf,
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        info_path = os.path.join(session_dir, 'info.json')
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'count': len(generated_files),
            'has_pdf': generate_pdf_flag,
            'message': 'Certificates generated successfully!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/results')
def results():
    """Results page with download options"""
    session_id = request.args.get('session', '')
    
    if not session_id or not session_id.startswith('cert_'):
        return "Invalid session ID", 400
    
    session_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        return "Session not found or expired", 404
    
    info_path = os.path.join(session_dir, 'info.json')
    if not os.path.exists(info_path):
        return "Session info not found", 404
    
    with open(info_path, 'r') as f:
        info = json.load(f)
    
    # Check if PDFs actually exist
    pdf_dir = os.path.join(session_dir, 'pdf')
    pdf_files = []
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    return render_template('results.html', info=info, session_id=session_id, pdf_files=pdf_files)


@app.route('/download')
def download():
    """Download ZIP file"""
    session_id = request.args.get('session', '')
    download_type = request.args.get('type', 'all')  # all, jpg, pdf
    
    if not session_id or not session_id.startswith('cert_'):
        return "Invalid session ID", 400
    
    session_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        return "Session not found or expired", 404
    
    # Determine ZIP file name
    type_names = {
        'all': 'All_Certificates',
        'jpg': 'JPG_Certificates',
        'pdf': 'PDF_Certificates'
    }
    
    zip_filename = f"{type_names.get(download_type, 'All_Certificates')}_{session_id}.zip"
    zip_path = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
    
    # Create ZIP archive
    has_files = False
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if download_type in ['all', 'jpg']:
            jpg_dir = os.path.join(session_dir, 'jpg')
            if os.path.exists(jpg_dir):
                for jpg_file in os.listdir(jpg_dir):
                    if jpg_file.endswith('.jpg'):
                        file_path = os.path.join(jpg_dir, jpg_file)
                        zipf.write(file_path, f'JPG/{jpg_file}')
                        has_files = True
        
        if download_type in ['all', 'pdf']:
            pdf_dir = os.path.join(session_dir, 'pdf')
            if os.path.exists(pdf_dir):
                for pdf_file in os.listdir(pdf_dir):
                    if pdf_file.endswith('.pdf'):
                        file_path = os.path.join(pdf_dir, pdf_file)
                        zipf.write(file_path, f'PDF/{pdf_file}')
                        has_files = True
        
        if download_type == 'all':
            # Add PNG files
            for png_file in os.listdir(session_dir):
                if png_file.endswith('.png'):
                    file_path = os.path.join(session_dir, png_file)
                    zipf.write(file_path, f'PNG/{png_file}')
                    has_files = True
    
    if not has_files:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return "No files found to download", 404
    
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)


@app.route('/output/<session_id>/<file_type>/<filename>')
def serve_file(session_id, file_type, filename):
    """Serve individual certificate files"""
    if not session_id.startswith('cert_'):
        return "Invalid session ID", 400
    
    if file_type not in ['jpg', 'pdf']:
        return "Invalid file type", 400
    
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], session_id, file_type, filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(file_path)


@app.route('/download-combined')
def download_combined():
    """Download combined PDF file"""
    session_id = request.args.get('session', '')
    
    if not session_id or not session_id.startswith('cert_'):
        return "Invalid session ID", 400
    
    session_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        return "Session not found or expired", 404
    
    combined_pdf_path = os.path.join(session_dir, 'combined_certificates.pdf')
    
    if not os.path.exists(combined_pdf_path):
        return "Combined PDF not found", 404
    
    return send_file(combined_pdf_path, as_attachment=True, download_name=f'Combined_Certificates_{session_id}.pdf')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

