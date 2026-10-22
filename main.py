"""MicroAssist terminal entry point: run with `python main.py`."""

from dotenv import load_dotenv

import errors
from microassist.recommender import get_recommendation


def main():
    load_dotenv()
    print("MicroAssist - microcontroller recommendation assistant")
    try:
        requirements = input("Describe your project requirements: ").strip()
        while not requirements:
            print(errors.EMPTY_INPUT)  # ask again; no API call is made
            requirements = input("Describe your project requirements: ").strip()

        print("\nAsking Google AI...\n")
        print(get_recommendation(requirements))
    except errors.MicroAssistError as exc:
        print(f"\n[MicroAssist] {exc}")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()