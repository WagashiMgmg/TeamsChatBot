import asyncio
import os
import openai
from flask import Flask, request, Response, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
import json
from dotenv import load_dotenv

load_dotenv()


openai.api_key = os.getenv("OPENAI_KEY")

app = Flask(__name__)
loop = asyncio.get_event_loop()

bot_settings = BotFrameworkAdapterSettings(os.getenv("BOT_FRAMEWORK_ID"), os.getenv("BOT_FRAMEWORK_PASS"))
bot_adapter = BotFrameworkAdapter(bot_settings)


async def on_turn(turn_context: TurnContext):
    if turn_context.activity.type == ActivityTypes.message:
        response = await generate_response(turn_context.activity.text)
        reply = Activity(type=ActivityTypes.message, text=response)
        await turn_context.send_activity(reply)


async def generate_response(prompt):
    #response = openai.Completion.create(
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}, 
        ]
    )
    message = response["choices"][0]["message"]["content"]
    return message


@app.route("/api/messages", methods=["POST"])
async def messages():
    if "application/json" in request.headers["Content-Type"]:
        json_data = request.get_data()
        data = json.loads(json_data)
    else:
        return Response(status=415)

    activity = Activity().deserialize(data)
    auth_header = request.headers["Authorization"] if "Authorization" in request.headers else ""
    try:
        response = await bot_adapter.process_activity(activity, auth_header, on_turn)
        if response:
            return jsonify(response)
        return Response(status=201)
    except Exception as exception:
        raise exception


if __name__ == "__main__":
    app.run()