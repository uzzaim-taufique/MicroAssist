# MicroAssist

## Agentic AI Microcontroller Selection & Debugging Assistant

MicroAssist is an Agentic AI application that helps users select suitable microcontrollers, verify component compatibility, and develop and debug embedded-system projects.

A coordinator agent analyzes the user's request and directs it to the appropriate specialized agent (MCU Selection, Debugging, or Code/Hardware Guidance).

---

## Team Members & Scrum Roles

| Name | Roll No. | Scrum Role |
|---|---:|---|
| Umar Yasir | 514375 | Product Owner |
| Uzzaim Taufique | 533213 | Scrum Master |
| Hammad Siddiqui | 534614 | Developer |

---

## Technologies Used

- **Python**
- **Google AI / Gemini API**
- **GitHub** (Version Control & Contribution Tracking)
- **Atlassian Jira** (Scrum Backlog Management)

- ---

## How to Run (Sprint 1)

1. Install Python 3.10 or newer.
2. Install the libraries:
   ```
   pip install -r requirements.txt
   ```
3. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
4. Copy `.env.example` to a new file named `.env` and replace `your-api-key-here` with your key. `.env` is listed in `.gitignore`, so the key is never committed.
5. Run MicroAssist and type your project requirements when asked:
   ```
   python main.py
   ```

The instruction prompt is versioned in `prompts/recommender_v1.md`, and its evaluation is in `tests/prompt_evaluation_v1.md`.
