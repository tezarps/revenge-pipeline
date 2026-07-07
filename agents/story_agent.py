"""Story generation — full revenge/betrayal script following the schema
confirmed across 5 viral videos (see revenge-story-lab/SCHEMA_COMPARISON.md).
Also generates the premise queue and per-video metadata. Fully autonomous:
the agent decides premises, no human approval step (user decision 2026-07-03)."""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import STORIES_FILE, SCRIPT_MIN_WORDS, SCRIPT_MAX_WORDS
from agents.llm import call_deepseek


def _call_deepseek_json(prompt, pattern, start_tokens=6000, attempts=3):
    """DeepSeek's v4-pro is a reasoning model: it spends part of max_tokens
    on a hidden reasoning pass before the visible output, and how much
    varies with prompt complexity, so a fixed token budget that worked in
    testing can still come back empty in production (confirmed 2026-07-07:
    story #5's real generate_metadata call failed at max_tokens=6000 even
    though the exact same prompt shape had passed a smoke test earlier).
    Retries with an escalating token budget instead of a fixed one, and
    raises with the raw response visible in the log if all attempts fail,
    rather than silently returning an empty result."""
    tokens = start_tokens
    last_raw = ""
    for attempt in range(1, attempts + 1):
        last_raw = call_deepseek(prompt, max_tokens=tokens)
        m = re.search(pattern, last_raw, re.S)
        if m:
            return m.group(0)
        print(f"    DeepSeek JSON parse failed (attempt {attempt}/{attempts}, max_tokens={tokens}, response length={len(last_raw)}), retrying with more tokens...")
        tokens = int(tokens * 1.8)
    raise RuntimeError(f"DeepSeek never returned parseable JSON after {attempts} attempts. Last raw response: {last_raw[:500]!r}")

# The 6 non-negotiable schema rules, distilled from the 5-video teardown.
SCHEMA = """You are the head writer for a faceless YouTube channel that narrates original first-person family-betrayal revenge stories (25-45yo US audience). Write ONE complete video script following this exact structure:

1. COLD-OPEN HOOK (first 3 sentences): restate the premise as a wound, then spoil the ending payoff ("...so I let them lose everything" energy). The viewer must know the OUTCOME and stay for the PROCESS.
2. SETUP (~15% of length): first-person narrator, always a WOMAN aged 24-45 (the channel's narration voice is female; e.g. "I'm a 31-year-old woman"), Reddit style, a real US city, hyper-specific details (dollar amounts, GPAs, years). Establish the golden-child sibling vs scapegoat-narrator dynamic. End setup with a foreshadow line ("Looking back, there were signs I ignored...").
3. INJUSTICE (~15%): the betrayal hits fast and brutally. The narrator is 100% innocent. Include quoted dialogue at the emotional peaks.
4. ROCK BOTTOM (~25%): extended suffering, each beat worse than the last. This is the watch-time engine, so do not rush it.
5. TURNING POINT + REBUILD (~20%): an unexpected ally/mentor, then a multi-year rebuild montage into quiet success. Time-skip is fine.
6. MID-STORY HOOK (place at roughly the halfway point of the full script): the family comes back, because they NEED something (money, a kidney, the company). New escalation.
7. CONFRONTATION (~15%): the payoff promised in the hook. The revenge must be CLEAN HANDS: the narrator never does anything cruel, they simply refuse to help, walk away, or let consequences land. Dignified refusal lines, quotable.
8. AFTERMATH (~5%): concrete karma details for the family, quiet fulfilled life for the narrator.
9. REDDIT-STYLE EDITS ENDING: finish with "Edit:" / "Edit 2:" ... Q&A blocks answering imagined commenters, at least one morally debatable stance to bait comment-section arguments. Close with one direct question to the listener: "What would you have done?" then a short punchline. NO subscribe call-to-action.

ENGAGEMENT LINE (comment engine, proven by active channels): right AFTER the cold-open hook and BEFORE the setup, insert one short spoken line: "Before we get into this, drop where you're listening from, and your local time, in the comments. I read every one." Then continue into the setup naturally.

Style rules: plain spoken American English, short sentences, first person past tense, no chapter headings, no markdown, output ONLY the narration text exactly as it will be read aloud. Numbers written for speech ("eighty thousand dollars" style is NOT needed, "$80,000" is fine, the TTS reads it). Never use the words "chapter" or "part". NEVER use an em dash (the "—" character) anywhere in the output; use a comma, period, or "and"/"but" instead."""

TITLE_RULES = """Title formula (from the proven pattern): [specific betrayal by family] + [abandonment], then a second clause with the turn, cut with a period and "So I..." (never an em dash). 70-95 characters. Examples of the shape:
- "My Family Believed My Sister's Lie, Disowned Me, And Let Me Rot. Now They Want My Help"
- "My Parents Gave My Sister $450K At Dinner. I Got A Gift Card. So I Called The Bank Mid-Bite"
The comeback clause must be PASSIVE and non-violent (refused, walked away, watched them lose it, said nothing) — never destructive imagery like burn/destroy/ruin someone physically, even metaphorically. Advertiser-safe.
"""

# Alternate mode (2026-07-04): a longer, more elaborate procedural-thriller
# structure, adapted from a real competitor script the user transcribed.
# Kept as a SEPARATE schema (not a replacement) so the channel has variety;
# story_agent picks between SCHEMA and HEIST_SCHEMA per story (see
# generate_script). Narrator stays female per the earlier voice decision,
# even though the source example used a male narrator.
HEIST_SCHEMA = """You are the head writer for a faceless YouTube channel that narrates original first-person family-betrayal revenge stories (25-45yo US audience). Write ONE long, elaborate procedural-thriller-style video script following this exact structure (this is the "heist" variant, richer and more detail-driven than a plain emotional drama):

1. COLD-OPEN HOOK (first 3-4 sentences): state the inciting object/moment (a hidden box, a locked drawer, a warning left behind) and spoil the shape of the ending. The viewer must know something big is coming and stay for the mechanics of how it unfolds.
2. ENGAGEMENT LINE: immediately after the hook, one line: "Before I continue this story, let me know where you're watching from in the comments below. Hit like and subscribe if you believe [a one-line moral premise tied to this story's theme]." Then continue naturally.
3. SETUP (~12%): first-person narrator, always a WOMAN aged 30-55 (the channel's narration voice is female), hyper-specific backstory (career, decades of sacrifice, a modest frugal life, a spouse or parent who was "the quiet architect" of the family's survival). Establish who she sacrificed for and how invisible that sacrifice was.
4. THE DISCOVERY (~10%): a death or major loss triggers the plot. Within a day, "the vultures circle": a golden-child relative and their slick, image-obsessed spouse arrive to manage rather than mourn. The narrator finds a small, unassuming object (a box, a book, an old note) that the golden-child relative dismisses as worthless junk and discards. The narrator secretly retrieves it. On its last page, in the deceased's handwriting, is a short chilling warning: "Do not trust them. Save yourself" (or equivalent).
5. THE MANIPULATION (~12%): the antagonists pressure the narrator to sign over the house, assets, or power of attorney, disguised as "taking care of you." The narrator strategically plays weak, foggy, and compliant to avoid suspicion while secretly refusing to sign anything yet. They are moved into the antagonists' home under the guise of care, which is actually a control tactic.
6. UNDERCOVER INVESTIGATION (~20%, the heart of the story): over several scenes, the narrator quietly observes financial red flags (frantic phone calls, dodged calls, panicked pacing, extravagant unsustainable spending). A household accident or chore gives the narrator a reason to fix something with a hidden skill from their old working-class life, revealing the contrast between their competence and the antagonists' helplessness. The narrator finds physical evidence (shredded documents, a filing cabinet, a locked office) and uses an old practical skill (not violence: lockpicking from a trade background, reading financial documents from decades of careful budgeting, etc.) to retrieve proof: a forged signature, an offshore account, a predatory loan, evidence the narrator is being set up as the legal scapegoat for the antagonists' debt.
7. THE ALLY (~10%): the narrator discovers the deceased had ALREADY seen this coming and had taken a quiet, brilliant countermeasure before dying (a dead-man's-switch style lock on funds or assets, tied to the narrator's own presence/identity, so the antagonists can never access it without the narrator physically present and willing). Optionally, the narrator makes contact with a legitimate authority (a bank compliance officer, a federal investigator, a lawyer) who confirms the scale of the antagonists' fraud and recruits the narrator to help gather final proof (e.g., planting a data-extraction tool, providing a key document).
8. MAXIMUM CRUELTY BEAT (~8%): a scene proving the antagonists have zero remaining humanity: the narrator stages a medical scare (a fake collapse) to test them, and the antagonist steps over the "dying" narrator with total indifference to grab a document instead of helping. This is the point of no return; any residual family loyalty the narrator felt is extinguished.
9. THE CONFRONTATION (~18%): the antagonists, desperate and cornered, march the narrator to the final location (a bank, an office) to force a signature or access code. The narrator refuses with a short, dignified, quotable line (never violent). Authorities or the countermeasure trigger at this exact moment: the antagonists are exposed, arrested, or financially ruined by their own scheme.
10. AFTERMATH (~10%): concrete consequences for the antagonists (prison, seized assets, public disgrace). The narrator receives quiet, EARNED restitution (never a violent windfall: a legitimate reward, reclaimed property, an inheritance that was rightfully theirs). The narrator reflects on the deceased's brilliance and closes with a short moral aphorism about integrity, boundaries, or family.
11. ENDING: one direct question to the audience ("Have you ever discovered a dark secret about someone you trusted completely? How did you handle it?") followed by a subscribe/like call-to-action tied to the story's theme, then a short sign-off. NO Reddit-style "Edit:" Q&A blocks in this variant (that belongs to the plain-drama SCHEMA only).

Style rules: plain spoken American English, richly detailed procedural/technical specifics (financial jargon, trade-skill mechanics, investigative detail) to build hyper-competence and authenticity, first person past tense, no chapter headings, no markdown, output ONLY the narration text exactly as it will be read aloud. NEVER use an em dash (the "—" character) anywhere in the output; use a comma, period, or "and"/"but" instead. This variant runs LONG: aim for the top of the target word range or beyond, since the procedural detail needs room to breathe."""


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
    raw_json = _call_deepseek_json(
        f"""Generate {n} fresh premises for first-person family-betrayal revenge stories (YouTube long-form niche). Each premise: 1-2 sentences, hyper-specific (who betrayed, what was taken incl. a dollar amount or concrete stake, what the comeback is). Narrator is ALWAYS a woman aged 24-45 (channel voice is female). Vary the betrayer (sister/brother/parents/in-laws) and the arena (inheritance, wedding, company, house, medical). Avoid anything similar to these already used:\n{used}\n\nReturn ONLY a JSON array of strings.""",
        r"\[.*\]",
    )
    premises = json.loads(raw_json)
    next_id = max([s["id"] for s in data["stories"]], default=0) + 1
    for p in premises:
        data["stories"].append({"id": next_id, "premise": p, "status": "pending"})
        next_id += 1
    _save(data)
    print(f"    Queue topped up with {len(premises)} premises")


# Fraction of stories that use the richer procedural-thriller variant
# (see HEIST_SCHEMA docstring above) instead of the plain emotional-drama
# SCHEMA. User request 2026-07-04: make it "a variation of our template",
# not a full replacement, so most stories stay on the original schema.
HEIST_SCHEMA_RATIO = 0.35


def generate_script(story):
    words_hint = f"{SCRIPT_MIN_WORDS}-{SCRIPT_MAX_WORDS}"
    rng = random.Random(story["id"])
    use_heist = rng.random() < HEIST_SCHEMA_RATIO
    schema = HEIST_SCHEMA if use_heist else SCHEMA
    variant_name = "heist-thriller" if use_heist else "plain-drama"
    print(f"    Schema variant: {variant_name}")

    script = call_deepseek(
        f"Premise: {story['premise']}\n\nWrite the full script now. Target length: {words_hint} words. Remember: output ONLY the narration text.",
        system=schema,
        max_tokens=32000,
    )
    wc = len(script.split())

    # At this word-count target, one extension pass is rarely enough, so
    # loop with a cap so a single stubborn generation can't run away with cost.
    attempts = 0
    while wc < SCRIPT_MIN_WORDS and attempts < 3:
        attempts += 1
        print(f"    Script short ({wc} words, need {SCRIPT_MIN_WORDS}+), extension pass {attempts}/3...")
        script = call_deepseek(
            f"Premise: {story['premise']}\n\nHere is a draft that is too short ({wc} words, need {words_hint}). Rewrite it at full target length by DEEPENING every section with more scenes, more procedural/emotional detail, and more beats, without changing the plot or ending. Output ONLY the narration text.\n\nDRAFT:\n{script}",
            system=schema,
            max_tokens=32000,
        )
        wc = len(script.split())
    return script


THUMB_LINES_RULES = """Also write "thumb_lines": a 5-segment escalating thumbnail script copying the exact proven structure of the niche's top-performing channel:
1. "setup" (short, yellow text): the lie or betrayal setup, ALL CAPS, 3-6 words.
2. "twist" (short punchy, magenta text, biggest): the immediate consequence, ALL CAPS, 3-6 words.
3. "context" (longer, white text): additional buildup context building to the climax moment, ALL CAPS, 8-14 words.
4. "climax1" (white text on a red highlight box): first half of the shocking climax moment, ALL CAPS, 4-8 words.
5. "climax2" (yellow text on a red highlight box): second half / punchline of the climax moment, ALL CAPS, 4-8 words.

Each segment is ALL CAPS, no em dash. Together they should read like an escalating true-crime-style thumbnail teaser, not a repeat of the video title."""


def generate_metadata(story, script):
    raw_json = _call_deepseek_json(
        f"""For this YouTube revenge-story video, write metadata. {TITLE_RULES}

{THUMB_LINES_RULES}

Story premise: {story['premise']}
Opening of script: {script[:1200]}

Never use an em dash (the "—" character) anywhere in any field; use a comma, period, or "and"/"but" instead.

Return ONLY JSON: {{"title": "...", "description": "2-3 sentence description ending with 3 relevant hashtags", "tags": ["10-14 tags"], "thumb_text": "6-10 word emotional punchline for the fallback thumbnail, ALL CAPS", "thumb_lines": [{{"style": "setup", "text": "..."}}, {{"style": "twist", "text": "..."}}, {{"style": "context", "text": "..."}}, {{"style": "climax1", "text": "..."}}, {{"style": "climax2", "text": "..."}}]}}""",
        r"\{.*\}",
    )
    return json.loads(raw_json)
