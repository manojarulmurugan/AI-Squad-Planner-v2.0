# SquadPlanner Evaluations

## Read this before interpreting a score

The **offline** tier replays frozen tool responses and frozen LLM output. It
catches code regressions in routing, constraints, date arithmetic, scoring,
schema and wiring. It **does not measure itinerary quality** and cannot prove a
prompt or model improved.

The **live** tier calls real tools and models. Only it measures prompt/model
quality. It is manually gated because each five-case run spends roughly 20–25
of the application's 200-search monthly SerpAPI budget.

Run live after a prompt, model or prompt-input change, when the report identifies
a prompt replay miss, and once at each phase boundary to detect stale fixtures.

## Commands

From `backend/`:

```bash
./venv/bin/python -m pytest evals/ -q
./venv/bin/python -m evals.run
./venv/bin/python -m evals.report
RUN_LIVE_EVALS=true ./venv/bin/python -m evals.run --live
```

Tool and LLM controls are independent:

- `EVALS_TOOL_MODE=off|record|replay`
- `EVALS_LLM_MODE=off|record|replay`

This independence supports mixed diagnostic runs, but exact tool replay cannot
be combined with a fresh planner output for calibration. Meal-place queries and
route coordinates are derived from the planner's generated schedule, so a new
schedule produces new request keys and strict replay misses.

## Human calibration handoff

The 20 calibration itineraries in `evals/calibration/itineraries/` are harvested
from the 30 Session 1 recordings. Those recordings contain genuine live planner
output captured during the fixture run; rebuilding the calibration set simply
replays that output for $0 and makes no network calls:

```bash
./venv/bin/python -m evals.calibration.build
```

Selection is stratified across group size, trip length, dietary load and budget
spread, and also across clean, mixed and degraded deterministic-score bands.
The score-band metadata stays in `manifest.json` and is never returned by the
labelling API.

The labelling page is `/debug/label.html`. It requires an account with
`is_admin: true`; registration intentionally defaults that field to false.
Label pass 1 contains all 20 items. After a break, `/debug/label.html?pass=2`
blindly re-labels the first three items for the intra-rater consistency check.
Progress is saved after every item in `evals/calibration/labels.json`.

The page and its GET API never receive saved ratings, deterministic verdicts or
automated suggestions. Do not add any such value to the item payload. Session 3
must not run the model evaluator until the human labels are complete and
committed.

## Current-baseline caveat

K-002 in `docs/KNOWN_ISSUES.md` means production flight searches currently
degrade to estimated data. Flight fixtures intentionally preserve and clearly
label that current behaviour. The calibration page therefore shows the same
fixed $300 estimate for every member and does not render the raw flight list,
which can also contain abandoned-destination entries because of K-001. Other
fallback responses are rejected by the recorder.
