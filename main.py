"""MicroAssist terminal entry point: run with `python main.py`."""

from dotenv import load_dotenv

from microassist.recommender import get_recommendation


def main():
    load_dotenv()
    print("MicroAssist - microcontroller recommendation assistant")
    requirements = input("Describe your project requirements: ").strip()
    if not requirements:
        print("Please describe your project requirements and try again.")
        return

    print("\nAsking Google AI...\n")
    print(get_recommendation(requirements))


if __name__ == "__main__":
    main()
