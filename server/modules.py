from multiprocessing import Pool

import global_vars
import library
from utils import Utils

def _recording_write(info):
    metadata = ({key: value for key, value in info['data'].items() if key != 'frame_data'})
    library.save_file(info['data']['frame_data'], dict(camera_name=info['camera_name'],
                                                      module_name=info['module_name'],
                                                      **metadata))
    return None

# here we perform an optimisation on the received motion
# data in order to better retrieve motion events in complete
# chunks on the web interface
def _motion_write(info):
    # true_events are the number of triggered motion events
    true_events = sum(map(lambda x: 1 if x['is_motion'] else 0, info['data']))
    # if more than 20% of the events were motion events, this block
    # contains motion
    info['triggered'] = float(true_events) / float(len(info['data'])) > 0.2
    
    # retrieve the start and end time and timestamp of this block
    # and store it in the top level info structure
    # to allow for indexing by mongodb
    info['start_time'] = info['data'][0]['time']
    info['end_time'] = info['data'][-1]['time']
    info['start_timestamp'] = info['data'][0]['timestamp']
    info['end_timestamp'] = info['data'][-1]['timestamp']

    # calculate and store the average motion level
    # in this block
    if len(info['data']) == 0:
        info['average_motion'] = 0
    else:
        info['average_motion'] = sum([x['motion_magnitude'] for x in info['data']]) / len(info['data'])
    
    # store the motion data in the library
    library.write(info)


MODULE_PROCESSORS = { "Recording": _recording_write,
                      "Motion": _motion_write }

PROCESSING_POOL = Pool(processes=4)

def process_data(i):
    info, data = i
    if data is not None:
        # check if a custom data handler
        # is defined for this module type
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
        or the library write function if there is no handler '''
    return MODULE_PROCESSORS.get(module_name, library.write)
