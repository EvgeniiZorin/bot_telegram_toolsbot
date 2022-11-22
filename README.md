_**Important note!!!**_

There is a problem with telegram module. Specifically, there are two different libraries that are both imported by the `import telebot` command - `telebot` and `pyTelegramBotApi` - which, nevertheless, have completely different functions. For this telegram bot, we are using the latter - `pyTelegramBotApi`. If you install both packages, or only one, you could have an error message such as "'Telebot' has no attribute 'types'" or similar. 

To prevent this problem of packaging name conflict, install the packages in `requirements.txt`. If you have already messed up, run the following:
```bash
pip uninstall telebot
pip uninstall pytelegrambotapi
pip install pytelegrambotapi
```
