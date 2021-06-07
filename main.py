import discord
from discord.ext import commands
import spotipy
import time
import os
from random import cho
from spotipy.oauth2 import SpotifyClientCredentials
from discord_slash import SlashCommand

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('CLIENTID'),
                                                           client_secret=os.getenv('CLIENTSEC')))

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')
slash = SlashCommand(bot, sync_commands=True)

s = ", "

usablegenres = [] # The genres you want to see in getartist

@slash.slash(name="help",
             description="Display more information about commands",
             guild_ids = ['SERVER IDS HERE'])
async def help(ctx):
  embed=discord.Embed(title="Help", color=0xae00ff)
  embed.add_field(name="goodbot", value="Praise the bot", inline=False)
  embed.add_field(name="badbot", value="Tell the bot off", inline=False)
  embed.add_field(name="genres", value="Display usable genres for recommendations", inline=False)
  embed.add_field(name="getartistran", value="Gives three tracks from random artist", inline=False)
  embed.add_field(name="getartist", value="Gives three tracks from given arist\n - Multiword names are done line so \"foo fighters\"", inline=False)
  embed.add_field(name="getartistgenre", value="Gives three tracks from random artist based on given genre\n - Multiword genres are done line so \"skate punk\"", inline=False)
  embed.add_field(name="getrecartists", value="Gives a track recommendation based on given artist(s)\n - Multiple artist searches are seprated like so \"Nirvana, U2\"\n - Single artist searches with spaces in the name are done like so \"Led Zeppelin\"", inline=False)
  embed.add_field(name="getrecgenres", value="Gives a track recommendation based on given genre(s)\n - Multiple genre searches are seprated like so \"emo, ska\"", inline=False)
  embed.add_field(name="getrecag", value="Gives a track recommendation based on given artist(s) and genre(s)\n - Single searches are done like so U2 ska\n - Multiple searches are done like so \"Nirvana, U2\" \"emo, ska\"", inline=True)
  await ctx.send(embed=embed)

@slash.slash(name="genres",
             description="Display usable genres for recommendations",
             guild_ids = ['SERVER IDS HERE'])
async def genres(ctx):
  g = sp.recommendation_genre_seeds()
  message = "Usable genres: " + s.join(g["genres"])
  await ctx.send(message)

@slash.slash(name="getrecartists",
             description="Track rec based on given artist(s). Multi artist \"Cake, U2\". Single artist with spaces \"Daft Punk\"",
             guild_ids = ['SERVER IDS HERE'])
async def getrecartists(ctx, artists):
  ids = getartids(artists.split(", "))
  if(len(ids) != 0):
    rec = sp.recommendations(seed_artists=ids,limit=100,country="US")
    if(len(rec['tracks']) != 0):
      tracklink = choice(rec['tracks'])['external_urls']['spotify']
      await ctx.send("Track Recommendation: " + tracklink)
      return
  await ctx.send("I have failed your request because you gave me bad input or because I am a dumb bot")

@slash.slash(name="badbot",
             description="Tell the bot off",
             guild_ids = ['SERVER IDS HERE'])
async def badbot(ctx):
  await ctx.send("Sorry :sob:")

@slash.slash(name="goodbot",
             description="Praise the bot",
             guild_ids = ['SERVER IDS HERE'])
async def goodbot(ctx):
  await ctx.send("Thank you")

@slash.slash(name="getrecgenres",
             description="Track recs based on given genre(s). Multiple genre searches are seprated like so \"emo, ska\"",
             guild_ids = ['SERVER IDS HERE'])
async def getrecgenres(ctx, genres):
  gen = checkgen(genres.split(", "))
  if(len(gen) != 0):
    try:
      rec = sp.recommendations(seed_genres=gen,limit=100,country="US")
      if(len(rec['tracks']) != 0):
        tracklink = choice(rec['tracks'])['external_urls']['spotify']
        await ctx.send("Track Recommendation: " + tracklink)
        return
      else:
        await ctx.send("I could not find any tracks :sob:")
    except Exception:
     await ctx.send("I have failed your request most likely because I am a dumb bot")
  else:
    await ctx.send("You did not give me any valid genres and thus I have failed my job :tired_face:")

@slash.slash(name="getrecag",
             description="Track recs based on given artist(s) and genre(s). Multi searches are done like \"Cake, U2\" \"emo, ska\"",
             guild_ids = ['SERVER IDS HERE'])
async def getrecag(ctx, artists, genres):
  ids = getartids(artists.split(", "))
  gens = checkgen(genre.split(", "))
  if(len(ids) == 0 and len(gens) == 0):
    await ctx.send("You did not give me any valid inputs and thus I have failed my job :tired_face:")
  elif(len(ids) == 0):
    await ctx.send("You did not give me any valid artists and thus I have failed my job :tired_face:")
  elif(len(gens) == 0):
    await ctx.send("You did not give me any valid genres and thus I have failed my job :tired_face:")
  else:
    try:
      rec = sp.recommendations(seed_artists=ids,seed_genres=gens,limit=100,country="US")
      if(len(rec['tracks']) != 0):
        tracklink = choice(rec['tracks'])['external_urls']['spotify']
        await ctx.send("Track Recommendation: " + tracklink)
      else:
        await ctx.send("I could not find any tracks :sob:")
    except Exception:
     await ctx.send("I have failed your request most likely because I am a dumb bot")

@slash.slash(name="getartistran",
             description="Three tracks from random artist",
             guild_ids = ['SERVER IDS HERE'])
async def getartistran(ctx):
  await bot.wait_until_ready()
  while True:
    genre = choice(usablegenres)
    genre = genre.replace("-"," ")
    if " " in genre:
      genre = '"' + genre + '"'

    total = sp.search('genre:' + genre,limit=50,offset=0,type="artist",market="US")['artists']['total']
    if total != 0:
      pages = math.ceil(total/50)
      if(pages > 952):
        pages = 951
      try:
        artist = choice(sp.search('genre:' + genre,limit=50,offset=randrange(pages),type="artist",market="US")['artists']['items'])
        tracks = sp.artist_top_tracks(artist['id'],country="US")
        artgenres = ', '.join(list(artist['genres']))

        embed=discord.Embed(title=thetitle, color=0x00fbff)
        embed.add_field(name="Name:", value=artist['name'], inline=False)
        embed.add_field(name="Genres:", value=artgenres, inline=False)
        embed.add_field(name="Track", value=tracks['tracks'][0]['external_urls']['spotify'], inline=True)
        embed.add_field(name="Track", value=tracks['tracks'][1]['external_urls']['spotify'], inline=True)
        embed.add_field(name="Track", value=tracks['tracks'][2]['external_urls']['spotify'], inline=True)
        embed.set_image(url=artist['images'][1]['url'])
        await ctx.send(embed=embed)
        return
      except Exception as e:
        print(str(e))
        time.sleep(.5)
        continue
        
@slash.slash(name="getartistgenre",
             description="Three tracks from random artist based on given genre. Multiword genres are done like so \"skate punk\"",
             guild_ids = ['SERVER IDS HERE'])
async def getartistgenre(ctx, genre):
  await getartistsearch('genre:',genre)

@slash.slash(name="getartist",
             description="Three tracks from given arist. Multiword names are done line so \"foo fighters\"",
             guild_ids = ['SERVER IDS HERE'])
async def getartist(ctx, artist):
  await getartistsearch('artist:',artist)

async def getartistsearch(thetype, tosearch):
  tosearch = tosearch.replace("-"," ")
  if " " in tosearch:
    tosearch = '"' + tosearch + '"'
  

  total = 0
  if thetype == 'genre:':
    try:
      total = sp.search(thetype + tosearch,limit=50,offset=0,type="artist",market="US")['artists']['total']
    except:
      await ctx.send("I have failed your request when searching most likely because I am a dumb bot")
      return

  pages = 0
  if total != 0:
    pages = math.ceil(total/50)
    if(pages > 952):
      pages = 951
  try:
    artist = {}
    if thetype == 'genre:':
      artist = choice(sp.search(thetype + tosearch,limit=50,offset=randrange(pages),type="artist",market="US")['artists']['items'])
    else:
      artist = sp.search(thetype + tosearch,limit=1,offset=0,type="artist",market="US")['artists']['items'][0]
    tracks = sp.artist_top_tracks(artist['id'],country="US")
    artgenres = ', '.join(list(artist['genres']))

    embed=discord.Embed(title="Artist", color=0x00fbff)
    embed.add_field(name="Name:", value=artist['name'], inline=False)
    if(len(artist['genres']) != 0):
      embed.add_field(name="Genres:", value=artgenres, inline=False)
    embed.add_field(name="Track", value=tracks['tracks'][0]['external_urls']['spotify'], inline=True)
    if(len(tracks['tracks']) >= 3):
      embed.add_field(name="Track", value=tracks['tracks'][1]['external_urls']['spotify'], inline=True)
      embed.add_field(name="Track", value=tracks['tracks'][2]['external_urls']['spotify'], inline=True)
    if(len(artist['images']) != 0):
      embed.set_image(url=artist['images'][1]['url'])
    await ctx.send(embed=embed)
    return
  except:
    await ctx.send("I have failed your request becuase I can't make a simple calculation due to being a dumb bot")
    return
        
  await ctx.send("I have failed your request because the genre did not return anything")

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
