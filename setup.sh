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
    sudo apt-get update
    sudo apt-get install python3 -y
    sudo apt-get install python3-pip -y
else
    echo "Python3 is already installed."
fi

# Step 4: Install required Python libraries
echo "Installing required Python libraries..."
pip3 install -r requirements.txt

# Step 5: Prompt for Telegram Bot Token
echo "Please enter your Telegram Bot Token:"
read TELEGRAM_BOT_TOKEN

# Step 6: Set up environment variables in a .env file
echo "Setting up environment variables..."
echo "TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN" > .env

# Step 7: Run the bot
echo "Setup is complete! You can now run the Telegram bot with the following command:"
echo "python3 bot.py"
