from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer


class GameSyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.group_name = f"game_{self.game_id}"
        self.send({"type": "websocket.accept"})

        # Join ticks group
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

    def websocket_disconnect(self, event):
        # Leave ticks group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def new_ticks(self, event):
        self.send(
            {
                "type": "websocket.send",
                "text": event["content"],
            }
        )
