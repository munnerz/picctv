from multiprocessing import Pool

import global_vars
import library
from utils import Utils

def _recording_write(info):
    library.save_file(info['data']['frameData'], dict(camera_name=info['camera_name'],
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
        PROCESSING_POOL.apply_async(handler, [argu])
    else:
        Utils.dbg("Notifying networking that this connection has failed...", "modules")
        global_vars.NETWORK.connection_failed(info)
        pass #todo: tell networking that some dud data has been received!

def _get_data_handler(module_name):
    ''' returns the appropriate handler for this modules data,
        or a library writer object if none found        '''
    return MODULE_PROCESSORS.get(module_name, library.write)
