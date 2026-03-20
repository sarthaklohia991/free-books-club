"""
Motivation Post Automation
- Generates unique quote via Gemini AI (never repeats)
- Picks next style from 50 rotating styles
- Renders beautiful image with Pillow
- Posts to Facebook Page with unique caption
"""

import os
import json
import random
import requests
import textwrap
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime
import google.generativeai as genai

# ── Config ─────────────────────────────────────────────────────────────────
FB_TOKEN   = os.environ["FB_PAGE_ACCESS_TOKEN"]
FB_PAGE_ID = os.environ["FB_PAGE_ID"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

IMG_SIZE   = 1080          # Square post
FONT_DIR   = "/tmp/fonts"
TRACK_FILE = "used_quotes.json"
STYLE_FILE = "style_counter.json"

# ── Load trackers ──────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

used_quotes  = load_json(TRACK_FILE, [])
style_data   = load_json(STYLE_FILE, {"last": 0})
current_style = (style_data["last"] % 50) + 1   # cycles 1→50→1

# ── Generate Quote + Caption via Gemini ───────────────────────────────────
def generate_content(used: list):
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    used_str = "\n".join(f"- {q}" for q in used[-80:]) if used else "None yet"

    prompt = f"""You are a copywriter for a premium motivation Facebook page.

Generate ONE original motivational quote and ONE Facebook caption.

Rules for the QUOTE:
- 10 to 20 words only
- Must be original, NOT a famous existing quote
- Themes: success, belief, resilience, hard work, mindset, vision, consistency
- Do NOT repeat or paraphrase these already used quotes:
{used_str}
- Mark exactly ONE short phrase (2-4 words) with asterisks like *this phrase* — this will be gold-highlighted
- End with a powerful short sentence after a pipe | symbol (this becomes bold)
- Example format: Greatness finds those who are *stubborn enough* to keep going|even on the hardest days.

Rules for the CAPTION:
- 2-3 sentences, conversational, emotional
- Include a call to action (like, share, tag someone)
- End with 6-8 relevant hashtags on a new line
- Do NOT use the word "hustle" or "grind" more than once

Respond ONLY in this exact JSON format, nothing else:
{{
  "quote": "Your quote here with *highlighted phrase* and|bold ending",
  "caption": "Your Facebook caption here\\n\\n#hashtag1 #hashtag2 #hashtag3"
}}"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    # Clean markdown fences if present
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    return data["quote"], data["caption"]

# ── 50 Style Definitions ───────────────────────────────────────────────────
STYLES = {
    1:  {"name":"Warm Ivory Classic",    "bg":"#f5f0e8","text":"#2a1f0e","hl":"#d4a843","hl_text":"#1a1000","wm":"#9a8870","font":"lora",   "dark":False},
    2:  {"name":"Slate Minimal",         "bg":"#2c2f33","text":"#c8c4bc","hl":"#d4b483","hl_text":"#1a1000","wm":"#555555","font":"josefin","dark":True},
    3:  {"name":"Cream Serif Editorial", "bg":"#ede8df","text":"#1e1810","hl":"#b8922a","hl_text":"#1a1000","wm":"#9a8860","font":"playfair","dark":False,"border":"#c8b898"},
    4:  {"name":"Charcoal Gold Line",    "bg":"#1e1e1e","text":"#cccccc","hl":"#c8a96e","hl_text":"#1a1000","wm":"#444444","font":"cormorant","dark":True,"left_bar":"#c8a96e"},
    5:  {"name":"Dusty Rose Soft",       "bg":"#e8ddd8","text":"#2e1e1a","hl":"#b87a6a","hl_text":"#1a0a08","wm":"#a08880","font":"spectral","dark":False},
    6:  {"name":"Forest Deep",           "bg":"#1a2018","text":"#b8c4b0","hl":"#8ab870","hl_text":"#0a1e08","wm":"#3a4a38","font":"garamond","dark":True},
    7:  {"name":"Aged Parchment",        "bg":"#d8cdb8","text":"#2a2010","hl":"#b48020","hl_text":"#1a1000","wm":"#7a6a50","font":"lora",   "dark":False,"lines":True},
    8:  {"name":"Midnight Navy",         "bg":"#111825","text":"#a8b4c8","hl":"#c8b87a","hl_text":"#1a1400","wm":"#2a3448","font":"raleway","dark":True},
    9:  {"name":"Stone Brutalist",       "bg":"#c8c4bc","text":"#1a1a1a","hl":"#555550","hl_text":"#f0f0f0","wm":"#5a5a5a","font":"josefin","dark":False},
    10: {"name":"Warm Black Luxury",     "bg":"#0e0c09","text":"#a09070","hl":"#c8a96e","hl_text":"#0a0800","wm":"#3a3020","font":"cinzel", "dark":True},
    11: {"name":"Soft Sage",             "bg":"#dce4d8","text":"#1e2a1a","hl":"#4a7a3a","hl_text":"#0e2008","wm":"#8a9e84","font":"lora",   "dark":False},
    12: {"name":"Warm Taupe Lines",      "bg":"#e0d8cc","text":"#1e1810","hl":"#8a6a30","hl_text":"#1a0800","wm":"#8a7860","font":"cormorant","dark":False},
    13: {"name":"Obsidian White",        "bg":"#0a0a0a","text":"#d8d8d8","hl":"#888880","hl_text":"#f0f0f0","wm":"#333333","font":"josefin","dark":True},
    14: {"name":"Terracotta Warm",       "bg":"#c8895a","text":"#1e0e06","hl":"#ffffff","hl_text":"#1a0800","wm":"#3e1e0a","font":"playfair","dark":False},
    15: {"name":"Linen Double Border",   "bg":"#f0ebe0","text":"#1a1408","hl":"#7a5a20","hl_text":"#1a0c00","wm":"#8a7860","font":"garamond","dark":False,"border":"#c8b898","border2":True},
    16: {"name":"Cool Fog",              "bg":"#d4d8dc","text":"#1e2228","hl":"#3a5a7a","hl_text":"#e8f0f8","wm":"#8898a8","font":"spectral","dark":False},
    17: {"name":"Dark Sepia",            "bg":"#1a1208","text":"#c8b888","hl":"#e8c870","hl_text":"#0a0800","wm":"#4a3818","font":"lora",   "dark":True},
    18: {"name":"Ash Minimal",           "bg":"#e8e8e4","text":"#282828","hl":"#888888","hl_text":"#f0f0f0","wm":"#aaaaaa","font":"josefin","dark":False},
    19: {"name":"Burgundy Depth",        "bg":"#1e0e10","text":"#c8b0a8","hl":"#d4847a","hl_text":"#0e0000","wm":"#3a2020","font":"lora",   "dark":True},
    20: {"name":"Sand Dune",             "bg":"#ddd0b8","text":"#1e1808","hl":"#6a4a10","hl_text":"#f0e8d8","wm":"#8a7a5a","font":"playfair","dark":False},
    21: {"name":"Ink Blue",              "bg":"#18202e","text":"#a8b8cc","hl":"#c8d890","hl_text":"#0a1800","wm":"#2a3448","font":"lora",   "dark":True},
    22: {"name":"Cream Corner Accent",   "bg":"#f2ece0","text":"#1a140a","hl":"#8a6020","hl_text":"#f0e8d0","wm":"#9a8868","font":"playfair","dark":False,"corners":"#b09060"},
    23: {"name":"Charcoal Soft",         "bg":"#343434","text":"#c4c0b8","hl":"#c8a060","hl_text":"#0a0800","wm":"#555555","font":"lora",   "dark":True},
    24: {"name":"Warm White Luxury",     "bg":"#faf7f2","text":"#1e1a12","hl":"#8a6820","hl_text":"#f0e8d8","wm":"#b8a880","font":"cinzel", "dark":False},
    25: {"name":"Midnight Copper",       "bg":"#0c0c0e","text":"#a09080","hl":"#b08040","hl_text":"#0a0600","wm":"#2a2820","font":"cormorant","dark":True},
    26: {"name":"Warm Grey Typewriter",  "bg":"#e4e0d8","text":"#222222","hl":"#c8c090","hl_text":"#1a1800","wm":"#888888","font":"lora",   "dark":False,"lines":True},
    27: {"name":"Olive Muted",           "bg":"#c8c4a8","text":"#1a1c10","hl":"#3a3e10","hl_text":"#f0f0d8","wm":"#6a6a4a","font":"spectral","dark":False},
    28: {"name":"Dark Teal",             "bg":"#0e1e1c","text":"#8ab8b0","hl":"#a8e8d8","hl_text":"#0a1810","wm":"#1e3a38","font":"garamond","dark":True},
    29: {"name":"Blush Minimal",         "bg":"#e8ddd8","text":"#2a1c18","hl":"#6a3028","hl_text":"#f0e8e4","wm":"#b09088","font":"josefin","dark":False},
    30: {"name":"Gunmetal Clean",        "bg":"#1c2028","text":"#a8aab0","hl":"#c8c0a0","hl_text":"#0c1018","wm":"#2a2e38","font":"raleway","dark":True},
    31: {"name":"Warm Cream Blocked",    "bg":"#1e1810","text":"#d8d0c0","hl":"#c8a96e","hl_text":"#0a0800","wm":"#8a7860","font":"playfair","dark":True,"split_bg":"#ede6d8"},
    32: {"name":"Silver Foil",           "bg":"#d0d0cc","text":"#1a1a18","hl":"#5a5a50","hl_text":"#f0f0f0","wm":"#888882","font":"cinzel", "dark":False},
    33: {"name":"Amber Dusk",            "bg":"#1a1208","text":"#b8a880","hl":"#e8b830","hl_text":"#0a0800","wm":"#3a2e10","font":"playfair","dark":True},
    34: {"name":"Concrete Raw",          "bg":"#b8b4ae","text":"#0e0e0c","hl":"#0e0e0c","hl_text":"#f0f0f0","wm":"#5a5a58","font":"josefin","dark":False},
    35: {"name":"Champagne Serif",       "bg":"#e8e0cc","text":"#1a1608","hl":"#7a6020","hl_text":"#f0e8d8","wm":"#9a9070","font":"lora",   "dark":False},
    36: {"name":"Night Ink",             "bg":"#08080e","text":"#9898b0","hl":"#b0a8d0","hl_text":"#08080a","wm":"#1e1e30","font":"spectral","dark":True},
    37: {"name":"Clay Brown",            "bg":"#c0a888","text":"#1a0e04","hl":"#0a0400","hl_text":"#f0e8d8","wm":"#3a1e08","font":"lora",   "dark":False},
    38: {"name":"Arctic White",          "bg":"#f4f6f8","text":"#1e2430","hl":"#3a6888","hl_text":"#f0f8ff","wm":"#b0b8c4","font":"raleway","dark":False},
    39: {"name":"Mocha Warm",            "bg":"#2a1c14","text":"#b8a090","hl":"#d0a868","hl_text":"#0a0800","wm":"#4a3020","font":"lora",   "dark":True},
    40: {"name":"Powder Blue Soft",      "bg":"#d8e0e8","text":"#1a2030","hl":"#284860","hl_text":"#e8f0ff","wm":"#90a0b0","font":"cormorant","dark":False},
    41: {"name":"Bone Diagonal",         "bg":"#e8e2d8","text":"#1a1610","hl":"#6a4a18","hl_text":"#f0e8d8","wm":"#9a9080","font":"garamond","dark":False},
    42: {"name":"Storm Grey",            "bg":"#3a3e44","text":"#b8bcc4","hl":"#d8c8a0","hl_text":"#0a0800","wm":"#555555","font":"lora",   "dark":True},
    43: {"name":"Old Gold",              "bg":"#c8a83a","text":"#1a1200","hl":"#0a0800","hl_text":"#f0e8a0","wm":"#3a2800","font":"playfair","dark":False},
    44: {"name":"Warm White Stamp",      "bg":"#f5f2ec","text":"#1a1810","hl":"#1a1810","hl_text":"#f5f2ec","wm":"#9a9880","font":"josefin","dark":False,"stamp_border":"#1a1810"},
    45: {"name":"Dusk Purple-Grey",      "bg":"#1e1c28","text":"#a098b8","hl":"#c8b8e0","hl_text":"#0a0818","wm":"#2e2c40","font":"lora",   "dark":True},
    46: {"name":"Warm Rust",             "bg":"#1c0e08","text":"#c0a090","hl":"#d87850","hl_text":"#0a0400","wm":"#3a1e14","font":"playfair","dark":True,"left_bar":"#8a3a20"},
    47: {"name":"Mist Linen",            "bg":"#dcdcd4","text":"#1e2018","hl":"#383c28","hl_text":"#f0f0e8","wm":"#9a9a90","font":"josefin","dark":False},
    48: {"name":"Deep Walnut",           "bg":"#140e08","text":"#9a8870","hl":"#c0a050","hl_text":"#0a0600","wm":"#2a2010","font":"lora",   "dark":True},
    49: {"name":"Stone Serif",           "bg":"#c4beb4","text":"#1a1810","hl":"#ffffff","hl_text":"#1a1810","wm":"#6a6860","font":"lora",   "dark":False},
    50: {"name":"Ivory & Ash Split",     "bg":"#e8e4dc","text":"#1a1810","hl":"#c8a96e","hl_text":"#0a0800","wm":"#9a9880","font":"playfair","dark":False,"split":"#1e1c18"},
}

# ── Font loader ────────────────────────────────────────────────────────────
def get_font(font_key, size):
    font_map = {
        "lora":      ["Lora.ttf",          "DejaVuSerif.ttf"],
        "playfair":  ["PlayfairDisplay.ttf","DejaVuSerif.ttf"],
        "josefin":   ["JosefinSans.ttf",    "DejaVuSans.ttf"],
        "cormorant": ["Cormorant.ttf",      "DejaVuSerif.ttf"],
        "spectral":  ["Spectral.ttf",       "DejaVuSerif.ttf"],
        "garamond":  ["EBGaramond.ttf",     "DejaVuSerif.ttf"],
        "raleway":   ["JosefinSans.ttf",    "DejaVuSans.ttf"],
        "cinzel":    ["PlayfairDisplay.ttf","DejaVuSerif.ttf"],
    }
    for fname in font_map.get(font_key, ["DejaVuSerif.ttf"]):
        for d in [FONT_DIR, "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"]:
            try:
                return ImageFont.truetype(os.path.join(d, fname), size)
            except:
                pass
    return ImageFont.load_default()

# ── Hex to RGB ─────────────────────────────────────────────────────────────
def hex_rgb(h, alpha=255):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return (r,g,b,alpha)

def hex_rgb3(h):
    r,g,b,_ = hex_rgb(h)
    return (r,g,b)

# ── Parse quote ────────────────────────────────────────────────────────────
def parse_quote(raw):
    """Returns (before_hl, hl_phrase, after_hl, bold_ending)"""
    parts = raw.split("|")
    main = parts[0].strip()
    bold = parts[1].strip() if len(parts) > 1 else ""
    import re
    m = re.search(r'\*([^*]+)\*', main)
    if m:
        before = main[:m.start()]
        hl     = m.group(1)
        after  = main[m.end():]
    else:
        before, hl, after = main, "", ""
    return before, hl, after, bold

# ── Draw text with inline highlight ───────────────────────────────────────
def draw_wrapped_quote(draw, img, style, quote_raw, handle, x, y, max_w):
    s = style
    font_key = s["font"]
    text_col  = hex_rgb3(s["text"])
    hl_col    = hex_rgb3(s["hl"])
    hl_text   = hex_rgb3(s["hl_text"])
    wm_col    = hex_rgb3(s["wm"])

    before, hl_phrase, after, bold = parse_quote(quote_raw)
    full_plain = before + hl_phrase + after

    # Determine font sizes
    body_size = 52
    bold_size = 58
    wm_size   = 28

    body_font = get_font(font_key, body_size)
    bold_font = get_font(font_key, bold_size)
    wm_font   = get_font(font_key, wm_size)

    # Wrap plain text to find line count
    avg_char_w = body_size * 0.55
    chars_per_line = max(10, int(max_w / avg_char_w))
    lines = textwrap.wrap(full_plain, width=chars_per_line)

    # Reconstruct lines with highlight awareness
    line_height = int(body_size * 1.72)
    cy = y

    # Simple approach: render word by word, track highlight words
    hl_words = set(hl_phrase.lower().split()) if hl_phrase else set()

    for line in lines:
        words = line.split()
        cx = x
        for word in words:
            clean_word = word.strip(".,!?;:'\"")
            use_hl = clean_word.lower() in hl_words and hl_phrase

            try:
                bbox = draw.textbbox((0,0), word + " ", font=body_font)
                word_w = bbox[2] - bbox[0]
                word_h = bbox[3] - bbox[1]
            except:
                word_w = body_size * len(word) * 0.55
                word_h = body_size

            if use_hl:
                pad = 6
                draw.rectangle([cx-pad, cy+int(word_h*0.52), cx+word_w+pad, cy+word_h+4],
                                fill=hl_col)
                draw.text((cx, cy), word + " ", font=body_font, fill=hl_text)
            else:
                draw.text((cx, cy), word + " ", font=body_font, fill=text_col)
            cx += word_w

        cy += line_height

    # Bold ending
    if bold:
        cy += 6
        bold_lines = textwrap.wrap(bold, width=int(chars_per_line * 0.9))
        bold_col = hex_rgb3(s.get("bold_col", s["text"]))
        # Make bold slightly lighter/darker for dark/light
        for bl in bold_lines:
            draw.text((x, cy), bl, font=bold_font, fill=bold_col)
            try:
                bh = draw.textbbox((0,0), bl, font=bold_font)[3]
            except:
                bh = bold_size
            cy += int(bh * 1.5)

    # Watermark
    cy += 20
    draw.text((x, cy), handle, font=wm_font, fill=wm_col)

# ── Add paper-like noise ───────────────────────────────────────────────────
def add_texture(img, intensity=18):
    import random as rnd
    pixels = img.load()
    w, h = img.size
    for _ in range(w * h // 6):
        px = rnd.randint(0, w-1)
        py = rnd.randint(0, h-1)
        noise = rnd.randint(-intensity, intensity)
        r,g,b = pixels[px,py][:3]
        pixels[px,py] = (
            max(0,min(255,r+noise)),
            max(0,min(255,g+noise)),
            max(0,min(255,b+noise))
        )
    return img

# ── Render image ───────────────────────────────────────────────────────────
def render_image(style_id, quote_raw, handle="@billion.dollars.motivation"):
    s = STYLES[style_id]
    size = IMG_SIZE

    img = Image.new("RGB", (size, size), hex_rgb3(s["bg"]))
    draw = ImageDraw.Draw(img)

    pad = 90   # inner padding
    text_x = pad
    text_y = int(size * 0.25)
    max_w  = size - pad * 2

    # ── Style-specific decorations ─────────────────────────────────────────
    # Left bar (styles 4, 46)
    if s.get("left_bar"):
        bar_col = hex_rgb3(s["left_bar"])
        draw.rectangle([0, 60, 8, size-60], fill=bar_col)
        text_x = pad + 20

    # Single border (styles 3, 15)
    if s.get("border") and not s.get("border2"):
        bc = hex_rgb3(s["border"])
        bw = 24
        draw.rectangle([bw, bw, size-bw, size-bw], outline=bc, width=2)
        text_x  = pad + 10
        text_y  = int(size * 0.28)

    # Double border (style 15)
    if s.get("border2"):
        bc = hex_rgb3(s["border"])
        draw.rectangle([22, 22, size-22, size-22], outline=bc, width=2)
        draw.rectangle([34, 34, size-34, size-34], outline=bc, width=2)
        text_x = pad + 14
        text_y = int(size * 0.28)

    # Corner accents (style 22)
    if s.get("corners"):
        cc = hex_rgb3(s["corners"])
        cw, cs = 3, 70
        # Top-left
        draw.rectangle([28, 28, 28+cs, 28+cw], fill=cc)
        draw.rectangle([28, 28, 28+cw, 28+cs], fill=cc)
        # Bottom-right
        draw.rectangle([size-28-cs, size-28-cw, size-28, size-28], fill=cc)
        draw.rectangle([size-28-cw, size-28-cs, size-28, size-28], fill=cc)

    # Stamp border (style 44)
    if s.get("stamp_border"):
        sc = hex_rgb3(s["stamp_border"])
        draw.rectangle([52, 52, size-52, size-52], outline=sc, width=5)
        text_x = pad + 20
        text_y = int(size * 0.28)

    # Horizontal ruled lines (styles 7, 26)
    if s.get("lines"):
        line_col = (*hex_rgb3(s["text"]), 18)
        line_img = Image.new("RGBA", (size, size), (0,0,0,0))
        ld = ImageDraw.Draw(line_img)
        for ly in range(0, size, 38):
            ld.line([(0,ly),(size,ly)], fill=line_col, width=1)
        img = Image.alpha_composite(img.convert("RGBA"), line_img).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Split bg (style 31, 50)
    if s.get("split"):
        sc = hex_rgb3(s["split"])
        draw.rectangle([0, 0, size//2, size], fill=sc)
    if s.get("split_bg"):
        sb = hex_rgb3(s["split_bg"])
        draw.rectangle([0, int(size*0.65), size, size], fill=sb)

    # ── Texture ─────────────────────────────────────────────────────────────
    img = add_texture(img, intensity=12)
    draw = ImageDraw.Draw(img)

    # ── Text ────────────────────────────────────────────────────────────────
    draw_wrapped_quote(draw, img, s, quote_raw, handle, text_x, text_y, max_w)

    return img

# ── Post to Facebook ───────────────────────────────────────────────────────
def post_to_facebook(image_path, caption):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(url, data={
            "caption": caption,
            "access_token": FB_TOKEN,
        }, files={"source": f})
    resp.raise_for_status()
    data = resp.json()
    print(f"✅ Posted! Post ID: {data.get('post_id', data.get('id'))}")
    return data

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print(f"🎨 Using style #{current_style}: {STYLES[current_style]['name']}")

    # Generate quote + caption
    print("🤖 Generating quote via Gemini...")
    quote, caption = generate_content(used_quotes)
    print(f"📝 Quote: {quote}")
    print(f"💬 Caption: {caption[:80]}...")

    # Render image
    print("🖼 Rendering image...")
    img = render_image(current_style, quote)
    img_path = "/tmp/motivation_post.jpg"
    img.save(img_path, "JPEG", quality=95)
    print(f"💾 Saved to {img_path}")

    # Post to Facebook
    print("📤 Posting to Facebook...")
    post_to_facebook(img_path, caption)

    # Update trackers
    used_quotes.append(quote.replace("*","").replace("|"," "))
    # Keep last 200 quotes in memory
    if len(used_quotes) > 200:
        used_quotes.pop(0)

    save_json(TRACK_FILE, used_quotes)
    save_json(STYLE_FILE, {"last": current_style})
    print(f"✅ Done! Next post will use style #{(current_style % 50) + 1}")

if __name__ == "__main__":
    main()
