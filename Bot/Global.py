headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0",
}
Host = "https://FridayDiscord.rudra1510.repl.co/"
Emoji = {
    "Okay": "\U0001F44C",
    "Wrong": "\u274C",
    "Right": "\u2705",
    "PingPong": "\U0001F3D3",
}

Whitelist = [529251441504681994, 858998113453080577]

import asyncio


async def Respond(
    Target, Payload, Send=False, Embed=False, SecPerCharacter=0.01, *args, **kwargs
):
    async with Target.typing():
        await asyncio.sleep(round(len(Payload) * SecPerCharacter))
    if Send:
        if Embed:
            return await Target.send(embed=Payload, *args, **kwargs)
        return await Target.send(Payload, *args, **kwargs)
    elif not Send:
        if Embed:
            return await Target.reply(embed=Payload, *args, **kwargs)
        return await Target.reply(Payload, *args, **kwargs)


async def Role(ctx):
    Check = ["Admin", "Developer"]

    try:

        if ctx.author.id in Whitelist:
            return True
        elif ctx.channel.type.value == 1:
            Roles = ["Member"]
        elif ctx.channel.type.value == 0:
            Roles = [Role.name for Role in ctx.author.roles]

        RolesInt = len(set(Roles).intersection(Check))

        if RolesInt < 1:
            await ctx.message.add_reaction(Emoji["Wrong"])
            Payload = f"Unauthorized Access Denied."
            Current = await Respond(ctx, Payload)
            await asyncio.sleep(3)
            await Current.delete()
            await ctx.message.delete()
            return None
        else:
            return True
    except Exception as e:
        await ctx.message.add_reaction(Emoji["Wrong"])
        Payload = f"Roles(): {type(e).__name__}"
        Current = await Respond(ctx, Payload)
        await asyncio.sleep(3)
        await Current.delete()
        await ctx.message.delete()
        return None
