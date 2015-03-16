import logging
import time
import multiprocessing

import settings

LOGGER = settings.logger("node")

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
            for output_name, output_data in output.items():
                map(lambda x: x.put(((module.name(), output_name), output_data)), module._output_queues.get(output_name, []))

if __name__ == "__main__":

    from importlib import import_module
    _MODULES = map(lambda x: import_module("modules.%s" % x), settings.ENABLED_MODULES)
    for module in _MODULES:
        module.arguments = settings.ENABLED_MODULES[module.name()].get('arguments', None)
        settings.ENABLED_MODULES[module.name()]['runtime'] = {}
        module._output_queues = {}
        module._input_queue = multiprocessing.Queue()
        settings.ENABLED_MODULES[module.name()]['runtime']['module'] = module

    for module in _MODULES:
        LOGGER.info("Initialising %s" % module.name())
        
        module._input_queue = multiprocessing.Queue()

        for input_module, input_xtra in settings.ENABLED_MODULES[module.name()]['inputs'].items():
            queue_temp = settings.ENABLED_MODULES[input_module]['runtime']['module']._output_queues.get(input_xtra, None)
            if queue_temp is None:
                queue_temp = settings.ENABLED_MODULES[input_module]['runtime']['module']._output_queues[input_xtra] = []
            queue_temp.append(module._input_queue)


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
            def shutdown_module(module):
                try:
                    module.shutdown_module()
                except Exception:
                    print("Error shutting down module: %s" % e)
                    pass

            map(shutdown_module, _MODULES)

            LOGGER.info("Shut down.")
