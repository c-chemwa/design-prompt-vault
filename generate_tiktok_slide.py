import json
import os
from PIL import Image, ImageDraw, ImageFont

DATA_FILE = "data.json"
OUTPUT_DIR = "tiktok_slides"

def create_slide_for_latest_item():
    if not os.path.exists(DATA_FILE):
        print("data.json not found.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        print("No items found in data.json")
        return

    # Grab the newest item
    item = items[0]
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1080x1920 vertical TikTok dimensions
    img_width, img_height = 1080, 1920
    img = Image.new("RGB", (img_width, img_height), color="#0D0D0D")
    draw = ImageDraw.Draw(img)

    # Load system fonts (fallback to default if custom ttf not present)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_mono = ImageFont.load_default()

    # Draw Neo-Brutalist Outer Border & Header Badge
    draw.rectangle([60, 60, img_width - 60, img_height - 60], outline="#2A2A2A", width=4)
    
    # Category Badge
    draw.rectangle([100, 120, 450, 190], fill="#1F1F1F", outline="#CCFF00", width=2)
    draw.text((120, 135), f"// {item.get('category', 'DESIGN SYSTEM').upper()}", fill="#CCFF00", font=font_mono)

    # Title
    title_text = item.get('title', 'Untitled System')
    # Simple multi-line text wrapper for title
    y_text = 240
    words = title_text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if draw.textlength(test_line, font=font_title) > 850:
            draw.text((100, y_text), line, fill="#F4F0EA", font=font_title)
            y_text += 80
            line = word + " "
        else:
            line = test_line
    draw.text((100, y_text), line, fill="#F4F0EA", font=font_title)

    # Trend Signal Teardown Box
    y_text += 120
    draw.rectangle([100, y_text, img_width - 100, y_text + 350], fill="#161616", outline="#2A2A2A", width=2)
    draw.text((140, y_text + 30), "INSIGHT & CONVERSION SIGNAL:", fill="#CCFF00", font=font_mono)
    
    signal_text = item.get('trend_signal', '')
    s_words = signal_text.split()
    s_line = ""
    s_y = y_text + 90
    for word in s_words:
        test_line = s_line + word + " "
        if draw.textlength(test_line, font=font_body) > 780:
            draw.text((140, s_y), s_line, fill="#D4D0C8", font=font_body)
            s_y += 50
            s_line = word + " "
        else:
            s_line = test_line
    draw.text((140, s_y), s_line, fill="#D4D0C8", font=font_body)

    # Typography Pairing
    y_text += 420
    draw.text((100, y_text), "TYPOGRAPHY SPEC:", fill="#888888", font=font_mono)
    y_text += 50
    draw.text((100, y_text), item.get('typography_pairing', 'Standard Pair'), fill="#CCFF00", font=font_mono)

    # Color Swatches Preview
    y_text += 100
    draw.text((100, y_text), "SYSTEM COLOR TOKENS:", fill="#888888", font=font_mono)
    y_text += 50
    
    palette = item.get('color_palette', ['#0D0D0D', '#F4F0EA', '#CCFF00', '#FF3366'])
    box_x = 100
    for hex_code in palette:
        draw.rectangle([box_x, y_text, box_x + 180, y_text + 90], fill=hex_code, outline="#FFFFFF", width=2)
        box_x += 210

    # Footer CTA
    footer_y = img_height - 200
    draw.rectangle([100, footer_y, img_width - 100, footer_y + 100], fill="#CCFF00")
    draw.text((140, footer_y + 30), "UNLOCK FULL VAULT → c-chemwa.github.io/design-prompt-vault", fill="#0D0D0D", font=font_mono)

    filename = os.path.join(OUTPUT_DIR, f"tiktok_{item.get('id', 'latest')}.png")
    img.save(filename)
    print(f"Generated TikTok slide: {filename}")

if __name__ == "__main__":
    create_slide_for_latest_item()
