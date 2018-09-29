from django.db import models


class Disc(models.Model):
    name = models.CharField(max_length=200)
    datetime = models.DateTimeField()
    comment = models.TextField()


class Folder(models.Model):
    name = models.CharField(max_length=200)
    disk = models.ForeignKey(Disc, on_delete=models.CASCADE)
    comment = models.TextField()


class File(models.Model):
    name = models.CharField(max_length=200)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    size = models.IntegerField()
    datetime = models.DateTimeField()
    rights = models.CharField(max_length=12)
    owner = models.CharField(max_length=20)
    group = models.CharField(max_length=20)
    sha1sum = models.CharField(max_length=40)
    comment = models.TextField()
