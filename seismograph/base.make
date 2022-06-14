.compile:
	arduino-cli compile --library include --fqbn ${FQBN} . 
.upload: .compile
	arduino-cli upload --fqbn ${FQBN} --port ${PORT} .
.monitor:
	arduino-cli monitor --port ${PORT} --config ${MONITOR_CONFIG_STRING}
default: .compile .upload
