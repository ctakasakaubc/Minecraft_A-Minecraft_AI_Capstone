# For receiving code from communicator.js and connecting with Minecraft
import asyncio
import websockets
from io import StringIO
import contextlib
import sys
# Required for communicating with Minecraft
import json
import uuid
import typing
# HTTP Server
from multiprocessing import Process
import serve
###########################################
# TODO: Delete this stuff soon            #
# Printing to CSV file (PEER TESTING ONLY)#
###########################################
import csv
CSV_PATH = "../minecraft_data/event_data.csv"
with open(CSV_PATH,'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow((
        'eventName',
        'block',
        'posX',
        'posZ'
    ))
###########################################

minecraft_socket = ""
_SUBSCRIPTIONS: typing.Dict[str, typing.List[typing.Any]] = {}
active_subscriptions = set()


async def subscribe_callback(websocket, event_name: str, callback,) -> str:
    '''
    Subscribes to minecraft event by sending JSON object
    '''
    if not isinstance(event_name, str):
        raise TypeError("expected 'str' for event_name")

    evt_id = uuid.uuid4().hex

    message = {
        "header": {
            "messagePurpose": "subscribe",
            "messageType": "commandRequest",
            "requestId": evt_id,
            "version": 1,
        },
        "body": {"eventName": event_name, "version": 1},
    }

    await websocket.send(json.dumps(message))
    _SUBSCRIPTIONS.setdefault(event_name, []).append((evt_id, callback))
    return evt_id

async def execute_command(websocket, command: str, *args):
    '''
    Sends JSON to execute a command in the game
    '''
    if not isinstance(command, str):
        raise TypeError("expected 'str' for command")

    if args:
        command += " " + " ".join(str(a) for a in args if a is not None)

    req_id = uuid.uuid4().hex
    message = {
        "header": {
            "messagePurpose": "commandRequest",
            "messageType": "commandRequest",
            "requestId": req_id,
            "version": 1,
        },
        "body": {"commandLine": command, "version": 1},
    }

    await websocket.send(json.dumps(message))

def handle_message(message):
    '''
    Handles JSON objects received over minecraft connection

    This will be what gets stored in the database we are using
    '''
    data = json.loads(message)
    with open(CSV_PATH,'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow((
            data['body']['eventName'],
            data['body']['properties']['Block'],
            data['body']['properties']['FeetPosX'],
            data['body']['properties']['FeetPosZ']
        ))

def handle_all(message):
    pass

# Communicates with Minecraft WebSockets
async def connect_minecraft(websocket, path):
    '''
    NOTE: Requires Player to use "/connect localhost:<port>" to connect

    Creates the websocket connection with Minecraft.
    Stores events that occur in a CSV file
    '''
    print("Connected to Minecraft")
    global minecraft_socket
    minecraft_socket = websocket # initializes the global variable
    try:
        async for message in websocket:
            handle_message(message) # stores message in the csv for the time being
    except:
        raise
            

# Communicates with JavaScript Pillbox
async def subscribe_to_event_list(websocket, path):
    '''
    Retrieves a comma separated list of events from the pillbox.
    Subscribes to each event in the comma separated list
    '''
    try:
        async for message in websocket:
            # Currently there is no means of unsubscribing to events
            #   Our unsubscription is handled via the acitve_subscription set

            # message assumed to be a comma separated list of events
            event_list = message.split(",")
            print(event_list)
            global active_subscriptions
            active_subscriptions = set(event_list)
            # subscribes to each event in the list
            for event in event_list:
                await subscribe_callback(minecraft_socket, event, handle_all)
    except:
        raise

async def receive_code(websocket, path):
    try:
        code_return = "NO CODE RETURN"
        received_msg = False
        async for message in websocket:
            received_msg = True
            print(message)
            try:
                with stdoutIO() as s:
                    exec(message)

                code_return = s.getvalue()
                print(code_return)

                await websocket.send(code_return) 
            except Exception as e:
                await websocket.send(str(e))
    except:
        raise

@contextlib.contextmanager
def stdoutIO(stdout=None):
    # store original standard out
    old = sys.stdout 
    # define new place for system to output
    if stdout is None:
        stdout = StringIO()
    # send new output area
    sys.stdout = stdout
    yield stdout
    # reset sys.stdout
    sys.stdout = old


if __name__ == "__main__":
    # Initialize Minecraft WebSocket connection
    print("starting websockets")
    print("/connect localhost:8765")
    start_mine_server = websockets.serve(
        connect_minecraft,
        "localhost",
        8765,
        subprotocols=["com.microsoft.minecraft.wsencrypt"],
        ping_interval=None
    )

    start_pillbox_server = websockets.serve(
        subscribe_to_event_list,
        "localhost",
        3005 # Pillbox port
    )

    # Starts Child Process for HTTP Server on port 3000, which Minecraft is listening to
    print("starting http server")
    http_process = Process(target=serve.run_server, args=(3000,))
    http_process.start()

    print("starting kernel")
    # Listens to receive code from webpage
    start_server = websockets.serve(receive_code, "localhost", 3001)

    # Run all Async
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_until_complete(start_pillbox_server)
    asyncio.get_event_loop().run_until_complete(start_mine_server)
    asyncio.get_event_loop().run_forever()
