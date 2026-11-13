# Reading the contest — documents, intent, winners, limits, evidence, kill round

Load the section the current phase needs. Everything here is procedure; the facts come from the contest being read.

## 1. Governing documents

An organizer's public text is layered, and the more specific and the more recent layer wins.

| Layer | Typically holds |
|---|---|
| Announcement, landing page, press | theme, dates, prizes: the cover |
| Rules tab, participation terms | eligibility, IP, disqualification, who decides |
| FAQ | exceptions, post-submission updates, what judges will or will not open |
| Submission form (file or field instructions) | file names, length limits, signature, anonymity and upload rules found nowhere else |
| Kickoff deck, organizer chat, email | criteria published late, mid-event rule changes |

- Read the terms layer first. Where the terms forbid automated access or collection, stop fetching and ask the entrant to save the pages from a browser.
- Read the layer itself: save each page once (`curl -sL -o rules.html <url> && wc -c rules.html`), keep the byte count, and cite `file:rules.html`. The gate strips tags from saved HTML before it checks a quote.
- Download the application form and convert it to text beside the original. Review-anonymity rules, field limits and signature rules are often only there.
- Not a reading: a fetch tool's summary, a search snippet, an aggregator's listing, a subagent's report, your own earlier notes. Conditional and exception clauses are the first thing a summary drops.
- A JavaScript or login wall is `blocked`. Ask the entrant for a screenshot with a specific request: which screen, which element to open, what to read back. Do not tell them to pick an option from a list you have not seen.
- "The rules do not mention X" is a claim only with a control: count X's tokens and, on the same file, tokens that must be present. All-zero controls mean the check failed, not that X is absent. Run ASCII tokens as `LC_ALL=C grep -ciw`, non-ASCII tokens as `grep -cF`.
- Silence is not permission. An unstated limit or rule is `unstated`; ask the organizer in writing and keep the reply as a document layer.
- What a thing is (a track, a mode, a category) and what is allowed in it are separate rulings, usually in separate layers. Do not define a track from its usage rules.
- When old and new tracks coexist, check which track the clause belongs to before applying it.
- Label every ruling `raw-verified`, `via-summary` or `unverified`, and keep the label when the ruling moves into a table. "None" and "only" are written only where the check actually ran; elsewhere write "not investigated".

## 2. Organizer intent

Why the event exists is read from, in order: the stated goal, the required technology, the prize structure (what the top prize rewards, special prizes), the sponsor list, who sits on the panel, what the organizer publicly did with earlier winners.

- Quote the sentence. An intent without a quote is a guess.
- The intent is where ideas come from. An idea that sits inside the organizer's stated goal, or next to the organizer's own product, is `wounded` at most on that ground, unless a published result shows that zone losing.
- When the intent names a required model, API or dataset, give each one a named job in the product and say what breaks without it.

## 3. Past winners and the field

Use only what the organizer or the entrants themselves published: winner announcements, public galleries, public repositories, recorded demo days.

- Collect at least three past winners and at least one finalist or non-selected entry. Winners alone show what winners share with everyone. An entry known only by its name is recorded with `detail: name_only` and does not count toward the three.
- For each, record what the judge saw: first screen, demo moment, the number shown, how the required technology appeared. Record the method, never only the rank.
- First edition: use the organizer's or sponsor's other events, then events with the same format and rubric wording. Write why each proxy is comparable.
- A public vote is evidence of what judges score only when the vote is the decider.
- Several independent sources pointing at one idea is a crowding forecast as well as a quality signal: expect many entries there and write the difference a judge will see.
- Keep a search log: query, surface, outcome `hits | zero | blocked`.

When past entries are public, compare them on observed properties rather than impressions, with your own entry as one row: what the first screen promises and shows; steps to the first result; whether a sample is preloaded for a first run with no input; any gate before the core moment (login, onboarding); whether the required technology is visibly doing work; what result a judge can keep or export. Gaps are properties the field fills and you do not.

## 4. Format limits and logistics

Pin each with a quoted sentence. Otherwise it is `tba` (the organizer wrote that it will be announced: quote that sentence and set `recheck_by`) or `unstated` (nobody said anything: record the date the organizer was asked, or an assumed value with its basis, such as a past edition's limit or the schedule arithmetic).

- Presentation: exists or not, live or recorded, on site or remote.
- Slides: maximum count; whether cover, team and appendix slides count; aspect ratio; file type and size.
- Time: minutes to present, minutes for questions, what happens at the limit.
- Deck due date: often days before the presentation; the deck is then frozen.
- Machine: own laptop or the organizer's; fonts, video, network and audio on that machine.
- Language of slides and speech.
- Evaluation window for asynchronous review: when judges open the link. Unknown means the submitted link stays on the last build judged as passing from submission close.
- Sponsor resources: which outputs are derivatives that must be destroyed or need written permission to publish. Write the list the day the resources enter the build.

## 5. Evidence for ideas

- Tiers: `primary` (official data, filings, the affected person's own published words), `secondary` (reporting, summaries), `self` (the entrant's own experience), `vendor` (anyone selling a fix). A vendor's description of a pain is not the user's pain.
- A base rate is a count beyond the entrant: how many, how often, counted where, in which window. First-person frequency alone does not show the problem is bigger than one person.
- Before comparing two figures, write each one's population, event and window. Two figures counting different events do not make a rate.
- In public comment threads count asks, not opinions, and count replies to an offer apart from spontaneous asks.
- A failed fetch is `blocked`, an empty result is `zero`. Name blocked sources in the output.

## 6. Kill round

Run before anything is built, once per proposal, each in a separate pass with no shared context (parallel agents when the runtime has them; otherwise sequential, and say so).

- Instruction, verbatim: "Kill this. This is refutation, not confirmation. When it is ambiguous, rule that it died." Asking to "evaluate" returns support.
- Angles to give each killer: most entrants will submit this · a published past winner already did it · a rule or licence forbids it · the organizer's or sponsor's product already does it · a prompt alone does it · the demo cannot run on an empty input · the entrant cannot get the input alone before the deadline.
- Each report lists the attacks that failed and answers "what would have to change for this to live".
- Record `dead` only with the killing sentence quoted from a source. A death on ambiguity, on "a competitor exists", or on closeness to the organizer's product is `wounded`.
- Adopt an escape only when two killers attacking different proposals name it. Log single-source escapes.
- The field default is the comparator, not a candidate: the pick must show one difference against it that a judge sees.
- A kill is dated evidence, never a permanent prohibition. With untried design variables left, write "this implementation is dead", not "this direction is dead".
- Closing an axis mid-build needs: what was tried, what was not, what would reopen it, and a `stop_by` date or observable for whatever stays open.
