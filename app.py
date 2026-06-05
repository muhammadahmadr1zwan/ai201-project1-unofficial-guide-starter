"""Gradio web UI for the NYU off-campus housing RAG guide."""

from __future__ import annotations

import sys

import gradio as gr
from dotenv import load_dotenv

from query import ask

load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def handle_query(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question.strip())
    except EnvironmentError as exc:
        return str(exc), ""
    except Exception as exc:
        return f"Error: {exc}", ""

    sources = "\n".join(f"• {s}" for s in result["sources"])
    if not sources:
        sources = "(no documents retrieved)"
    return result["answer"], sources


def main() -> None:
    with gr.Blocks(title="NYU Off-Campus Housing Guide") as demo:
        gr.Markdown(
            "# NYU Off-Campus Housing Guide\n"
            "Ask about rent, neighborhoods, timing, dorm vs off-campus tradeoffs, "
            "and where students search for housing. Answers use **only** retrieved documents."
        )
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g., How much do NYU students pay for off-campus rent?",
            lines=2,
        )
        btn = gr.Button("Ask", variant="primary")
        answer = gr.Textbox(label="Answer", lines=12)
        sources = gr.Textbox(label="Retrieved from", lines=6)

        btn.click(handle_query, inputs=inp, outputs=[answer, sources])
        inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

        gr.Examples(
            examples=[
                ["How much do NYU students usually pay for off-campus rent?"],
                ["Which neighborhoods are realistic on a budget?"],
                ["How early should I start looking before fall semester?"],
                ["Is living off campus cheaper than dorming?"],
                ["Where do students find roommates or apartments?"],
                ["What is the best NYU dining hall for pizza?"],
            ],
            inputs=inp,
        )

    demo.launch()


if __name__ == "__main__":
    main()
