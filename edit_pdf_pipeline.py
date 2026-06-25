"""
PDF Text Replacement Pipeline for Scanned Documents
===================================================
Strategy: Render page → OCR → find text → paint over → write replacement → rebuild PDF
"""

import fitz, pytesseract, sys, os, io
from PIL import Image, ImageDraw, ImageFont
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
INPUT_PDF = r"D:\Ai_Tools\Open_code\project_folder\samarthan 23 24 docs.pdf"
OUTPUT_PDF = r"D:\Ai_Tools\Open_code\project_folder\samarthan 23 24 docs_edited.pdf"
DPI = 300

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Replacements: (search_text, replacement_text, page_number or None for all)
REPLACEMENTS = [
    ("પ્રવૃતિઓ -2010-2011", "પ્રવૃતિઓ -2022-2023"),
    ("Year 2006-2007", "Year 2022-2023"),
    ("DIST. SUREDRANAGAR", "DIST. MORBI"),
    ("For the year 2005-2006, 60cases", "For the year 2022-2023, 60cases"),
]

# Fallback search strings (more OCR-friendly substrings)
FALLBACKS = {
    "પ્રવૃતિઓ -2010-2011": "-2010-2011",
    "For the year 2005-2006, 60cases": "2005-2006",
    "Year 2006-2007": "2006-2007",
    "DIST. SUREDRANAGAR": "SUREDRANAGAR",
}

# Font configuration
FONT_NAME = "Nirmala UI"  # Windows font with Gujarati support

# ─── FUZZY MATCHING ─────────────────────────────────────────────────────────
def similar(a, b):
    """Compute string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_text_in_data(data, search_text, fallback=None):
    """
    Search for text in OCR data output.
    Returns list of (bbox, confidence) tuples.
    bbox = (left, top, right, bottom) in image pixels.
    """
    matches = []
    n = len(data["text"])
    
    # Strategy 1: Try to find exact/fuzzy match in individual words
    best_ratio = 0.3
    best_indices = []
    
    # Look for the search text across consecutive words
    for i in range(n):
        if not data["text"][i] or not data["text"][i].strip():
            continue
        for j in range(i, min(i + 6, n)):
            if not data["text"][j] or not data["text"][j].strip():
                continue
            # Build phrase from i to j
            phrase_parts = []
            for k in range(i, j + 1):
                if data["text"][k] and data["text"][k].strip():
                    phrase_parts.append(data["text"][k].strip())
            phrase = " ".join(phrase_parts)
            
            ratio = similar(search_text, phrase)
            if ratio >= best_ratio:
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_indices = []
                best_indices.append((i, j + 1))
    
    if best_indices:
        # Use the best match
        i, j_end = best_indices[0]
        # Calculate combined bounding box
        xs = [data["left"][k] for k in range(i, j_end) if data["text"][k] and data["text"][k].strip()]
        ys = [data["top"][k] for k in range(i, j_end) if data["text"][k] and data["text"][k].strip()]
        xes = [data["left"][k] + data["width"][k] for k in range(i, j_end) if data["text"][k] and data["text"][k].strip()]
        yes = [data["top"][k] + data["height"][k] for k in range(i, j_end) if data["text"][k] and data["text"][k].strip()]
        
        if xs:
            bbox = (min(xs), min(ys), max(xes), max(yes))
            matches.append((bbox, best_ratio))
            print(f"    ✓ Found via fuzzy match (ratio={best_ratio:.2f}): '{' '.join(data['text'][k].strip() for k in range(i, j_end) if data['text'][k] and data['text'][k].strip())}'")
            return matches
    
    # Strategy 2: Try fallback substring if provided
    if fallback:
        for i in range(n):
            t = data["text"][i]
            if t and fallback.lower() in t.lower():
                bbox = (
                    data["left"][i],
                    data["top"][i],
                    data["left"][i] + data["width"][i],
                    data["top"][i] + data["height"][i],
                )
                # Expand the bbox to the left to capture the full text
                # The fallback might only match part of the text
                expanded_bbox = (
                    max(0, bbox[0] - 200),  # expand left
                    max(0, bbox[1] - 10),
                    bbox[2] + 50,
                    bbox[3] + 10,
                )
                matches.append((expanded_bbox, 0.8))
                print(f"    ✓ Found via fallback '{fallback}' at word index {i}: '{data['text'][i]}'")
                return matches
    
    return matches

def find_fallback_substring(data, fallback_text):
    """Find a fallback substring anywhere in the OCR data and return expanded bbox."""
    n = len(data["text"])
    for i in range(n):
        t = data["text"][i]
        if t and fallback_text.lower() in t.lower():
            bbox = (
                data["left"][i],
                data["top"][i],
                data["left"][i] + data["width"][i],
                data["top"][i] + data["height"][i],
            )
            return bbox
    return None

# ─── IMAGE EDITING ──────────────────────────────────────────────────────────
def get_font(size):
    """Get a font that supports Gujarati text."""
    try:
        return ImageFont.truetype(FONT_NAME, size)
    except Exception:
        try:
            return ImageFont.truetype("Nirmala Text", size)
        except Exception:
            return ImageFont.load_default()

def replace_text_on_page(img, bbox, new_text, font_size=14):
    """
    Paint white over the bbox area and write new text.
    bbox = (left, top, right, bottom) in image pixels.
    """
    draw = ImageDraw.Draw(img)
    
    # Add some padding
    padding = 4
    x1 = max(0, bbox[0] - padding)
    y1 = max(0, bbox[1] - padding)
    x2 = min(img.width, bbox[2] + padding)
    y2 = min(img.height, bbox[3] + padding)
    
    # Paint white rectangle
    draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255))
    
    # Try to determine good font size based on bbox height
    bbox_height = y2 - y1
    use_font_size = max(10, min(bbox_height - 4, 72))
    
    # Try different font sizes to fit within the bbox width
    font = get_font(use_font_size)
    
    # Measure text
    try:
        text_bbox = draw.textbbox((0, 0), new_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except Exception:
        text_width = len(new_text) * use_font_size * 0.6
        text_height = use_font_size
    
    bbox_width = x2 - x1
    
    # Scale down if text is too wide
    if text_width > bbox_width * 1.2 and use_font_size > 6:
        use_font_size = int(use_font_size * bbox_width * 0.8 / text_width)
        use_font_size = max(6, use_font_size)
        font = get_font(use_font_size)
        try:
            text_bbox = draw.textbbox((0, 0), new_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except Exception:
            text_width = len(new_text) * use_font_size * 0.6
            text_height = use_font_size
    
    # Center text vertically in the bbox area
    text_y = y1 + (bbox_height - text_height) // 2
    
    # Draw new text
    try:
        draw.text((x1, text_y), new_text, fill=(0, 0, 0), font=font)
    except Exception:
        # Fallback: draw with default font
        draw.text((x1, y1), new_text, fill=(0, 0, 0))
    
    print(f"    ✓ Replaced with '{new_text}' at [{x1}, {y1}, {x2}, {y2}], font={use_font_size}px")

# ─── MAIN ────────────────────────────────────────────────────────────────────
print("=" * 60)
print("PDF EDIT PIPELINE")
print("=" * 60)
print(f"Input: {INPUT_PDF}")
print(f"Output: {OUTPUT_PDF}")
print(f"DPI: {DPI}")
print()

doc = fitz.open(INPUT_PDF)
print(f"Total pages: {len(doc)}")

# Process each page
modified_images = []

for page_num in range(len(doc)):
    page = doc[page_num]
    print(f"\n{'─' * 50}")
    print(f"Processing page {page_num + 1}...")
    
    # Render page at high DPI
    pix = page.get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # OCR the page
    print(f"  OCR-ing page {page_num + 1}...")
    data = pytesseract.image_to_data(
        img, lang="eng+guj", output_type=pytesseract.Output.DICT
    )
    
    page_modified = False
    
    # Process each replacement
    for search_text, replace_text in REPLACEMENTS:
        fallback = FALLBACKS.get(search_text)
        print(f"\n  🔍 Searching for: '{search_text}'")
        
        matches = find_text_in_data(data, search_text, fallback)
        
        if matches:
            for bbox, confidence in matches:
                print(f"    📍 BBox: {bbox}, confidence: {confidence:.2f}")
                replace_text_on_page(img, bbox, replace_text)
                page_modified = True
        else:
            print(f"    ❌ NOT FOUND via fuzzy match or fallback")
            
            # Last resort: try scanning the full page text
            full_text = pytesseract.image_to_string(img, lang="eng+guj")
            if fallback and fallback in full_text:
                print(f"    ⚠  Found fallback in full text but couldn't locate bounding box")
            
            # Check if we should try the fallback as a direct search
            if fallback:
                fb_bbox = find_fallback_substring(data, fallback)
                if fb_bbox:
                    print(f"    📍 Found fallback '{fallback}' at {fb_bbox}")
                    # Expand bbox significantly to capture the full phrase
                    expanded = (
                        max(0, fb_bbox[0] - 300),
                        max(0, fb_bbox[1] - 30),
                        fb_bbox[2] + 150,
                        fb_bbox[3] + 30,
                    )
                    print(f"    📍 Expanded to: {expanded}")
                    replace_text_on_page(img, expanded, replace_text)
                    page_modified = True
    
    modified_images.append(img)
    
    if page_modified:
        print(f"  ✅ Page {page_num + 1} modified")
    else:
        print(f"  ⏭️  Page {page_num + 1} unchanged")

# ─── SAVE AS PDF ─────────────────────────────────────────────────────────────
print(f"\n{'=' * 50}")
print("Saving modified PDF...")

# Save images as PDF
if modified_images:
    first_img = modified_images[0]
    # Convert PIL images to RGB mode if needed
    rgb_images = []
    for img in modified_images:
        if img.mode != "RGB":
            img = img.convert("RGB")
        rgb_images.append(img)
    
    # Save as PDF
    pdf_bytes = io.BytesIO()
    rgb_images[0].save(
        pdf_bytes,
        format="PDF",
        save_all=True,
        append_images=rgb_images[1:] if len(rgb_images) > 1 else [],
        resolution=DPI / 72,  # PIL expects resolution in DPI
    )
    
    # Write to file
    with open(OUTPUT_PDF, "wb") as f:
        f.write(pdf_bytes.getvalue())
    
    print(f"✅ Saved to: {OUTPUT_PDF}")
else:
    print("❌ No images to save")

print(f"\n{'=' * 50}")
print("Done!")
