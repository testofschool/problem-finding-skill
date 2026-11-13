---
name: "hackathon-win-protocol"
description: "Builds an evidence-backed submission for judged hackathons and contests: reads organizer intent, past winners, judge panel, rubric and format limits from primary sources, then gates evidence-backed ideas and a proof for every criterion with one script. Use for '해커톤 어떻게 접근하지', '주최 의도랑 심사위원 분석해줘', '공모전 뽑히려면', 'how do I win this hackathon'. Not for metric-scored leaderboards."
---

# hackathon-win-protocol — prepare a sourced submission

A judged contest is decided by people scoring named criteria inside a fixed format. Read who decides, on what and in what format; then put a sourced answer to every criterion where the judge actually looks. The procedure helps find missing evidence and organize the submission around those criteria. It does not predict judging outcomes or guarantee selection.

One file, `WINCASE.json`, holds the case. `scripts/win_case_gate.py` refuses to call it ready while a cell is empty, guessed, or read from a summary.

This skill is procedure only. It ships no data about any real contest, organizer, judge or entrant, and nothing in it is tuned to one person; every fact in a case comes from the user's own contest, read from that contest's public pages.

## Scope

- For events where people choose: a panel, a vote, or both; live presentation or asynchronous review. When rank is computed from a metric, say this skill does not apply and stop.
- The entrant states the target (which round or prize) and the signal that shows it was reached. Ask once when it is missing; never invent it.
- Rules outrank strategy. An unmet eligibility clause stops the run until it is resolved.
- "Found nothing" is written as `zero` (looked, nothing there) or `blocked` (could not look). Only `zero` supports a claim.
- Public, professional sources only. Nothing here licenses collecting private information about judges or other entrants, or fetching a site against its terms.

## Run order

Start by running `python3 scripts/win_case_gate.py` with no arguments: it prints a passing verdict on a bundled synthetic sample. Copy `examples/WINCASE.sample.json`, replace every cell, and run the gate after each phase:

`python3 scripts/win_case_gate.py WINCASE.json --phase read` (then `idea`, `case`).

- Exit 1 lists the cells to fill. Fill them from sources; do not reword a cell to get past a rule.
- Open items are the assumptions the case rests on. Each is addressed to the organizer or to the entrant; pass them on that way.
- No idea is proposed before `read` passes. No build starts before `idea` passes. Nothing is submitted before `case` passes.
- Multi-stage contests: build the case for the stage scored next. A later stage's rubric and limits that the organizer says will be announced are `tba` (the organizer's sentence, source, `recheck_by`), which passes `read` and stays open.
- Load a reference only in the phase that names it.

### Phase 1 — read the contest (`read`)

Details, tables and commands: `references/reading-the-contest.md`.

- **Documents.** List at least two layers. The governing clause is rarely on the announcement; look in the rules tab, the FAQ, the downloadable submission form, the terms, the organizer's chat or email. Read the site's terms first: where they forbid automated access, fetch nothing further and ask the entrant to save the pages. Otherwise save each page once and cite `file:<path>`; the gate checks every quote against the saved file. A fetch tool's summary, a search snippet and a subagent's report are not readings.
- **Decider and eligibility** come first: who chooses, in the organizer's words, and every clause that can disqualify. Mark a clause `unknown` with `ask: entrant` or `ask: organizer`, and `pending` when it is an action the entrant still owes.
- **Intent.** Quote why the organizer runs the event: stated goal, required technology, prize structure, sponsors. Ideas start here.
- **Rubric.** Each criterion verbatim with its weight. Unpublished: name the proxy.
- **Past winners.** At least three that the organizer or the winners published, with what the judge saw, plus at least one finalist or non-selected entry as control. First edition: the organizer's or sponsor's other events, with the reason they compare. An entry known only by name does not count.
- **Judges.** Follow `references/judge-panel.md`: every attribute sourced or left out, every implication tied to something that judge wrote, built, funded or asked.
- **Limits.** Presentation or not, slide maximum (and whether cover and appendix count), minutes, Q&A minutes, file format, deck due date, whose computer, evaluation window. An unstated limit is not unlimited: write the question for the organizer and record the date it was sent, or record an assumption with its basis. A value with no basis is not entered.

### Phase 2 — choose the idea (`idea`)

- After `read` passes, seed slots from intent and criteria: `python3 scripts/idea_seed.py WINCASE.json --write WINCASE.json`. Fill each in terms of what a judge sees; drop slots with no honest fill.
- At least one proposal comes from outside the entrant's own history (a published past winner's method, a sponsor case study, an unfamiliar field), with its source.
- Add the `field_default`: what most entrants will submit, with the basis it was read from. The pick must show one difference against it that a judge sees.
- Evidence on the pick: two or more quoted lines with sources, one or more primary, and one base rate measured beyond the entrant (how many, how often, counted where). A vendor's account of a pain is not the user's.
- Kill round, before anything is built: one separate pass per proposal with the instruction "Kill this. This is refutation, not confirmation. When it is ambiguous, rule that it died." Use parallel agents when the runtime has them; otherwise run the passes one after another and say so. Record `dead` only with the killing sentence quoted from a source; an idea ruled out on ambiguity, on a competitor's existence, or on closeness to the organizer's own product is `wounded`. Adopt an escape route only when two killers attacking different ideas name it.
- The pick fills every heavy criterion (weight 15 or more by default, `--vacate-floor` to change; every criterion when unweighted). A principle of the entrant's that leaves a criterion empty is dropped or conceded in writing with the points given up.
- Present the proposals, verdicts and evidence, and stop. The entrant picks.
- The day the pick is made, write the first build session's date and a day-one skeleton (one real input through to one real output). An idea whose first run needs another person's data, recording or consent is swapped for one the entrant can run alone.

### Phase 3 — make the case visible (`case`)

- For each criterion write what the judge sees, where (slide number, demo second, form field) and the proof with its source, using the organizer's wording of the criterion.
- When judges open the link or run the artifact themselves, their first run has no login, no file and no instructions. It must reach a full result from bundled sample data. Record how it was invoked and keep the run log; a remembered pass is not a pass.
- The submission text carries three lines: how often the problem occurs for the entrant (a number), a base rate beyond the entrant, and a recon sentence (which terms were searched among published entries, how many were found, how this differs).
- A written requirement no script can measure gets a named human check before submission, or is listed as unjudged in the first line of the submission record.
- A planned deck is recorded as `deck.slides_planned`; the gate fails a count over the limit.
- Sponsor data or keys in the build: list which outputs must be destroyed or need written permission before anything is published.

### Submit

- From submission close until results, the link serves the last build the entrant judged as passing. Preview images and index pages may change; scored screens do not.
- Re-read the submitted text itself (the confirmation copy), not the draft, for the three lines and the criterion wording.
- Trace every figure in the deck and the form to its source once before submission. An adjective without a number is measured or cut.

## Output

`python3 scripts/win_case_gate.py WINCASE.json --report` prints the one-page brief: goal, decider, intent, the criterion table (verbatim, weight, what the judge sees, where, proof), judges with the signal behind each change, limits, then the phase verdicts and open items grouped by who must answer.

Reply in the entrant's language, in this order: the nearest deadline and anything that can disqualify; the verdict per phase; the brief; the exact questions to send the organizer; what the entrant must confirm.

## Failure modes

1. Proposing ideas before the rubric and limits are read from the governing layer.
2. Ruling from a summary and reporting it as read.
3. Writing "no limit" for a limit nobody stated.
4. Profiling judges by group traits instead of their own published signals.
5. Studying winners only, with no non-winner to compare.
6. Killing an idea because it sits inside the organizer's goal or because a competitor exists.
7. Filling a cell with a guess so the gate passes.

## Bundle

- `scripts/win_case_gate.py`: the gate and the brief. Exit 0 pass, 1 fail, 2 unreadable. Stdlib only.
- `scripts/idea_seed.py`: idea slots from intent and criteria.
- `examples/WINCASE.sample.json`, `examples/rules.sample.txt`: a synthetic passing case and its saved rules page. Every name in them is invented.
- `references/reading-the-contest.md`, `references/judge-panel.md`.
- `tests/test_win_case_gate.py`: one case per gate rule; `tests/trigger_cases.json`.
- `FIRST_RUN.md`: acceptance checklist. `CHANGELOG.md`: release notes.
