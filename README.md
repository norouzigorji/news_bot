### Installation and Usage Guide for Telegram News Bot Script

This guide covers the steps for installing, activating, and using the Telegram News Bot script.

#### Prerequisites
1. **Python 3.x**: Ensure you have Python version 3 or higher installed.
2. **Git**: Git is needed to clone the repository from GitHub.

#### Installing Git
Install Git according to your operating system:

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install git
```

**For Fedora:**
```bash
sudo dnf install git
```

**For macOS (using Homebrew):**
```bash
brew install git
```

**For Windows:**
1. Go to the [Git download page](https://git-scm.com/download/win).
2. Download and run the installer.

#### Cloning the GitHub Repository
After installing Git, clone the `news_bot` repository:

1. **Open Terminal** (or Git Bash on Windows).
2. Run the following command to clone the repository:
   ```bash
   git clone https://github.com/norouzigorji/news_bot.git
   ```
3. Navigate to the `news_bot` directory:
   ```bash
   cd news_bot
   ```

#### Installing Required Libraries
In the `news_bot` directory, run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

#### Creating a Telegram Bot
1. Go to [BotFather](https://telegram.me/BotFather) and create a new bot.
2. Obtain the bot token.

#### Setting the Bot Token and Admin ID
In the script, locate the `if __name__ == '__main__':` section. Run the script with your bot token and admin ID:
```bash
python news_bot.py <YOUR_BOT_TOKEN> <YOUR_ADMIN_ID>
```
Replace `<YOUR_BOT_TOKEN>` and `<YOUR_ADMIN_ID>` with your bot token and your Telegram numeric admin ID, respectively.

#### Using the Bot
1. **Starting the Bot**:
   After running the script, the bot will automatically start.

2. **Admin Commands**:
   As an admin, send the `/start` command to the bot to see the main menu, which includes the following options:
   - Add Channel
   - Delete Channel
   - Search Channel by Name
   - Show Channel Info

3. **Adding a Channel**:
   - Select "Add Channel" in the main menu.
   - Enter the numeric ID of the channel.
   - After entering the channel ID, you will see the following options:
     - Add Bot to Channel
     - Set Time Interval
     - Confirm
     - Back

4. **Deleting a Channel**:
   - Select "Delete Channel" in the main menu.
   - Enter the numeric ID of the channel to delete it.

5. **Searching for a Channel by Name**:
   - Select "Search Channel by Name" in the main menu.
   - Enter the channel name to display the search results.

6. **Showing Channel Info**:
   - Select "Show Channel Info" in the main menu.
   - Enter the numeric ID of the channel to display its information.

#### Bot's Main Functionality
The bot automatically fetches the latest news from the `bloghnews.com` website and sends it to the configured channels at the specified intervals.

#### Running the Script Permanently
To keep the script running even after closing the terminal, you can use service management tools like `systemd` (for Linux-based systems) or `pm2` (for Node and Python applications).

#### Example Setup with `screen`:
```bash
screen -S news_bot
python news_bot.py <YOUR_BOT_TOKEN> <YOUR_ADMIN_ID>
# To detach from screen without stopping the program:
Ctrl + A, then D
# To reattach to the screen session:
screen -r news_bot
```

By following these steps, your news bot will be fully installed, configured, and ready to operate.

**Need a similar project?**<br/>
If you have any questions about this project, feel free to post your request in the issues section. <br/>
For similar projects, you can contact me on Telegram: <br/>
Telegram 🆔: [@Norouzi_Gorji](https://t.me/Norouzi_Gorji)
