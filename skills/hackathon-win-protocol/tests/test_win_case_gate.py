#!/usr/bin/env python3
"""Regression cases for win_case_gate.py and idea_seed.py. Run from a copy: python3 -B tests/test_win_case_gate.py
Each case mutates the bundled sample and states the exit code and the rule that must fire. Exit 0 = all pass."""
import copy
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GATE = os.path.join(ROOT, "scripts", "win_case_gate.py")
SEED = os.path.join(ROOT, "scripts", "idea_seed.py")
SAMPLE = json.load(open(os.path.join(ROOT, "examples", "WINCASE.sample.json"), encoding="utf-8"))
RULES = open(os.path.join(ROOT, "examples", "rules.sample.txt"), encoding="utf-8").read()


def run(d, *args):
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "rules.sample.txt"), "w", encoding="utf-8").write(RULES)
        open(os.path.join(tmp, "rules.sample.html"), "w", encoding="utf-8").write(
            "<html><body><script>var x='<p>';</script><p>We want small clinics to adopt the <b>ExampleCo</b> scheduling&nbsp;API in daily work.</p></body></html>")
        p = os.path.join(tmp, "WINCASE.json")
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        r = subprocess.run([sys.executable, "-B", GATE, p] + list(args), capture_output=True, text=True)
    try:
        out = json.loads(r.stdout[r.stdout.index("{"):r.stdout.rindex("}") + 1])
    except ValueError:
        out = {}
    return r.returncode, out


def idea(d, i):
    return next(x for x in d["ideas"] if x["id"] == i)


def m_goal(d): d["goal"] = {"target": "win"}
def m_cover_only(d): d["documents"] = [x for x in d["documents"] if x["layer"] == "announcement"] + [{"layer": "press", "source": "news", "read": "raw"}]
def m_summary_only(d):
    for x in d["documents"]: x["read"] = "summary"
def m_metric(d): d["decider"]["who"] = "metric"
def m_inelig(d): d["eligibility"][0]["met"] = "no"
def m_paraphrase(d): d["host_intent"][0]["quote"] = "The sponsor would like clinics to use the API."
def m_weights(d): d["rubric"]["criteria"][0]["weight"] = 50
def m_truncated(d): d["rubric"]["criteria"][1]["verbatim"] = "Use of the ExampelCo API"
def m_winners_only(d): d["winners"]["entries"] = [e for e in d["winners"]["entries"] if e["result"] == "winner"] * 3
def m_guess_attr(d): d["judges"]["panel"][0]["age_band"] = {"value": "40s"}
def m_attr_implication(d): d["judges"]["panel"][1]["implications"] = [{"change": "use simpler words"}]
def m_no_signal(d): d["judges"]["panel"][1].pop("signals_searched")
def m_slides_silent(d): d["limits"]["slides"] = {"status": "unstated"}
def m_all_own(d): idea(d, "A")["origin"] = "own"
def m_no_baseline(d): d["ideas"] = [x for x in d["ideas"] if x.get("kind") != "field_default"]
def m_dead_no_source(d): idea(d, "C")["kill"] = {"verdict": "dead", "sentence": "it felt weak"}
def m_unattacked(d): idea(d, "C").pop("kill")
def m_vacate(d): idea(d, "A")["covers"]["C2"] = ""
def m_no_base_rate(d): idea(d, "A")["evidence"][0]["kind"] = "other"
def m_self_rule(d): d["self_rules"][0]["vacates"] = ["C2"]
def m_case_hole(d): d["case"] = [r for r in d["case"] if r["criterion"] != "C3"]
def m_empty_run(d): d["empty_run"]["result"] = "fail"
def m_deck_over(d): d["deck"]["slides_planned"] = 14
def m_deck_unknown(d): d.pop("deck")
def m_no_presentation(d):
    d["limits"]["presentation"] = {"required": False, "quote": "There is no live presentation.", "source": "FAQ screenshot"}
    for k in ("slides", "minutes", "qa_minutes", "file_format"):
        d["limits"][k] = {"status": "na"}
def m_unpublished(d):
    d["rubric"] = {"status": "unpublished", "proxy_source": "2029 rubric page", "criteria": [{"id": "C1", "verbatim": "usefulness"}, {"id": "C2", "verbatim": "API use"}, {"id": "C3", "verbatim": "demo"}]}
def m_judges_unannounced(d): d["judges"] = {"status": "unannounced", "proxy_source": "2029 panel page", "recheck_by": "2030-01-03"}
def m_tba(d):
    for k in ("slides", "minutes", "qa_minutes", "file_format"):
        d["limits"][k] = {"status": "tba", "quote": "Each finalist presents for 5 minutes followed by 3 minutes of questions.", "source": "file:rules.sample.txt", "recheck_by": "2030-01-10"}
def m_tba_bare(d): d["limits"]["slides"] = {"status": "tba"}
def m_assumed_bare(d): d["limits"]["slides"] = {"status": "unstated", "assumed": "10"}
def m_assumed_basis(d): d["limits"]["slides"] = {"status": "unstated", "assumed": "10", "basis": "the 2029 edition capped decks at 10"}
def m_name_only(d):
    for e in d["winners"]["entries"][1:]: e["detail"] = "name_only"
def m_unspecified(d): d["decider"]["who"] = "unspecified"
def m_pending(d): d["eligibility"][1]["met"] = "pending"
def m_html(d):
    d["host_intent"][0]["source"] = "file:rules.sample.html"
def m_conceded(d): d["self_rules"][0].update({"vacates": ["C2"], "conceded": {"points": 30, "by": "team lead"}})

CASES = [  # (name, mutation, args, expected exit, rule prefix that must appear or None)
    ("sample passes", None, [], 0, None),
    ("goal without signal", m_goal, ["--phase", "read"], 1, "R1"),
    ("announcement and press only", m_cover_only, ["--phase", "read"], 1, "R2"),
    ("everything read through a summary", m_summary_only, ["--phase", "read"], 1, "R2"),
    ("metric-scored contest", m_metric, ["--phase", "read"], 1, "R3"),
    ("eligibility not met", m_inelig, ["--phase", "read"], 1, "R4"),
    ("paraphrased intent", m_paraphrase, ["--phase", "read"], 1, "R5"),
    ("weights sum to 110", m_weights, ["--phase", "read"], 1, "R6"),
    ("criterion text not in the saved page", m_truncated, ["--phase", "read"], 1, "R6"),
    ("winners with no control", m_winners_only, ["--phase", "read"], 1, "R7"),
    ("guessed judge attribute", m_guess_attr, ["--phase", "read"], 1, "R8"),
    ("implication with no signal", m_attr_implication, ["--phase", "read"], 1, "R8"),
    ("judge with no signal and no search", m_no_signal, ["--phase", "read"], 1, "R8"),
    ("slide limit silently unstated", m_slides_silent, ["--phase", "read"], 1, "R9"),
    ("unpublished rubric with proxy passes", m_unpublished, ["--phase", "read"], 0, None),
    ("limits to be announced, quoted, pass", m_tba, ["--phase", "read"], 0, None),
    ("tba without the organizer's sentence", m_tba_bare, ["--phase", "read"], 1, "R9"),
    ("assumed limit without a basis", m_assumed_bare, ["--phase", "read"], 1, "R9"),
    ("assumed limit with a basis passes", m_assumed_basis, ["--phase", "read"], 0, None),
    ("winners known by name only do not count", m_name_only, ["--phase", "read"], 1, "R7"),
    ("decider unspecified passes as open", m_unspecified, ["--phase", "read"], 0, None),
    ("pending eligibility passes as open", m_pending, ["--phase", "read"], 0, None),
    ("quote checked inside saved HTML", m_html, ["--phase", "read"], 0, None),
    ("unannounced judges with proxy pass", m_judges_unannounced, ["--phase", "read"], 0, None),
    ("all ideas from own history", m_all_own, ["--phase", "idea"], 1, "I2"),
    ("no field default", m_no_baseline, ["--phase", "idea"], 1, "I3"),
    ("dead without a source", m_dead_no_source, ["--phase", "idea"], 1, "I4"),
    ("idea never attacked", m_unattacked, ["--phase", "idea"], 1, "I4"),
    ("pick empties a heavy criterion", m_vacate, ["--phase", "idea"], 1, "I5"),
    ("self rule empties a criterion", m_self_rule, ["--phase", "idea"], 1, "I6"),
    ("conceded self rule passes", m_conceded, ["--phase", "idea"], 0, None),
    ("no base rate", m_no_base_rate, ["--phase", "idea"], 1, "I7"),
    ("criterion missing from the case", m_case_hole, ["--phase", "case"], 1, "C1"),
    ("empty run failed", m_empty_run, ["--phase", "case"], 1, "C2"),
    ("14 slides against a limit of 10", m_deck_over, ["--phase", "case"], 1, "C3"),
    ("deck count missing passes as open", m_deck_unknown, ["--phase", "case"], 0, None),
    ("no presentation: limits may be na", m_no_presentation, [], 0, None),
]


def main():
    bad = 0
    for name, mut, args, want, rule in CASES:
        d = copy.deepcopy(SAMPLE)
        if mut:
            mut(d)
        code, out = run(d, *args)
        hit = rule is None or any(v.startswith(rule) for v in out.get("violations", []))
        ok = code == want and hit
        print("%s  %s  (exit %d, want %d%s)" % ("ok  " if ok else "FAIL", name, code, want, "" if rule is None else ", rule " + rule))
        bad += 0 if ok else 1
    # unreadable input
    r = subprocess.run([sys.executable, "-B", GATE, os.path.join(HERE, "does-not-exist.json")], capture_output=True, text=True)
    ok = r.returncode == 2
    print("%s  missing file exits 2 (exit %d)" % ("ok  " if ok else "FAIL", r.returncode)); bad += 0 if ok else 1
    # empty run of the gate itself
    r = subprocess.run([sys.executable, "-B", GATE], capture_output=True, text=True)
    ok = r.returncode == 0 and "bundled synthetic sample" in r.stdout
    print("%s  empty invocation runs the sample (exit %d)" % ("ok  " if ok else "FAIL", r.returncode)); bad += 0 if ok else 1
    # seeding never manufactures a pass
    with tempfile.TemporaryDirectory() as tmp:
        d = copy.deepcopy(SAMPLE); d["ideas"] = [x for x in d["ideas"] if x.get("kind") == "field_default"]; d["pick"] = None
        src, dst = os.path.join(tmp, "in.json"), os.path.join(tmp, "out.json")
        open(os.path.join(tmp, "rules.sample.txt"), "w", encoding="utf-8").write(RULES)
        json.dump(d, open(src, "w", encoding="utf-8"))
        r1 = subprocess.run([sys.executable, "-B", SEED, src, "--write", dst], capture_output=True, text=True)
        r2 = subprocess.run([sys.executable, "-B", GATE, dst, "--phase", "idea"], capture_output=True, text=True)
        n = len(json.load(open(dst, encoding="utf-8"))["ideas"])
    ok = r1.returncode == 0 and r2.returncode == 1 and n == 6
    print("%s  seeded skeletons still fail the idea phase (seed %d, gate %d, ideas %d)" % ("ok  " if ok else "FAIL", r1.returncode, r2.returncode, n)); bad += 0 if ok else 1
    print("\n%d failed" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
