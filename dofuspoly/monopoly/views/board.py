from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Board
from ..serializers import (
    BoardSerializer,
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
