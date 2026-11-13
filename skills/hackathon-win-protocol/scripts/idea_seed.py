#!/usr/bin/env python3
"""idea_seed.py — turns the pinned intent and rubric into idea slots to fill (run before the idea phase of the gate).

The gate checks that >=3 sourced proposals exist; it never produces them. This script lists the slots so ideas
start from what the judge scores, not from what the entrant already likes building.

Slots
  X  one per (intent Ii x heavy criterion Cj): what does a judge scoring Cj see that exists only because the organizer wants Ii?
  M  one max-coverage slot: one idea with a judge-visible line for every heavy criterion
  V  one per self-imposed rule that empties a criterion: keep the rule and still fill the criterion
  E  one external slot: an idea whose source lies outside the entrant's own history (gate rule I2)
Heavy = weight >= --vacate-floor (default 15); an unweighted or unpublished rubric makes every criterion heavy.
Also prints which heavy criteria no existing proposal covers (holes).

Usage: idea_seed.py WINCASE.json [--vacate-floor 15] [--write OUT.json]
  --write appends empty slot skeletons to "ideas" (covers left empty, so the gate still fails a pick nobody filled).
Exit 0 seeds produced · 1 intent or rubric missing · 2 unreadable input. Stdlib only.
"""
import argparse
import json
import sys


def heavy(rubric, floor):
    crit = rubric.get("criteria") or []
    nums = [c for c in crit if isinstance(c.get("weight"), (int, float)) and c.get("weight")]
    if rubric.get("status") == "unpublished" or len(nums) < len(crit):
        return [c["id"] for c in crit]
    return [c["id"] for c in crit if c["weight"] >= floor]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("wincase")
    ap.add_argument("--vacate-floor", type=float, default=15)
    ap.add_argument("--write")
    a = ap.parse_args(argv)
    try:
        d = json.load(open(a.wincase, encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(json.dumps({"result": "UNREADABLE", "error": str(e)}))
        return 2
    intents = d.get("host_intent") or []
    rubric = d.get("rubric") or {}
    missing = [k for k, v in (("host_intent", intents), ("rubric.criteria", rubric.get("criteria"))) if not v]
    if missing:
        print(json.dumps({"result": "NO_SEED", "missing": missing,
                          "fix": "pin the organizer's intent (quoted) and the rubric (verbatim) first"}))
        return 1
    hv = heavy(rubric, a.vacate_floor)
    verb = {c["id"]: c.get("verbatim", "") for c in rubric["criteria"]}
    seeds = []
    for i, it in enumerate(intents):
        for cid in hv:
            seeds.append({"id": "X-I%d-%s" % (i, cid), "kind": "proposal", "derived_from": ["I%d" % i, cid], "covers": {},
                          "prompt": "A judge scoring %s ('%s') sees ___, which exists only because the organizer wants: %s"
                                    % (cid, verb[cid], it.get("claim", ""))})
    seeds.append({"id": "M-all", "kind": "proposal", "derived_from": ["I%d" % i for i in range(len(intents))] + hv, "covers": {},
                  "prompt": "One idea with a judge-visible line for every heavy criterion: " + ", ".join(hv)})
    for r in d.get("self_rules") or []:
        for cid in r.get("vacates") or []:
            seeds.append({"id": "V-%s-%s" % (r.get("id"), cid), "kind": "proposal", "derived_from": [cid], "covers": {},
                          "prompt": "Keep the rule '%s' and still give the judge of %s ('%s') something to score"
                                    % (r.get("rule", ""), cid, verb.get(cid, ""))})
    seeds.append({"id": "E-external", "kind": "proposal", "derived_from": ["I%d" % i for i in range(len(intents))], "covers": {},
                  "origin": "external", "origin_source": "",
                  "prompt": "One idea whose source is outside your own history (a past winner, a sponsor case study, "
                            "a field you have not worked in); cite it in origin_source"})
    props = [x for x in (d.get("ideas") or []) if (x.get("kind") or "proposal") == "proposal"]
    matrix = {cid: [x["id"] for x in props if str((x.get("covers") or {}).get(cid, "")).strip()] for cid in hv}
    out = {"result": "SEEDED", "heavy_criteria": hv, "slots": len(seeds), "seeds": seeds,
           "existing_coverage": matrix, "holes": [cid for cid, who in matrix.items() if not who],
           "next": "fill each slot's covers in judge-visible terms, drop slots with no honest fill, then run win_case_gate.py --phase idea"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if a.write:
        ideas = d.get("ideas") or []
        have = {x.get("id") for x in ideas}
        for s in seeds:
            if s["id"] not in have:
                row = {k: v for k, v in s.items() if k != "prompt"}
                row["seed_prompt"] = s["prompt"]
                ideas.append(row)
        d["ideas"] = ideas
        json.dump(d, open(a.write, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
