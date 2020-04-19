import time
import asyncio
import logging
from datetime import datetime

import networking

# Set up logging
logging.basicConfig(filename="data.log", level=logging.DEBUG, filemode="w")

# Read in bearer token and user ID
BEARER_TOKEN = "NzAxNDYwOTc0NDkzODkyNzM5.Xpx5PQ.yM8lOt3qSrUcezvHyoYmHYBYWg0"
USER_ID = "701460974493892739"

main_url = "https://api-quiz.hype.space/shows/now?type=hq&userId={USER_ID}"
headers = {"Authorization": "Bearer {BEARER_TOKEN}",
           "x-hq-client": "Android/1.3.0"}
# "x-hq-stk": "MQ==",
# "Connection": "Keep-Alive",
# "User-Agent": "okhttp/3.8.0"}

while True:
    print()
    try:
        response_data = asyncio.get_event_loop().run_until_complete(
            networking.get_json_response(main_url, timeout=1.5, headers=headers))
    except:
        print("Server response not JSON, retrying...")
        time.sleep(1)
        continue

    logging.debug(response_data)

    if "broadcast" not in response_data or response_data["broadcast"] is None:
        if "error" in response_data and response_data["error"] == "Auth not valid":
            raise RuntimeError("Connection settings invalid")
        else:
            print("Show not on.")
            next_time = datetime.strptime(
                response_data["nextShowTime"], "%Y-%m-%dT%H:%M:%S.000Z")
            now = time.time()
            offset = datetime.fromtimestamp(
                now) - datetime.utcfromtimestamp(now)

            print(
                "Next show time: {(next_time + offset).strftime('%Y-%m-%d %I:%M %p')}")
            print("Prize: " + response_data["nextShowPrize"])
            time.sleep(5)
    else:
        socket = response_data["broadcast"]["socketUrl"]
        print("Show active, connecting to socket at {socket}")
        asyncio.get_event_loop().run_until_complete(
            networking.websocket_handler(socket, headers))
