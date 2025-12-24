# Certificate Generator - Python Version

A Python Flask web application for generating certificates from templates.

## Features

- Upload high-resolution PNG certificate templates
- Add multiple names (automatically converted to proper case)
- Select from various fonts including handwriting styles
- Real-time preview with name overlay
- Generate JPG and PDF certificates
- Download as ZIP files (all, JPG only, or PDF only)
- Automatic center alignment of names

## Installation

1. Install Python 3.7 or higher

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install Flask Pillow img2pdf
```

## Running the Application

1. Navigate to the `py` directory:
```bash
cd py
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and visit:
```
http://localhost:5000
```

## Requirements

- Python 3.7+
- Flask 3.0.0
- Pillow 10.1.0 (for image processing)
- img2pdf 0.5.1 (for PDF generation)

## Directory Structure

```
py/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   ├── index.html     # Main form page
│   └── results.html   # Results/download page
├── uploads/          # Uploaded templates (auto-created)
└── output/            # Generated certificates (auto-created)
```

## Usage

1. **Upload Template**: Select a PNG certificate template
2. **Configure Settings**:
   - Choose font style and size
   - Set Y position (vertical position from top)
   - Select text color
3. **Enter Names**: Add names, one per line (automatically converted to proper case)
4. **Generate**: Click "Generate Certificates"
5. **Download**: Choose download option (All, JPG only, or PDF only)

## Notes

- Names are automatically center-aligned horizontally
- All names are converted to proper case (e.g., "dhruv saidava" → "Dhruv Saidava")
- PDF generation requires the `img2pdf` library
- The application runs on port 5000 by default

## Troubleshooting

If PDF generation fails:
- Ensure `img2pdf` is installed: `pip install img2pdf`
- Check that the template image is valid
- Verify file permissions for the output directory

