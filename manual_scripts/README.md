# Manual scripts (no API cost)

Drop a finished story script here instead of letting the pipeline pay
Sonnet to generate it. This skips `agents/story_agent.py`'s `generate_script()`
entirely — the cache check in `scheduler.py` only looks at word count, it
doesn't care whether the text came from the API or was typed/pasted by hand.

## How to use

1. Pick a pending story from [`stories.json`](../stories.json) (currently:
   id 3, "I ran my dad's roofing company for 12 years..."). Story 2 is
   mid-render right now and doesn't need one.
2. Write the full narration (Sonnet or Opus, your subscription, not the API)
   following the rules below.
3. Save it here as `{id}.txt` — e.g. `manual_scripts/3.txt`.
4. Tell Claude ("naskah manual sudah siap di manual_scripts/3.txt") — it will
   check word count and the no-em-dash rule, move it into
   `output/scripts/{id}.txt`, commit, and push. The next pipeline run for
   that story sees a cached script already past `SCRIPT_MIN_WORDS` and skips
   straight to Kokoro TTS — no Sonnet API call, no cost.

## Format rules (must match, or the auto-check will flag it back to you)

- **Length**: 17,000-21,000 words (`SCRIPT_MIN_WORDS`/`SCRIPT_MAX_WORDS` in
  [`config.py`](../config.py)). Below 17,000 and the pipeline treats it as
  stale and re-generates via the API anyway, defeating the point.
- **No em dash** (the "—" character) anywhere. Use a comma, period, or
  "and"/"but" instead.
- **Plain narration only** — first-person past tense, no chapter headings,
  no markdown, no stage directions. Output exactly what Kokoro should read
  aloud, nothing else (no "Note:", no bracketed asides).
- **Narrator is always a woman, 24-55**, matching the channel voice.
- **Follow one of the two schemas** (see `SCHEMA` / `HEIST_SCHEMA` in
  [`agents/story_agent.py`](../agents/story_agent.py) for the exact beat
  structure) — either the plain 9-beat family-betrayal drama, or the
  11-beat procedural-thriller "heist" variant. Pick whichever fits the
  premise better.
