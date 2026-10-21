# MicroAssist

An AI assistant that helps electronics students choose a microcontroller.
Built with the Google AI (Gemini) API. EC-360 Software Engineering, NUST.

Team: Uzzaim Taufique, Hammad Siddiqui, Umar Yasir, Abdullah

## How to run

You need Python 3.10 or newer.

1. Download the project:
```
   git clone https://github.com/uzzaim-taufique/MicroAssist.git
   cd MicroAssist
```
2. Install the libraries:
```
   pip install -r requirements.txt
```
3. Add your API key: copy `.env.example` to a new file called `.env`
   and paste your key from https://aistudio.google.com/apikey
4. Start the app:
```
   python main.py
```

## How to enter your requirements

When the app starts, it asks: "Describe your project requirements".
Type a short description and press **Enter**. Example:

```
I want to build a room-monitoring system with a temperature sensor and Wi-Fi connectivity.
```

Spaces at the start and end of your text are removed automatically.
The words inside your description are not changed.

## Run the tests

```
python -m unittest discover -v
```
The tests use a fake AI client, so they need no internet or API key.

## Help with error messages

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).