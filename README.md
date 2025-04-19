# Steel Grade Finder Telegram Bot

A Telegram bot that helps metallurgists and engineers find steel grades based on chemical composition. The bot searches through a database to identify steel grades that match the specified composition ranges.

## Features

- 🔍 Find steel grades based on chemical composition
- 📊 Element-by-element input with confirmation
- 📝 Easy data management through Excel
- 🔄 Simple database updates
- 🌐 Russian language interface
- 📈 User activity tracking and messaging

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram account
- Basic knowledge of steel grades and chemical compositions

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/it_metalloved_bot.git
cd it_metalloved_bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a new Telegram bot:
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the instructions
   - Copy the API token provided by BotFather

4. Configure the bot:
   - Open the `.env` file
   - Replace `your_bot_token_here` with your actual bot token:
   ```
   BOT_TOKEN=your_bot_token_here
   ```

5. Create the steel grade database:
   - Use the provided `steel_grades_template.xlsx` file as a template
   - Edit the file with your steel grade data
   - Initialize the database:
   ```bash
   python init_db.py
   ```

6. Start the bot:
```bash
python bot.py
```

## Usage

1. Open Telegram and search for your bot by username
2. Start a conversation with the bot by clicking "Start" or sending `/start`
3. Use the `/find` command to begin searching for steel grades
4. The bot will ask you to input each chemical element one by one:
   - For each element, enter a numerical value (e.g., `0.45` for carbon)
   - After entering a value, you'll see two buttons:
     - "Подтвердить" (Confirm) - to confirm the value and move to the next element
     - "Исправить" (Edit) - to re-enter the value for the current element
5. After entering all elements, the bot will search the database and return matching steel grades

## Data Management

### Excel File Structure

The `steel_grades.xlsx` file contains the following columns:
- `steel_grade`: The name of the steel grade (e.g., "AISI 1045")
- `specification`: The specification details (e.g., "Medium Carbon Steel")
- Element ranges: Min/max values for each chemical element (C, Si, Mn, S, P, Cr, Ni, Cu, Mo, V, Nb, Ti, N, W, B, Zr)

### Updating the Database

To update the database with new steel grade data:

1. Edit the `steel_grades.xlsx` file with your updated data
2. Run the database initialization script:
```bash
python init_db.py
```

## Database Structure

The SQLite database (`steel_database.db`) contains a table `steel_grades` with the following columns:
- `steel_grade`: The name of the steel grade
- `specification`: The specification details
- Element ranges: Min/max values for each chemical element

## Troubleshooting

- **Bot not responding**: Check your internet connection and ensure the bot is running
- **Database errors**: Verify that the Excel file has all required columns and valid data
- **No matches found**: Try adjusting your chemical composition values or add more steel grades to the database

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.