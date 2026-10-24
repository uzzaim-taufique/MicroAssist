# MicroAssist Troubleshooting Guide

This page explains the messages MicroAssist can show and how to fix them.

## 1. "Please enter your project requirements."

**What it means:** You pressed Enter without typing anything,
or you typed only spaces.

**How to fix:** Type a short description of your project,
for example: "A room monitor with a temperature sensor and Wi-Fi".
Then press Enter.

**Tip:** The more detail you give (sensors, Wi-Fi/Bluetooth, battery or mains power, budget), the better the recommendation will be.

## 2. "API key not found. Add GEMINI_API_KEY to your .env file and try again."

**What it means:** MicroAssist cannot find your Google AI API key.

**How to fix:**
1. Get a free key from https://aistudio.google.com/apikey
2. In the project folder, copy .env.example to a new file called .env
3. Open .env and put your key after GEMINI_API_KEY=
4. Start MicroAssist again with: python main.py

Never share your API key or upload the .env file to GitHub.

**Tip:** Make sure the file is named exactly `.env` (not `.env.txt`) and that there are no spaces around the `=` sign or inside the key.

## 3. "Could not connect to Google AI. Check your internet connection and try again."

**What it means:** MicroAssist could not reach Google AI.

**How to fix:** Check your Wi-Fi or internet connection, then try again.

**Tip:** If other websites open fine, a firewall, VPN or proxy may be blocking the connection. Try turning the VPN off.

## 4. "Google AI took too long to respond. Please try again in a moment."

**What it means:** Google AI did not answer within 30 seconds.

**How to fix:** Wait a minute and try again.

## 5. "Google AI returned an error. Check that your API key is correct, or try again later."

**What it means:** The API key is wrong, the free daily limit was
reached, or Google AI had a problem.

**How to fix:** Check the key in your .env file. If it is correct,
try again later.

**Tip:** Copy the key again from https://aistudio.google.com/apikey and paste it fresh, so no letter is missing or changed.

## 6. "No recommendation was received. Please try again or describe your project in more detail."

**What it means:** Google AI answered, but the answer was empty.

**How to fix:** Try again, or describe your project in more detail.
