from multiprocessing import Pool

import library

class RecordProcessor(object):

    def __init__(self, output):
        self._output = output

    def write(self, i):
        #do h264 wrapping
        #add metadata
        (info, d) = i
        (data, metadata) = d
        self._output.save_file(data, metadata)


RECORD_PROCESSOR = RecordProcessor(output=library.Writer()) # change output to reroute video processing

MODULE_PROCESSORS = {   "Record": RECORD_PROCESSOR,
                    }

PROCESSING_POOL = Pool(processes=4)

def process_data(i):
    (info, data) = i
    if data is not None:
        handler = _get_data_handler(info['module_name'])
        PROCESSING_POOL.apply_async(handler.write, (handler, dict(camera_name=info['camera_name'],
                                                                            module_name=info['module_name'],
                                                                            **data)) ).get()
    else:
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
