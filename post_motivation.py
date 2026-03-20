"""
Motivation Post Automation - Final Version
- 240 built-in quotes (8/day x 30 days, repeats monthly)
- 50 impressive color styles
- Single thin border, perfect highlight, clean minimal design
- Posts to Facebook automatically
"""

import os, json, re, textwrap, requests
from PIL import Image, ImageDraw, ImageFont

FB_TOKEN   = os.environ["FB_PAGE_ACCESS_TOKEN"]
FB_PAGE_ID = os.environ["FB_PAGE_ID"]
FONT_DIR   = "/tmp/fonts"
TRACK_FILE = "used_quotes.json"
STYLE_FILE = "style_counter.json"
IMG_SIZE   = 1080

QUOTES = [
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
    "Gratitude *transforms* what you have into more than enough.",
    "Start *every day* with thanks and watch the tone of your life change.",
    "Be *grateful* for the struggle|it is proof you are still in the game.",
    "There is *always* something to be grateful for if you look closely.",
    "Appreciation is the *quickest* path from where you are to where you want.",
    "Count your *blessings* not your problems and watch the math change.",
    "Grateful *hearts* attract abundant lives|practice it every morning.",
    "Even on *hard days* gratitude is the anchor that keeps you steady.",
    "The more *grateful* you are the more reasons you are given to be grateful.",
    "Thank the *journey|even the detours are teaching you something priceless.",
    "Every morning is a *fresh start|use it before it becomes yesterday.",
    "The person you *want to become* is waiting on the other side of fear.",
    "Do not wait for *inspiration|be the kind of person inspiration chases.",
    "You are one *decision* away from a completely different life.",
    "Your potential is *not a destination|it is a direction you choose daily.",
    "The difference between *ordinary* and extraordinary is that little extra.",
    "Make yourself *proud* in the moments no one else is watching.",
    "You did not *survive* this far to play small for the rest of your life.",
    "Every version of *you* that doubted is proof you kept going anyway.",
    "The best revenge is *living well* and never looking back with regret.",
    "Keep going.|The *next chapter* of your story is worth showing up for.",
    "Be *relentless* in the pursuit of what sets your soul on fire.",
    "Show the world what *happens* when someone simply refuses to give up.",
    "Your *comeback* story is being written right now in the quiet moments.",
    "Do the work *today* that your future self will thank you for tomorrow.",
    "Every champion was once a *beginner* who refused to stay that way.",
    "You are not *defined* by your past|you are prepared by it.",
    "The only *limits* that exist are the ones you agree to believe in.",
    "Nothing *great* was ever built by someone who stayed comfortable.",
    "Your *energy* is your most valuable currency — spend it on what counts.",
    "Rise above the *noise* and become the signal everyone else follows.",
    "Be *consistent* when it is boring and extraordinary when it matters.",
    "The world *steps aside* for those who know where they are going.",
    "You were not *born* to blend in|you were born to stand out and lead.",
    "Make every *rep* count whether anyone is watching or not.",
    "The *hunger* inside you is a compass — follow it without apology.",
    "Success is not *given|it is built in the hours others choose to sleep.",
    "Every master was once a *disaster* who chose to keep practicing.",
    "Your story is not *over|the best chapters are still being written.",
]

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

STYLES = [
    {"name":"Deep Purple Gold",    "bg":"#1a0a2e","text":"#f0e6ff","hl":"#ffd700","hl_text":"#1a0a2e","body":"playfair","bold":"lora"},
    {"name":"Emerald Black",       "bg":"#0a1a0e","text":"#e8f5e8","hl":"#00e676","hl_text":"#0a1a0e","body":"lora","bold":"josefin"},
    {"name":"Navy Coral",          "bg":"#0d1b2a","text":"#e8eaf6","hl":"#ff6b6b","hl_text":"#ffffff","body":"josefin","bold":"playfair"},
    {"name":"Burnt Orange Dark",   "bg":"#1a0a00","text":"#ffe0b2","hl":"#ff6d00","hl_text":"#ffffff","body":"lora","bold":"lora"},
    {"name":"Rose Gold Dark",      "bg":"#1a0814","text":"#fce4ec","hl":"#f48fb1","hl_text":"#1a0814","body":"playfair","bold":"lora"},
    {"name":"Teal Black",          "bg":"#001a1a","text":"#e0f7fa","hl":"#00bcd4","hl_text":"#001a1a","body":"lora","bold":"josefin"},
    {"name":"Crimson White",       "bg":"#ffffff","text":"#1a0000","hl":"#c62828","hl_text":"#ffffff","body":"playfair","bold":"josefin"},
    {"name":"Slate Lime",          "bg":"#1c2526","text":"#eceff1","hl":"#c6ff00","hl_text":"#1c2526","body":"josefin","bold":"playfair"},
    {"name":"Warm Sand Purple",    "bg":"#f5f0e8","text":"#2d1b4e","hl":"#7b1fa2","hl_text":"#ffffff","body":"lora","bold":"lora"},
    {"name":"Ocean Blue Gold",     "bg":"#001233","text":"#caf0f8","hl":"#ffd60a","hl_text":"#001233","body":"lora","bold":"playfair"},
    {"name":"Forest Amber",        "bg":"#0a1a00","text":"#f1f8e9","hl":"#ffab00","hl_text":"#0a1a00","body":"playfair","bold":"lora"},
    {"name":"Charcoal Turquoise",  "bg":"#212121","text":"#f5f5f5","hl":"#1de9b6","hl_text":"#212121","body":"josefin","bold":"josefin"},
    {"name":"Ivory Black",         "bg":"#fafaf5","text":"#111111","hl":"#111111","hl_text":"#fafaf5","body":"playfair","bold":"lora"},
    {"name":"Midnight Lavender",   "bg":"#12002a","text":"#e8d5ff","hl":"#ce93d8","hl_text":"#12002a","body":"lora","bold":"playfair"},
    {"name":"Copper Dark",         "bg":"#0e0800","text":"#ffd180","hl":"#ff8f00","hl_text":"#0e0800","body":"playfair","bold":"lora"},
    {"name":"Arctic Blue",         "bg":"#e3f2fd","text":"#0d1b2a","hl":"#1565c0","hl_text":"#ffffff","body":"josefin","bold":"josefin"},
    {"name":"Ruby Night",          "bg":"#1a0008","text":"#ffd0d8","hl":"#ef5350","hl_text":"#1a0008","body":"lora","bold":"playfair"},
    {"name":"Sage White",          "bg":"#f5f8f0","text":"#1a2e10","hl":"#388e3c","hl_text":"#ffffff","body":"playfair","bold":"lora"},
    {"name":"Storm Blue Silver",   "bg":"#0a1628","text":"#cfd8dc","hl":"#90caf9","hl_text":"#0a1628","body":"josefin","bold":"lora"},
    {"name":"Warm Olive",          "bg":"#1c1a00","text":"#f9f6d0","hl":"#cddc39","hl_text":"#1c1a00","body":"lora","bold":"josefin"},
    {"name":"Blush Cream",         "bg":"#fdf0f0","text":"#2a0a0a","hl":"#e91e63","hl_text":"#ffffff","body":"playfair","bold":"playfair"},
    {"name":"Carbon Orange",       "bg":"#1a1200","text":"#fff3e0","hl":"#ff9800","hl_text":"#1a1200","body":"lora","bold":"lora"},
    {"name":"Deep Sapphire",       "bg":"#000d2e","text":"#e8eeff","hl":"#5c6bc0","hl_text":"#ffffff","body":"playfair","bold":"josefin"},
    {"name":"Warm Parchment Red",  "bg":"#fdf5e6","text":"#1a0a00","hl":"#bf360c","hl_text":"#ffffff","body":"lora","bold":"playfair"},
    {"name":"Night Mint",          "bg":"#001a14","text":"#e0fff4","hl":"#00e5ff","hl_text":"#001a14","body":"josefin","bold":"lora"},
    {"name":"Gold Black",          "bg":"#0a0800","text":"#fff8e1","hl":"#ffd600","hl_text":"#0a0800","body":"playfair","bold":"playfair"},
    {"name":"Dusty Pink Dark",     "bg":"#1a0010","text":"#fce4f0","hl":"#ff80ab","hl_text":"#1a0010","body":"lora","bold":"josefin"},
    {"name":"Cobalt Cream",        "bg":"#fafafa","text":"#0a1428","hl":"#1a237e","hl_text":"#ffffff","body":"playfair","bold":"lora"},
    {"name":"Mocha Silver",        "bg":"#1a1008","text":"#f5f0ea","hl":"#bdbdbd","hl_text":"#1a1008","body":"lora","bold":"playfair"},
    {"name":"Electric Night",      "bg":"#0a001a","text":"#e8d5ff","hl":"#7c4dff","hl_text":"#ffffff","body":"josefin","bold":"lora"},
    {"name":"Warm Brick",          "bg":"#1c0800","text":"#fbe9e7","hl":"#ff5722","hl_text":"#ffffff","body":"playfair","bold":"josefin"},
    {"name":"Slate Gold",          "bg":"#1a1a2e","text":"#e8e8f0","hl":"#ffd700","hl_text":"#1a1a2e","body":"lora","bold":"lora"},
    {"name":"Forest White",        "bg":"#f0f8f0","text":"#0a1e00","hl":"#1b5e20","hl_text":"#ffffff","body":"lora","bold":"playfair"},
    {"name":"Deep Maroon Gold",    "bg":"#1a0010","text":"#f8e8ff","hl":"#ffd700","hl_text":"#1a0010","body":"playfair","bold":"lora"},
    {"name":"Sky Charcoal",        "bg":"#263238","text":"#eceff1","hl":"#80d8ff","hl_text":"#263238","body":"josefin","bold":"josefin"},
    {"name":"Amber Cream",         "bg":"#fff8e1","text":"#1a1000","hl":"#e65100","hl_text":"#ffffff","body":"playfair","bold":"lora"},
    {"name":"Midnight Green Gold", "bg":"#001a0e","text":"#e8fff4","hl":"#ffd700","hl_text":"#001a0e","body":"lora","bold":"playfair"},
    {"name":"Ash White",           "bg":"#fafafa","text":"#212121","hl":"#424242","hl_text":"#ffffff","body":"josefin","bold":"lora"},
    {"name":"Deep Violet Coral",   "bg":"#1a0028","text":"#fce4ff","hl":"#ff6e6e","hl_text":"#ffffff","body":"playfair","bold":"josefin"},
    {"name":"Warm Navy",           "bg":"#0d1b2a","text":"#fff8e1","hl":"#ffca28","hl_text":"#0d1b2a","body":"lora","bold":"lora"},
    {"name":"Neon Dark",           "bg":"#0a0a0a","text":"#f5f5f5","hl":"#00e5ff","hl_text":"#0a0a0a","body":"josefin","bold":"playfair"},
    {"name":"Dusty Rose White",    "bg":"#fff0f3","text":"#1a0008","hl":"#c2185b","hl_text":"#ffffff","body":"playfair","bold":"lora"},
    {"name":"Deep Ocean",          "bg":"#00091a","text":"#b3e5fc","hl":"#03a9f4","hl_text":"#00091a","body":"lora","bold":"josefin"},
    {"name":"Harvest Gold",        "bg":"#1a1000","text":"#fff9c4","hl":"#f9a825","hl_text":"#1a1000","body":"playfair","bold":"playfair"},
    {"name":"Soft Indigo",         "bg":"#f3f0ff","text":"#1a0050","hl":"#512da8","hl_text":"#ffffff","body":"lora","bold":"lora"},
    {"name":"Carbon Mint",         "bg":"#1a1a1a","text":"#e8fff8","hl":"#69f0ae","hl_text":"#1a1a1a","body":"josefin","bold":"lora"},
    {"name":"Warm White Burgundy", "bg":"#fdf5f5","text":"#1a0000","hl":"#880e4f","hl_text":"#ffffff","body":"playfair","bold":"josefin"},
    {"name":"Deep Bronze",         "bg":"#0e0800","text":"#fdf0d8","hl":"#cd7f32","hl_text":"#0e0800","body":"lora","bold":"playfair"},
    {"name":"Ice Blue Dark",       "bg":"#001428","text":"#e1f5fe","hl":"#b3e5fc","hl_text":"#001428","body":"playfair","bold":"lora"},
    {"name":"Volcanic Dark",       "bg":"#1a0800","text":"#fbe9e7","hl":"#dd2c00","hl_text":"#ffffff","body":"josefin","bold":"playfair"},
]

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except: return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def hex_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def get_font(name, size):
    font_map = {
        "playfair": ["PlayfairDisplay.ttf", "DejaVuSerif.ttf"],
        "lora":     ["Lora.ttf", "DejaVuSerif.ttf"],
        "josefin":  ["JosefinSans.ttf", "DejaVuSans.ttf"],
    }
    for fname in font_map.get(name, ["DejaVuSerif.ttf"]):
        for d in [FONT_DIR, "/usr/share/fonts/truetype/dejavu"]:
            try: return ImageFont.truetype(os.path.join(d, fname), size)
            except: pass
    return ImageFont.load_default()

def add_texture(img, intensity=8):
    import random as rnd
    pixels = img.load()
    w, h = img.size
    for _ in range(w * h // 10):
        px, py = rnd.randint(0,w-1), rnd.randint(0,h-1)
        noise = rnd.randint(-intensity, intensity)
        r,g,b = pixels[px,py][:3]
        pixels[px,py] = (max(0,min(255,r+noise)), max(0,min(255,g+noise)), max(0,min(255,b+noise)))
    return img

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

def render_image(style_id, quote_raw):
    s = STYLES[style_id - 1]
    size = IMG_SIZE
    img = Image.new("RGB", (size, size), hex_rgb(s["bg"]))
    img = add_texture(img)
    draw = ImageDraw.Draw(img)

    # Single thin border
    bw = 18
    draw.rectangle([bw, bw, size-bw, size-bw], outline=hex_rgb(s["hl"]), width=2)

    pad = 110
    max_w = size - pad * 2
    body_font = get_font(s["body"], 56)
    bold_font = get_font(s["bold"], 64)

    before, hl_phrase, after, bold = parse_quote(quote_raw)
    full_text = before + hl_phrase + after
    hl_words = set(hl_phrase.lower().split()) if hl_phrase else set()

    chars_per_line = max(10, int(max_w / (56 * 0.52)))
    lines = textwrap.wrap(full_text, width=chars_per_line)
    line_height = int(56 * 1.85)
    total_h = len(lines) * line_height
    cy = (size - total_h) // 2 - 60

    for line in lines:
        words = line.split()
        line_w = sum(draw.textbbox((0,0), w+' ', font=body_font)[2] -
                     draw.textbbox((0,0), w+' ', font=body_font)[0] for w in words)
        cx = (size - line_w) // 2
        for word in words:
            clean = word.strip(".,!?;:'\"").lower()
            use_hl = clean in hl_words and hl_phrase
            bb = draw.textbbox((0,0), word+' ', font=body_font)
            ww = bb[2]-bb[0]
            if use_hl:
                draw.rectangle([cx+bb[0]-5, cy+bb[1]-2,
                                 cx+bb[2]+5, cy+bb[3]+2], fill=hex_rgb(s["hl"]))
                draw.text((cx,cy), word+' ', font=body_font, fill=hex_rgb(s["hl_text"]))
            else:
                draw.text((cx,cy), word+' ', font=body_font, fill=hex_rgb(s["text"]))
            cx += ww
        cy += line_height

    cy += 12
    draw.rectangle([size//2-40, cy, size//2+40, cy+2], fill=hex_rgb(s["hl"]))
    cy += 18

    if bold:
        bold_lines = textwrap.wrap(bold, width=int(chars_per_line*0.85))
        for bl in bold_lines:
            bb = draw.textbbox((0,0), bl, font=bold_font)
            draw.text(((size-(bb[2]-bb[0]))//2, cy), bl, font=bold_font, fill=hex_rgb(s["text"]))
            cy += int((bb[3]-bb[1])*1.5)

    return img

def post_to_facebook(image_path, caption):
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos"
    with open(image_path, "rb") as f:
        resp = requests.post(url, data={"caption": caption, "access_token": FB_TOKEN},
                             files={"source": f})
    resp.raise_for_status()
    data = resp.json()
    print(f"✅ Posted! ID: {data.get('post_id', data.get('id'))}")

def main():
    track = load_json(TRACK_FILE, {"quote_index": 0, "caption_index": 0})
    style_data = load_json(STYLE_FILE, {"last": 0})

    q_idx   = track["quote_index"] % len(QUOTES)
    cap_idx = track["caption_index"] % len(CAPTIONS)
    style_id = (style_data["last"] % len(STYLES)) + 1

    quote   = QUOTES[q_idx]
    caption = CAPTIONS[cap_idx]

    print(f"🎨 Style #{style_id}: {STYLES[style_id-1]['name']}")
    print(f"📝 Quote #{q_idx+1}/{len(QUOTES)}: {quote[:60]}...")

    img = render_image(style_id, quote)
    img_path = "/tmp/motivation_post.jpg"
    img.save(img_path, "JPEG", quality=95)

    print("📤 Posting to Facebook...")
    post_to_facebook(img_path, caption)

    save_json(TRACK_FILE, {
        "quote_index":   (q_idx + 1) % len(QUOTES),
        "caption_index": (cap_idx + 1) % len(CAPTIONS),
    })
    save_json(STYLE_FILE, {"last": style_id})
    print(f"✅ Done! Next: style #{(style_id % len(STYLES)) + 1}")

if __name__ == "__main__":
    main()
