from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from .exceptions import GameException
from .decorators import is_player_in_game
from .realtimes import update_game
from .models import Board, Game, Player
from .serializers import (
    BoardSerializer,
    GameSerializer,
    PlayerSerializer,
)


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def make_board(self, request, pk=None):
        board = Board()
        board.save()
        board.make_board()
        return Response({"status": "board created"})


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    @is_player_in_game
    def roll_dice(self, request, game: Game = None, player: Player = None, pk=None):
        try:
            game.roll_dice()
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


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
