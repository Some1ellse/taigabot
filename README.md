# TaigaBot

A Discord bot that seamlessly integrates Taiga project management with Discord, bringing your agile workflow directly into your team's communication hub.

![TaigaBot Example](https://raw.githubusercontent.com/taigaio/taiga-front/master/screenshots/Taiga_Dashboard.png)

## Features

- 🔄 **Real-time Updates**: Automatically posts updates from Taiga to Discord when:
  - User stories are created, modified, or deleted
  - Tasks are created or updated
  - Comments are added
  - Status changes occur
  - Assignments are modified

- 📌 **Smart Threading**: Creates and maintains organized Discord forum threads for each user story

- 👥 **Mention Integration**: Automatically mentions Discord users when they are:
  - Assigned to a user story
  - Added as watchers
  - Tagged in comments

- 📊 **Status Tracking**: Maintains a pinned message with current story status that's always up-to-date

- 🎨 **Rich Embeds**: Beautiful Discord embeds that display:
  - Story details and descriptions
  - Status changes
  - Assignment updates
  - Blocking status
  - Links back to Taiga

## Setup

1. Create a Discord bot and get your token
2. Set up a Taiga webhook
3. Configure environment variables:
   ```env
   DISCORD_TOKEN=your_discord_token
   TAIGA_USERNAME=your_taiga_username
   TAIGA_PASSWORD=your_taiga_password
   TAIGA_BASE_URL=your_taiga_url
   WEBHOOK_SECRET=your_webhook_secret
   FORUM_ID=your_discord_forum_id
   ```

## Discord Integration

To link your Discord username with Taiga, add your Discord username to your Taiga bio with the format:
```
@YourDiscordUsername
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
