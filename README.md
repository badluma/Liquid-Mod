# Liquid Mod

A discord bot made to prevent scams on the Liquid AI Community Server

---

## Features

- **Keyword moderation** — automatically delete, kick, ban, or mute users based on configurable word lists
- **AI scam detection** — uses a local LLM to flag and delete likely scam messages above a character threshold
- **Debug mode** — when enabled, the bot processes all messages including those from admins and itself

---

## Prerequisites

- Python 3.9+
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) installed with GPU support (recommended) or CPU
- A Discord bot token with the `Message Content Intent` enabled

---

## Installation

### Windows

```bat
REM 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

REM 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

REM 3. Install llama-cpp-python (CPU only - for GPU support install CUDA and use cu124 wheel)
pip install llama-cpp-python

REM 4. Install Python dependencies
pip install discord.py python-dotenv tomli

REM 5. Download the model
REM Download LFM2.5-1.2B-Instruct-Q4_K_M.gguf from:
REM https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF
REM Place it in a "models" folder in the project root
```

### Ubuntu (with llama-cpp-python)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. Install system dependencies
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev python3-dev python3-venv

# 3. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install llama-cpp-python
# For CUDA GPU support:
pip install llama-cpp-python --force-reinstall --no-cache-dir \
    --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124

# For CPU only (slower, no GPU):
# pip install llama-cpp-python

# 5. Install Python dependencies
pip install discord.py python-dotenv tomli

# 6. Create models directory and download the model
mkdir -p models
cd models
```

### Unix (Linux / macOS)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd <repo-folder>

# 2. Install system dependencies (Linux only)
# For Ubuntu/Debian:
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev python3-dev python3-venv

# 3. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install llama-cpp-python (CPU only - for GPU see Ubuntu section)
pip install llama-cpp-python

# 5. Install Python dependencies
pip install discord.py python-dotenv tomli
```

### Setting up the AI

The bot requires the LFM2.5-1.2B-Instruct-Q4_K_M.gguf model file. Download it from HuggingFace:

```bash
# Create models directory
mkdir -p models

# Download using huggingface-cli
pip install huggingface-hub
huggingface-cli download LiquidAI/LFM2.5-1.2B-Instruct-GGUF LFM2.5-1.2B-Instruct-Q4_K_M.gguf --local-dir models
```

Or manually from: https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-GGUF

However, if you want to use your own model, you can customize it inside the `config.toml` file.

### Creating the bot
![Creating the bot application](./instructions/screenshot-01-bot-creation.png)
![Setting bot permissions](./instructions/screenshot-02-bot-permissions.png)
![Copying the bot token](./instructions/screenshot-03-copy-token.png)
![Opening server settings](./instructions/screenshot-04-server-settings.png)
![Creating a bot role](./instructions/screenshot-05-create-role.png)
![Setting role permissions](./instructions/screenshot-06-role-permissions.png)
![Managing role order](./instructions/screenshot-07-role-order.png)
![Assigning bot role](./instructions/screenshot-08-bot-role.png)
![Final configuration](./instructions/screenshot-09-reset-token.png)

---

## Configuration

1. Create a `.env` file in the project root:
   ```
   BOT_TOKEN=your_discord_bot_token_here
   ```

2. Edit `config.toml` to configure moderation rules and AI settings:
   - Add words/phrases to the `delete`, `kick`, `ban`, or `mute` lists under `[moderation]`
   - Adjust `time_to_mute` (in minutes) for timed-out users
   - Set `min_chars` under `[ai]` to control the minimum message length the AI will check
   - Set `debug_mode = false` under `[debug]` when deploying to production

---

## Running the Bot

Make sure your GGUF model file is in place (see `model_path` in `config.toml`), then start the bot:

```bash
python main.py
```