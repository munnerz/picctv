_files = {}
arguments = None

def start_module():
    return None

def process_data(data):
    global _files, arguments
    (module, data) = data

    f = _files.get(module[0], None)
    if f is None:
        f = _files[module[0]] = open('%s/%s.csv' % (arguments['save_path'], module[0]), 'w')
        f.write("Timestamp,Triggered,Magnitude,Frame Num")

    f.write("%s,%s,%s,%s" % (data['timestamp'], data['is_motion'], data['motion_magnitude'], data['frame_number']))

    return None

def shutdown_module():
    global _files
    map(lambda x: x.close(), _files)
    return None