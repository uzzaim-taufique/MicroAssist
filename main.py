
"""MicroAssist terminal entry point: run with `python main.py`.

Every request goes to the router agent first (SCRUM-15), which decides whether
the recommendation agent or the debugging agent should answer.
"""

from dotenv import load_dotenv

import errors
from microassist.debugger import get_debug_help
from microassist.recommender import get_recommendation
from microassist.router import CLARIFICATION, DEBUGGING, SELECTION, route
from microassist.verifier import format_report, verify

PROMPT = "Describe your project requirements or your problem: "


def main():
    load_dotenv()
    print("MicroAssist - microcontroller selection and debugging assistant")

    try:
        text = input(PROMPT).strip()

        while not text:
            print(errors.EMPTY_INPUT)
            text = input(PROMPT).strip()

        print("\nAsking Google AI...\n")

        agent = route(text)

        if agent == SELECTION:
            print("[Recommendation agent]\n")
            answer = get_recommendation(text)
            print(answer)
            print()
            print(format_report(verify(answer)))

        elif agent == DEBUGGING:
            print("[Debugging agent]\n")
            print(get_debug_help(text))

        else:
            print("[MicroAssist]\n")
            print(CLARIFICATION)

    except errors.MicroAssistError as exc:
        print(f"\n[MicroAssist] {exc}")

    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
