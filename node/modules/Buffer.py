import settings

event_buffers = {}
arguments = None

LOGGER = settings.logger("node.modules.Buffer")

def process_data(data):
	(module, data) = data
	(module_name, input_name) = module

	try:
		module_buffers = event_buffers[module_name]
	except KeyError:
		module_buffers = event_buffers[module_name] = {}

	try:
		input_buffer = module_buffers[input_name]
	except KeyError:
		input_buffer = module_buffers[input_name] = []

	input_buffer.append(data)

	if len(input_buffer) >= arguments['buffer_size']:
		buffer_to_send = input_buffer
		module_buffers[input_name] = []
		LOGGER.debug("Sending buffer of size %d for module %s" % (len(buffer_to_send), ("%s:%s" % module)))
		return {("%s:%s" % module): buffer_to_send}


def shutdown_module():
	LOGGER.info("TODO: Flush all data on shutdown")

def name():
	return "Buffer"