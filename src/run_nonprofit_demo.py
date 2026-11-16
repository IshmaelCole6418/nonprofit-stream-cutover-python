from nonprofit_stream import NonprofitRequest, decide_delivery, render_once


def main() -> None:
    request = NonprofitRequest(
        kind="receipt",
        recipient_name="Mina",
        campaign_name="Community Pantry",
        amount_cents=5000,
    )
    decision = decide_delivery(request)
    print(f"queue={decision.queue} reason={decision.reason}")
    print(render_once(request))


if __name__ == "__main__":
    main()

