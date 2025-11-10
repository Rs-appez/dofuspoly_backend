from django.db import models


class Card(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.ForeignKey("CardType", on_delete=models.CASCADE)

    image = models.ImageField(upload_to="statics/cards/")
    image_back = models.ImageField(upload_to="statics/cards/", null=True, blank=True)

    def __str__(self):
        return self.name


class CardType(models.Model):
    type = models.CharField(max_length=255)

    def __str__(self):
        return self.type
