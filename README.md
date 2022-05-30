# second-assignment
**CORE:**

The idea is to build an adaptive sensor network which is aware of a new node coming in the network. Each new node is based at least two MCUs, that can be a NodeMCU and/or MKR.
Use the first assignment as starting point. The idea is that one node of the network may act as master node and the others as slave node. The master node is already registered in the sensor network while the slave is to be dinamically added to the sensor network. The sensor network communications should be handled by using MQTT. The master node may act as root user of the sensor network: it may collect the messages coming from all the nodes in the network (in this case one) and it may log these messages on the suitable database (MySQL or InfluxDB).


**ADD-ONS**

Set up a remote control of the monitoring system (start, stop, etc.) through a web page. All the sensed values and alerting events values must be showed. Sensors need to communicate alerts based on web of things technologies such as REST HTTP, JSON.


**INGREDIENTS:**

- Micro of your choice
- Sensor or actuators of your choice.

**EXPECTED DELIVERABLES:**

- Github code upload at: [Classroom link](https://classroom.github.com/a/0FHRKbTa)
- Powerpoint presentation of 10 mins (5 mins per person)
>>>>>>> 5fd367d0ec72781933ac504d685f89bbf16505f9
