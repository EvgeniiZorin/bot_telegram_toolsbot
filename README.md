# Main

This is a Telegram bot that does all sorts of things. 

# Notes

_**Important note!!!**_

There is a problem with telegram module. Specifically, there are two different libraries that are both imported by the `import telebot` command - `telebot` and `pyTelegramBotApi` - which, nevertheless, have completely different functions. For this telegram bot, we are using the latter - `pyTelegramBotApi`. If you install both packages, or only one, you could have an error message such as "'Telebot' has no attribute 'types'" or similar. 

To prevent this problem of packaging name conflict, install the packages in `requirements.txt`. If you have already messed up, run the following:
```bash
pip uninstall telebot
pip uninstall pytelegrambotapi
pip install pytelegrambotapi
```

# Development notes

Set a collapsible menu with commands on the bottom of the screen:
- Go to `Botfather`
- Press commands `/help` -> `/setcommands` 
- Choose your bot in `choose bot`, then `set commands`
