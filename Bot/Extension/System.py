import re
import os
import asyncio
import discord
from discord.ext import commands
from Global import *


class System(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.Cog.listener()
    async def on_ready(self):
        Game = discord.Game(name=".help")
        Target = self.Bot.get_channel(843016447839567912)
        await self.Bot.change_presence(activity=Game)
        await Respond(Target, "----------Booting Up.----------", True)

    @commands.command(aliases=["ext"])
    async def extension(self, ctx, Function="", Extension=""):
        if not await Role(ctx):
            return ctx.message.delete()

        try:
            FileList = [filename[:-3] for filename in os.listdir("./Bot/Extension")]
            HelpMessage = (
                "```.ext <Function> <Extension>"
                + "\nFunction = [load, unload, reload, list]"
                + "\nExtension = "
                + f"[{', '.join(FileList)}]```"
            )

            Function = Function.strip().lower()

            if Function == "list":
                await ctx.message.add_reaction(Emoji["Right"])
                return await Respond(ctx, f"Extension = [{', '.join(FileList)}]", True)

            if Extension == "":
                pass

            elif Extension not in FileList:
                await ctx.message.add_reaction(Emoji["Wrong"])
                return await Respond(ctx, HelpMessage, True)

            if Function == "load":
                self.Bot.load_extension(f"Extension.{Extension}")
                return await ctx.message.add_reaction(Emoji["Right"])

            elif Function == "unload":
                self.Bot.unload_extension(f"Extension.{Extension}")
                return await ctx.message.add_reaction(Emoji["Right"])

            elif Function == "reload":
                self.Bot.reload_extension(f"Extension.{Extension}")
                return await ctx.message.add_reaction(Emoji["Right"])

            elif Function == "list":
                pass

            else:
                await ctx.message.add_reaction(Emoji["Wrong"])
                return await Respond(ctx, HelpMessage)

        except Exception as e:
            await ctx.message.add_reaction(Emoji["Wrong"])
            Payload = f"System.extnesion(): {type(e).__name__}"
            return await Respond(ctx, Payload)


class Management(commands.Cog):
    def __init__(self, Bot):
        self.Bot = Bot

    @commands.command(aliases=["delete", "purge"])
    async def clear(self, ctx, Value=5):
        if not await Role(ctx):
            return ctx.message.delete()

        try:
            await ctx.message.add_reaction(Emoji["Right"])
            await asyncio.sleep(1)
            return await ctx.channel.purge(limit=Value + 1)
        except Exception as e:
            Payload = f"Management.clear(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
            return await Respond(ctx, Payload)

    @commands.command(aliases=["say", "tell"])
    async def send(self, ctx, Variable, *, Text=""):
        if not await Role(ctx):
            return ctx.message.delete()

        try:
            if "<@!" in Variable:
                Target = await self.Bot.fetch_user(
                    int(re.match(r"<@!(.*)>", Variable).group(1))
                )
            else:
                Target = await self.Bot.fetch_user(Variable)

            await ctx.message.add_reaction(Emoji["Right"])
            return await Respond(Target, Text, True)

        except Exception as e:
            try:
                if "<#" in Variable:
                    Target = self.Bot.get_channel(
                        int(re.match(r"<#(.*)>", Variable).group(1))
                    )
                else:
                    Target = self.Bot.get_channel(Variable)

                await ctx.message.add_reaction(Emoji["Right"])
                return await Respond(Target, Text, True)

            except Exception as e:
                try:
                    Target = ctx
                    if Variable.isdigit():
                        if int(Variable) > 100:
                            Variable = 100
                        await ctx.message.add_reaction(Emoji["Right"])
                        for i in range(int(Variable)):
                            await Respond(Target, Text, True)
                    else:
                        Payload = Variable + " " + Text
                        await ctx.message.add_reaction(Emoji["Right"])
                        return await Respond(Target, Payload, True)

                except Exception as e:
                    Payload = f"Management.send(): {type(e).__name__}"
                    await ctx.message.add_reaction(Emoji["Wrong"])
                    await Respond(ctx, Payload)

    @commands.command(aliases=["cover"])
    async def blank(self, ctx, Iteration=1):
        if not await Role(ctx):
            return

        try:
            Void = "\n " * 100
            Payload = f"```{Void}```"
            await ctx.message.add_reaction(Emoji["Right"])
        except Exception as e:
            Payload = f"Management.cover(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
        finally:
            if "Management.cover():" not in Payload:
                for i in range(Iteration):
                    await Respond(ctx, Payload, True, False)
            else:
                await Respond(ctx, Payload, True, False)
            if ctx.channel.type.value == 0:
                await ctx.message.delete()
            return

    @commands.command()
    async def data(self, ctx, Function=None, File=None):
        if not await Role(ctx):
            return ctx.message.delete()

        try:
            Functions = ["deletea", "deletef", "list", "link"]
            HelpMessage = f"```.Data <Function> <File=None>\n-----\nFunction ={str(Functions)}\n<File> is only usable for deletef command.```"

            if Function == None:  # or Key == None:
                await ctx.message.add_reaction(Emoji["Wrong"])
                return await Respond(ctx, HelpMessage)

            elif Function.lower() not in Functions:
                await ctx.message.add_reaction(Emoji["Wrong"])
                return await Respond(ctx, HelpMessage)

            elif Function.lower() == "deletea":
                await ctx.message.add_reaction(Emoji["Right"])

                RawData = os.listdir("Data")
                DataLength = len(RawData)
                DataString = "\n".join(RawData)
                Payload = f"```Deleted {DataLength} Files from the Data folder. Named as:\n{DataString}\n------```"

                RawData.remove("Empty.txt")
                if "Data.json" in RawData:
                    RawData.remove("Data.json")
                for File in RawData:
                    os.remove("Data/" + File)

                return await Respond(ctx, Payload, False, False)

            elif Function.lower() == "deletef":
                RawData = os.listdir("Data")
                DataLength = len(RawData)
                DataString = "\n".join(RawData)
                Payload1 = f"```There are {DataLength} Files in the Data folder. Please use any one of this file as an argument for deletef function:\n{DataString}\n------```"

                if File == None:
                    await ctx.message.add_reaction(Emoji["Wrong"])
                    return await Respond(ctx, HelpMessage, False, False)
                elif File not in RawData:
                    await ctx.message.add_reaction(Emoji["Wrong"])
                    return await Respond(ctx, Payload1, False, False)
                elif File in RawData:
                    await ctx.message.add_reaction(Emoji["Right"])
                    Payload2 = f"```Deleted: {File}```"
                    os.remove("Data/" + File)
                    await Respond(ctx, Payload2, False, False)

            elif Function.lower() == "list":
                await ctx.message.add_reaction(Emoji["Right"])

                RawData = os.listdir("Data")
                DataLength = len(RawData)
                DataString = "\n".join(RawData)
                Payload = f"```There are {DataLength} Files in the Data folder. Named as:\n{DataString}\n------```"

                return await Respond(ctx, Payload, False, False)

            elif Function.lower() == "link":
                await ctx.message.add_reaction(Emoji["Right"])

                RawData = os.listdir("Data")
                DataLength = len(RawData)
                DataString = "\n".join(
                    [Host + File.replace(" ", "%20") for File in RawData]
                )
                Payload = f"There are {DataLength} Files in the Data folder. Here are the links:\n{DataString}\n------"

                return await Respond(ctx, Payload, False, False)

        except Exception as e:
            Payload = f"Dash.Data(): {type(e).__name__}"
            await ctx.message.add_reaction(Emoji["Wrong"])
            return await Respond(ctx, Payload)


def setup(Bot):
    Bot.add_cog(System(Bot))
    Bot.add_cog(Management(Bot))
