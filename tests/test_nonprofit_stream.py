from src.nonprofit_stream import NonprofitRequest, decide_delivery


def test_receipt_with_amount_is_automatically_delivered():
    request = NonprofitRequest(
        kind="receipt",
        recipient_name="Mina",
        campaign_name="Community Pantry",
        amount_cents=5000,
    )

    decision = decide_delivery(request)

    assert decision.queue == "automatic"
    assert decision.reason == "receipt has a verified amount"

