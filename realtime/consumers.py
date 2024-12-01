import redis
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from urllib.parse import parse_qs

# Connecting to the Redis server
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Globalizing the key name for the waiting lobby in Redis
WAITING_LOBBY = 'waiting_lobby'

class ConnectionConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer that handles WebSocket connections and communication
    for users in the waiting lobby.
    """

    async def connect(self):
        """
        Handles the initial connection of a user.

        - Retrieves the username from the request.
        - Closes the connection if no username is provided.
        - Pushes the user data (channel name and username) to the Redis waiting lobby.
        - Accepts the WebSocket connection.
        - Attempts to match the user with another user in the waiting lobby.
        """

        # Retrieve the username of the user
        username = self.get_username()

        # Reject the connection if no username is provided
        if not username:
            print("Connection without username rejected !")
            self.close()
            return
        
        # Store the user's data (channel name and username)
        self.user_data = json.dumps({
            "username": username,
            "channel_name": self.channel_name
        })
        
        # Add the user to the waiting pool in Redis
        redis_client.lpush(WAITING_LOBBY, self.user_data)

        # Accept the WebSocket connection (handshake)
        await self.accept()

        # Try to match the user with another user in the waiting pool
        await self.match_user()
    
    async def match_user(self):
        # Check if there are at least 2 users in the waiting pool
        waiting_count = redis_client.llen(WAITING_LOBBY)
        if waiting_count > 1:
            print("Matching users...")

            # Pop two users from the right of the waiting pool in Redis
            user1 = json.loads(redis_client.rpop(WAITING_LOBBY))
            user2 = json.loads(redis_client.rpop(WAITING_LOBBY))
            # Create a unique room name based on both users

            data_to_send = {
                    "type": "match.notification",   # Type of event to trigger the corresponding handler
                    "user1":user1,
                    "user2":user2
            }
            await self.channel_layer.send(user1["channel_name"], data_to_send)

    async def match_notification(self, event):
        await self.send_json({
            "signal_type":"match",
            "user1":event["user1"],
            "user2":event["user2"],
        })

    async def receive_json(self, content, **kwargs):
        """
            This format will be coming in the content 
            content = {
                "signal_type":"offer / answer / ice_candiate_user1 / ice_candiate_user2",
                "sdp":"sdp_of_user",
                "user1":{
                    "channel_name":"user1_channel_name",
                    "username":"username_of_user1"
                },
                "user2":{
                    "channel_name":"user2_channel_name",
                    "username":"username_of_user2"
                }
            }
        """
        # try:
        user_mapping_by_type = {
            "offer": "user2",
            "answer": "user1",
            "ice_candidate_user1": "user2",
            "ice_candidate_user2": "user1",
        }

        user_to_send = user_mapping_by_type[content["signal_type"]]
        content["type"] = "handle.signal"

        await self.channel_layer.send(content[user_to_send]["channel_name"], content)

        # except Exception as e:
        #     print("!!! Got Error when signaling through users !!!", e)
        #     # Handle any unexpected errors gracefully
        #     return

    async def handle_signal(self, data):
        data.pop("type")
        await self.send_json(data)
        
    async def transfer_between(self, event):
        """
        Transfer the received data to the WebSocket client.
        
        This method takes the data sent by the group and forwards it to the client.
        """
        try:
            # Extract the 'data' field from the event
            data = event.get("data")
            
            # If no data is present, exit without doing anything
            if not data:
                return

            # Send the data to the WebSocket client
            await self.send_json(content=data)

        except Exception:
            # Handle any unexpected errors while sending the message
            return
    
    async def disconnect(self, code):
        """
        Handles the WebSocket disconnection.

        - Removes the user from the Redis waiting lobby.
        - Cleans up the connection before closing it.
        """
        # Remove the user from the Redis waiting pool
        redis_client.lrem(WAITING_LOBBY, 0, self.user_data)

        # Handle any necessary cleanup before closing the connection
        await self.close()

    def get_username(self):
        """
        Retrieves the username from the WebSocket connection.

        - Checks if the user is authenticated.
        - If authenticated, uses the username from the user object.
        - If not authenticated, parses the query string for a 'username' parameter.

        Returns:
            str or None: The username if found, otherwise None.
        """
        username = None

        # Check if the user is authenticated via the WebSocket connection
        if self.scope["user"].is_authenticated:
            # Use the authenticated user's username
            username = self.scope["user"].username
        else:
            # Decode and parse the query string for 'username'
            query_params = parse_qs(self.scope['query_string'].decode())
            username = query_params.get('username', [None])[0]  # Get the first value if present

        return username

    