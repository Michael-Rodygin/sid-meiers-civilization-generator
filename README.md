# Civilization Starting Generator

A web-based random generator for Civilization game starting configurations. This tool helps players randomly assign bonuses, technologies, nations, and other starting elements for a fair and balanced game setup.

## Features

- **Random Starting Configuration**: Automatically generates random bonuses, technologies, and nations for each player
- **Multi-Player Support**: Supports 4-5 players
- **Victory Probability Calculator**: Calculates and displays victory probabilities for different victory types (Culture, Economy, War, Technology)
- **Player Seating Arrangement**: Randomly arranges player seating positions
- **Random Events**: Generates random events for each game session
- **Interactive Web Interface**: Built with Streamlit for easy use
- **Reroll Functionality**: Allows players to reroll their starting configuration

## Requirements

- Python 3.11+
- See `requirements.txt` for package dependencies

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CivilizationStartingGenerator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Ensure you have the `Civ_bonuses.xlsx` file in the project root directory.

2. Edit `main.py` to specify your players:
```python
players = ['Миша', 'Даня', 'Слава', 'Папа']
```

3. Run the application:
```bash
streamlit run main.py
```

4. The web interface will open in your browser. You can:
   - View each player's randomly generated starting configuration
   - Reroll individual player configurations
   - See victory probabilities
   - View player seating arrangements
   - See random events

## Project Structure

```
CivilizationStartingGenerator/
├── main.py                 # Main entry point
├── web_page.py             # Streamlit web interface
├── read_file.py            # Excel file parsing
├── random_generator.py      # Random generation logic
├── Civ_bonuses.xlsx        # Data file with bonuses, technologies, and nations
├── static/
│   └── img/                # Civilization images
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

1. The application reads starting configurations from `Civ_bonuses.xlsx`
2. Data is organized by tiers (1-6)
3. For each player, the system randomly selects:
   - 1 bonus from tier 1
   - 1 bonus from tier 2
   - 1 bonus from tier 3
   - 1 technology from tier 4
   - 1 nation from tier 5
4. Victory probabilities are calculated based on the selected bonuses
5. Random events are selected from tier 6

## Notes

- The Excel file (`Civ_bonuses.xlsx`) must be present in the project root
- Player names can be customized in `main.py` or through the web interface
- The application uses session state to maintain configurations during use

## License

This project is for personal/educational use.

