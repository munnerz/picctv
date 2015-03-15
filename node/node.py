import logging
import math
import time
import multiprocessing

import settings

LOGGER = logging.getLogger(name="node")
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOGGER.addHandler(ch)

def shutdown_module(module):
    try:
        module.shutdown()
    except NotImplementedError as e:
        print("Error shutting down module: %s" % e)
        pass

def run_module(module):
    try:
        module.module_started()
    except AttributeError:
        LOGGER.debug("%s module does not implement a module_started() method." % module.name())
        pass
    while True:
        next_data = module._input_queue.get()
        if next_data is None:
            # this module is shutting down..
            module.shutdown()
            break
        output = module.process_data(next_data)
        if output is not None:
            map(lambda x: x.put((module.name(), output)), x._output_queues['all'])

if __name__ == "__main__":

    from importlib import import_module
    _MODULES = map(lambda x: import_module("modules.%s" % x), settings.ENABLED_MODULES)
    for module in _MODULES:
        module.arguments = settings.ENABLED_MODULES[module.name()].get('arguments', None))
        module._output_queues = {}
        settings.ENABLED_MODULES[module.name()]['runtime']['module'] = module

    for module in _MODULES:
        LOGGER.info("Initialising %s" % module.name())
        
        module._input_queue = multiprocessing.Queue()

        for output_module, output in settings.ENABLED_MODULES[module.name()]['outputs']:
            settings.ENABLED_MODULES[output_module]['runtime']['module']._output_queues.get(output, []).append(module._input_queue)

        LOGGER.info("Set up inputs for module %s" % module.name())

    LOGGER.info("Launching all modules...")
    _MODULE_PROCESSES = map(lambda x: multiprocessing.Process(target=run_module,
                                                              args=(x,)), _MODULES)
    map(lambda x: x.start(), _MODULE_PROCESSES)
    LOGGER.info("All modules launched!")


    try:
        while True: #main process loop
            time.sleep(1)
    except KeyboardInterrupt:
            #shut down all modules here
            map(lambda m: shutdown_module(m), _MODULES)

            LOGGER.info("Shut down.")
