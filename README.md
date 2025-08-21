
# Oguri

Oguri is a lightweight yet powerful Discord music bot written in Python. It brings a smooth and enjoyable music experience to your server, supporting YouTube playback, queue management, volume control, pause/resume, skip, and loop features. With simple commands and reliable performance, Oguri makes listening to music with friends on Discord easy and fun.


## Screenshots
Play command
![Play command](README%20Image/o!play%20name.png?raw=true)

Queue - Skip - Nowplaying command
![Queue - Skip - Nowplaying command](README%20Image/o!queue%20-%20o!skip%20-%20o!nowplaying.png?raw=true)

## Commands
🎵 Play: o!play <song name | YouTube link> — Play music from YouTube or search by name.

📃 Queue: o!queue or o!q — View the current queue.

⏭️ Skip: o!skip — Skip the current song.

⏸️ Pause: o!pause — Pause the music.

▶️ Resume: o!resume — Resume paused music.

🔁 Loop: o!loop — Toggle looping for the current song.

🔊 Volume: o!vol <0-200> — Adjust volume level.

❌ Stop: o!stop — Stop playback and clear the queue.

🎤 Join: o!join — Call the bot into your voice channel.

🚪 Leave: o!leave — Disconnect the bot from voice channel.

## Installation

Clone the repository

```bash
git clone https://github.com/withoutminh/Oguri.git
cd Oguri
```

Install FFmpeg and Python

https://ffmpeg.org/  
https://www.python.org/

Install required Python packages

```bash
py -m pip install --upgrade pip
py -m pip install "discord.py[voice]==2.6.0" yt-dlp
```

Setup Discord Bot
1. Open https://discord.com/developers/applications
2. Create a new application.
3. Copy a token in "Bot".
4. Open oguri.py and replace the TOKEN variable with your bot token.
5. Make sure to enable Message Content Intent in "Bot".
6. Invite Bot to your server in OAuth2 ( OAuth2 --> Find OAuth2 URL Generator --> Choose Bot and then choose Administrator in Bot permissions --> Copy link and paste it into your browser ).

Run bot
```bash
py oguri.py
````

## FAQ
#### 1. Token has an invalid format
Cause: Your bot token is incorrect or copied with extra spaces.  
Fix: Double-check your token in [Discord Developer Portal](https://discord.com/developers/applications) and paste it correctly into oguri.py
### 2. Reactions not working in o!play search results
Cause: You reacted too quickly before the bot added its own reactions.  
Fix: Wait until the bot finishes adding reactions before choosing.

## Support

Need help? please open an issue in this repository.
