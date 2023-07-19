# atsui-yo
[![atsui yo](https://i.imgur.com/y6ltubQ.png)](https://www.youtube.com/watch?v=0BqAlaSXEkE "atsui yo")

**あっつい…**

**暑くて干からびそう…**

**動いてないのに暑いよ～…**
---

## Overview
This is a simple Discord bot that grabs the weather for a location and posts it. It can tell the current weather with a 12-hour forecast, or it can tell the upcoming weather forecast, from 1 to 7 days. 

In addition, there is a feature implemented just for fun, where the bot will post the 12-hour forecast every day at a chosen time. With this daily post, it will also post a video based on how high the max temperature for the day is.

This bot is highly configurable, with many commands available to change the values without having to open up the config file.

**This bot is developed purely for fun, as there are probably other Discord bots out there that can post weather data just fine.**

## Features
- Ask for the current weather with a 12-hour forecast
- Ask for the upcoming weather forecast, from 1 to 7 days
- Configure multiple parameters of the bot with chat commands (administrator permissions required)
- Restart and shutdown the bot with chat commands (administrator permissions required)

## Customization
- Location of where you want to see weather forecasts
- Temperature thresholds to determine what video gets posted daily
- The hour and minute that the bot makes its daily post

## Can I add this bot to my Discord server?
If you have a way to host it, then sure go ahead. You will have to modify *config.yaml* before you can fully run it. You will have to obtain your own Discord bot token, choose the channel ID that this bot will post to, and generate your Open-Meteo API request URL to use with the bot.

**Please do note that this is bot is not meant to operate in multiple servers simultaneously**, it is meant to serve one server (ie. a personal emote/sticker server). 

## Special Thanks
### [Open-Meteo](https://open-meteo.com/)
They have a really nice API for requesting weather data that is free, is very customizable, has a broad time range, and most importantly of all, doesn't require you to sign up for an account to use.

### [れいるか](https://twitter.com/hana87z)
They made the video which was pretty much the main reason why I began developing this bot in the first place.

# [Go watch it](https://twitter.com/hana87z/status/1565271229057372160)