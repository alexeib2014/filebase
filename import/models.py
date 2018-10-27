from django.db import models


class Location(models.Model):
    comment = models.TextField()


class Disk(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, db_index=True)
    file_name = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, db_index=True)
    scan_datetime = models.DateTimeField(db_index=True)
    create_datetime = models.DateTimeField()
    next_version = models.ForeignKey('Disk', on_delete=models.CASCADE, null=True)
    comment = models.TextField()


class Folder(models.Model):
    disk = models.ForeignKey(Disk, on_delete=models.CASCADE, null=True, db_index=True)
    parent = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    comment = models.TextField()


class FileUnique(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    size = models.IntegerField(db_index=True)
    datetime = models.DateTimeField()
    rights = models.CharField(max_length=12)
    owner = models.CharField(max_length=20)
    group = models.CharField(max_length=20)
    sha1sum = models.CharField(max_length=40, db_index=True)
    comment = models.TextField()


class File(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, db_index=True)
    file = models.ForeignKey(FileUnique, on_delete=models.CASCADE, null=True, db_index=True)
