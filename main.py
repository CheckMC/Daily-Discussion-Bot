from ast import Import
from code import interact
from doctest import debug_script
from pickle import STRING
from queue import Empty
from sched import scheduler
import string
from tokenize import String
import interactions
from discord import app_commands
import numpy
import datetime
import os
from dotenv import load_dotenv
from configparser import ConfigParser

from datetime import time

from pytest import Config
from datetime import datetime

from interactions.ext.tasks import IntervalTrigger, create_task

# CONFIG SETUP ----------------------------------------------------------------------

config = ConfigParser()
config.read("config.ini")

promptBankFile = 'prompt_bank.txt'

# scheduling ------------------------------------------------------------------------------
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

async def tick():
    print("RUNNING RUNNING RUNNING RUNNING")


lastPost = datetime.date(datetime.strptime(config.get('BOT','LASTPOSTDATE'),'%m/%d/%Y'))
print(lastPost)
today = datetime.date(datetime.today())

currentTime = datetime.today()
desiredPostTime = datetime(today.year, today.month, today.day, int(config.get('BOT','POSTHOUR')),int(config.get('BOT','POSTMINUTE')),0,0)

print("desired: "+str(desiredPostTime))
print("current: "+str(currentTime))

time_diff = desiredPostTime - currentTime
timeSecs = time_diff.seconds

timeTillPost = 0
alreadyPosted = False

if (today != lastPost):
    timeTillPost = timeSecs
    print("days not same")
    print("time until post: "+str(timeSecs))

 

load_dotenv()
logintoken = os.getenv('LOGIN')
bot = interactions.Client(token=logintoken)


# SUFFIXES  -----------------------------------------------------------------------

def suffix_function(n):
    if n == 1: return "st"
    if n == 2: return "nd"
    if n == 3: return "rd"
    if n >= 4 and n <= 20: return "th"
    if n == 21: return "st"
    if n == 22: return "nd"
    if n == 23: return "rd"
    if n >= 24 and n <= 30: return "th"
    if n == 31: return "st"
   
# BOT SETUP -------------------------------------------------------------------------



print('Daily Discussion Bot started!')

# COMMANDS  ---------------------------------------------------------------------

#add prompt command
@bot.command(
    name="add_prompt",
    description="Adds a prompt to the backup prompt bank.",
    scope=744023087950987325,
    options = [
        interactions.Option(
            name="prompt",
            description="Your prompt. Do not include date, only the question.",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def add_prompt(ctx: interactions.CommandContext, prompt: string):
    text_file = open(promptBankFile, "a")
    print("Adding prompt - "+prompt)
    await ctx.send("Added prompt: "+prompt)
    text_file.write(prompt+"\n")
    text_file.close

#remove prompt command
@bot.command(
    name="remove_prompt",
    description="Removes a prompt from the prompt bank.",
    scope=744023087950987325,
    options = [
        interactions.Option(
            name="prompt",
            description="Using /list_prompts, copy and paste the exact prompt you want to remove. Must be exact.",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def remove_prompt(ctx: interactions.CommandContext,prompt: string):
    print(prompt)
    text_file = open(promptBankFile, "r")
    print("Removing prompt - "+prompt)
    promptArray = text_file.read().split('\n')
    promptArray.remove(prompt)
    promptsString = '\n'.join(promptArray)
    print(promptsString)
    text_file_write = open(promptBankFile, "w")
    text_file_write.write(promptsString)
    text_file_write.close
    await ctx.send("Removed Prompt: "+prompt)

@bot.command(
    name="set_time",
    description="Set the time that the bot posts. 24HR time, EST.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
    options= [
        interactions.Option(
            name='hour',
            description='Hour in 24Hr time, EST.',
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name='minute',
            description='Minute of the hour.',
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def set_time(ctx:interactions.CommandContext,hour: STRING, minute: STRING):

    if(hour.isdigit() == False):
        await ctx.send("**ERROR: You entered an invalid value.**")
        return
    if(minute.isdigit() == False):
        await ctx.send("**ERROR: You entered an invalid value.**")
        return

    if(int(hour) >= 25 or int(hour) <= -1):
        await ctx.send("**ERROR: You entered an invalid value.**")
        return
    
    if(int(minute) >= 25 or int(minute) <= -1):
        await ctx.send("**ERROR: You entered an invalid value.**")
        return
    config.set('BOT','POSTHOUR', hour)
    config.set('BOT','POSTMINUTE', minute)
    with open('config.ini','w') as configfile:
        config.write(configfile)
    await ctx.send("**Post time set: **"+str(hour)+":"+str(minute)+" EST")


#list prompt command
@bot.command(
    name="list_prompts",
    description="Lists all prompts in the bank.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def list_prompts(ctx: interactions.CommandContext):
    promptsFileRead = open(promptBankFile, "r")
    promptArray = promptsFileRead.read().split('\n')
    promptsString = '\n'.join(promptArray)
    if(len(promptArray) == 1):
        await ctx.send("**NO PROMPTS**")
        return
    #await ctx.send(promptsString)

@bot.command(
    name='reset',
    description='Resets all config to default. Disables bot.',
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def reset(ctx: interactions.CommandContext):
    await ctx.send("**Resetting all values to default.")
    config.set('BOT','BOTENABLED',"False")
    await ctx.send("Bot Enabled = False")
    config.set('BOT','POSTHOUR', "17")
    await ctx.send("Post hour = 17")
    config.set('BOT','POSTMINUTE',"0")
    await ctx.send("Post minute = 0")
    config.set('BOT','DAY','0')
    await ctx.send("Day = 0")

    with open('config.ini','w') as configfile:
        config.write(configfile)
    await ctx.send("**All settings reset.**")

@bot.command(
    name='set_day',
    description='Set current day number.',
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
    options= [
        interactions.Option(
            name='day',
            description='Day number, only numbers please',
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def set_day(ctx: interactions.CommandContext, day: STRING):
    if day.isdigit() == True:
        config.set('BOT','DAY',day)
        with open('config.ini','w') as configfile:
            config.write(configfile)
        await ctx.send("Current day number set to "+day)
    else:
        ctx.send("**ERROR: Invalid value.**")
    
#test forum sending command
@bot.command(
    name="test_forum_sending",
    description="Test Command - Creates a thread with a discussion question.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def test_forum_sending(ctx: interactions.CommandContext):
    await postForumTopic()
    await ctx.send("test successful :)")

@bot.command(
    name="toggle_bot",
    description="Toggles the bot. When off, will still accept other commands.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,
)
async def toggle_bot(ctx: interactions.CommandContext):
    botRunning = config.get('BOT',"BOTENABLED")

    if (botRunning == "False"):
        config.set('BOT','BOTENABLED', "True")

        with open('config.ini','w') as configfile:
            config.write(configfile)
        await ctx.send("**Bot Enabled: I will post until I am disabled, or out of prompts.**")
        print("Bot set to ENABLED")


    else:
        config.set('BOT','BOTENABLED', "False")

        with open('config.ini','w') as configfile:
            config.write(configfile)
        await ctx.send("**Bot Disabled: I will not post until I am re-enabled.**")
        print("Bot set to DISABLED")


# POST DISCUSSION FUNCTION -------------------------------------------------------------------------------------
async def postForumTopic():
    staffChannel = await interactions.get(bot, interactions.Channel, object_id="777996362477993984")

    botRunning = bool(config.get('BOT',"BOTENABLED"))
    if botRunning == False:
        staffChannel.send("**DAILY DISCUSSION ERROR: Bot disabled, did not post.**")
        return

    promptsFileRead = open(promptBankFile, "r")
    promptArray = promptsFileRead.read().split('\n')
    todaysQuestion = promptArray[0]

    if len(promptArray) == 1:
        staffChannel.send("**DAILY DISCUSSSION ERROR: No prompts available, failed to post.")
        return

    day = config.get('BOT',"DAY")
    print("day: "+day)

    print("SCHEDULE ACTIVATED!")
    now = datetime.now()
    datenum = now.strftime('%d')
    dateint = int(datenum)
    print(dateint)
    dateSuffix = suffix_function(dateint)
    dateString = now.strftime('%B %d'+dateSuffix)

    forumChannel = await interactions.get(bot, interactions.Channel, object_id='1006432594881167470')
    sentMessage = await forumChannel.create_forum_post(dateString,todaysQuestion, applied_tags=[1006433604013932625])
    announcementChannel = await interactions.get(bot, interactions.Channel, object_id="766077932686278686")

    msgID = sentMessage.id

    announcementLink = "https://www.discord.com/channels/744023087950987325/"+str(msgID)
    await announcementChannel.send("**"+dateString+", "+"Day "+day+", Today's Topic Is: **_"+todaysQuestion+"_"+"\n \nFind the discussion post here:\n"+announcementLink)

    promptsFileWrite = open(promptBankFile, "w")
    promptArray.pop(0)
    print(promptArray)
    #updating day count in config file
    config.set('BOT','DAY', str(int(day)+1))

    with open('config.ini','w') as configfile:
        config.write(configfile)

    if len(promptArray) == 1:
        await staffChannel.send("**NO MORE PROMPTS! If no new prompts are added with /add_prompt, I will not be able to post the daily discussion tomorrow!**")

    promptsString = '\n'.join(promptArray)
    print(promptsString)
    promptsFileWrite.write(promptsString)
    promptsFileWrite.close()

@bot.event()
async def on_start():

    await asyncio.sleep(timeSecs)
    await postForumTopic()
    tickTask = create_task(IntervalTrigger(86400))(postForumTopic)
    tickTask.start()

bot.start()
