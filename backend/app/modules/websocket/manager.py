from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections for the application."""

    def __init__(self):
        """Initialize the ConnectionManager with an empty active connections map."""
        # Maps session_id -> list of connection dicts
        self.active_connections: dict[int, list[dict]] = {}

    async def connect(
        self, ws: WebSocket, session_id: int, user_id: int, user_name: str | None = None
    ):
        """Accept a WebSocket connection and add it to the active pool.

        Args:
            ws (WebSocket): The accepted WebSocket connection.
            session_id (int): The ID of the session the user is joining.
            user_id (int): The ID of the connecting user.
            user_name (str | None, optional): The name of the connecting user. Defaults to None.

        Returns:
            None
        """
        await ws.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        # Check if this user already has a connection (reconnect scenario)
        already_connected = False
        for i, conn in enumerate(self.active_connections[session_id]):
            if conn["user_id"] == user_id:
                # Silently replace the old connection — don't broadcast "joined" again
                try:
                    await conn["ws"].close()
                except Exception:
                    pass
                self.active_connections[session_id].pop(i)
                already_connected = True
                break

        connection = {"ws": ws, "user_id": user_id, "name": user_name}
        self.active_connections[session_id].append(connection)

        # Only broadcast "joined" for genuinely new users
        if not already_connected:
            await self.broadcast(
                session_id,
                {
                    "type": "system",
                    "content": f"{user_name or 'User'} joined the chat",
                    "user_id": user_id,
                },
            )

    def disconnect(self, ws: WebSocket, session_id: int):
        """Remove a WebSocket connection from the active pool.

        Args:
            ws (WebSocket): The WebSocket connection to remove.
            session_id (int): The ID of the session the user was connected to.

        Returns:
            dict | None: The removed connection object if found, otherwise None.
        """
        if session_id in self.active_connections:
            for i, conn in enumerate(self.active_connections[session_id]):
                if conn["ws"] == ws:
                    self.active_connections[session_id].pop(i)
                    return conn
        return None

    async def broadcast(
        self, session_id: int, message: dict, exclude_user_id: int = None
    ):
        """Send a JSON message to all active connections in a session.

        Args:
            session_id (int): The ID of the session to broadcast to.
            message (dict): The JSON serializable message to broadcast.
            exclude_user_id (int, optional): A user ID to exclude from the broadcast. Defaults to None.

        Returns:
            None
        """
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                if exclude_user_id and connection["user_id"] == exclude_user_id:
                    continue
                try:
                    await connection["ws"].send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()
