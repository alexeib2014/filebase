from django.http import HttpResponse


def readline(f):
    line = f.readline().replace('\n','').replace('\r','')
    return line


def translate_disk_datetime(line):
    return line


def translate_file_line0(line):
    rights = ''
    owner = ''
    group = ''
    size = ''
    file_datetime = ''
    fullname0 = ''


def translate_file_line1(line):
    sha1sum = ''
    fullname1 = ''


def insert_record():
    pass


def log_error(message):
    pass


def loaddata(fname):
    count = 0
    f = open(fname)

    line = readline(f)
    if line != '--------------------------------':
        return 0

    line = readline(f)
    disk_datetime = translate_disk_datetime(line)

    line = readline(f)
    disk_name = line

    pair = 0
    while line:
        line = readline(f)
        if pair == 0:
            rights, owner, group, size, file_datetime, fullname0 = translate_file_line0(line)
            if rights:
                pair = 1
            else:
                log_error('Invalid first line')
        else:
            sha1sum, fullname1 = translate_file_line1(line)
            if sha1sum:
                pair = 0
                if fullname0 == fullname1:
                    insert_record()
                else:
                    log_error('Filename first and second lines does not match')
            else:
                log_error('Invalid second line')
                rights, owner, group, size, file_datetime, fullname0 = translate_file_line0(line)
                if rights:      # maybe one line skipped, try to fix
                    pair = 1
                else:
                    pair = 0

    f.close()

    return count


def index(request):
    fname = request.GET.get('file')
    files = 0
    if fname:
        files = loaddata(fname)

    return HttpResponse('Hello, world! Loaded %i files from %s' % (files,fname))

