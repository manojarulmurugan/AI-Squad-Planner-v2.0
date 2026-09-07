# Known Issues

Findings recorded while measuring the current product. Phase 1 does not repair
product behaviour; its baseline intentionally makes these defects visible.

## K-001 — Severe-budget retries duplicate flights and activities

`TripState.flights` and `TripState.activities` use additive reducers. A severe
budget result loops back through destination selection and data fetching without
clearing the prior destination's values, so both sets remain in state. Budget,
fairness and itinerary calculations then consume duplicated data.

Offline budget-retry cases preserve this behaviour as the Phase 1 baseline.

## K-002 — Flight searches pass a city name as `arrival_id`

`parallel_data_fetch` passes `selected_destination` (for example,
`"New York City"`) into `search_flights`. SerpAPI's Google Flights engine
requires an uppercase three-letter airport code or a Google location ID and
returns HTTP 400. Production therefore degrades every flight to the fixed $300
estimate.

The Phase 1 baseline records this estimated flight response as an explicit,
labelled exception to the general anti-fallback fixture rule. Fixing the airport
mapping belongs to a later behaviour-changing phase.

## K-003 — HTTP exception text exposed the SerpAPI query URL

The safe SerpAPI response logger omitted the API key, but the outer exception
handler subsequently logged `HTTPStatusError.__str__`, whose request URL
contained the query-string key. Phase 1 changed that outer log to emit only the
HTTP status. This is a security-only logging correction, not product behaviour.

The SerpAPI key that appeared in development output should be rotated.

## K-004 — Production SSE handles only one city-selection pause

The severe-budget route can return to destination selection and interrupt for a
second city choice. The production SSE helper resumes once and then returns to
its caller without looping over a second interrupt, so the stream can end while
the graph remains paused. The evaluation runner does loop until completion and
therefore measures the graph itself correctly. Repairing the product stream is
behaviour-changing and remains out of Phase 1.

## K-005 — Flight schema cannot support arrival-alignment scoring

`FlightResult.depart_time` is the outbound departure from the member's origin,
while `return_time` is populated from the final leg's arrival. The state does
not retain destination arrival or return departure timestamps. The Phase 1
alignment scorer therefore marks estimated or legacy-schema flights
`scorable: false` instead of presenting a misleading pass/fail result.
