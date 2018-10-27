from django.http import HttpResponse
import time
import re
from .models import Disk, Folder, File, FileUnique, Log


class FileRecord:
    @classmethod
    def get_disk(cls, name, scan_datetime):
        disks = Disk.objects.filter(name=name, scan_datetime=scan_datetime)
        if len(disks) == 0:
            return None
        if len(disks) > 1:
            Log.error('Multiple disks in database (%s,%s)' % (name, scan_datetime))
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
    def create_disk(cls, file_name, name, scan_datetime):
        if cls.get_disk(name, scan_datetime):
            Log.warning('Disk already imported (%s,%s)' % (name, scan_datetime))
            return False

        create_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        disk = Disk(file_name = file_name,
                         name = name,
                scan_datetime = scan_datetime,
              create_datetime = create_datetime )
        disk.save()

        Log.info('Created disk "%s" from file "%s"' % (name, file_name))
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

        file, created = FileUnique.objects.get_or_create(name = file_name,
                                                         size = size,
                                                     datetime = datetime,
                                                       rights = rights,
                                                        owner = owner,
                                                        group = group,
                                                      sha1sum = sha1sum)

        File.objects.create(disk = disk,
                          folder = folder,
                            file = file)


class ImportFile:
    line_number = 0
    lines_total = 0
    re_line0 = None
    re_line1 = None

    def __init__(self):
        self.re_line0 = re.compile(r'^(\S+)\s+\d+\s+(\S+)\s+(\S+)\s+(\d+)\s+(\S+)\s+([^\.\s]+)\S*\s+\S+\s+(.*)$')
        self.re_line1 = re.compile(r'^(\S+)\s+(.*)$')

    def readline(self, f):
        self.line_number += 1
        if  self.lines_total>0 and self.line_number % 100 == 0:
            print('Read %i lines of %i (%i%%)\n' % (self.line_number, self.lines_total, self.line_number*100/self.lines_total), end='')
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
            line_arr = self.re_line0.split(line)
            rights = line_arr[1]
            owner = line_arr[2]
            group = line_arr[3]
            size = line_arr[4]
            file_datetime = line_arr[5] + ' ' + line_arr[6]
            fullname0 = line_arr[7]
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
            line_arr = self.re_line1.split(line)
            sha1sum = line_arr[1]
            fullname1 = line_arr[2]
        except:
            sha1sum = ''
            fullname1 = ''

        return sha1sum, fullname1

    def is_empty(self, line):
        if len(line) == 0:
            return True
        if line[0] == '\n':
            return True
        if line[0] == '#':
            return True
        return False

    def loaddata(self, file_name):
        f = open(file_name)

        line = self.readline(f)
        while line:
            line = self.readline(f)
        self.lines_total = self.line_number
        self.line_number = 0

        f.seek(0)

        line = self.readline(f)
        if line != '--------------------------------':
            return 0

        line = self.readline(f)
        disk_datetime = self.translate_disk_datetime(line)

        line = self.readline(f)
        disk_name = line

        if not FileRecord.create_disk(file_name, disk_name, disk_datetime):
            return 0

        count = 0
        pair = 0
        while line:
            line = self.readline(f)
            if self.is_empty(line):
                continue
            if pair == 0:
                rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                if rights:
                    pair = 1
                else:
                    Log.error('Invalid first line at line %i' % self.line_number)
            else:
                sha1sum, fullname1 = self.translate_file_line1(line)
                if sha1sum:
                    pair = 0
                    if fullname0 != fullname1:
                        Log.error('Filename first and second lines does not match at line %i' % self.line_number)
                    elif fullname0[:len(disk_name)] != disk_name:
                        Log.error('Filename does not match to disk name at line %i' % self.line_number)
                    else:
                        try:
                            FileRecord.write_record(disk_name, disk_datetime, fullname0, size, file_datetime, rights, owner, group, sha1sum)
                        except Exception as error:
                            Log.error(str(error))
                        count += 1
                else:
                    Log.error('Invalid second line at line %i' % self.line_number)
                    rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                    if rights:      # maybe one line skipped, try to fix
                        pair = 1
                    else:
                        pair = 0

        f.close()
        print('Read %i lines of %i (%i%%)' % (self.line_number, self.lines_total, self.line_number * 100 / self.lines_total))

        Log.info('Loaded disk "%s" from file "%s" with %i file records' % (disk_name, file_name, count))

        return count


def index(request):
    fname = request.GET.get('file')

    # Record.reset_database()

    import_file = ImportFile()
    files = 0
    if fname:
        files = import_file.loaddata(fname)

    return HttpResponse('Hello, world! Loaded %i file records from %s' % (files,fname))
