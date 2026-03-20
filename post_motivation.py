"""
Motivation Post Automation - No AI needed
- 240 built-in quotes (8/day x 30 days = 1 month, then repeats)
- 50 rotating visual styles
- Posts to Facebook automatically
"""

import os, json, re, textwrap, requests
from PIL import Image, ImageDraw, ImageFont

# ── Config ─────────────────────────────────────────────────────────────────
FB_TOKEN   = os.environ["FB_PAGE_ACCESS_TOKEN"]
FB_PAGE_ID = os.environ["FB_PAGE_ID"]
FONT_DIR   = "/tmp/fonts"
TRACK_FILE = "used_quotes.json"
STYLE_FILE = "style_counter.json"
IMG_SIZE   = 1080

# ── 240 Quotes (repeats monthly) ───────────────────────────────────────────
QUOTES = [
    # Belief
    "You were *built* for this|the storm was never bigger than you.",
    "Believe so deeply that *doubt* has no room|to breathe inside you.",
    "The mind that believes it *can* will always|outrun the one that doubts.",
    "You are not behind.|You are *exactly* where your growth needs you.",
    "Faith in yourself is the *first* step|every great story starts there.",
    "Your belief is the *seed*|everything else is just water and time.",
    "Doubt kills more dreams than *failure* ever will|choose belief instead.",
    "The moment you *believe* it is possible|the path begins to appear.",
    "You have always been *stronger* than the story|you told yourself.",
    "Trust the version of you *working in silence|their time is coming.",
    # Resilience
    "Every setback is secretly a *setup|for something far greater ahead.",
    "You did not come this far *only* to come this far|keep moving.",
    "Scars are just proof that *healing* happened|wear them with pride.",
    "The comeback is always *louder* than the setback|stay in the fight.",
    "Bend but never *break|you are more durable than you know.",
    "Fall seven times *rise* eight|that is the only math that matters.",
    "Hard seasons *grow* the strongest people|you are being grown right now.",
    "What tried to *break* you only made you unbreakable|remember that.",
    "Pain is temporary.|Glory belongs to those who *refused* to quit.",
    "You survived every *hard day* so far|your record is still perfect.",
    # Success
    "Success is just *discipline* repeated|until the world notices.",
    "The gap between where you are and *where you want* to be is action.",
    "Small steps *every day* build the mountains|others marvel at tomorrow.",
    "Greatness is not a *gift|it is a choice made daily.",
    "Your future self is *cheering* for the decision you make right now.",
    "Success does not come *dressed in comfort|it arrives with effort.",
    "The ones who *win* are the ones who refused to stop trying.",
    "Every expert was once a *beginner* who chose not to give up.",
    "Outwork your *excuses* and you will outgrow your limitations.",
    "Results come to those who *show up* even when they do not feel like it.",
    # Mindset
    "Your mindset is the *lens|change it and the whole world shifts.",
    "Think *bigger* than your fears and smaller than your potential.",
    "The right *mindset* turns every obstacle into an opportunity.",
    "You attract what you *repeatedly think|choose your thoughts wisely.",
    "A disciplined *mind* is the most powerful tool you will ever own.",
    "Change your inner *dialogue* and watch your outer world transform.",
    "What you *focus on* grows|point your attention at what matters.",
    "Your thoughts are *seeds|plant only what you want to harvest.",
    "A *growth mindset* sees every failure as a lesson waiting to be learned.",
    "The strongest force in the world is a *made-up mind.",
    # Hard Work
    "Nobody remembers the *easy days|they remember who showed up anyway.",
    "Hard work *compounds|the longer you stay in the game the bigger the return.",
    "Talent is common.|*Relentless effort* is what sets legends apart.",
    "The grind you *hate* today is the story you will love tomorrow.",
    "Work in silence.|Let *results* do all the talking for you.",
    "Put in the *reps* no one sees and earn the results everyone wants.",
    "Ordinary effort produces *ordinary results|be extraordinary instead.",
    "The hours you invest when *no one is watching* define who you become.",
    "Outworking your *past self* is the only competition that truly matters.",
    "Great things are built *brick by brick|not in a single day.",
    # Purpose
    "Live with *intention* and every day becomes a step toward greatness.",
    "Your *purpose* is bigger than your fear|let it pull you forward.",
    "A life with *meaning* is built on decisions, not on circumstances.",
    "Know your *why* and the how will always find a way to appear.",
    "You are not here *by accident|own your presence and your purpose.",
    "The world needs *exactly* what only you can offer|do not hold back.",
    "Chase purpose *not* applause|the right people will always notice.",
    "When you are *aligned* with your purpose nothing can stop your progress.",
    "Your gifts were not given *to be hidden|share them with the world.",
    "A clear *purpose* makes every sacrifice feel like an investment.",
    # Action
    "Stop *waiting* for the perfect moment|this moment is perfect enough.",
    "Ideas without *action* are just wishes|move before you feel ready.",
    "The first step is *always* the hardest and always the most important.",
    "Progress over *perfection|done is always better than perfect.",
    "Start *now* with what you have|improve as you go.",
    "Every great journey *begins* with a single decision to move.",
    "Action is the *antidote* to fear|start and the courage follows.",
    "You cannot *steer* a parked car|start moving in any direction.",
    "Done is *infinitely* better than perfect and never started.",
    "The universe *rewards* motion|get up and go after what you want.",
    # Growth
    "Growth is *uncomfortable* and absolutely worth every moment of discomfort.",
    "You are not the *same* person you were a year ago|celebrate that.",
    "Every day is a *chance* to be slightly better than yesterday.",
    "Embrace the *struggle|it is shaping you into who you need to be.",
    "Comfort zones are *beautiful* places where nothing ever grows.",
    "The version of you *six months* from now will thank today's effort.",
    "Growth requires you to *outgrow* the old version of yourself first.",
    "Every challenge is *disguised* as an invitation to level up.",
    "You grow the most *in the moments* that stretch you the furthest.",
    "Invest in your *growth* daily and compound interest will amaze you.",
    # Consistency
    "Consistency is the *superpower* most people are too impatient to develop.",
    "Show up *every single day|that is the whole secret.",
    "It is not what you do *once* that defines you|it is what you repeat.",
    "Champions are made *in the moments* no one else bothers to show up.",
    "One percent *better* every day is three hundred sixty five percent a year.",
    "The secret to *momentum* is never letting two bad days happen in a row.",
    "Discipline is just *consistency* with a commitment attached to it.",
    "Your habits are *quietly* building or destroying your future right now.",
    "Stay *consistent* even when the results are not visible yet.",
    "The compound effect of *daily effort* is the most underrated force alive.",
    # Courage
    "Courage is not the *absence* of fear|it is moving forward despite it.",
    "Be *brave enough* to start the conversation only you can have.",
    "The biggest risk is *never taking* one|play bold or play small forever.",
    "Fortune *favors* the bold and the consistent and the resilient.",
    "Step outside your *comfort zone* daily|that is where life expands.",
    "Say yes *before* you feel ready|growth lives on the other side.",
    "Be the person *brave enough* to begin what others only dream about.",
    "Courage is a *muscle|train it daily and it will never fail you.",
    "The world *opens up* for those willing to ask for what they want.",
    "Do the *scary thing first* and the rest of the day becomes easy.",
    # Patience
    "Good things *take time|great things take even longer|stay patient.",
    "Trust the *process* even when the results are not visible yet.",
    "Patience is not *waiting|it is working calmly toward what you want.",
    "Everything that *matters* took longer than expected|do not give up.",
    "Slow progress is *still* progress|do not confuse pace with direction.",
    "The tree that *grows slowly* roots deeply|so do you.",
    "What is meant *for you* will not pass you if you keep showing up.",
    "Timing is *everything|trust that yours is being prepared right now.",
    "You are planting *seeds* today that your future self will harvest.",
    "Patience plus *persistence* is the formula no one talks about enough.",
    # Attitude
    "Your *attitude* is the one thing no circumstance can take from you.",
    "Choose *gratitude* daily and watch your whole world begin to shift.",
    "A positive *attitude* does not fix everything but it starts everything.",
    "Energy is *contagious|make sure yours is worth catching today.",
    "Smile at *hard times|you have outlasted every single one before.",
    "The way you *see* a problem is already half of the solution.",
    "Attitude is the *paintbrush* with which you color your entire day.",
    "Show up with *enthusiasm* and people will follow you anywhere.",
    "Your *response* to life is always more powerful than any circumstance.",
    "Choose *joy* not because life is easy but because you deserve it.",
    # Wisdom
    "Learn from *yesterday|live for today|build for tomorrow.",
    "The wisest people are the ones who *never stopped being students.",
    "Knowledge is *power|applied knowledge is transformation.",
    "Surround yourself with *people* who make you better and expect the same.",
    "Speak less.|*Listen more|the wisdom is always in the silence.",
    "The best *investment* you will ever make is in your own mind.",
    "Teach what you know and *learn* what you do not|never stop both.",
    "Time is the *only currency* you can never earn back|spend it wisely.",
    "Your *network* is your net worth|invest in relationships that matter.",
    "Wisdom is knowing *what to ignore* and what to pursue with everything.",
    # Vision
    "See it *clearly* before it exists and then do the work to make it real.",
    "Your *vision* should scare you a little|that means it is big enough.",
    "The people who *change the world* saw it differently before anyone else.",
    "Dream with your *eyes open* and your hands moving toward it daily.",
    "A powerful *vision* acts like a magnet|it pulls your future toward you.",
    "Write down your *vision* make it plain and then run toward it daily.",
    "You become what you *consistently* visualize|see the best version.",
    "The clearer your *picture* of success the faster your path to it.",
    "Vision without *execution* is just a dream|pair them together always.",
    "See yourself *already there* and let that image guide every decision.",
    # Leadership
    "Leaders *lead* themselves first before they can lead anyone else.",
    "The best leaders *lift others* as they climb|make room at the top.",
    "Lead with *integrity* and people will follow you through anything.",
    "Influence is *earned* through consistency trust and genuine care.",
    "A leader *creates* more leaders|not more followers.",
    "Your *example* is your loudest leadership statement|make it count.",
    "True leaders *serve first* and receive greatness as a result.",
    "Lead with *empathy* and you will build teams that move mountains.",
    "The mark of *great leadership* is what grows after you leave the room.",
    "Be the *leader* you needed when you had no one to look up to.",
    # Self-Worth
    "You are *enough* right now|not when you achieve more.",
    "Stop *shrinking* yourself to fit spaces you have already outgrown.",
    "Know your *worth* and never let anyone negotiate it down.",
    "You do not need *permission* to take up space in your own life.",
    "Respect yourself *enough* to walk away from what no longer serves you.",
    "Your *value* does not decrease based on someone's inability to see it.",
    "You are *worthy* of every good thing you have been dreaming about.",
    "Never *apologize* for how much you want or how high you aim.",
    "You are *not too much|you are exactly enough for the right people.",
    "Own who you *are* unapologetically|that is where confidence begins.",
    # Focus
    "Focus is the *rarest* and most valuable resource you own|guard it.",
    "Where *attention* goes energy flows and results follow.",
    "Cut out the *noise|your best work happens in deep focused silence.",
    "Eliminate the *distractions* that are stealing your destiny daily.",
    "One thing *done well* beats ten things done halfway every single time.",
    "Stay *locked in* on your goal and let the opinions float on by.",
    "The ability to *focus* on one thing longer than most is a superpower.",
    "Protect your *attention* like it is your most valuable asset because it is.",
    "A scattered *mind* produces scattered results|choose one thing today.",
    "Winners *focus* on winning.|Losers focus on winners.",
    # Gratitude
    "Gratitude *transforms* what you have into more than enough.",
    "Start *every day* with thanks and watch the tone of your life change.",
    "Be *grateful* for the struggle|it is proof you are still in the game.",
    "There is *always* something to be grateful for if you look closely.",
    "Appreciation is the *quickest* path from where you are to where you want to be.",
    "Count your *blessings* not your problems and watch the math change.",
    "Grateful *hearts* attract abundant lives|practice it every morning.",
    "Even on *hard days* gratitude is the anchor that keeps you steady.",
    "The more *grateful* you are the more reasons you are given to be grateful.",
    "Thank the *journey|even the detours are teaching you something priceless.",
]

# ── Captions (rotate through 12) ──────────────────────────────────────────
CAPTIONS = [
    "This is your reminder that you are capable of more than you know. 💪\n\nSave this and read it every morning this week.\n\n#motivation #mindset #success #inspiration #growth #believe #dailymotivation #positivity",
    "Someone needed to read this today. Share it with them. ❤️\n\nDrop a 🔥 if this speaks to you!\n\n#motivationalquotes #successmindset #inspiration #growth #believe #hardwork #winning #mindsetmatters",
    "Start your day with this energy and nothing can stop you. ☀️\n\nTag someone who needs this right now!\n\n#morningmotivation #dailyquotes #inspiration #success #hustle #growthmindset #positivevibes #motivation",
    "The words you tell yourself matter more than anything. Read this twice. 👊\n\nSave this post — you will need it on a tough day.\n\n#selfbelief #motivation #inspiration #mindset #success #resilience #growthmindset #dailymotivation",
    "Every great story started with someone who refused to quit. 🌟\n\nDouble tap if you needed this reminder today!\n\n#nevergiveup #motivation #success #inspiration #believe #hardwork #winners #dailymotivation",
    "This one hits different. Read it slowly. 🙏\n\nShare with someone who is going through a hard time right now.\n\n#wisdom #motivation #inspiration #life #mindset #growth #positivity #successquotes",
    "Your future self is counting on the decisions you make today. ⚡\n\nComment YES if you are committed to showing up!\n\n#growthmindset #motivation #success #discipline #hardwork #inspiration #goals #dailymotivation",
    "Bookmark this. Screenshot it. Put it on your wall. 📌\n\nBecause some days you will need this more than you know.\n\n#motivation #inspiration #mindset #success #believe #resilience #positivity #dailyquotes",
    "This is your sign to keep going. Do not stop now. 🚀\n\nTag your accountability partner below!\n\n#keepgoing #motivation #success #inspiration #believe #hardwork #goals #growthmindset",
    "The people who change their lives read things like this and actually apply it. 💯\n\nSave this and share it — someone needs it today.\n\n#motivation #mindset #success #inspiration #discipline #growth #dailymotivation #winning",
    "Quiet reminder: you are stronger than you think you are. 💎\n\nDrop a ❤️ if you believe in your own comeback!\n\n#strength #motivation #inspiration #resilience #believe #success #mindset #positivevibes",
    "The secret? Show up every single day even when it is hard. 🔑\n\nTag someone who inspires you to keep going!\n\n#consistency #motivation #success #hardwork #discipline #inspiration #growthmindset #dailymotivation",
]

# ── 50 Styles ─────────────────────────────────────────────────────────────
STYLES = {
    1:  {"name":"Warm Ivory",       "bg":"#f5f0e8","text":"#2a1f0e","hl":"#d4a843","hl_text":"#1a1000","wm":"#9a8870","font":"lora"},
    2:  {"name":"Midnight Gold",    "bg":"#1a1a2e","text":"#c8c4bc","hl":"#d4b483","hl_text":"#1a1000","wm":"#555555","font":"josefin"},
    3:  {"name":"Cream Editorial",  "bg":"#ede8df","text":"#1e1810","hl":"#b8922a","hl_text":"#1a1000","wm":"#9a8860","font":"playfair"},
    4:  {"name":"Charcoal Gold",    "bg":"#1e1e1e","text":"#cccccc","hl":"#c8a96e","hl_text":"#1a1000","wm":"#444444","font":"lora"},
    5:  {"name":"Dusty Rose",       "bg":"#e8ddd8","text":"#2e1e1a","hl":"#b87a6a","hl_text":"#1a0a08","wm":"#a08880","font":"lora"},
    6:  {"name":"Forest Deep",      "bg":"#1a2018","text":"#b8c4b0","hl":"#8ab870","hl_text":"#0a1e08","wm":"#3a4a38","font":"lora"},
    7:  {"name":"Aged Parchment",   "bg":"#d8cdb8","text":"#2a2010","hl":"#b48020","hl_text":"#1a1000","wm":"#7a6a50","font":"lora"},
    8:  {"name":"Midnight Navy",    "bg":"#111825","text":"#a8b4c8","hl":"#c8b87a","hl_text":"#1a1400","wm":"#2a3448","font":"josefin"},
    9:  {"name":"Stone Minimal",    "bg":"#c8c4bc","text":"#1a1a1a","hl":"#555550","hl_text":"#f0f0f0","wm":"#5a5a5a","font":"josefin"},
    10: {"name":"Warm Black",       "bg":"#0e0c09","text":"#a09070","hl":"#c8a96e","hl_text":"#0a0800","wm":"#3a3020","font":"playfair"},
    11: {"name":"Soft Sage",        "bg":"#dce4d8","text":"#1e2a1a","hl":"#4a7a3a","hl_text":"#0e2008","wm":"#8a9e84","font":"lora"},
    12: {"name":"Warm Taupe",       "bg":"#e0d8cc","text":"#1e1810","hl":"#8a6a30","hl_text":"#1a0800","wm":"#8a7860","font":"lora"},
    13: {"name":"Obsidian White",   "bg":"#0a0a0a","text":"#d8d8d8","hl":"#888880","hl_text":"#f0f0f0","wm":"#333333","font":"josefin"},
    14: {"name":"Terracotta",       "bg":"#c8895a","text":"#1e0e06","hl":"#ffffff","hl_text":"#1a0800","wm":"#3e1e0a","font":"playfair"},
    15: {"name":"Linen Classic",    "bg":"#f0ebe0","text":"#1a1408","hl":"#7a5a20","hl_text":"#1a0c00","wm":"#8a7860","font":"lora"},
    16: {"name":"Cool Fog",         "bg":"#d4d8dc","text":"#1e2228","hl":"#3a5a7a","hl_text":"#e8f0f8","wm":"#8898a8","font":"lora"},
    17: {"name":"Dark Sepia",       "bg":"#1a1208","text":"#c8b888","hl":"#e8c870","hl_text":"#0a0800","wm":"#4a3818","font":"lora"},
    18: {"name":"Ash Minimal",      "bg":"#e8e8e4","text":"#282828","hl":"#888888","hl_text":"#f0f0f0","wm":"#aaaaaa","font":"josefin"},
    19: {"name":"Burgundy",         "bg":"#1e0e10","text":"#c8b0a8","hl":"#d4847a","hl_text":"#0e0000","wm":"#3a2020","font":"lora"},
    20: {"name":"Sand Dune",        "bg":"#ddd0b8","text":"#1e1808","hl":"#6a4a10","hl_text":"#f0e8d8","wm":"#8a7a5a","font":"playfair"},
    21: {"name":"Ink Blue",         "bg":"#18202e","text":"#a8b8cc","hl":"#c8d890","hl_text":"#0a1800","wm":"#2a3448","font":"lora"},
    22: {"name":"Cream Accent",     "bg":"#f2ece0","text":"#1a140a","hl":"#8a6020","hl_text":"#f0e8d0","wm":"#9a8868","font":"playfair"},
    23: {"name":"Charcoal Soft",    "bg":"#343434","text":"#c4c0b8","hl":"#c8a060","hl_text":"#0a0800","wm":"#555555","font":"lora"},
    24: {"name":"Warm White",       "bg":"#faf7f2","text":"#1e1a12","hl":"#8a6820","hl_text":"#f0e8d8","wm":"#b8a880","font":"playfair"},
    25: {"name":"Midnight Copper",  "bg":"#0c0c0e","text":"#a09080","hl":"#b08040","hl_text":"#0a0600","wm":"#2a2820","font":"lora"},
    26: {"name":"Warm Grey",        "bg":"#e4e0d8","text":"#222222","hl":"#c8c090","hl_text":"#1a1800","wm":"#888888","font":"lora"},
    27: {"name":"Olive Muted",      "bg":"#c8c4a8","text":"#1a1c10","hl":"#3a3e10","hl_text":"#f0f0d8","wm":"#6a6a4a","font":"lora"},
    28: {"name":"Dark Teal",        "bg":"#0e1e1c","text":"#8ab8b0","hl":"#a8e8d8","hl_text":"#0a1810","wm":"#1e3a38","font":"lora"},
    29: {"name":"Blush Minimal",    "bg":"#e8ddd8","text":"#2a1c18","hl":"#6a3028","hl_text":"#f0e8e4","wm":"#b09088","font":"josefin"},
    30: {"name":"Gunmetal",         "bg":"#1c2028","text":"#a8aab0","hl":"#c8c0a0","hl_text":"#0c1018","wm":"#2a2e38","font":"josefin"},
    31: {"name":"Espresso",         "bg":"#1e1810","text":"#d8d0c0","hl":"#c8a96e","hl_text":"#0a0800","wm":"#8a7860","font":"playfair"},
    32: {"name":"Silver Clean",     "bg":"#d0d0cc","text":"#1a1a18","hl":"#5a5a50","hl_text":"#f0f0f0","wm":"#888882","font":"playfair"},
    33: {"name":"Amber Dusk",       "bg":"#1a1208","text":"#b8a880","hl":"#e8b830","hl_text":"#0a0800","wm":"#3a2e10","font":"playfair"},
    34: {"name":"Concrete Raw",     "bg":"#b8b4ae","text":"#0e0e0c","hl":"#555550","hl_text":"#f0f0f0","wm":"#5a5a58","font":"josefin"},
    35: {"name":"Champagne",        "bg":"#e8e0cc","text":"#1a1608","hl":"#7a6020","hl_text":"#f0e8d8","wm":"#9a9070","font":"lora"},
    36: {"name":"Night Ink",        "bg":"#08080e","text":"#9898b0","hl":"#b0a8d0","hl_text":"#08080a","wm":"#1e1e30","font":"lora"},
    37: {"name":"Clay Brown",       "bg":"#c0a888","text":"#1a0e04","hl":"#3a1e08","hl_text":"#f0e8d8","wm":"#3a1e08","font":"lora"},
    38: {"name":"Arctic White",     "bg":"#f4f6f8","text":"#1e2430","hl":"#3a6888","hl_text":"#f0f8ff","wm":"#b0b8c4","font":"josefin"},
    39: {"name":"Mocha Warm",       "bg":"#2a1c14","text":"#b8a090","hl":"#d0a868","hl_text":"#0a0800","wm":"#4a3020","font":"lora"},
    40: {"name":"Powder Blue",      "bg":"#d8e0e8","text":"#1a2030","hl":"#284860","hl_text":"#e8f0ff","wm":"#90a0b0","font":"lora"},
    41: {"name":"Bone Classic",     "bg":"#e8e2d8","text":"#1a1610","hl":"#6a4a18","hl_text":"#f0e8d8","wm":"#9a9080","font":"lora"},
    42: {"name":"Storm Grey",       "bg":"#3a3e44","text":"#b8bcc4","hl":"#d8c8a0","hl_text":"#0a0800","wm":"#555555","font":"lora"},
    43: {"name":"Old Gold",         "bg":"#c8a83a","text":"#1a1200","hl":"#0a0800","hl_text":"#f0e8a0","wm":"#3a2800","font":"playfair"},
    44: {"name":"Paper White",      "bg":"#f5f2ec","text":"#1a1810","hl":"#555550","hl_text":"#f5f2ec","wm":"#9a9880","font":"josefin"},
    45: {"name":"Dusk Purple",      "bg":"#1e1c28","text":"#a098b8","hl":"#c8b8e0","hl_text":"#0a0818","wm":"#2e2c40","font":"lora"},
    46: {"name":"Warm Rust",        "bg":"#1c0e08","text":"#c0a090","hl":"#d87850","hl_text":"#0a0400","wm":"#3a1e14","font":"playfair"},
    47: {"name":"Mist Linen",       "bg":"#dcdcd4","text":"#1e2018","hl":"#383c28","hl_text":"#f0f0e8","wm":"#9a9a90","font":"josefin"},
    48: {"name":"Deep Walnut",      "bg":"#140e08","text":"#9a8870","hl":"#c0a050","hl_text":"#0a0600","wm":"#2a2010","font":"lora"},
    49: {"name":"Stone Serif",      "bg":"#c4beb4","text":"#1a1810","hl":"#ffffff","hl_text":"#1a1810","wm":"#6a6860","font":"lora"},
    50: {"name":"Ivory Ash",        "bg":"#e8e4dc","text":"#1a1810","hl":"#c8a96e","hl_text":"#0a0800","wm":"#9a9880","font":"playfair"},
}

# ── Helpers ────────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except: return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def get_font(font_key, size):
    font_map = {
        "lora":     ["Lora.ttf", "DejaVuSerif.ttf"],
        "playfair": ["PlayfairDisplay.ttf", "DejaVuSerif.ttf"],
        "josefin":  ["JosefinSans.ttf", "DejaVuSans.ttf"],
    }
    for fname in font_map.get(font_key, ["DejaVuSerif.ttf"]):
        for d in [FONT_DIR, "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"]:
            try: return ImageFont.truetype(os.path.join(d, fname), size)
            except: pass
    return ImageFont.load_default()

def parse_quote(raw):
    parts = raw.split("|")
    main = parts[0].strip()
    bold = parts[1].strip() if len(parts) > 1 else ""
    m = re.search(r'\*([^*]+)\*', main)
    if m:
        before, hl, after = main[:m.start()], m.group(1), main[m.end():]
    else:
        before, hl, after = main, "", ""
    return before, hl, after, bold

def add_texture(img, intensity=10):
    import random as rnd
    pixels = img.load()
    w, h = img.size
    for _ in range(w * h // 8):
        px, py = rnd.randint(0,w-1), rnd.randint(0,h-1)
        noise = rnd.randint(-intensity, intensity)
        r,g,b = pixels[px,py][:3]
        pixels[px,py] = (max(0,min(255,r+noise)), max(0,min(255,g+noise)), max(0,min(255,b+noise)))
    return img

# ── Render Image ───────────────────────────────────────────────────────────
def render_image(style_id, quote_raw, handle="@billion.dollars.motivation"):
    s = STYLES[style_id]
    size = IMG_SIZE
    img = Image.new("RGB", (size, size), hex_rgb(s["bg"]))
    draw = ImageDraw.Draw(img)

    pad = 90
    text_x = pad
    text_y = int(size * 0.22)
    max_w  = size - pad * 2

    # Corner decorations
    cc = hex_rgb(s["hl"])
    clen = 80
    lw = 3
    # Top-left
    draw.rectangle([30,30,30+clen,30+lw], fill=cc)
    draw.rectangle([30,30,30+lw,30+clen], fill=cc)
    # Top-right
    draw.rectangle([size-30-clen,30,size-30,30+lw], fill=cc)
    draw.rectangle([size-30-lw,30,size-30,30+clen], fill=cc)
    # Bottom-left
    draw.rectangle([30,size-30-lw,30+clen,size-30], fill=cc)
    draw.rectangle([30,size-30-clen,30+lw,size-30], fill=cc)
    # Bottom-right
    draw.rectangle([size-30-clen,size-30-lw,size-30,size-30], fill=cc)
    draw.rectangle([size-30-lw,size-30-clen,size-30,size-30], fill=cc)

    # Big faded quote mark
    qfont = get_font("playfair", 260)
    qcol = (*hex_rgb(s["hl"]), 18)
    qimg = Image.new("RGBA", (size,size), (0,0,0,0))
    qdraw = ImageDraw.Draw(qimg)
    qdraw.text((30, -30), "\u201c", font=qfont, fill=qcol)
    img = Image.alpha_composite(img.convert("RGBA"), qimg).convert("RGB")
    draw = ImageDraw.Draw(img)

    img = add_texture(img)
    draw = ImageDraw.Draw(img)

    # Parse quote
    before, hl_phrase, after, bold = parse_quote(quote_raw)
    full_text = before + hl_phrase + after

    body_size = 54
    bold_size = 60
    wm_size   = 26
    body_font = get_font(s["font"], body_size)
    bold_font = get_font(s["font"], bold_size)
    wm_font   = get_font(s["font"], wm_size)
    it_font   = get_font(s["font"], wm_size)

    avg_char_w = body_size * 0.52
    chars_per_line = max(10, int(max_w / avg_char_w))
    lines = textwrap.wrap(full_text, width=chars_per_line)
    hl_words = set(hl_phrase.lower().split()) if hl_phrase else set()
    line_height = int(body_size * 1.75)

    cy = text_y
    for line in lines:
        words = line.split()
        # Calculate line width for centering
        line_w = 0
        for word in words:
            try:
                bb = draw.textbbox((0,0), word+" ", font=body_font)
                line_w += bb[2]-bb[0]
            except:
                line_w += body_size * len(word) * 0.55
        cx = (size - line_w) // 2

        for word in words:
            clean = word.strip(".,!?;:'\"").lower()
            use_hl = clean in hl_words and hl_phrase
            try:
                bb = draw.textbbox((0,0), word+" ", font=body_font)
                ww = bb[2]-bb[0]
                wh = bb[3]-bb[1]
            except:
                ww = body_size*len(word)*0.55
                wh = body_size

            if use_hl:
                pad2 = 5
                draw.rectangle([cx-pad2, cy+int(wh*0.5), cx+ww+pad2, cy+wh+6], fill=hex_rgb(s["hl"]))
                draw.text((cx,cy), word+" ", font=body_font, fill=hex_rgb(s["hl_text"]))
            else:
                draw.text((cx,cy), word+" ", font=body_font, fill=hex_rgb(s["text"]))
            cx += ww
        cy += line_height

    # Divider line
    cy += 18
    lc = hex_rgb(s["hl"])
    draw.rectangle([size//2-60, cy, size//2+60, cy+2], fill=lc)
    cy += 18

    # Bold ending
    if bold:
        bold_lines = textwrap.wrap(bold, width=int(chars_per_line*0.85))
        for bl in bold_lines:
            try:
                bw = draw.textbbox((0,0), bl, font=bold_font)[2]
                bh = draw.textbbox((0,0), bl, font=bold_font)[3]
            except:
                bw = bold_size*len(bl)*0.55
                bh = bold_size
            draw.text(((size-bw)//2, cy), bl, font=bold_font, fill=hex_rgb(s["text"]))
            cy += int(bh*1.5)

    # Handle at bottom
    cy = size - 90
    draw.line([(pad, cy), (size-pad, cy)], fill=hex_rgb(s["wm"]), width=1)
    cy += 16
    try:
        hw = draw.textbbox((0,0), handle, font=wm_font)[2]
    except:
        hw = wm_size*len(handle)*0.55
    draw.text(((size-hw)//2, cy), handle, font=wm_font, fill=hex_rgb(s["wm"]))

    return img

# ── Post to Facebook ───────────────────────────────────────────────────────
def post_to_facebook(image_path, caption):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(url, data={"caption": caption, "access_token": FB_TOKEN},
                             files={"source": f})
    resp.raise_for_status()
    data = resp.json()
    print(f"✅ Posted! ID: {data.get('post_id', data.get('id'))}")

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    import json as _json
    track = load_json(TRACK_FILE, {"quote_index": 0, "caption_index": 0})
    style_data = load_json(STYLE_FILE, {"last": 0})

    q_idx  = track["quote_index"] % len(QUOTES)
    cap_idx = track["caption_index"] % len(CAPTIONS)
    style_id = (style_data["last"] % 50) + 1

    quote   = QUOTES[q_idx]
    caption = CAPTIONS[cap_idx]

    print(f"🎨 Style #{style_id}: {STYLES[style_id]['name']}")
    print(f"📝 Quote #{q_idx+1}/{len(QUOTES)}: {quote[:60]}...")

    img = render_image(style_id, quote)
    img_path = "/tmp/motivation_post.jpg"
    img.save(img_path, "JPEG", quality=95)

    print("📤 Posting to Facebook...")
    post_to_facebook(img_path, caption)

    # Update trackers
    save_json(TRACK_FILE, {
        "quote_index":   (q_idx + 1) % len(QUOTES),
        "caption_index": (cap_idx + 1) % len(CAPTIONS),
    })
    save_json(STYLE_FILE, {"last": style_id})
    print(f"✅ Done! Next: quote #{(q_idx+2)%len(QUOTES)+1}, style #{(style_id%50)+1}")

if __name__ == "__main__":
    main()
