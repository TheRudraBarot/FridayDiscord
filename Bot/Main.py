import os
import flask
import threading
from discord.ext import commands
from dotenv import load_dotenv


Bot = commands.Bot(command_prefix=".")
App = flask.Flask("")


class WebServer:
    @App.route("/")
    def Home():
        return "<01000110><01110010><01101001><01100100><01100001><01111001>"

    @App.route("/<path:Path>")
    def File(Path):
        try:
            return flask.send_from_directory("Data", Path, as_attachment=True)
        except Exception as e:
            return f"<01000101><01010010><01010010><01001111><01010010> : {type(e).__name__}"

    def Run():
        App.run(host="0.0.0.0", port=5050)

    def StayAwake():
        threading.Thread(target=WebServer.Run).start()


for File in os.listdir("./Bot/Extension"):
    if File.endswith(".py"):
        Bot.load_extension(f"Extension.{File[:-3]}")


WebServer.StayAwake()
if load_dotenv():
    Bot.run(os.environ["Discord_Bot_Token"])
