from multiprocessing import Pool

import library

def _recording_write(info):
    library.save_file(info['data'], dict(camera_name=info['camera_name'],
                                         module_name=info['module_name']))
    return None


MODULE_PROCESSORS = { "Recording": _recording_write }

PROCESSING_POOL = Pool(processes=4)

def process_data(i):
    info, data = i
    if data is not None:
        handler = _get_data_handler(info['module_name'])
        argu = {"camera_name": info['camera_name'],
                "module_name": info['module_name'],
                "data": data}
        PROCESSING_POOL.apply_async(handler, [argu]).get()
    else:
        print ("Data was none...")
        pass #todo: tell networking that some dud data has been received!

def _get_data_handler(module_name):
    ''' returns the appropriate handler for this modules data,
        or a library writer object if none found        '''
    processor = MODULE_PROCESSORS[module_name]
    if processor is not None:
        return processor
    else:
        MODULE_PROCESSORS[module_name] = library.Writer()
        return MODULE_PROCESSORS[module_name]
