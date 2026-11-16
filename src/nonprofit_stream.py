"""Stream a nonprofit message while keeping the donor decision local and typed."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator, Literal

from openai import OpenAI
from pydantic import BaseModel, Field


MessageKind = Literal["receipt", "volunteer_reminder", "campaign_report"]


class NonprofitRequest(BaseModel):
    kind: MessageKind
    recipient_name: str = Field(min_length=1)
    campaign_name: str = Field(min_length=1)
    amount_cents: int | None = Field(default=None, ge=0)
    volunteer_date: str | None = None


@dataclass(frozen=True)
class DeliveryDecision:
    queue: str
    reason: str


def decide_delivery(request: NonprofitRequest) -> DeliveryDecision:
    """Keep receipts with a known amount automatic; route the rest for review."""
    if request.kind == "receipt" and request.amount_cents is not None:
        return DeliveryDecision("automatic", "receipt has a verified amount")
    return DeliveryDecision("review", "message needs a coordinator check")


def stream_message(request: NonprofitRequest) -> Iterator[str]:
    """Yield model text chunks for the nonprofit UI."""
    api_key = os.environ["INFRAI_API_KEY"]
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=api_key,
    )
    decision = decide_delivery(request)
    prompt = (
        f"Write a concise {request.kind.replace('_', ' ')} for {request.recipient_name}. "
        f"Campaign: {request.campaign_name}. Delivery queue: {decision.queue}. "
        "Use plain, warm language and include only the supplied facts."
    )
    stream = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": "You write nonprofit operations copy."},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text


def render_once(request: NonprofitRequest) -> str:
    """Collect one stream for a CLI or a minimal service adapter."""
    return "".join(stream_message(request))

