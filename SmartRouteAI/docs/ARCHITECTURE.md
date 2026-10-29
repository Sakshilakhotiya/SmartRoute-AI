# SmartRoute AI — architecture and research notes

## Request flow
1. React submits route preferences to the authenticated Express API.
2. Express validates input, resolves each location using Nominatim, and requests actual driving-route alternatives from OSRM.
3. Express forwards the returned route metrics and selected preferences to FastAPI.
4. FastAPI normalizes distance/time/cost, estimates fuel cost from user assumptions, and calculates a weighted relative score. It returns route alternatives, metrics, and explanations.
5. Express writes a planning-history record to SQLite; the user can persist a full route comparison as a saved route.
6. Dashboard/analytics aggregate persisted rows, not invented sample records.

## Data model
- `users`: unique email, bcrypt password hash, creation timestamp.
- `saved_routes`: owner FK, route labels, vehicle/priority/preference, selected distance/cost, JSON route snapshot, timestamp.
- `route_history`: owner FK, route labels, preference, selected distance/cost, timestamp.
- Foreign keys are enabled; indexes support user/date lookups. All saved-route read/delete endpoints scope by authenticated owner.

## Score model
Each cost-like metric is min-max normalized over the alternatives returned for this request, so lower travel time, distance and estimated fuel cost receive a higher utility. Accessibility and risk are neutral when no trustworthy source is available and are returned as `null` with explicit labels; they are not presented as verified data. User weights are normalized to sum to one; strategy and urgency modify the weighting policy. The score is relative to the current alternatives, not a probability, universal quality metric, or safety guarantee.

## External data limitations
- Nominatim geocoding and OSRM routing are public demo services. They may rate-limit or become unavailable; follow the providers' usage policies and configure alternative compatible services as needed.
- OSRM public routing does not provide reliable live traffic data. Its duration is a routing estimate.
- The API attempts to retrieve current destination context from Open-Meteo; if unavailable, weather remains null. This is not road-level weather and is not used to claim live road safety.
- Vehicle restrictions and road width are not verified because a trustworthy road-attribute pipeline is not included. The service reports unknown rather than asserting compliance.
- ML model is not pretrained or claimed trained. Import a real, documented dataset and run `python -m app.ml_training data.csv`; held-out MAE and RMSE are written only after training.

## Testing
FastAPI tests cover health, basic score behavior, strategy ranking, invalid input, and normalization. Backend includes a live health integration test. Execute the test commands in README after installing dependencies; no passing result is claimed until they run locally.
