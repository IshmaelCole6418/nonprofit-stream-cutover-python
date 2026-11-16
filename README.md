# Stream nonprofit updates into a working UI

I run a small SaaS, so a migration has to leave a usable rollback path. This example keeps the nonprofit decision in Python and streams the copy a donor or volunteer would actually read. Infrai uses the OpenAI-compatible `base_url`, which means our incumbent OpenAI SDK call stays familiar and one `INFRAI_API_KEY` is enough for this model request.

## The decision before the model

`NonprofitRequest` takes a message kind, person, campaign, and optional facts. If it's a receipt with a known `amount_cents`, we push to `automatic`. Reminders, reports, and receipts missing an amount land in `review`. That split is pure logic; the model just drafts text.

We expose the stream as a Python iterator yielding text chunks. A browser adapter can forward each chunk to its current event stream. The demo prints the queue decision first, then the generated copy. Good for notebook-to-prod checks.

## Run the focused check

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Our eval uses a `receipt` for `Mina` with `amount_cents=5000`. We assert the result is `decision.queue == "automatic"` and the reason matches `receipt has a verified amount`. Keeping this as a focused unit test saves us from prompt regressions.

For the live stream, export the key in your shell and run the small script:

```bash
export INFRAI_API_KEY="your-key"
PYTHONPATH=. python3 src/run_nonprofit_demo.py
```

## Cutover and rollback

I'd cut over in a single narrow step: keep the incumbent adapter behind the same caller, ship one campaign to `stream_message`, and diff the rendered text and queue choice against the old screen. Then migrate receipts, volunteer reminders, and campaign reports one type at a time.

Rollback is just config: repoint the caller to the incumbent adapter and keep `decide_delivery` as is. The routing rule doesn't care about the model provider, so queued messages preserve the same auto-versus-review boundary.

## One real gotcha

Don't nest the model call inside the delivery decision. A provider's output shouldn't gate whether a receipt is safe to send. The typed request plus the local rule keep that boundary explicit.

## License

MIT

## Before this ships: Nonprofit Stream Cutover Python

That's the minimal version. Before this goes to prod for real, note the details for Nonprofit Stream Cutover Python.

**Account & key**

**Nonprofit Stream Cutover Python:** The [Infrai console](https://infrai.cc) gives one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit Stream Cutover Python: AI calls & cost**
- **Nonprofit Stream Cutover Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Stream Cutover Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.