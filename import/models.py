from django.db import models


class Disk(models.Model):
    name = models.CharField(max_length=200)
    scan_datetime = models.DateTimeField()
    create_datetime = models.DateTimeField()
    comment = models.TextField()


class Folder(models.Model):
    disk = models.ForeignKey(Disk, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    comment = models.TextField()


class File(models.Model):
    disk = models.ForeignKey(Disk, on_delete=models.CASCADE, null=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    size = models.IntegerField()
    datetime = models.DateTimeField()
    rights = models.CharField(max_length=12)
    owner = models.CharField(max_length=20)
    group = models.CharField(max_length=20)
    sha1sum = models.CharField(max_length=40)
    comment = models.TextField()
