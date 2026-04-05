# Converter

Modern dark-themed unit converter desktop app built with Python and Tkinter.

## Features

- Clean dark interface with smooth real-time updates
- Eleven conversion categories
- Length, mass, area, time, data, volume, speed, temperature
- Currency with live exchange rates (falls back to static rates)
- Number base converter (binary, octal, decimal, hex)
- BMI calculator with category scale

All results update instantly as you type or change units.

## Screenshots

<img width="484" height="897" alt="image" src="https://github.com/user-attachments/assets/41da6834-59a9-430b-9d08-656ca6cb8394" />


## Installation

1. Make sure you have Python 3.8 or newer installed.
2. Clone the repository:
git clone https://github.com/Nanostar007/unit-converter.git
cd unit-converter
text3. Run the app:
python converter.py
textNo additional packages are required for basic use.  
Currency live rates need the `requests` library (optional).

## Usage

- Launch the app to see the category grid.
- Click any card to open that converter.
- Enter a value and select units. Results appear immediately.
- Use the back button to return to the home screen.
- Currency rates update automatically on startup when online.

## Categories

- Currency (live or static rates)
- Length
- Mass
- Area
- Time
- Data
- Volume
- Speed
- Temperature
- Numbers (base conversion)
- BMI

## Technical Notes

- Built entirely with Tkinter and ttk
- Threaded currency fetch to keep the UI responsive
- Precise conversion factors for all physical units
- Graceful offline handling for currency

## License

MIT License. Feel free to use and modify.

