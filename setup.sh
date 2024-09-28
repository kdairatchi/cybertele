#!/bin/bash

echo "Welcome to the Cybersecurity Telegram Bot Setup!"
echo "This script will help you set up everything you need to run the bot."

# Step 1: Clone the repository
echo "Cloning the repository from GitHub..."
git clone YOUR_GITHUB_REPO_URL

REPO_DIR=$(basename YOUR_GITHUB_REPO_URL .git)

# Step 2: Navigate into the cloned repository
if [ -d "$REPO_DIR" ]; then
  cd "$REPO_DIR"
else
  echo "Failed to find repository directory."
  exit 1
fi

# Step 3: Check for Python installation
echo "Checking if Python3 is installed..."
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3..."
    # Install Python3 and Pip
    sudo apt-get update
    sudo apt-get install python3 -y
    sudo apt-get install python3-pip -y
else
    echo "Python3 is already installed."
fi

# Step 4: Automatically create requirements.txt if not found
if [ ! -f "requirements.txt" ]; then
    echo "Creating a default requirements.txt file..."
    cat <<EOL > requirements.txt
python-telegram-bot==13.15
requests
beautifulsoup4
schedule
EOL
fi

# Step 5: Install required Python libraries
echo "Installing required Python libraries from requirements.txt..."
pip3 install -r requirements.txt

# Step 6: Prompt for Telegram Bot Token
echo "Please enter your Telegram Bot Token:"
read TELEGRAM_BOT_TOKEN

# Step 7: Set up environment variables in a .env file
echo "Setting up environment variables..."
echo "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN" > .env

# Step 8: Run the bot
echo "Setup is complete! You can now run the Telegram bot with the following command:"
echo "python3 bot.py"
