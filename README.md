# TimeToLeave

A Python 3.11+ command-line tool and private-chat Telegram bot that estimates when to leave for a driving trip.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env with your token, contact User-Agent and service endpoints.
.venv/bin/python telegram_bot.py
# Or use the interactive CLI:
.venv/bin/python main.py
```

Enter arrival as 24-hour `HH:MM` and buffer as whole minutes (for example `15`). `/start` resets a conversation; `/cancel` deletes it. Only private Telegram chats are processed. Estimates use the user's local clock, have no date or timezone conversion, and exclude live traffic. Departures on earlier days are explicitly labeled. Addresses use the first geocoding match; include city and country to reduce ambiguity.

## Deployment

### Railway (always running)

1. Push this repository to GitHub and create a Railway service from that repository. Railway builds the included `Dockerfile`; `railway.json` starts `python server.py`, checks `/health`, disables sleeping, sets one replica, requires the `/data` volume mount, and configures automatic restarts.
2. Attach a **persistent volume mounted at `/data`** before deploying. Set `DATABASE_PATH=/data/bot.sqlite3` in Railway Variables. Without a volume, conversation state is lost when a deployment is replaced.
3. Set `TELEGRAM_BOT_TOKEN` in Railway Variables. Set `GEOCODING_USER_AGENT` to your application name and contact, and configure your map-provider endpoints as described below. Do not upload `.env`.
4. Keep **one replica in one region**, disable **Serverless**, and use a plan that supports the configured **Always** restart policy. Free/trial plans only support limited On Failure retries; see [Railway restart policies](https://docs.railway.com/deployments/restart-policy). Disable PR preview deployments for this service or give previews their own bot token and volume. Stop any local copy of this bot before deploying.
5. Deploy. The server listens on `0.0.0.0:$PORT` (Railway supplies `PORT`). A public domain is optional: Telegram messages arrive through outbound long polling, without a webhook. If you generate a Railway domain, visit `/health` to check it.
6. Send **hi** to your bot in Telegram, answer the questions, and confirm you receive a trip estimate.

`GET /` returns service information. `GET /health` returns 200 only while the bot worker is alive and has successfully polled/processed updates within the last three minutes; otherwise it returns 503. The server exits if its bot worker or HTTP thread fails, allowing Railway to restart it. Temporary upstream errors retain the existing retry backoff. The health endpoint never exposes tokens, chat IDs, or addresses.

Railway's healthcheck is a deployment check, [not continuous monitoring](https://docs.railway.com/deployments/healthchecks). Add an uptime monitor to `/health` if you want outage alerts. [Serverless must remain disabled](https://docs.railway.com/deployments/serverless) for an always-running service. This setup runs continuously while Railway keeps the service active; provider outages and volume-backed redeployments can still cause interruptions.

To run the same server locally:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
# Open http://localhost:8080/health
```

The container copies only application Python files and dependencies; `.env`, local SQLite databases, and the virtual environment are excluded. The Railway container uses its default user so the mounted volume is writable. On another host, provision volume ownership before choosing an unprivileged container user. The server uses restrictive file permissions (`umask 077`).

### Operations

Run exactly **one bot process per token and database**, under a process supervisor with restart-on-failure. Polling does not require an inbound port. Remove any previously configured Telegram webhook before using polling. Provide `TELEGRAM_BOT_TOKEN` through your deployment secret store; never commit it or enable HTTP debug logging. Environment variables override `.env`.

Set `DATABASE_PATH` to a writable file on a persistent volume, owned by the service account. Run as an unprivileged user with restrictive file permissions (`umask 077`). Back up SQLite while the process is stopped (or with SQLite's backup API). Conversations and polling offsets survive restarts; stale conversations are purged on the next handled message after 24 hours. Completed and cancelled conversations are removed. Backups need their own retention policy.

Configure `GEOCODING_URL` with a Nominatim-compatible `/search` endpoint and `ROUTING_URL` with an OSRM-compatible base URL. Use managed or self-hosted endpoints with capacity and availability appropriate to your deployment. Requests use finite timeouts. Polling failures back off to 60 seconds; SIGTERM stops cleanly after an in-flight request finishes (allow at least 90 seconds before forced termination).

The default public Nominatim endpoint is for limited use only. Its [usage policy](https://operations.osmfoundation.org/policies/nominatim/) requires at most one request per second, application identification, attribution, caching, and no heavy use. The code serializes geocoding requests at least 1.1 seconds apart and keeps a bounded process-local cache. Set `GEOCODING_USER_AGENT` to identify your deployment and contact. Do not run multiple processes against the public service or treat it as a production availability guarantee. Users' addresses are sent to the configured geocoder, and coordinates to the router; disclose these providers in your deployment privacy notice.

SQLite state and the polling checkpoint commit together after a successful response. Telegram sends and local commits cannot be atomic: a crash or timeout after Telegram accepts a message may cause a duplicate response when retried. This is an at-least-once delivery design. Monitor process exits, repeated service-failure logs, disk capacity and provider availability. No public deployment or live Telegram smoke test is performed by the automated tests.

## Verify

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pip check
```

Tests mock external services and never send Telegram messages. CI runs on Python 3.11–3.13. Dependency versions are constrained by compatible major version; resolve and lock exact versions in your deployment build for reproducibility.
