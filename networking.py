import asyncio
import json
import logging
import re

import aiohttp
from unidecode import unidecode

import question


async def fetch(url, session, timeout):
    try:
        async with session.get(url, timeout=timeout) as response:
            return await response.text()
    except Exception:
        print("Server timeout/error to {url}")
        logging.exception("Server timeout/error to {url}")
        return ""


async def get_responses(urls, timeout, headers):
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            task = asyncio.ensure_future(fetch(url, session, timeout))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


async def get_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        return await fetch(url, session, timeout)


async def get_json_response(url, timeout, headers):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()


async def websocket_handler(uri, headers, client=None, channel=None):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(uri, headers=headers, heartbeat=5, timeout=30) as ws:
            if channel and client:
                await client.send_message(channel, "Connected")
            print("Connected")
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    message = msg.data
                    message = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", message)

                    message_data = json.loads(message)
                    logging.debug(str(message_data).encode("utf-8"))

                    if "error" in message_data and message_data["error"] == "Auth not valid":
                        logging.debug(message_data)
                        await client.send_message(bot_channel, "Connection settings invalid")
                        #raise RuntimeError("Connection settings invalid")
                    elif message_data["type"] != "interaction":
                        logging.debug(message_data)
                        if message_data["type"] == "question":
                            question_str = unidecode(message_data["question"])
                            answers = [unidecode(ans["text"])
                                       for ans in message_data["answers"]]
                            if channel and client:
                                message_text = '\n' * 5 + "\nQuestion detected\n" + \
                                    "Question {message_data['questionNumber']} out of {message_data['questionCount']}\n" + \
                                    question_str + '\n' + answers
                                await client.send_message(channel, message_text)
                                answer = await question.answer_question(question_str, answers)
                                await client.send_message(channel, answer)
                            else:
                                print("\n" * 5)
                                print("Question detected.")
                                print(
                                    "Question {message_data['questionNumber']} out of {message_data['questionCount']}")
                                print(question_str)
                                print(answers)
                                print()
                                print(await question.answer_question(question_str, answers))

    print("Socket closed")
