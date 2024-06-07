# leetcode_bot_backend

### What does this service do?

Contains API endpoints related to our leetcode services. More information in this [doc](https://docs.google.com/document/d/1IZ5wDk3WyJygq-MJ-t95tfrTrXs4eqVlWgh4zHZOyR0/edit)

Link to [Logs](https://console.cloud.google.com/logs/query;query=resource.type%3D%22gae_app%22%0Aresource.labels.module_id%3D%22leetcode-backend%22;cursorTimestamp=2024-05-12T00:18:10.104768Z;duration=PT1H?serviceId=default&hl=en&project=gothic-sled-375305)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Quick Jump

- [Deployment](#️-deployment)
- [Testing](#how-to-run-discord-bot-for-local-testing-on-docker)

### Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8 or newer
- pip (Python package installer)

### 🔧 Installing

To set up your local development environment, please follow the steps below:

1. Clone the repository:
   ```bash
   git clone https://github.com/WhatcomCodersDev/leetcode_bot_backend
   cd leetcode_bot_backend
   ```
2. Create python virtual environment called `env` and install the required packages:

   Windows:

   ```powershell
   python -m venv env
   pip  install -r  .\requirements.txt

   ```

3. Environment variables - Please contact the developers to access environment variables:

- Discord bot token
- Google project id
- Redis port, password, and host

4. To run bot locally:

   Windows:

   ```powershell
   python .\app.py
   ```

# ☁️ Deployment

Run `gcloud app deploy` for regular deployments

Run `gcloud app deploy app.yaml cron.yaml` if updating the cron
