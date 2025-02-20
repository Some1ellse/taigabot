# TaigaBot

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/some1ellse)

A simple Discord bot written in Python.
Integrates with Taiga webhooks and REST API for automatic updates and notifications.

There are no commands, this is not an interactive bot.

![TaigaBot Example](https://some1ellse.s3.us-west-2.amazonaws.com/images/TaigaBot_Example.png)

## Features

- 🔄 **Real-time Updates**:
Automatically posts updates from Taiga to Discord when:
  - User stories are created, modified, or deleted
  - Tasks are created or updated
  - Comments are added
  - Status changes occur
  - Assignments are modified

- 📌 **Forum Threads**: Creates and maintains organized Discord forum threads for each user story

- 👥 **Mention Integration**: Automatically mentions Discord users when they are:
  - Assigned to a user story
  - Added as watchers
  - Tagged in comments (Coming soon! ...possibly)

- 📊 **Status Tracking**: Maintains a pinned message with current story status that's always up-to-date
![Pinned Example](https://some1ellse.s3.us-west-2.amazonaws.com/images/Status_embed.png)

- 🎨 **Rich Embeds**: Beautiful Discord embeds that display:
  - Story details and descriptions
  - Status changes
  - Assignment updates
  - Blocking status
  - Links back to Taiga

- 🌟 **Automatic Tagging**: Automatically tag forum posts for easy sorting.
  - Taiga Swimlanes count as tags. Posts are tagged with the swimlane they are in.
    - Swimlane and Discord tag names must match exactly.
  - Tags (Coming soon! ...possibly)

## Setup

### Prerequisites

#### Discord
1. Create a Discord application and get your token
2. Invite the bot to your server
3. Ensure your Discord server is Community enabled, and create a forum channel for posts.

#### Proxy
1. Ensure there is some form of proxy between the bot and Taiga, so you can properly catch the webhook route.
   - Nginx Proxy Manager is a good easy way to do this- https://nginxproxymanager.com/ 

#### Taiga
1. Enable webhooks on your Taiga instance
2. Create a webhook on your Taiga project
   - set secret key (use your favorite method to generate one.)
   - set webhook URL: including route. example: https://taiga.example.com/webhook
```
Secret Key Generation Examples:

(Using OpenSSL)
openssl rand -base64 32

(Using powershell)
powershell -Command "[Convert]::ToBase64String((1..32 | % {Get-Random -Maximum 256}))"

or a random string generator of some kind.
```

### Run the bot

#### Run in python
1. Clone the repository
2. Setup virtual envrionment (recommended)
3. Create a .env file in the taiga_bot directory and fill it in with the env variables below.
4. Ensure python 3.12.7 is installed
5. python -m pip install -r requirements.txt
6. python main.py

#### Build docker image yourself.
1. Clone the repository
2. Comment out lines #4 and #6 in config.py
3. Build the Docker image using the provided dockerfile, or make your own
4. Run the container and pass the environment variables below to your run command or via a compose file.

#### Run from dockerhub
1. Pull the image some1ellse/taigabot:latest
2. Run the container and pass the environment variables below to your run command or via a compose file.

### Port mapping
1. If you are running in python, edit the main.py run_flask function to map the desired port.
2. If you are running in docker, map the container port 5000 to your desired port via the -p flag or in your compose file.

### Configure environment variables:
   ```env
  # Discord configuration
  DISCORD_TOKEN: Discord bot token
  FORUM_ID: Discord forum channel ID

  # Taiga configuration
  TAIGA_USERNAME: Taiga username
  TAIGA_PASSWORD: Taiga password
  TAIGA_BASE_URL: Taiga base URL


  # Webhook configuration
  SECRET_KEY: Secret key for webhook signing
  WEBHOOK_ROUTE: Webhook route (defualt is /webhook)
   ```

## Discord Mention Integration

To link your Discord username with Taiga, add your Discord username to your Taiga bio with the format:
```
@YourDiscordUsername
```

## Contributing

I'm not sure I'll have the time to maintain, so feel free to fork and make changes yourself if I don't respond.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
