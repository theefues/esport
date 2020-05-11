import coc
import traceback
import discord

from discord.ext import commands
from riotwatcher import LolWatcher, ApiError

# Read info at Discord Developer Portal and Clash of Clans Developer Portal before use!

'''
Store authentication info in separate file:
line 1: CoC dev username
line 2: CoC dev password
line 3: DC info channel ID
line 4: DC bot OAUTH2 token
line 5: Your clan's tag
line 6: LoL API key
'''
# Load credentials from credentials.txt
with open("credentials.txt") as f:
    auth = f.readlines()
auth = [x.strip() for x in auth] 

clan_tag = auth[4] # Tag of the clan that you want to follow.
coc_client = coc.login(auth[0], auth[1], key_count=5, key_names="Bot key", client=coc.EventsClient,)

lol_api = LolWatcher(auth[5]) # Get your API key on https://developer.riotgames.com (you have to be logged in)
region = "eun1"

bot = commands.Bot(command_prefix="!")
INFO_CHANNEL_ID = int(auth[2]) # ID of the info channel where the bot will post messages.

@coc_client.event
async def on_clan_member_versus_trophies_change(old_trophies, new_trophies, player):
	await bot.get_channel(INFO_CHANNEL_ID).send(
        "{0.name} has {1} versus trophies.".format(player, new_trophies))

# Hello command
@bot.command()
async def hello(ctx):
    await ctx.send("Oh, hello there!")

# Get LoL account details
@bot.command()
async def lolme(ctx, name):
    me = lol_api.summoner.by_name(my_region, name)
    await ctx.send("Name: {0} (Level: {1})".format(me["name"], me["summonerLevel"]))

# Get ranked stat history
@bot.command()
async def lolranked(ctx, name):
    ply = lol_api.summoner.by_name(my_region, name)
    ranked = lol_api.league.by_summoner(my_region, ply['id'])
    if not ranked:
        await ctx.send("No ranked history!")
    else:
        data = ranked[0]
        output = "Name: {0} \nRanked: {1} {2}\n Wins: {3} Losses: {4} \n".format(data['summonerName'], data['tier'], data['rank'], data['wins'], data["losses"])
        data = ranked[1]
        output += "Ranked FLEX: {0} {1} \n Wins: {2} Losses: {3}".format(data['tier'], data['rank'], data['wins'], data['losses'])
        await ctx.send(output)

# List of commands
@bot.command()
async def commands(ctx):
    await ctx.send("!hello, !cocheroes \{player_tag\}, !cocmembers !lolme \{summoner_name\} !lolranked \{summoner_name\}")

# Owned CoC heroes 
@bot.command()
async def cocheroes(ctx, player_tag):
    player = await coc_client.get_player(player_tag)
    to_send = "Heroes: \n"
    for hero in player.heroes:
        to_send += "{}: Lv {}/{}\n".format(str(hero), hero.level, hero.max_level)

    await ctx.send(to_send)

# CoC Clan Members
@bot.command()
async def cocmembers(ctx):
    members = await coc_client.get_members(clan_tag)

    to_send = "Members:\n"
    for player in members:
        to_send += "{0} ({1})\n".format(player.name, player.tag)

    await ctx.send(to_send)

coc_client.add_clan_update(
    [clan_tag], retry_interval=60
)
coc_client.start_updates()

bot.run(auth[3])
