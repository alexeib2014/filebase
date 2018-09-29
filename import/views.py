from django.http import HttpResponse
from .models import Disk


class CRecord:
    disk_name = ''
    disk_scan_datetime = ''
    disk_id = 0

    def find_disk(self, name, scan_datetime):
        if self.disk_name==name and self.disk_scan_datetime==scan_datetime:
            return self.disk_id

        disk = Disk.objects.filter(name=name, scan_datetime=scan_datetime)
        if len(disk) == 0:
            return 0
        if len(disk) > 1:
            self.log('Multiple disks in database (%s,%s)' % (name, scan_datetime))

        self.disk_name = name
        self.disk_scan_datetime = scan_datetime
        self.disk_id = disk[0].id
        return disk[0].id

    def create_disk(self, name, scan_datetime):
        if self.find_disk(name, scan_datetime):
            self.log('Disk already imported (%s,%s)' % (name, scan_datetime))
            return False

        create_datetime = '2018-01-01 01:02:03'
        disk = Disk( name = name,
            scan_datetime = scan_datetime,
          create_datetime = create_datetime )
        disk.save()
        return True

    def write_record(self, disk_name, disk_datetime, file_name, size, datetime, rights, owner, group, sha1sum):
        pass

    def reset_database(self):
        disks = Disk.objects.all()
        for disk in disks:
            disk.delete()

    def log(self, message):
        pass


Record = CRecord()


class ImportFile:
    line_number = 0

    def readline(self, f):
        self.line_number += 1
        line = f.readline().replace('\n','').replace('\r','')
        return line

    def translate_disk_datetime(self, line):
        line = '2018-01-01 01:02:03'
        return line

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

    def log_error(self, message):
        pass

    def loaddata(self, fname):
        count = 0
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

        pair = 0
        while line:
            line = self.readline(f)
            if pair == 0:
                rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                if rights:
                    pair = 1
                else:
                    self.log_error('Invalid first line')
            else:
                sha1sum, fullname1 = self.translate_file_line1(line)
                if sha1sum:
                    pair = 0
                    if fullname0 != fullname1:
                        self.log_error('Filename first and second lines does not match')
                    elif fullname0[:len(disk_name)] != disk_name:
                        self.log_error('Filename does not match to disk name')
                    else:
                        Record.write_record(disk_name, disk_datetime, fullname0, size, file_datetime, rights, owner, group, sha1sum)
                else:
                    self.log_error('Invalid second line')
                    rights, owner, group, size, file_datetime, fullname0 = self.translate_file_line0(line)
                    if rights:      # maybe one line skipped, try to fix
                        pair = 1
                    else:
                        pair = 0

        f.close()

        return count


def index(request):
    fname = request.GET.get('file')

    import_file = ImportFile()
    files = 0
    if fname:
        files = import_file.loaddata(fname)

    return HttpResponse('Hello, world! Loaded %i files from %s' % (files,fname))


def reset_database(request):
    Record.reset_database()
    return HttpResponse('Reset database finished')
