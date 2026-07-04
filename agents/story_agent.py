"""Story generation — full revenge/betrayal script following the schema
confirmed across 5 viral videos (see revenge-story-lab/SCHEMA_COMPARISON.md).
Also generates the premise queue and per-video metadata. Fully autonomous:
the agent decides premises, no human approval step (user decision 2026-07-03)."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import STORIES_FILE, SCRIPT_MIN_WORDS, SCRIPT_MAX_WORDS
from agents.llm import call, call_haiku

# The 6 non-negotiable schema rules, distilled from the 5-video teardown.
SCHEMA = """You are the head writer for a faceless YouTube channel that narrates original first-person family-betrayal revenge stories (25-45yo US audience). Write ONE complete video script following this exact structure:

1. COLD-OPEN HOOK (first 3 sentences): restate the premise as a wound, then spoil the ending payoff ("...so I let them lose everything" energy). The viewer must know the OUTCOME and stay for the PROCESS.
2. SETUP (~15% of length): first-person narrator with age+gender in Reddit style (e.g. "I'm a 31-year-old woman"), a real US city, hyper-specific details (dollar amounts, GPAs, years). Establish the golden-child sibling vs scapegoat-narrator dynamic. End setup with a foreshadow line ("Looking back, there were signs I ignored...").
3. INJUSTICE (~15%): the betrayal hits fast and brutally. The narrator is 100% innocent. Include quoted dialogue at the emotional peaks.
4. ROCK BOTTOM (~25%): extended suffering, each beat worse than the last. This is the watch-time engine — do not rush it.
5. TURNING POINT + REBUILD (~20%): an unexpected ally/mentor, then a multi-year rebuild montage into quiet success. Time-skip is fine.
6. MID-STORY HOOK (place at roughly the halfway point of the full script): the family comes back — because they NEED something (money, a kidney, the company). New escalation.
7. CONFRONTATION (~15%): the payoff promised in the hook. The revenge must be CLEAN HANDS — the narrator never does anything cruel; they simply refuse to help, walk away, or let consequences land. Dignified refusal lines, quotable.
8. AFTERMATH (~5%): concrete karma details for the family, quiet fulfilled life for the narrator.
9. REDDIT-STYLE EDITS ENDING: finish with "Edit:" / "Edit 2:" ... Q&A blocks answering imagined commenters — at least one morally debatable stance to bait comment-section arguments. Close with one direct question to the listener: "What would you have done?" — then a short punchline. NO subscribe call-to-action.

ENGAGEMENT LINE (comment engine, proven by active channels): right AFTER the cold-open hook and BEFORE the setup, insert one short spoken line: "Before we get into this — drop where you're listening from, and your local time, in the comments. I read every one." Then continue into the setup naturally.

Style rules: plain spoken American English, short sentences, first person past tense, no chapter headings, no markdown — output ONLY the narration text exactly as it will be read aloud. Numbers written for speech ("eighty thousand dollars" style is NOT needed — "$80,000" is fine, the TTS reads it). Never use the words "chapter" or "part"."""

TITLE_RULES = """Title formula (from the proven pattern): [specific betrayal by family] + [abandonment], then a second clause with the turn, cut with an em-dash or "So I...". 70-95 characters. Examples of the shape:
- "My Family Believed My Sister's Lie, Disowned Me, And Let Me Rot. Now They Want My Help"
- "My Parents Gave My Sister $450K At Dinner. I Got A Gift Card. So I Called The Bank Mid-Bite"
The comeback clause must be PASSIVE and non-violent (refused, walked away, watched them lose it, said nothing) — never destructive imagery like burn/destroy/ruin someone physically, even metaphorically. Advertiser-safe.
"""


def _load():
    return json.loads(STORIES_FILE.read_text()) if STORIES_FILE.exists() else {"stories": []}


def _save(data):
    STORIES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def next_pending():
    """First premise with status=pending; tops the queue up first if empty."""
    data = _load()
    pending = [s for s in data["stories"] if s["status"] == "pending"]
    if not pending:
        top_up_queue(5)
        data = _load()
        pending = [s for s in data["stories"] if s["status"] == "pending"]
    return pending[0] if pending else None


def mark(story_id, status, video_id=None):
    data = _load()
    for s in data["stories"]:
        if s["id"] == story_id:
            s["status"] = status
            if video_id:
                s["video_id"] = video_id
    _save(data)


def top_up_queue(n=5):
    """Agent generates fresh premises, avoiding repeats of what's in the queue."""
    data = _load()
    used = "\n".join(f"- {s['premise']}" for s in data["stories"][-30:]) or "(none yet)"
    raw = call_haiku(
        f"""Generate {n} fresh premises for first-person family-betrayal revenge stories (YouTube long-form niche). Each premise: 1-2 sentences, hyper-specific (who betrayed, what was taken incl. a dollar amount or concrete stake, what the comeback is). Vary the narrator (gender, age 24-45), the betrayer (sister/brother/parents/in-laws), and the arena (inheritance, wedding, company, house, medical). Avoid anything similar to these already used:\n{used}\n\nReturn ONLY a JSON array of strings.""",
        max_tokens=1500,
    )
    m = re.search(r"\[.*\]", raw, re.S)
    premises = json.loads(m.group(0)) if m else []
    next_id = max([s["id"] for s in data["stories"]], default=0) + 1
    for p in premises:
        data["stories"].append({"id": next_id, "premise": p, "status": "pending"})
        next_id += 1
    _save(data)
    print(f"    Queue topped up with {len(premises)} premises")


def generate_script(story):
    words_hint = f"{SCRIPT_MIN_WORDS}-{SCRIPT_MAX_WORDS}"
    script = call(
        f"Premise: {story['premise']}\n\nWrite the full script now. Target length: {words_hint} words. Remember: output ONLY the narration text.",
        system=SCHEMA,
        max_tokens=16000,
    )
    wc = len(script.split())
    # One continuation pass if it came in short — cheaper than a full regen.
    if wc < SCRIPT_MIN_WORDS:
        print(f"    Script short ({wc} words) — extending rock-bottom + rebuild...")
        script = call(
            f"Premise: {story['premise']}\n\nHere is a draft that is too short ({wc} words, need {words_hint}). Rewrite it at full target length by DEEPENING the rock-bottom section and the rebuild montage (more beats, more specific detail) without changing the plot. Output ONLY the narration text.\n\nDRAFT:\n{script}",
            system=SCHEMA,
            max_tokens=16000,
        )
    return script


def generate_metadata(story, script):
    raw = call_haiku(
        f"""For this YouTube revenge-story video, write metadata. {TITLE_RULES}

Story premise: {story['premise']}
Opening of script: {script[:1200]}

Return ONLY JSON: {{"title": "...", "description": "2-3 sentence description ending with 3 relevant hashtags", "tags": ["10-14 tags"], "thumb_text": "6-10 word emotional punchline for the thumbnail, ALL CAPS"}}""",
        max_tokens=1200,
    )
    m = re.search(r"\{.*\}", raw, re.S)
    return json.loads(m.group(0))
