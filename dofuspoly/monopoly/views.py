from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


from .exceptions import GameException
from .models import Board, Color, Case, Game, Rent, CaseType, Card, CardType, Player
from .serializers import (
    BoardSerializer,
    ColorSerializer,
    CaseSerializer,
    GameSerializer,
    RentSerializer,
    CaseTypeSerializer,
    CardSerializer,
    CardTypeSerializer,
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
    def roll_dice(self, request, pk=None):
        game: Game = self.get_object()
        player = get_object_or_404(Player, user=request.user)

        if game.current_player != player:
            return Response(
                {"status": "error", "message": "It's not your turn!"}, status=403
            )

        try:
            game.roll_dice()
        except GameException as e:
            return Response({"status": "error", "message": str(e)}, status=403)

        game_serializer = self.get_serializer(game)
        return Response(
            {
                "status": "dice rolled",
                "game": game_serializer.data,
            }
        )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def current_game(self, request):
        player = get_object_or_404(Player, user=request.user)
        game = Game.objects.filter(players=player, finished=False).first()
        serializer = self.get_serializer(game)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
