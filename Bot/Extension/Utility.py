import re
import os
import bs4
import json
import random
import discord
import requests
import datetime
import calendar
import giphy_client
import nest_asyncio
import googlesearch
from discord.ext import commands
from giphy_client.rest import ApiException
from moviepy.editor import *

from itertools import repeat

from multiprocessing.pool import ThreadPool

import time
import youtube_dl
import pyshorteners
from selenium import webdriver

from Global import *

nest_asyncio.apply()


class UtilityFunctions:
    def Shorten(self, Link):
        return pyshorteners.Shortener().tinyurl.short(Link)

    async def YouTube(self, Text):
        AudioPref = {
            "outtmpl": "Data/%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        VideoPref = {
            "outtmpl": "Data/%(title)s.%(ext)s",
            "merge-output-format": "mp4",
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        }

        Texts = Text.split()

        if len(Texts) > 1:
            for T in Texts:
                if "youtu" in T:
                    Link = T
                    break
        else:
            Link = Text
            Options = AudioPref

        if "mp3" in Text or "audio" in Text:
            Options = AudioPref
        elif "vid" in Text:
            Options = VideoPref
        else:
            Options = AudioPref

        with youtube_dl.YoutubeDL(Options) as Cursor:
            InfoDict = Cursor.extract_info(Link, download=False)
            Title = (
                InfoDict["title"]
                .replace('"', "")
                .replace("'", "")
                .replace("|", "-")
                .replace("?", "#")
            )
            FileName = f"{Title}.mp4"
            Options["outtmpl"] = "Data/" + FileName
        with youtube_dl.YoutubeDL(Options) as Downloader:
            Downloader.download([Link])

        for File in os.listdir("Data"):
            if Title in File:
                return File.replace(" ", "%20")

    def Twitter(self, url):
        op = webdriver.ChromeOptions()
        op.add_argument("--no-sandbox")
        op.add_argument("--disable-dev-shm-usage")

        with webdriver.Chrome(chrome_options=op) as driver:
            driver.implicitly_wait(10)
            driver.get("https://twipix.co/dash/")

            driver.find_element_by_class_name("input--style-4").send_keys(url)
            driver.find_element_by_xpath('//*[@id="theme"]/option[2]').click()
            driver.find_element_by_xpath(
                "/html/body/div/div/div/div/form/div[3]/div/div/div/label[1]"
            ).click()
            time.sleep(1)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
            driver.find_element_by_xpath(
                "/html/body/div/div/div/div/form/div[6]/button"
            ).click()
            time.sleep(1)
            Image = driver.find_element_by_xpath(
                "/html/body/div/div/div/div/form/img"
            ).get_attribute("src")

        import base64

        ImageBytes = bytes(str(Image).replace("data:;base64,", ""), encoding="utf-8")
        RawImage = base64.decodestring(ImageBytes)
        with open("Tweet.jpeg", "wb") as OutputImage:
            OutputImage.write(RawImage)

        return "Tweet.jpeg"


class Fun(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    def GetGiphy(self, Query, Rating):
        ApiKey = os.environ["GiphyToken"]
        ApiInstance = giphy_client.DefaultApi()

        try:
            ApiResponse = ApiInstance.gifs_search_get(
                ApiKey, q=Query, limit=25, rating=Rating
            )
            Image = random.choice(list(ApiResponse.data))
        except ApiException as e:
            print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)
            Image = None
        finally:
            return Image

    async def Fun(self, ctx, User, Base):
        try:
            if not User:
                User = ctx.author

            if Base == "kiss" or Base == "punch":
                End = "es"
            else:
                End = "s"

            Query = random.choice([Base, f"{Base}{End}"])
            if ctx.channel.is_nsfw():
                Image = self.GetGiphy(Query, "r")
            else:
                Image = self.GetGiphy(Query, "pg-13")

            Payload = discord.Embed(
                title=f"**{ctx.author} {Base}{End} {User}.**", color=ctx.author.color
            )
            Payload.set_image(url=f"https://media.giphy.com/media/{Image.id}/giphy.gif")

            await ctx.message.add_reaction(Emoji["Right"])

        except Exception as e:
            Payload = discord.Embed(
                title="Fun.Fun()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])

        finally:
            SentMessage = await Respond(ctx, Payload, False, True)
            await SentMessage.add_reaction("\U0001F923")  # LOL

    @commands.command()
    async def slap(self, ctx, *, User: discord.Member = None):
        await self.Fun(ctx, User, "slap")

    @commands.command()
    async def kick(self, ctx, *, User: discord.Member = None):
        await self.Fun(ctx, User, "kick")

    @commands.command()
    async def hug(self, ctx, *, User: discord.Member = None):
        await self.Fun(ctx, User, "hug")

    @commands.command()
    async def punch(self, ctx, *, User: discord.Member = None):
        await self.Fun(ctx, User, "punch")

    @commands.command()
    async def gif(self, ctx, *, Query):
        try:
            if ctx.channel.is_nsfw():
                Image = self.GetGiphy(Query, "r")
            else:
                Image = self.GetGiphy(Query, "pg-13")

            Payload = discord.Embed().set_image(
                url=f"https://media.giphy.com/media/{Image.id}/giphy.gif"
            )

            await ctx.message.add_reaction(Emoji["Right"])

        except Exception as e:
            Payload = discord.Embed(
                title="Fun.gif()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])

        finally:
            await Respond(ctx, Payload, False, True)


class Random(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command(aliases=["num"])
    async def number(self, ctx, start: int = 1, stop: int = 10):
        try:
            Payload = str(random.randint(start, stop))
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = f"Random.number(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            return await Respond(ctx, Payload)

    @commands.command()
    async def dice(self, ctx, NumberOfDice: int = 1):
        try:
            Payload = ", ".join(
                [str(random.randint(1, 6)) for i in range(NumberOfDice)]
            )
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = f"Random.dice(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            return await Respond(ctx, Payload)

    @commands.command()
    async def letter(self, ctx):
        try:
            Payload = random.choice([Letter for Letter in "abcdefghijklmnopqrstuvwxyz"])
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = f"Random.letter(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            return await Respond(ctx, Payload)

    @commands.command()
    async def quote(self, ctx):
        try:
            r = requests.get("https://api.quotable.io/random")
            Payload = r.json()["content"] + "\n    **-" + r.json()["author"] + "**"
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = f"Random.quote(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            return await Respond(ctx, Payload)


class Utility(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command()
    async def test(self, ctx):
        return await ctx.message.add_reaction(Emoji["Okay"])

    @commands.command()
    async def ping(self, ctx):
        try:
            Payload = f"Pong {round(self.Bot.latency,2)}"
            await ctx.message.add_reaction(Emoji["PingPong"])
        except Exception as e:
            Payload = f"Utility.ping(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            await Respond(ctx, Payload)

    @commands.command()
    async def shorten(self, ctx, Link=None):
        try:
            Payload = UtilityFunctions().Shorten(Link)
            await ctx.message.add_reaction(Emoji["Right"])
            await ctx.message.delete()
        except Exception as e:
            Payload = f"Utility.shorten(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            await Respond(ctx, Payload, True)

    @commands.command()
    async def search(self, ctx, Number="", *, Query=""):
        try:
            if Number.isdigit():
                Number = int(Number)
            else:
                Query = Number + " " + Query
                Number = 3

            await ctx.message.add_reaction(Emoji["Right"])

            Results = "\n".join(
                [result for result in googlesearch.search(Query, num_results=Number)]
            )
            Payload = discord.Embed(
                title="\U0001F50D " + Query, description=Results, color=ctx.author.color
            )  # .set_thumbnail(url=str(ctx.guild.icon_url))

        except Exception as e:
            Payload = discord.Embed(
                title="Utility.search()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])

        finally:
            await Respond(ctx, Payload, False, True)

    @commands.command(aliases=["horo", "libra"])
    async def horoscope(self, ctx, Sign="Libra"):
        def UpdateHoroscopes(FunctionRawData, FunctionData):
            def GetFreshData(Now):
                FreshData = {}
                TargetClass = "product_group_carousel full_carousel_100"

                URL = f"https://www.vogue.in/horoscope/collection/horoscope-today-{calendar.month_name[Now.month]}-{Now.day}-{Now.year}/"
                Request = requests.get(URL, headers=headers)
                Soup = bs4.BeautifulSoup(Request.content, "html.parser")

                for i in Soup.find_all("div", attrs={"class": TargetClass}):
                    for j in i.find_all(
                        "div", attrs={"class": "product-block-full pc_full"}
                    ):
                        Sign = j.find("h2").text.split()[0].lower()
                        Text = [k.text.strip() for k in j.find_all("p")]

                        FreshData[Sign] = {}
                        FreshData[Sign]["Horoscope"] = Text[0]
                        FreshData[Sign]["CosmicTip"] = Text[1]

                return FreshData

            Now = datetime.datetime.now()
            DateID = f"{str(Now.day).zfill(2)}.{str(Now.month).zfill(2)}.{Now.year}"

            FunctionData[DateID] = {}
            FunctionData[DateID] = GetFreshData(Now)

            with open("Data/Data.json", "w") as f:
                json.dump(FunctionRawData, f, indent=4)

        await ctx.message.add_reaction(Emoji["Okay"])
        Sign = Sign.lower()
        Now = datetime.datetime.now()
        DateID = f"{str(Now.day).zfill(2)}.{str(Now.month).zfill(2)}.{Now.year}"
        with open("Data/Data.json", "r") as f:
            RawData = json.loads(f.read())
            Data = RawData["Horoscope"]

        if Sign.lower() == "purge" and await Role(ctx):
            for L_DATE in Data:
                if L_DATE not in ["ZSigns", "ZImages"]:
                    del Data[L_DATE]

            await ctx.message.remove_reaction(Emoji["Okay"], self.Bot.user)
            return await ctx.message.add_reaction(Emoji["Right"])

        if DateID not in Data or Data[DateID] == {}:
            try:
                Payload = "Updating horoscope database. Please wait."
                WaitMessage = await Respond(ctx, Payload, False, False)
                UpdateHoroscopes(RawData, Data)
                with open("Data/Data.json", "r") as f:
                    RawData = json.loads(f.read())
                    Data = RawData["Horoscope"]
            except Exception as e:
                await ctx.message.remove_reaction(Emoji["Okay"], self.Bot.user)
                return await ctx.message.add_reaction(Emoji["Wrong"])
            finally:
                await WaitMessage.delete()

        # Payload = f"{DateID}: Horoscope for {Sign.title()}.\n```{Data[DateID][Sign]['Horoscope']}```\n**{Data[DateID][Sign]['CosmicTip']}**"
        Payload = f"> *{DateID}: Horoscope for {Sign.title()}.*\n```{Data[DateID][Sign]['Horoscope']}```\n**{Data[DateID][Sign]['CosmicTip']}**\n{Data['ZImages'][Sign.title()]}"

        # Title = f"{DateID}: Horoscope for {Sign.title()}"
        # Content = Data[DateID][Sign]["Horoscope"]
        # Tip = Data[DateID][Sign]["CosmicTip"]

        # Timestamp = datetime.datetime.now()
        # Color = 0x03C5FF
        # embed = discord.Embed(colour=Color, timestamp=Timestamp)
        # embed.add_field(name=Title, value=Content, inline=True)
        # embed.set_image(url=Data["ZImages"][Sign.title()])
        # await ctx.message.remove_reaction(Emoji["Okay"], self.Bot.user)
        # await ctx.message.add_reaction(Emoji["Right"])
        # await Respond(ctx, embed, False, True, 0)
        # return await Respond(ctx, f"**{Tip}**", True, False)
        return await Respond(ctx, Payload, False, False, 0)

    @commands.command()
    async def define(self, ctx, *, Word=""):

        await ctx.message.add_reaction(Emoji["Okay"])

        try:
            Base = "https://api.dictionaryapi.dev/api/v2/entries/en/" + Word.replace(
                " ", "%20"
            )
            Request = requests.get(Base).json()[0]

            await ctx.message.remove_reaction(Emoji["Okay"], self.Bot.user)
            await ctx.message.add_reaction(Emoji["Right"])

            RawMeaningList = [
                _Data_["definition"] for _Data_ in Request["meanings"][0]["definitions"]
            ]
            MeaningList = [
                _Data_["definition"] for _Data_ in Request["meanings"][0]["definitions"]
            ][:3]
            Data = {
                "Word": Word.title(),
                "RawMeaning": "; ".join(RawMeaningList),
                "Meaning": "; ".join(MeaningList),
                "Synonyms": ", ".join(
                    list(
                        set(
                            [
                                Synonym
                                for _Data_ in Request["meanings"][0]["definitions"]
                                for Synonym in _Data_["synonyms"]
                            ]
                        )
                    )[:3]
                ),
            }
            Payload = f"**{Word.title()}**\n**Meaning**: {Data['Meaning']}\n**Synonyms**: {Data['Synonyms']}"
        except Exception as e:
            await ctx.message.remove_reaction(Emoji["Okay"], self.Bot.user)
            await ctx.message.add_reaction(Emoji["Wrong"])
            Payload = f"Cannot find a meaning for the word **{Word.title()}**"

        return await Respond(ctx, Payload, False, False, 0)


class Information(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command(aliases=["si"])
    async def serverinfo(self, ctx):
        try:
            Server = str(ctx.guild.name)
            Description = "It's space to hang-out with friends."
            Owner = "<@529251441504681994>"
            MemberCount = str(ctx.guild.member_count)
            ChannelCount = len(ctx.guild.channels)
            Icon = str(ctx.guild.icon_url)

            Payload = discord.Embed(
                title=Server, description=Description, color=ctx.author.color
            )
            Payload.set_thumbnail(url=Icon)
            Payload.add_field(name="Owner", value=Owner, inline=True)
            Payload.add_field(name="Member Count", value=MemberCount, inline=True)
            Payload.add_field(name="Channel Count", value=ChannelCount, inline=True)
            Payload.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

            await ctx.message.add_reaction(Emoji["Right"])

        except Exception as e:
            Payload = discord.Embed(
                title="Information.serverinfo()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])

        finally:
            await Respond(ctx, Payload, False, True)

    @commands.command(aliases=["ui"])
    async def userinfo(self, ctx, *, User: discord.Member = None):
        try:
            if User is None:
                User = ctx.author

            Title = User.display_name
            Color = User.color
            Icon = User.avatar_url
            Joined = User.joined_at.strftime("%d %b, %Y")
            Reg = User.created_at.strftime("%d %b, %Y")

            Payload = discord.Embed(title=Title, color=Color)
            Payload.set_thumbnail(url=Icon)
            Payload.add_field(name="Joined", value=Joined, inline=True)
            Payload.add_field(name="Registered", value=Reg, inline=True)
            if len(User.roles) > 1:
                RoleString = " ".join([Role.mention for Role in User.roles][1:])
                Roles = f"Roles [{len(User.roles) - 1}]"
                Payload.add_field(
                    name=Roles,
                    value=RoleString,
                    inline=True,
                )

            await ctx.message.add_reaction(Emoji["Right"])

        except Exception as e:
            Payload = discord.Embed(
                title="Information.userinfo()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])

        finally:
            await Respond(ctx, Payload, False, True)

    @commands.command(aliases=["av"])
    async def avatar(self, ctx, *, User: discord.Member = None):
        try:
            if User is None:
                User = ctx.author
            Payload = discord.Embed(title=User.display_name, color=User.color)
            Payload.set_image(url=User.avatar_url)
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = discord.Embed(
                title="Information.avatar()",
                description=type(e).__name__,
                color=ctx.author.color,
            )
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            await Respond(ctx, Payload, False, True)


class Testing(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command()
    async def yttrim(self, ctx, URL=None, Start=None, Stop=None):
        HelpMessage = "```.yttrim <URL> <Start> <Stop>\nTime is only vaild in seconds as of now.```"
        IncorrectArgs = "**Incorrect Arguments.**\n```.yttrim <URL> <Start> <Stop>\nTime is only vaild in seconds as of now.```"

        if URL == None or Start == None or Stop == None:
            return await Respond(ctx, HelpMessage, False, False)

        if "https://" not in URL or "youtu" not in URL:
            return await Respond(ctx, HelpMessage, False, False)

        StartRE = re.search(r"(\d\d):(\d\d)", Start)
        StopRE = re.search(r"(\d\d):(\d\d)", Stop)
        if StartRE != None or StopRE != None:
            Start = StartRE[1] * 60 + StartRE[2]
            Stop = StopRE[1] * 60 + StopRE[2]

        VideoPref = {
            "outtmpl": "Data/%(title)s.%(ext)s",
        }

        with youtube_dl.YoutubeDL(VideoPref) as Cursor:
            InfoDict = Cursor.extract_info(URL, download=False)
            Duration = InfoDict["duration"]
            Title = (
                InfoDict["title"].replace('"', "").replace("'", "").replace("|", "-")
            )
            FileName = f"{Title}.{InfoDict['ext']}"
            VideoPref["outtmpl"] = "Data/" + FileName

        try:
            if type(int(Start)) != int or type(int(Stop)) != int:
                return await Respond(ctx, IncorrectArgs, False, False)
        except ValueError:
            return await Respond(ctx, IncorrectArgs, False, False)

        Start, Stop = int(Start), int(Stop)

        if Start > Stop:
            return await (ctx, IncorrectArgs + "\n**Start>Stop**")

        elif Start > Duration or Stop > Duration:
            return await (ctx, IncorrectArgs + "\n**Start or Stop > Duration**")

        # If everything is perfect
        FileName = await UtilityFunctions().YouTube(URL + " vid").replace("%20", " ")
        TrimFileName = "Trim - " + FileName
        TrimFile = "Data/Trim - " + FileName
        File = "Data/" + FileName
        with VideoFileClip(filename=File) as Clip:
            Clip = Clip.subclip(Start, Stop)
            Clip.write_videofile(TrimFile)
        os.remove(File)

        Payload = Host + TrimFileName.replace(" ", "%20")
        return await Respond(ctx, Payload, False, False)


class Message(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == True:
            return

        BackupChannel = self.Bot.get_channel(842390320057942028)
        await BackupChannel.send(f"{message.author}:{message.content}")

        if "youtu" in message.content.lower():
            try:
                File = await UtilityFunctions().YouTube(message.content)
                await message.author.send(f"{Host}{File}")
            except Exception as e:
                Payload = f"Message.youtube(): {type(e).__name__}"
                await message.author.send(Payload)

        if message.author.id not in Whitelist:
            return

        if "twitter.com" in message.content.lower():
            try:
                File = UtilityFunctions().Twitter(message.content)
                await message.author.send(file=discord.File(File))
                time.sleep(1)
                os.remove(File)
            except Exception as e:
                Payload = f"Message.twitter(): {type(e).__name__}"
                await message.author.send(Payload)


def setup(Bot):
    Bot.add_cog(Fun(Bot))
    Bot.add_cog(Random(Bot))
    Bot.add_cog(Utility(Bot))
    Bot.add_cog(Information(Bot))
    Bot.add_cog(Message(Bot))


