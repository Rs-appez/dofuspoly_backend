import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Game
from .serializers import GameSerializer


def update_game(game: Game) -> None:
    """
    Send a ticket to update the game.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"game_{game.id}",
        {
            "type": "new_ticks",
            "content": json.dumps(
                {
                    "game": GameSerializer(game).data,
                }
            ),
        },
    )
