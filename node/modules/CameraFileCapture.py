_files = {}
arguments = None

def start_module():
    return None

def process_data(data):
    global _files, arguments
    (module, data) = data
    (frame, frame_info) = data

    f = _files.get("%s:%s" % (module[0], module[1]), None)
    if f is None:
        f = _files["%s:%s" % (module[0], module[1])] = open('%s/%s:%s.clip' % (arguments['save_path'], module[0], module[1]), 'w+b')
    f.write(frame)

    return None

def shutdown_module():
    global _files
    map(lambda x: x.close(), _files)
    return None

def name():
    return "CameraFileCapture"
