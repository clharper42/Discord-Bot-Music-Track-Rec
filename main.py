import discord
from discord.ext import commands
import spotipy
import time
import os
from random import choice
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('CLIENTID'),
                                                           client_secret=os.getenv('CLIENTSEC')))

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

s = ", "

usablegenres = [] # The genres you want to see in getartist

@bot.command()
async def help(ctx):
  embed=discord.Embed(title="Help", color=0xae00ff)
  embed.add_field(name="goodbot", value="Praise the bot", inline=False)
  embed.add_field(name="badbot", value="Tell the bot off", inline=False)
  embed.add_field(name="genres", value="Display usable genres", inline=False)
  embed.add_field(name="getartist", value="Gives three tracks from random artist", inline=False)
  embed.add_field(name="getrecartists", value="Gives a track recommendation based on given artist(s)\n - Multiple artist searches are seprated like so \"Nirvana, U2\"\n - Single artist searches with spaces in the name are done like so \"Led Zeppelin\"", inline=False)
  embed.add_field(name="getrecgenres", value="Gives a track recommendation based on given genre(s)\n - Multiple genre searches are seprated like so \"emo, ska\"", inline=False)
  embed.add_field(name="getrecag", value="Gives a track recommendation based on given artist(s) and genre(s)\n - Single searches are done like so U2 ska\n - Multiple searches are done like so \"Nirvana, U2\" \"emo, ska\"", inline=True)
  await ctx.send(embed=embed)


@bot.command()
async def genres(ctx):
  channel = bot.get_channel('CHANNEL ID')
  g = sp.recommendation_genre_seeds()
  message = "Usable genres: " + s.join(g["genres"])
  await channel.send(message)

@bot.command()
async def getrecartists(ctx, artists):
  channel = bot.get_channel('CHANNEL_ID')
  ids = getartids(artists.split(", "))
  if(len(ids) != 0):
    rec = sp.recommendations(seed_artists=ids,limit=100,country="US")
    if(len(rec['tracks']) != 0):
      tracklink = choice(rec['tracks'])['external_urls']['spotify']
      await channel.send("Track Recommendation: " + tracklink)
      return
  await channel.send("I have failed your request because you gave me bad input or because I am a dumb bot")

@bot.command()
async def badbot(ctx):
  channel = bot.get_channel('CHANNEL_ID')
  await channel.send("Sorry :sob:")

@bot.command()
async def goodbot(ctx):
  channel = bot.get_channel('CHANNEL_ID')
  await channel.send("Thank you")

@bot.command()
async def getrecgenres(ctx, genres):
  channel = bot.get_channel('CHANNEL_ID')
  gen = checkgen(genres.split(", "))
  if(len(gen) != 0):
    try:
      rec = sp.recommendations(seed_genres=gen,limit=100,country="US")
      if(len(rec['tracks']) != 0):
        tracklink = choice(rec['tracks'])['external_urls']['spotify']
        await channel.send("Track Recommendation: " + tracklink)
        return
      else:
        await channel.send("I could not find any tracks :sob:")
    except Exception:
     await channel.send("I have failed your request most likely because I am dumb bot")
  else:
    await channel.send("You did not give me any valid genres and thus I have failed my job :tired_face:")

@bot.command()
async def getrecag(ctx, artists, genre):
  channel = bot.get_channel('CHANNEL_ID')
  ids = getartids(artists.split(", "))
  gens = checkgen(genre.split(", "))
  if(len(ids) == 0 and len(gens) == 0):
    await channel.send("You did not give me any valid inputs and thus I have failed my job :tired_face:")
  elif(len(ids) == 0):
    await channel.send("You did not give me any valid artists and thus I have failed my job :tired_face:")
  elif(len(gens) == 0):
    await channel.send("You did not give me any valid genres and thus I have failed my job :tired_face:")
  else:
    try:
      rec = sp.recommendations(seed_artists=ids,seed_genres=gens,limit=100,country="US")
      if(len(rec['tracks']) != 0):
        tracklink = choice(rec['tracks'])['external_urls']['spotify']
        await channel.send("Track Recommendation: " + tracklink)
      else:
        await channel.send("I could not find any tracks :sob:")
    except Exception:
     await channel.send("I have failed your request most likely because I am dumb bot")

@bot.command()
async def getartist(ctx):
  channel = bot.get_channel('CHANNEL_ID')
  while True:
    try:
      artist = sp.artist(choice(sp.search(choice(usablegenres),limit=50,offset=randrange(951),type="track",market="US")['tracks']['items'])['artists'][0]['id'])
      tracks = sp.artist_top_tracks(artist['id'],country="US")

      embed=discord.Embed(title="Artist", color=0xff0000)
      embed.add_field(name="Name:", value=artist['name'], inline=False)
      embed.add_field(name="Track", value=tracks['tracks'][0]['external_urls']['spotify'], inline=True)
      embed.add_field(name="Track", value=tracks['tracks'][1]['external_urls']['spotify'], inline=True)
      embed.add_field(name="Track", value=tracks['tracks'][2]['external_urls']['spotify'], inline=True)
      embed.set_image(url=artist['images'][1]['url'])
      await channel.send(embed=embed)
      return
    except Exception:
      time.sleep(.5)
      continue

def checkgen(genres):
  gen = []
  cmp = sp.recommendation_genre_seeds()['genres']
  for g in genres:
    if(g.lower() in cmp):
      gen.append(g.lower())
  return gen

def getartids(artists):
  ids = []
  for a in artists:
    try:
      res = sp.search(a,limit=1,type='artist')
      if(len(res['artists']['items']) != 0 and res['artists']['items'][0]['name'].lower() == a.lower()):
        ids.append(res['artists']['items'][0]['id'])
        time.sleep(1)
    except Exception:
      time.sleep(1)
      continue
  return ids

bot.run(os.getenv('TOKEN'))
