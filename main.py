from ast import Import
from code import interact
from doctest import debug_script
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

from pytest import Config

# CONFIG SETUP ----------------------------------------------------------------------

config = ConfigParser()
config.read("config.ini")

promptBankFile = 'prompt_bank.txt'

# Date/Time  -----------------------------------------------------------------------

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
load_dotenv()
logintoken = os.getenv('LOGIN')
bot = interactions.Client(token=logintoken)

print('Daily Discussion Bot started!')

# COMMANDS  ---------------------------------------------------------------------

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
    name="list_prompts",
    description="Lists all prompts in the bank.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def list_prompts(ctx: interactions.CommandContext):
    promptsFileRead = open(promptBankFile, "r")
    promptArray = promptsFileRead.read().split('\n')
    promptsString = '\n'.join(promptArray)
    await ctx.send(promptsString)


@bot.command(
    name="test_forum_sending",
    description="Test Command - Creates a thread with a discussion question.",
    scope=744023087950987325,
    default_member_permissions=interactions.Permissions.MUTE_MEMBERS,  # staff only :)
)
async def test_forum_sending(ctx: interactions.CommandContext):
    await postForumTopic()
    await ctx.send("test successful :)")

async def postForumTopic():

    day = config.get('BOT',"DAY")
    print("day: "+day)

    print("SCHEDULE ACTIVATED!")
    now = datetime.datetime.now()
    datenum = now.strftime('%d')
    dateint = int(datenum)
    print(dateint)
    dateSuffix = suffix_function(dateint)
    dateString = now.strftime('%B %d'+dateSuffix)

    promptsFileRead = open(promptBankFile, "r")
    promptArray = promptsFileRead.read().split('\n')
    todaysQuestion = promptArray[0]

    forumChannel = await interactions.get(bot, interactions.Channel, object_id='1006432594881167470')
    #error is here
    sentMessage = await forumChannel.create_forum_post(dateString,todaysQuestion, applied_tags=[1006433604013932625])
    msgID = sentMessage.id

    staffChannel = await interactions.get(bot, interactions.Channel, object_id="777996362477993984")

    announcementLink = "https://www.discord.com/channels/744023087950987325/"+str(msgID)
    announcementChannel = await interactions.get(bot, interactions.Channel, object_id="766077932686278686")
    await announcementChannel.send("**"+dateString+", "+"Day "+day+", Today's Topic Is: **_"+todaysQuestion+"_"+"\n \nFind the discussion post here:\n"+announcementLink)

    promptsFileWrite = open(promptBankFile, "w")
    promptArray.pop(0)
    print(promptArray)

    config.set('BOT','DAY', str(int(day)+1))

    with open('config.ini','w') as configfile:
        config.write(configfile)

    if len(promptArray) == 1:
        await staffChannel.send("**NO MORE PROMPTS! If no new prompts are added with /add_prompt, I will not be able to post the daily discussion tomorrow!**")

    promptsString = '\n'.join(promptArray)
    print(promptsString)
    promptsFileWrite.write(promptsString)
    promptsFileWrite.close()

bot.start()
