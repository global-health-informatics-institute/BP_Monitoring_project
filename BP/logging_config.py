import logging

def setup_logging():
	logging.basicConfig(
		level = logging.DEBUG,
		filename = '/home/pi/BP_Monitoring_project/BP/BP_log.log',
		format = '%(acstime)s [%(levelname)s] %(message)s',
		datefmt = '%Y-%m-%d %H:%M:%S'
		)
