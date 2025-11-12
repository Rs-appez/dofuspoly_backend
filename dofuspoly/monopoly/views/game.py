from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..exceptions import GameException
from ..decorators import is_player_in_game
from ..realtimes import update_game
from ..models import Game, Player
from ..serializers import (
    GameSerializer,
)


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    @is_player_in_game
    def roll_dice(self, request, game: Game = None, pk=None):
        try:
            game.roll_dice()
            game.current_player.trigger_space_effect(game)

        except GameException as e:
            return Response({"status": "error", "message": str(e)}, status=403)

        update_game(game)
        return Response(
            {
                "status": "dice rolled",
            }
        )

    @action(detail=False, methods=["get"])
    def current_game(self, request):
        player = get_object_or_404(Player, user=request.user)
        game = player.get_current_game()
        serializer = self.get_serializer(game)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    @is_player_in_game
    def end_turn(self, request, pk=None, game: Game = None, player: Player = None):
        player.end_turn(game)
        update_game(game)
        return Response({"status": "turn ended"})

    @action(detail=True, methods=["get"])
    @is_player_in_game
    def buy_space(self, request, pk=None, game: Game = None, player: Player = None):
        space = game.board.spaces.get(position=player.position)

        try:
            player.buy_space(game, space)
        except GameException as e:
            return Response({"status": "error", "message": str(e)}, status=403)

        update_game(game)
        return Response({"status": "space bought"})
