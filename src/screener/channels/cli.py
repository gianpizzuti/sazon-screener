"""Terminal channel: chat with the agent as a candidate.

    python -m screener.channels.cli [--debug] [--lang en]

Commands: /data shows the structured screening data, /quit exits.
--debug prints what the model understood and the stage after every message.
"""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.panel import Panel

from screener.engine.engine import TurnResult
from screener.factory import build_engine

console = Console()


def show(result: TurnResult, debug: bool) -> None:
    for message in result.messages:
        console.print(Panel(message.text, title="Sofía", title_align="left", border_style="green", width=72))
        if message.quick_replies:
            console.print("  " + "  ".join(f"[cyan][{q}][/cyan]" for q in message.quick_replies))
    if debug and result.analysis:
        a = result.analysis
        extracted = {k: v for k, v in a.extracted.model_dump(mode="json").items() if v not in (None, [])}
        console.print(
            f"[dim]intents={a.intents} lang={a.language}({'clear' if a.language_is_clear else 'unclear'}) "
            f"sentiment={a.sentiment} faq={a.faq_id} extracted={json.dumps(extracted, ensure_ascii=False)} "
            f"→ stage={result.stage.value}[/dim]"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the screening agent as a candidate.")
    parser.add_argument("--debug", action="store_true", help="show the model's understanding of each message")
    parser.add_argument("--lang", choices=["es", "en"], default=None, help="language of the opening message")
    args = parser.parse_args()

    try:
        engine = build_engine()
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1)

    result = engine.start(channel="cli", language=args.lang)
    conversation_id = result.conversation_id
    console.print(f"[dim]conversation {conversation_id} · /data to see the extracted data · /quit to exit[/dim]\n")
    show(result, args.debug)

    while True:
        try:
            text = console.input("[bold]Tú › [/bold]").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text == "/quit":
            break
        if text == "/data":
            console.print_json(engine.repo.get_state(conversation_id).data.model_dump_json())
            continue
        with console.status("Sofía está escribiendo…"):
            result = engine.handle(conversation_id, text)
        show(result, args.debug)
        if result.completed and engine.repo.get_summary(conversation_id) is None:
            with console.status("Generating recruiter summary…"):
                summary = engine.summarize(conversation_id)
            if summary:
                console.print(Panel(json.dumps(summary, ensure_ascii=False, indent=2), title="Recruiter summary", border_style="blue"))


if __name__ == "__main__":
    main()
