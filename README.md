## Wish bot

Wish bot is bot that stores wishes of users for other users. For example, if you want to present something to one person
for his birthday, you can watch his wish list in this bot

The bot has two scripts - poller, that makes long polls and get updates from telegram bot api and sends tasks to
rabbitmq. Then worker script takes tasks from rabbitmq and does them. Worker with db and have logic and therefore i
decided to run it in three instances for more productivity. All bot works with docker-compose. Help to know how to user
this bot you can get in /help command sended to bot

## Installing

To run this bot on your pc you need to execute next steps:

* clone this repository
* set variables in .env file
* create directory logs - it needs for docker to store logs of poller and worker scripts
* execute command: docker-compose up
