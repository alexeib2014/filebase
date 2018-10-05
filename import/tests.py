from django.test import TestCase
from .views import Record
from .models import Disk, Folder


class ImportTestCase(TestCase):
    disk_name = 'DiskName'
    disk_time = '2018-01-01 00:00:00'
    disk = None

    def setUp(self):
        disk = Record.create_disk(self.disk_name, self.disk_time)
        assert disk == True
        self.disk = Record.get_disk(self.disk_name, self.disk_time)
        assert self.disk.name == self.disk_name

    def test_create_disk(self):
        disk = Disk.objects.get(id=1)
        assert disk.name == self.disk_name

    def test_recreate_disk(self):
        disk1 = Disk.objects.get(id=1)
        assert disk1.name == self.disk_name
        disk = Record.create_disk(self.disk_name, self.disk_time)
        assert disk == False

    def test_create_empty_folder(self):
        Record.get_folder(self.disk, [])
        folders = Folder.objects.all()
        assert len(folders) == 0

    def test_create_folder(self):
        Record.get_folder(self.disk, ['folder'])
        folders = Folder.objects.all()
        assert len(folders) == 1
