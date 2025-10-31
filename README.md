# Steel Grades Bot 🤖

A Telegram bot that helps users find steel grades based on their chemical composition. The bot can search for exact matches or find the closest matching steel grade in the database.

## Features

- Search for steel grades by chemical composition
- Interactive interface for inputting composition values
- Find exact matches or closest matching steel grades
- User feedback and rating system
- Logging of user interactions
- Docker support for easy deployment

## Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)
- Telegram Bot Token (obtain from [@BotFather](https://t.me/BotFather))

## Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/mxteen/steel_grades_bot.git
cd steel_grades_bot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Telegram bot token:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### Docker Installation

#### Building the Container

1. **Ensure Docker is installed and running:**
   - Verify Docker installation:
     ```bash
     docker --version
     ```
   - Check if Docker daemon is running:
     ```bash
     docker info
     ```

2. **Build the Docker image:**
   ```bash
   docker build -t steel-grades-bot .
   ```

   This command will:
   - Use Python 3.11-slim as the base image
   - Install all dependencies from `requirements.txt`
   - Copy the application files into the container
   - Create the logs directory
   - Set up the container to run `bot.py` on startup

3. **Verify the image was created successfully:**
   ```bash
   docker images | grep steel-grades-bot
   ```

   You should see the `steel-grades-bot` image listed with its size and creation date.

4. **(Optional) Test the image:**
   ```bash
   docker run --rm steel-grades-bot python --version
   ```
   This should output Python 3.11.x and confirms the image is working correctly.

#### Running the Container

1. Run the container with environment variables and volume mounts for persistent data:
```bash
docker run -d \
  --name steel-bot \
  --restart unless-stopped \
  -e BOT_TOKEN=your_telegram_bot_token_here \
  -v $(pwd)/steel_database.db:/app/steel_database.db \
  -v $(pwd)/logs:/app/logs \
  steel-grades-bot
```

**Note for Windows (PowerShell):**
```powershell
docker run -d `
  --name steel-bot `
  --restart unless-stopped `
  -e BOT_TOKEN=your_telegram_bot_token_here `
  -v ${PWD}/steel_database.db:/app/steel_database.db `
  -v ${PWD}/logs:/app/logs `
  steel-grades-bot
```

**Alternative: Using .env file**
If you prefer to use a `.env` file, you can mount it as well:
```bash
docker run -d \
  --name steel-bot \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/steel_database.db:/app/steel_database.db \
  -v $(pwd)/logs:/app/logs \
  steel-grades-bot
```

The volume mounts ensure that your database and log files persist even when the container is removed or recreated.

#### Managing the Container

**Check container status:**
```bash
docker ps -a | grep steel-bot
```

**View container logs:**
```bash
docker logs steel-bot
```

**Follow logs in real-time:**
```bash
docker logs -f steel-bot
```

**Stop the container:**
```bash
docker stop steel-bot
```

**Start a stopped container:**
```bash
docker start steel-bot
```

**Restart the container:**
```bash
docker restart steel-bot
```

**Remove the container:**
```bash
docker stop steel-bot
docker rm steel-bot
```

**Rebuild the image (after code changes):**
```bash
docker build -t steel-grades-bot .
docker stop steel-bot
docker rm steel-bot
# Then run the container again using the commands from step 1 above
```

## Usage

1. Start the bot by sending `/start` command
2. Use `/find` command to begin searching for steel grades
3. Input the chemical composition values for each element
4. The bot will search for matching steel grades in the database
5. If no exact matches are found, you can request to find the closest match

## Project Structure

```
steel_grades_bot/
├── bot.py              # Main bot code
├── steel_database.db   # SQLite database with steel grades
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── .env              # Environment variables (not in repo)
└── logs/             # Log files directory
```

## Dependencies

- aiogram >= 3.0.0 - Telegram Bot Framework
- python-dotenv >= 1.0.0 - Environment variable management
- pandas == 2.1.0 - Data manipulation
- openpyxl == 3.1.2 - Excel file support

## Logging

The bot maintains detailed logs in the `logs` directory:
- Daily log files with format `steel_bot_YYYYMMDD.log`
- User feedback is stored in `user_feedback.log`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - [@mxter_ru](https://t.me/mxter_ru)

Project Link: [https://github.com/yourusername/steel_grades_bot](https://github.com/yourusername/steel_grades_bot)