"""
PDF Text Replacement v2 - Page-Specific, High-Confidence
=========================================================
Only targets specific pages known to contain each text.
Uses high confidence thresholds and fallback expansion for Gujarati.
"""

import fitz, pytesseract, sys, io
from PIL import Image, ImageDraw, ImageFont
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")

INPUT_PDF = r"D:\Ai_Tools\Open_code\project_folder\samarthan 23 24 docs.pdf"
OUTPUT_PDF = r"D:\Ai_Tools\Open_code\project_folder\samarthan 23 24 docs_edited.pdf"
DPI = 300
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
FONT_PATH = r"C:\Windows\Fonts\Nirmala.ttc"
FONT_INDEX = 0  # Nirmala UI Regular

# Page-specific replacements: (search_text, replacement_text, target_page, fallback, expand_left)
# Each replacement is ONLY searched on its target page(s)
REPLACEMENTS = [
    # Page 1: Gujarati heading with years
    # Search for "-2010-2011" (reliably OCR'd), then expand bbox left 400px to capture Gujarati text
    ("-2010-2011", "પ્રવૃતિઓ -2022-2023", 1, None, 400),
    
    # Page 2: Year header
    ("Year 2006-2007", "Year 2022-2023", 2, None, 0),
    
    # Page 5: District name
    ("DIST. SUREDRANAGAR", "DIST. MORBI", 5, None, 0),
    
    # Page 6: Year in case count
    ("For the year 2005-2006, 60cases", "For the year 2022-2023, 60cases", 6, None, 0),
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def similar(a, b):
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size, index=FONT_INDEX)
    except Exception as e:
        print(f"      ⚠ Font load failed ({e}), trying fallback...")
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype(FONT_PATH, size, index=1)
            except:
                return ImageFont.load_default()

def draw_replacement(img, bbox, new_text, bbox_hint=None):
    """
    Paint white over bbox area and draw new text.
    bbox = (left, top, right, bottom) in image pixels.
    """
    draw = ImageDraw.Draw(img)
    padding = 6
    x1 = max(0, bbox[0] - padding)
    y1 = max(0, bbox[1] - padding)
    x2 = min(img.width, bbox[2] + padding)
    y2 = min(img.height, bbox[3] + padding)
    
    # White rectangle
    draw.rectangle([x1, y1, x2, y2], fill=(255, 255, 255))
    
    # Determine font size from bbox height
    bbox_h = y2 - y1
    font_size = max(10, min(int(bbox_h * 0.75), 72))
    font = get_font(font_size)
    
    # Measure text
    try:
        tb = draw.textbbox((0, 0), new_text, font=font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
    except:
        tw = len(new_text) * font_size * 0.6
        th = font_size
    
    bbox_w = x2 - x1
    
    # Scale down if too wide
    if tw > bbox_w * 1.1 and font_size > 6:
        font_size = int(font_size * bbox_w * 0.85 / max(tw, 1))
        font_size = max(6, font_size)
        font = get_font(font_size)
        try:
            tb = draw.textbbox((0, 0), new_text, font=font)
            tw = tb[2] - tb[0]
            th = tb[3] - tb[1]
        except:
            tw = len(new_text) * font_size * 0.6
            th = font_size
    
    # Center vertically
    text_y = y1 + (bbox_h - th) // 2
    draw.text((x1, text_y), new_text, fill=(0, 0, 0), font=font)
    print(f"      Wrote '{new_text}' at ({x1},{y1},{x2},{y2}) font={font_size}px")

def scan_page_ocr(img, search_text, page_num, fallback=None):
    """
    Scan page image via OCR to find search_text.
    Returns (bbox, confidence) or None.
    bbox = (left, top, right, bottom) in image pixels.
    """
    data = pytesseract.image_to_data(
        img, lang="eng+guj", output_type=pytesseract.Output.DICT
    )
    n = len(data["text"])
    
    best_score = 0.0
    best_bbox = None
    
    # Strategy 1: Check each individual word
    for i in range(n):
        t = data["text"][i]
        if not t or not t.strip():
            continue
        score = similar(search_text, t.strip())
        if score > best_score:
            best_score = score
            best_bbox = (
                data["left"][i], data["top"][i],
                data["left"][i] + data["width"][i],
                data["top"][i] + data["height"][i]
            )
    
    # Strategy 2: Check consecutive word groups (up to 8 words)
    for i in range(n - 1):
        phrase_parts = []
        start_i = i
        for j in range(i, min(i + 8, n)):
            if data["text"][j] and data["text"][j].strip():
                phrase_parts.append(data["text"][j].strip())
            phrase = " ".join(phrase_parts)
            score = similar(search_text, phrase)
            if score > best_score:
                best_score = score
                # Combined bbox
                xs = [data["left"][k] for k in range(start_i, j + 1) if data["text"][k] and data["text"][k].strip()]
                ys = [data["top"][k] for k in range(start_i, j + 1) if data["text"][k] and data["text"][k].strip()]
                xes = [data["left"][k] + data["width"][k] for k in range(start_i, j + 1) if data["text"][k] and data["text"][k].strip()]
                yes = [data["top"][k] + data["height"][k] for k in range(start_i, j + 1) if data["text"][k] and data["text"][k].strip()]
                if xs:
                    best_bbox = (min(xs), min(ys), max(xes), max(yes))
                    
    # Strategy 3: Fallback substring search
    if fallback and best_score < 0.6:
        for i in range(n):
            t = data["text"][i]
            if t and fallback in t:
                score = 0.8
                if score > best_score:
                    best_score = score
                    best_bbox = (
                        data["left"][i], data["top"][i],
                        data["left"][i] + data["width"][i],
                        data["top"][i] + data["height"][i]
                    )
                # Also expand left to capture surrounding text
                expanded = (
                    max(0, best_bbox[0] - 350),  # expand left for Gujarati characters
                    max(0, best_bbox[1] - 15),
                    best_bbox[2] + 50,
                    best_bbox[3] + 15,
                )
                best_bbox = expanded
                print(f"      Fallback match: '{t}' → expanded bbox to {expanded}")
    
    return (best_bbox, best_score) if best_bbox and best_score > 0.5 else None


# ─── MAIN ────────────────────────────────────────────────────────────────────

print("=" * 60)
print("PDF EDIT PIPELINE v2 - Page Specific")
print("=" * 60)

doc = fitz.open(INPUT_PDF)
print(f"Input: {INPUT_PDF}")
print(f"Output: {OUTPUT_PDF}")
print(f"Pages: {len(doc)}")
print()

# Render all pages first
page_images = []
for pn in range(len(doc)):
    pix = doc[pn].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    page_images.append(img)
    print(f"Rendered page {pn + 1}: {img.width}x{img.height}px")

# Process replacements
modified_pages = set()

for search_text, replace_text, target_page, fallback, expand_left in REPLACEMENTS:
    page_idx = target_page - 1  # 0-indexed
    img = page_images[page_idx]
    print(f"\n{'─' * 50}")
    print(f"Target: Page {target_page} → '{search_text}'")
    
    result = scan_page_ocr(img, search_text, target_page, fallback)
    
    if result:
        bbox, confidence = result
        print(f"  Match found (confidence: {confidence:.2f})")
        print(f"  BBox: {bbox}")
        
        # Expand bbox to the left if needed (for Gujarati text that OCR didn't capture)
        if expand_left > 0:
            bbox = (max(0, bbox[0] - expand_left), bbox[1], bbox[2] + 50, bbox[3])
            print(f"  Expanded left by {expand_left}px: {bbox}")
        
        draw_replacement(img, bbox, replace_text)
        modified_pages.add(page_idx)
    else:
        print(f"  ❌ No match found on page {target_page}")

# Save as PDF
print(f"\n{'=' * 50}")
print(f"Modified pages: {[p + 1 for p in modified_pages]}")
print("Saving PDF...")

if modified_pages:
    rgb_images = [img if img.mode == "RGB" else img.convert("RGB") for img in page_images]
    pdf_bytes = io.BytesIO()
    rgb_images[0].save(
        pdf_bytes, format="PDF", save_all=True,
        append_images=rgb_images[1:] if len(rgb_images) > 1 else [],
        resolution=DPI,  # DPI for the output PDF
    )
    with open(OUTPUT_PDF, "wb") as f:
        f.write(pdf_bytes.getvalue())
    print(f"✅ Saved: {OUTPUT_PDF}")
else:
    print("No changes made.")

print("\nDone!")
