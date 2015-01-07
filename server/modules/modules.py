from multiprocessing import Pool

from .. import library

class RecordProcessor(object):

    def __init__(self, output):
        self._output = output

    def write(self, (data, metadata)):
        #do h264 wrapping
        #add metadata
        self._output.save_file(data, metadata)


RECORD_PROCESSOR = RecordProcessor(output=library.Writer()) # change output to reroute video processing

MODULE_PROCESSORS = {   "Record": RECORD_PROCESSOR,
                    }

PROCESSING_POOL = Pool(processes=4)

def process_data(data, module_name):
    handler = _get_data_handler(module_name)
    PROCESSING_POOL.apply_async(lambda x, y: x.write(y), (handler, data))

def _get_data_handler(module_name):
    ''' returns the appropriate handler for this modules data,
        or a library writer object if none found        '''
    processor = MODULE_PROCESSORS[module_name]
    if processor is not None:
        return processor
    else:
        MODULE_PROCESSORS[module_name] = library.Writer()
        return MODULE_PROCESSORS[module_name]
