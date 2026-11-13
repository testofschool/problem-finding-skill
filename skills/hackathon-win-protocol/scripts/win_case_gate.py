#!/usr/bin/env python3
"""win_case_gate.py — refuses "ready" while the win case has an empty or unsourced cell.

Usage
  python3 scripts/win_case_gate.py                      # no file: runs the bundled synthetic sample
  python3 scripts/win_case_gate.py WINCASE.json         # all three phases
  python3 scripts/win_case_gate.py WINCASE.json --phase read|idea|case
  python3 scripts/win_case_gate.py WINCASE.json --report   # one-page brief (Markdown) after the verdict

Exit 0 PASS · 1 FAIL (every violation listed) · 2 unreadable input. Stdlib only.

Phases and rules
  read   R1 goal (target + observable signal)
         R2 documents: >=2 layers, one more specific than the announcement, >=1 read as raw text or screenshot
         R3 decider (panel | vote | hybrid | unspecified) quoted; "metric" is out of scope
         R4 eligibility clauses quoted with met yes/no/unknown/pending ("no" fails; unknown names who must answer)
         R5 organizer intent quoted from a source (a file: source is checked to contain the quote;
            saved HTML is stripped to text before the check)
         R6 rubric verbatim, weights sum to 100, or unpublished with a named proxy
         R7 past winners: >=3 described entries (detail "name_only" does not count) with sources and what the
            judge saw, >=1 non-winner as control, or first edition / unavailable with proxies or a search log
            that separates zero from blocked
         R8 judges: announced -> affiliation with source per judge, no unsourced attribute,
            every implication cites a signal; unannounced -> proxy source + recheck date
         R9 format limits: presentation, slides, minutes, Q&A, file format each stated (quote), tba (the organizer's
            sentence that it will be announced, with recheck_by), or unstated (asked_on, or assumed with its basis)
  idea   I1 >=3 proposals derived from an intent or criterion   I2 >=1 from outside the entrant's own history
         I3 a field_default baseline exists                      I4 every proposal attacked; "dead" needs a quoted source
         I5 pick covers every heavy criterion and says how it beats the field default
         I6 a self-imposed rule that vacates a criterion is conceded with points
         I7 pick carries >=2 sourced evidence lines, >=1 primary, >=1 base rate measured beyond the entrant
  case   C1 every heavy criterion has: what the judge sees, where, and a sourced proof
         C2 the judge's first, empty run passes (with a log) when judges run the artifact themselves
         C3 a planned deck stays inside the slide limit
"""
import argparse
import html
import json
import os
import re
import sys

PHASES = ["read", "idea", "case"]
SPECIFIC_LAYERS = {"rules", "faq", "form", "terms", "chat", "email"}
READ_OK = {"raw", "screenshot"}
LIMIT_KEYS = ["slides", "minutes", "qa_minutes", "file_format"]


def _ws(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def _has(x, *keys):
    return isinstance(x, dict) and all(_ws(x.get(k)) for k in keys)


def _file_quote(base, src, quote):
    """True/False when src is file:<path>, None when the file is unreadable, 'url' otherwise."""
    src = _ws(src)
    if not src.startswith("file:"):
        return "url"
    path = re.sub(r":\d+(-\d+)?$", "", src[len("file:"):])
    try:
        body = open(os.path.join(base, path), encoding="utf-8", errors="ignore").read()
    except OSError:
        return None
    return _ws(quote) in _ws(_as_text(body))


def _as_text(body):
    """Saved HTML is compared as visible text: scripts, styles and tags removed, entities decoded."""
    if not re.search(r"<(html|body|div|p|span)\b", body[:20000], re.I):
        return body
    body = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", body)
    return html.unescape(re.sub(r"(?s)<[^>]+>", " ", body))


def _num(v, what):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        raise ValueError("%s is not a number" % what)


def heavy(rubric, floor):
    crit = rubric.get("criteria") or []
    weighted = rubric.get("status") != "unpublished" and any(_num(c.get("weight"), c.get("id")) > 0 for c in crit)
    return [c for c in crit if _num(c.get("weight"), c.get("id")) >= floor] if weighted else list(crit)


def check_read(d, base, errs, opens):
    g = d.get("goal") or {}
    if not _has(g, "target", "signal"):
        errs.append("R1 goal: write the target (which prize or round) and the observable signal that shows it was reached")

    docs = d.get("documents") or []
    layers = {_ws(x.get("layer")).lower() for x in docs if isinstance(x, dict)}
    if len(layers) < 2:
        errs.append("R2 documents: list at least 2 layers (announcement, rules, faq, form, terms, chat, email)")
    if not (layers & SPECIFIC_LAYERS):
        errs.append("R2 documents: only the announcement was listed; the governing clause usually sits in rules, FAQ, form or terms")
    if not any(_ws(x.get("read")).lower() in READ_OK for x in docs if isinstance(x, dict)):
        errs.append("R2 documents: no layer was read as raw text or a screenshot; a tool summary is not a reading")
    for x in docs:
        if isinstance(x, dict) and _ws(x.get("read")).lower() not in READ_OK:
            opens.append("document layer '%s' is %s, not read raw: nothing may be ruled from it" % (x.get("layer"), _ws(x.get("read")) or "unread"))

    dec = d.get("decider") or {}
    who = _ws(dec.get("who")).lower()
    if who == "metric":
        errs.append("R3 decider: ranking by a computed metric is outside this skill (no one is choosing)")
    elif who not in ("panel", "vote", "hybrid", "unspecified") or not _has(dec, "quote", "source"):
        errs.append("R3 decider: name who decides (panel | vote | hybrid | unspecified) with the sentence that says so and its source")
    elif who == "unspecified":
        opens.append("organizer: the rules say entries are judged but not by whom; ask who scores and whether any vote counts")

    elig = d.get("eligibility") or []
    none_stated = d.get("eligibility_none_stated") or {}
    if not elig and not (none_stated.get("layers_checked") or []):
        errs.append("R4 eligibility: quote each eligibility or disqualification clause, or record eligibility_none_stated.layers_checked")
    for k, e in enumerate(elig):
        met = _ws(e.get("met")).lower()
        if not _has(e, "clause", "source") or met not in ("yes", "no", "unknown", "pending"):
            errs.append("R4 eligibility[%d]: needs clause, source and met yes|no|unknown|pending" % k)
        elif met == "no":
            errs.append("R4 eligibility[%d]: not met: \"%s\"; resolve this before any other work" % (k, _ws(e["clause"])[:70]))
        elif met == "unknown":
            who_asks = "organizer" if _ws(e.get("ask")).lower() == "organizer" else "entrant"
            opens.append("%s: confirm eligibility: \"%s\"" % (who_asks, _ws(e["clause"])[:90]))
        elif met == "pending":
            opens.append("entrant: still to do: \"%s\"" % _ws(e["clause"])[:90])

    intents = [i for i in (d.get("host_intent") or []) if _has(i, "claim", "quote", "source")]
    if not intents:
        errs.append("R5 intent: no organizer intent with a quoted sentence and its source")
    for k, i in enumerate(intents):
        ok = _file_quote(base, i["source"], i["quote"])
        if ok is None:
            errs.append("R5 intent[%d]: source file not readable: %s" % (k, i["source"]))
        elif ok is False:
            errs.append("R5 intent[%d]: the quote is not in %s; copy the sentence, do not paraphrase" % (k, i["source"]))
        elif ok == "url":
            opens.append("intent[%d] quote is unverified against the page; save the page and cite file:<path>" % k)

    rub = d.get("rubric") or {}
    crit = rub.get("criteria") or []
    if not crit:
        errs.append("R6 rubric: no criteria")
    if rub.get("status") == "unpublished":
        if not _ws(rub.get("proxy_source")):
            errs.append("R6 rubric: unpublished, so name the proxy (last edition's rubric, the organizer's stated goals)")
        else:
            opens.append("rubric unpublished; working from proxy: %s" % _ws(rub["proxy_source"]))
    else:
        if any(not _ws(c.get("verbatim")) for c in crit):
            errs.append("R6 rubric: a criterion lacks its verbatim text")
        tot = sum(_num(c.get("weight"), c.get("id")) for c in crit)
        if crit and tot and abs(tot - 100) > 0.01:
            errs.append("R6 rubric: weights sum to %g, not 100" % tot)
        if crit and not tot:
            opens.append("rubric has no weights; every criterion is treated as heavy")
    rsrc = _ws(rub.get("source"))
    if crit and rsrc.startswith("file:"):
        for c in crit:
            ok = _file_quote(base, rsrc, c.get("verbatim"))
            if ok is None:
                errs.append("R6 rubric: source file not readable: %s" % rsrc)
                break
            if ok is False:
                errs.append("R6 criterion %s: verbatim text not found in %s; copied from a summary?" % (c.get("id"), rsrc))
    elif crit and rub.get("status") != "unpublished":
        opens.append("rubric text is unverified against the page; save the rules page and set rubric.source to file:<path>")

    w = d.get("winners") or {}
    status = _ws(w.get("status")).lower()
    listed = [e for e in (w.get("entries") or []) if _has(e, "name", "judge_saw", "source")]
    entries = [e for e in listed if _ws(e.get("detail")).lower() != "name_only"]
    if len(listed) > len(entries):
        opens.append("%d past entries are known by name only; they show nothing about what the judge saw" % (len(listed) - len(entries)))
    log = w.get("search_log") or []
    log_ok = [x for x in log if _has(x, "query", "surface") and _ws(x.get("outcome")).lower() in ("hits", "zero", "blocked")]
    if status == "found":
        if len(entries) < 3:
            errs.append("R7 winners: %d usable entries; need >=3, each with a source and what the judge saw" % len(entries))
        if not any(_ws(e.get("result")).lower() in ("finalist", "not_selected", "field") for e in entries):
            errs.append("R7 winners: no non-winner control; winners alone show what winners share with everyone")
    elif status in ("first_edition", "unavailable"):
        if not _ws(w.get("proxy_reason")):
            errs.append("R7 winners: say why the proxies are comparable (same organizer, sponsor, format or rubric)")
        if len(entries) < 3 and len(log_ok) < 3:
            errs.append("R7 winners: give >=3 described proxy entries, or a search log of >=3 queries marked hits|zero|blocked")
        if not any(_ws(e.get("result")).lower() in ("finalist", "not_selected", "field") for e in entries):
            opens.append("no non-winner control among the proxies; what the winners share may be what everyone had")
    else:
        errs.append("R7 winners: status must be found | first_edition | unavailable")
    for x in log_ok:
        if _ws(x["outcome"]).lower() == "blocked":
            opens.append("winner search blocked on %s ('%s'): not searched is not the same as none" % (x["surface"], x["query"]))

    j = d.get("judges") or {}
    jstatus = _ws(j.get("status")).lower()
    if jstatus == "announced":
        panel = j.get("panel") or []
        if not panel or not _ws(j.get("source")):
            errs.append("R8 judges: list the panel and the source that announces it")
        for p in panel:
            name = _ws(p.get("name")) or "?"
            if not _has(p.get("affiliation"), "value", "source"):
                errs.append("R8 judge %s: affiliation needs value and source" % name)
            for key, val in p.items():
                if key in ("name", "signals", "implications", "signals_searched", "note"):
                    continue
                if not _has(val, "value", "source"):
                    errs.append("R8 judge %s: attribute '%s' has no source; record it as unknown, never guess" % (name, key))
            sigs = [s for s in (p.get("signals") or []) if _has(s, "quote", "source")]
            if not sigs and not p.get("signals_searched"):
                errs.append("R8 judge %s: no signal (something they wrote, built, funded or judged) and no search recorded" % name)
            if not sigs and p.get("signals_searched"):
                opens.append("judge %s: searched, no public signal found" % name)
            for im in p.get("implications") or []:
                ref = im.get("signal") if isinstance(im, dict) else None
                if not _has(im, "change") or not isinstance(ref, int) or not (0 <= ref < len(sigs)):
                    errs.append("R8 judge %s: an implication must name the change and cite a signal by index; an attribute alone implies nothing" % name)
    elif jstatus == "unannounced":
        if not _has(j, "proxy_source", "recheck_by"):
            errs.append("R8 judges: unannounced, so name the proxy (last panel, organizer team) and a recheck date")
        else:
            opens.append("entrant: judges unannounced; proxy %s; recheck by %s" % (_ws(j["proxy_source"]), _ws(j["recheck_by"])))
    else:
        errs.append("R8 judges: status must be announced | unannounced")

    lim = d.get("limits") or {}
    pres = lim.get("presentation") or {}
    req = pres.get("required")
    if req in (True, False):
        if not _has(pres, "quote", "source"):
            errs.append("R9 limits.presentation: quote the sentence that says whether a presentation exists")
    elif _ws(req).lower() == "unknown" and _ws(pres.get("asked_on")):
        opens.append("organizer: presentation unknown; asked on %s" % _ws(pres["asked_on"]))
    else:
        errs.append("R9 limits.presentation.required: true | false with a quote, or \"unknown\" with asked_on")
    for key in LIMIT_KEYS:
        x = lim.get(key) or {}
        st = _ws(x.get("status")).lower()
        if st == "stated":
            if not _has(x, "value", "quote", "source"):
                errs.append("R9 limits.%s: stated, so give value, quote and source" % key)
        elif st == "tba":
            if not _has(x, "quote", "source", "recheck_by"):
                errs.append("R9 limits.%s: tba needs the organizer's sentence that it will be announced, its source and recheck_by" % key)
            else:
                opens.append("organizer: limit %s to be announced; recheck by %s" % (key, _ws(x["recheck_by"])))
        elif st == "unstated":
            if _ws(x.get("asked_on")):
                opens.append("organizer: limit %s unstated; asked on %s" % (key, _ws(x["asked_on"])))
            elif _has(x, "assumed", "basis"):
                opens.append("entrant: limit %s unstated; ASSUMED %s because %s (unstated is not unlimited)" % (key, _ws(x["assumed"]), _ws(x["basis"])))
            else:
                errs.append("R9 limits.%s: unstated, so record asked_on, or an assumed value with its basis (a past edition's limit, the schedule arithmetic)" % key)
        elif st == "na" and req is False:
            pass
        else:
            errs.append("R9 limits.%s: status must be stated | tba | unstated%s" % (key, " | na" if req is False else ""))


def check_idea(d, floor, errs, opens):
    rub = d.get("rubric") or {}
    crit = rub.get("criteria") or []
    ids = {c.get("id") for c in crit}
    intents = d.get("host_intent") or []
    valid = ids | {"I%d" % k for k in range(len(intents))}
    ideas = d.get("ideas") or []
    props = [i for i in ideas if _ws(i.get("kind") or "proposal").lower() == "proposal"]
    base_ideas = [i for i in ideas if _ws(i.get("kind")).lower() == "field_default"]
    if len(props) < 3:
        errs.append("I1 ideas: %d proposals; need >=3" % len(props))
    for i in props:
        src = i.get("derived_from") or []
        if not src or any(s not in valid for s in src):
            errs.append("I1 idea %s: derived_from must name an intent (I0..) or a criterion id; got %s" % (i.get("id"), src))
    if props and not any(_ws(i.get("origin")).lower() == "external" and _ws(i.get("origin_source")) for i in props):
        errs.append("I2 ideas: every proposal comes from the entrant's own history; add one whose source is outside it (a past winner, a sponsor case, an unfamiliar field) and cite it")
    if not any(_ws(b.get("basis")) for b in base_ideas):
        errs.append("I3 baseline: add kind \"field_default\" (what most entrants will submit) with the basis you read it from")
    for i in props:
        k = i.get("kill") or {}
        v = _ws(k.get("verdict")).lower()
        if v not in ("stood", "wounded", "dead"):
            errs.append("I4 idea %s: not attacked yet (kill.verdict stood | wounded | dead)" % i.get("id"))
        elif v == "dead" and not _has(k, "sentence", "source"):
            errs.append("I4 idea %s: ruled dead without a quoted source; record it as wounded" % i.get("id"))
    pick = d.get("pick")
    p = next((i for i in props if i.get("id") == pick), None)
    if not pick:
        errs.append("I5 pick: none yet; the build does not start without one")
    elif p is None:
        errs.append("I5 pick %s is not among the proposals" % pick)
    else:
        if _ws((p.get("kill") or {}).get("verdict")).lower() == "dead":
            errs.append("I5 pick %s was ruled dead" % pick)
        cov = p.get("covers") or {}
        for c in heavy(rub, floor):
            if not _ws(cov.get(c["id"])):
                errs.append("I5 pick %s leaves criterion %s (%s) with nothing for the judge to score" % (pick, c["id"], c.get("weight")))
        if not _ws(p.get("beats_field")):
            errs.append("I5 pick %s: write beats_field, the one difference a judge sees against the field default" % pick)
        ev = [e for e in (p.get("evidence") or []) if _has(e, "claim", "quote", "source")]
        if len(ev) < 2:
            errs.append("I7 pick %s: %d sourced evidence lines; need >=2 (claim, quote, source)" % (pick, len(ev)))
        if not any(_ws(e.get("tier")).lower() == "primary" for e in ev):
            errs.append("I7 pick %s: no primary evidence (official data, the affected party's own words); vendor and second-hand lines do not count" % pick)
        if not any(_ws(e.get("kind")).lower() == "base_rate" and _ws(e.get("tier")).lower() != "self" for e in ev):
            errs.append("I7 pick %s: no base rate measured beyond the entrant (how many, how often, counted where)" % pick)
    for r in d.get("self_rules") or []:
        for v in r.get("vacates") or []:
            if v in ids:
                con = r.get("conceded") or {}
                if isinstance(con.get("points"), (int, float)) and _ws(con.get("by")):
                    opens.append("conceded: rule %s gives up criterion %s (%g pt), accepted by %s" % (r.get("id"), v, con["points"], con["by"]))
                else:
                    errs.append("I6 self-rule %s empties criterion %s; drop the rule or record conceded.points and conceded.by" % (r.get("id"), v))


def check_case(d, floor, errs, opens):
    rows = {r.get("criterion"): r for r in (d.get("case") or []) if isinstance(r, dict)}
    for c in heavy(d.get("rubric") or {}, floor):
        r = rows.get(c["id"])
        if not r or not _has(r, "judge_sees", "where") or not _has(r.get("proof"), "value", "source"):
            errs.append("C1 criterion %s: needs judge_sees, where (slide, demo second or form field) and proof {value, source}" % c["id"])
    er = d.get("empty_run") or {}
    if er.get("applies") is True:
        if _ws(er.get("result")).lower() != "pass" or not _has(er, "invoked_as", "log"):
            errs.append("C2 empty run: judges run the artifact themselves, so record invoked_as, result pass and the run log")
    elif er.get("applies") is False:
        if not _ws(er.get("reason")):
            errs.append("C2 empty run: applies false needs a reason (judges never run it)")
    else:
        errs.append("C2 empty run: set applies true | false")
    lim = d.get("limits") or {}
    if (lim.get("presentation") or {}).get("required") is True:
        cap = _limit_value(lim, "slides")
        planned = (d.get("deck") or {}).get("slides_planned")
        if isinstance(planned, int) and cap is not None and planned > cap:
            errs.append("C3 deck: %d slides planned against a limit of %g" % (planned, cap))
        elif not isinstance(planned, int):
            opens.append("entrant: deck slide count not yet checked against the limit (%s)" % ("%g" % cap if cap is not None else "not yet known"))


def _limit_value(lim, key):
    x = lim.get(key) or {}
    raw = x.get("value") if _ws(x.get("status")).lower() == "stated" else x.get("assumed")
    m = re.search(r"\d+(\.\d+)?", _ws(raw))
    return float(m.group(0)) if m else None


def report(d, floor):
    rub = d.get("rubric") or {}
    rows = {r.get("criterion"): r for r in (d.get("case") or []) if isinstance(r, dict)}
    out = ["# Win case: %s" % _ws(d.get("contest")), ""]
    g = d.get("goal") or {}
    out.append("Goal: %s (signal: %s)" % (_ws(g.get("target")), _ws(g.get("signal"))))
    dec = d.get("decider") or {}
    out.append("Decider: %s (\"%s\")" % (_ws(dec.get("who")), _ws(dec.get("quote"))))
    for i in d.get("host_intent") or []:
        out.append("Intent: %s (\"%s\")" % (_ws(i.get("claim")), _ws(i.get("quote"))))
    out += ["", "| Criterion (verbatim) | Weight | What the judge sees | Where | Proof |", "|---|---|---|---|---|"]
    for c in rub.get("criteria") or []:
        r = rows.get(c.get("id")) or {}
        pr = r.get("proof") or {}
        out.append("| %s | %s | %s | %s | %s (%s) |" % (
            _ws(c.get("verbatim")), _ws(c.get("weight")) or "-", _ws(r.get("judge_sees")) or "EMPTY",
            _ws(r.get("where")) or "-", _ws(pr.get("value")) or "-", _ws(pr.get("source")) or "-"))
    j = d.get("judges") or {}
    out += ["", "Judges (%s):" % _ws(j.get("status"))]
    for p in j.get("panel") or []:
        sigs = p.get("signals") or []
        for im in p.get("implications") or []:
            if isinstance(im, dict) and isinstance(im.get("signal"), int) and 0 <= im["signal"] < len(sigs):
                out.append("- %s (%s): %s, because \"%s\"" % (_ws(p.get("name")), _ws((p.get("affiliation") or {}).get("value")),
                                                            _ws(im.get("change")), _ws(sigs[im["signal"]].get("quote"))))
    lim = d.get("limits") or {}
    bits = []
    for key in LIMIT_KEYS:
        x = lim.get(key) or {}
        st = _ws(x.get("status")).lower()
        bits.append("%s %s" % (key, _ws(x.get("value")) if st == "stated" else ("ASSUMED " + _ws(x.get("assumed")) if _ws(x.get("assumed")) else (st.upper() or "?"))))
    out += ["", "Limits: " + " · ".join(bits)]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gate for WINCASE.json")
    ap.add_argument("wincase", nargs="?", help="omit to run the bundled synthetic sample")
    ap.add_argument("--phase", choices=PHASES + ["all"], default="all")
    ap.add_argument("--vacate-floor", type=float, default=15)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    path = a.wincase or os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "examples", "WINCASE.sample.json")
    if not a.wincase:
        print("note: no WINCASE.json given; running the bundled synthetic sample")
    try:
        d = json.load(open(path, encoding="utf-8"))
        if not isinstance(d, dict):
            raise ValueError("top level must be an object")
    except (OSError, ValueError) as e:
        print(json.dumps({"result": "UNUSABLE", "error": str(e)}))
        return 2
    base = os.path.dirname(os.path.abspath(path))
    todo = PHASES if a.phase == "all" else [a.phase]
    phases, opens, all_errs = {}, [], []
    try:
        for ph in todo:
            errs = []
            if ph == "read":
                check_read(d, base, errs, opens)
            elif ph == "idea":
                check_idea(d, a.vacate_floor, errs, opens)
            else:
                check_case(d, a.vacate_floor, errs, opens)
            phases[ph] = "FAIL" if errs else "PASS"
            all_errs += errs
    except ValueError as e:
        print(json.dumps({"result": "UNUSABLE", "error": str(e)}))
        return 2
    if a.report:
        print(report(d, a.vacate_floor))
        print()
        print("Phases: " + " · ".join("%s %s" % (k, v) for k, v in phases.items()))
        for v in all_errs:
            print("- to fill: " + v)
        for who in ("organizer", "entrant", ""):
            for o in opens:
                head = o.split(":", 1)[0]
                if (who and head == who) or (not who and head not in ("organizer", "entrant")):
                    print("- open (%s): %s" % (who or "note", o.split(":", 1)[1].strip() if who else o))
    else:
        print(json.dumps({"contest": d.get("contest"), "result": "FAIL" if all_errs else "PASS", "phases": phases,
                          "violations": all_errs, "open_items": opens}, ensure_ascii=False, indent=1))
    return 1 if all_errs else 0


if __name__ == "__main__":
    sys.exit(main())
