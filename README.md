# Uptime Monitor and Alerting System

A lightweight, modular Python script to monitor website uptime and send alerts to Discord via Webhooks.

## Project Structure

- index.py: Main entry point. Runs a continuous loop to monitor all configured targets.
- src/checker.py: Probes URLs, checks HTTP status, and measures network latency.
- src/evaluator.py: Tracks consecutive failures, applies failure thresholds, and determines whether an alert should be triggered (downtime or recovery).
- src/notifier.py: Handles sending the actual alert messages to Discord.

## Configuration

1. Discord Webhook:
   Create a file named .env inside the src/ directory (src/.env) and add your webhook URL:
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

2. Target Websites:
   Configure the websites you want to monitor in config/sites.json. You can define custom failure thresholds for each site before an alert is triggered.

## Installation & Usage

1. Navigate to the project root and activate the virtual environment:
   source venv/bin/activate

2. Install the required dependencies:
   pip install httpx python-dotenv

3. Start the monitoring system:
   python index.py

The system will periodically check the status of your configured URLs. If a service goes down or recovers, you will receive a notification in your configured Discord channel.
