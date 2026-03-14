"""Interaction tools — human-in-the-loop communication."""

from langchain_core.tools import BaseTool, tool


def make_interaction_tools() -> list[BaseTool]:
    return [ask_user]


@tool
def ask_user(question: str) -> str:
    """Ask the user a question and wait for their response.

    Use this when you need clarification, confirmation, or additional
    information before proceeding. The question will be displayed to the
    user and execution pauses until they respond.

    Args:
        question: The question to ask the user.
    """
    # In CLI mode, this directly prompts stdin.
    # In gateway mode, this returns the question as a signal
    # for the frontend to collect user input.
    try:
        response = input(f"\n🤖 {question}\n> ")
        return response.strip()
    except EOFError:
        return "(no response)"
