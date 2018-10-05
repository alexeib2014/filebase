from django.http import HttpResponse
import time
from .models import Disk, Folder, File


class Record:
    @classmethod
    def get_disk(cls, name, scan_datetime):
        disks = Disk.objects.filter(name=name, scan_datetime=scan_datetime)
        if len(disks) == 0:
            return None
        if len(disks) > 1:
            cls.log('Multiple disks in database (%s,%s)' % (name, scan_datetime))
        cls.disk = disks[0]
        return cls.disk

    @classmethod
    def get_folder(cls, disk, folder_arr):
        folder = None
        for folder_name in folder_arr:
            parent = folder
            folders = Folder.objects.filter(disk=disk, parent=parent, name=folder_name)
            if folders:
                folder = folders[0]
            else:
                folder = Folder(disk=disk,
                                parent=parent,
                                name=folder_name)
                folder.save()
        return folder

    @classmethod
    def create_disk(cls, name, scan_datetime):
        if cls.get_disk(name, scan_datetime):
            cls.log('Disk already imported (%s,%s)' % (name, scan_datetime))
            return False

        create_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        disk = Disk( name = name,
            scan_datetime = scan_datetime,
          create_datetime = create_datetime )
        disk.save()
        return True

    @classmethod
    def write_record(cls, disk_name, disk_datetime, full_name, size, datetime, rights, owner, group, sha1sum):
        disk = cls.get_disk(disk_name, disk_datetime)
        if disk is None:
            raise Exception("Disk doesn't exist (%s, %s)" % (disk_name, disk_datetime))

        folder_file_name = full_name[len(disk_name):]
        folder_file_name_arr = folder_file_name.split('/')
        folder = cls.get_folder(disk, folder_file_name_arr[1:-1])

        file_name = folder_file_name_arr[-1]

        file = File(disk = disk,
                  folder = folder,
                    name = file_name,
                    size = size,
                datetime = datetime,
                  rights = rights,
                   owner = owner,
                   group = group,
                 sha1sum = sha1sum)
        file.save()

    @classmethod
    def reset_database(cls):
        disks = Disk.objects.all()
        for disk in disks:
            disk.delete()

    @classmethod
    def log(cls, message):
        print(message)


class ImportFile:
    line_number = 0

    def readline(self, f):
        self.line_number += 1
        line = f.readline().replace('\n','').replace('\r','')
        return line

    def translate_disk_datetime(self, line):
        months = {'Jan': '01',
                  'Feb': '02',
                  'Mar': '03',
                  'Apr': '04',
                  'May': '05',
                  'Jun': '06',
                  'Jul': '07',
                  'Aug': '08',
                  'Sep': '09',
                  'Oct': '10',
                  'Nov': '11',
                  'Dec': '12'}
        year = line[-4:]
        month = months[line[4:7]]
        day = '%02i' % int(line[8:10])
        time = line[11:19]
        result = '%s-%s-%s %s' % (year, month, day, time)
        return result

    def translate_file_line0(self, line):
        try:
            line_arr = line.split(' ')
            rights = line_arr[0]
            owner = line_arr[2]
            group = line_arr[3]
            size = line_arr[4]
            file_datetime = line_arr[5] + ' ' + line_arr[6][:8]
            fullname0 = line_arr[-1]
        except:
            rights = ''
            owner = ''
            group = ''
            size = ''
            file_datetime = ''
            fullname0 = ''

        return rights, owner, group, size, file_datetime, fullname0

    def translate_file_line1(self, line):
        try:
            line_arr = line.split(' ')
            sha1sum = line_arr[0]
            fullname1 = line_arr[-1]
        except:
            sha1sum = ''
            fullname1 = ''

        return sha1sum, fullname1

    def log(self, message):
        pass

    def loaddata(self, fname):
        f = open(fname)

        line = self.readline(f)
        if line != '--------------------------------':
            return 0

        line = self.readline(f)
        disk_datetime = self.translate_disk_datetime(line)

        line = self.readline(f)
        disk_name = line

        if not Record.create_disk(disk_name, disk_datetime):
            return 0

        count = 0
        pair = 0
        while line:
            line = self.readline(f)
            if pair == 0:
                rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                if rights:
                    pair = 1
                else:
                    self.log('Invalid first line')
            else:
                sha1sum, fullname1 = self.translate_file_line1(line)
                if sha1sum:
                    pair = 0
                    if fullname0 != fullname1:
                        self.log('Filename first and second lines does not match')
                    elif fullname0[:len(disk_name)] != disk_name:
                        self.log('Filename does not match to disk name')
                    else:
                        try:
                            Record.write_record(disk_name, disk_datetime, fullname0, size, file_datetime, rights, owner, group, sha1sum)
                        except Exception as error:
                            self.log(str(error))
                        count += 1
                else:
                    self.log('Invalid second line')
                    rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                    if rights:      # maybe one line skipped, try to fix
                        pair = 1
                    else:
                        pair = 0

        f.close()

        return count


def index(request):
    fname = request.GET.get('file')

    Record.reset_database()

    import_file = ImportFile()
    files = 0
    if fname:
        files = import_file.loaddata(fname)

    return HttpResponse('Hello, world! Loaded %i file records from %s' % (files,fname))


def reset_database(request):
    Record.reset_database()
    return HttpResponse('Reset database finished')
