# CHANGELOG — hackathon-win-protocol

## 1.1 — 2026-11-12
- Removed the presentation-coaching phase (showmanship, delivery, memorable-deck rules) and its reference file. The
  skill now ends at the proof table. Slide, time and Q&A limits are still read in the `read` phase, and a planned
  slide count over the limit fails the `case` phase.
- Removed the evidence reference. The package contains no data about any real contest, organizer, sponsor, judge or
  entrant: no event statistics, no outcomes, no names. Rules that rested only on that data were removed with it.
- Removed post-results gallery capture and vote analysis.
- Sample files use invented names only.
- Added an English trigger phrase; the description names no third-party platform.

## 1.0 — 2026-11-12
- First edition: `read`, `idea`, `case` phases gated by `scripts/win_case_gate.py`; idea slots by `scripts/idea_seed.py`.

## What this skill is
Procedure for reading a judged contest from its own public pages and for showing a sourced answer to every scored
criterion. It works the same for any entrant and any contest; nothing in it is tuned to a person or an event.

## What it does not cover
- Contests ranked by a computed metric.
- Choosing which contest to enter.
- Presentation coaching.

## Test status
- Gate: `tests/test_win_case_gate.py`, one case per rule plus pass-paths; run it from a copy of the folder.
- Triggering: `tests/trigger_cases.json` is a typed case list; no executed trigger measurement ships with this release.
- The rules are procedural. No claim is made that following them raises the chance of winning by any measured amount.
