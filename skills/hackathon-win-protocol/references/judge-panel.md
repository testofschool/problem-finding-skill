# Judge panel — who is scoring, and what that changes

The panel is the audience. The profile exists to choose examples, vocabulary, proof and order of emphasis that these specific people can score quickly. It is built from what each judge has published, never from what a group of people is assumed to like, and it is kept in the entrant's own case file, not published.

## Sources, in order

1. The organizer's judge page or announcement (name, title, affiliation, bio).
2. The judge's own professional output: talks, papers, posts, repositories, products shipped, portfolio companies, interviews.
3. Earlier events the judge scored: which entries they awarded, feedback they gave in public, questions they asked on recorded demo days.
4. The judge's employer: what it sells, what it announced this year, what it is hiring for.

Professional, public sources only. No private accounts, family, addresses or anything the judge did not publish in a professional capacity.

## Fields per judge

| Field | Rule |
|---|---|
| `name`, `affiliation` | from the organizer's page; `affiliation` carries its source |
| role, seniority, domain (engineer, designer, investor, operator, academic, official) | `{value, source}` |
| career stage or age band, gender | record only when the organizer's bio or the judge's own profile states it; otherwise leave the field out. A guess from a photo or a name is not a value. The gate fails any attribute without a source. |
| `signals` | things this judge wrote, built, funded, awarded or asked: `{quote, source}` |
| `implications` | `{change, signal}`: a concrete change to the case, citing one signal by index |

An attribute alone produces no implication. "The panel is mostly senior executives" may shape register and pacing for the whole room; a claim about what one judge values needs that judge's own signal. The gate enforces this.

## Reading the panel as a whole

- Composition: count by domain. A panel of engineers scores "technical implementation" from the request log; a panel of operators scores it from whether it ran.
- Shared ground: the examples, units and references every judge already knows. Jargon only one judge knows goes to the appendix.
- The sponsor's judge: show the sponsor's product doing real work where the judge will see it. An integration that does nothing gives the judge nothing to score.
- The judge most likely to object: find the signal that predicts the objection and put its answer in the Q&A bank.
- Language and formality follow the panel's published material, not the entrant's habit.

## When the panel is unannounced

Record `status: unannounced`, the proxy (last edition's published panel, the organizer's own team) and `recheck_by`. Re-run the read phase on that date.

## Output

One line per judge in the brief: name, affiliation, the change, and the quoted signal behind it. Judges with no public signal are listed as "searched, none found", which is different from not searched.
