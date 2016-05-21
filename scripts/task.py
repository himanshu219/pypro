TASK_DIR = '~/.tasks/'

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", dest="add", help="adding task", action="store_true", default=False)
    parser.add_option("-e", dest="edit", help="editing task", action="store", default=0)
    parser.add_option("-l", dest="list", help="list all tasks", action="store_true", default=False)
    parser.add_option("-d", dest="delete", help="deletes task", action="store_true", default=False)
    parser.add_option("-f", dest="finish", help="done task", action="store_true", default=False)
    parser.add_option("-m", dest="message", type='str', help="adds description", action="store", default='')
    parser.add_option("-n", dest="name", type='str', help="adds name", action="store", default='')
    parser.add_option("-p", dest="priority", type='int', help="adds priority", action="store", default=0)
    parser.add_option("-m", dest="message", type='str', help="adds description", action="store", default='')

    (options, args) = parser.parse_args(sys.argv[1:])
