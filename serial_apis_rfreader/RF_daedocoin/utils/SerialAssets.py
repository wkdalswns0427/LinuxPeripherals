from utils.imports import * 

class SerialAgent:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        self.rfagent = self.serialSetup('/dev/ttyS0')

    def readAvailablePorts(self):
        self.portsList = sp.comports()
        self.connected = []
        for i in self.portsList:
            self.connected.append(i.device)
        return self.connected

    def serialSetup(self, port , baudrate :str ="19200", parity : str = "N", bytesize : int = 8, stopbits : int = 1, timeout : int = 2):
        self.serial_io = serial.Serial()
        self.serial_io.port = port
        self.serial_io.baudrate = baudrate
        self.serial_io.parity = parity
        self.serial_io.bytesize = bytesize
        self.serial_io.stopbits = stopbits
        self.serial_io.timeout = timeout
        return self.serial_io
        
    
    def _open_port(self, agent) -> None:
        if not agent.is_open:
            try:
                agent.open()
            except Exception as e:
                raise Exception("Failed to open serial port!")

    def _close_port(self, agent) -> None:
        if agent.is_open:
            agent.close()
    
    def read(self, agent, size, timeout = 3):
        agent.timeout = timeout
        ret = agent.read(size)
        agent.flush()
        return ret

    def write(self, agent, data, timeout = 3) -> None:
        agent.write_timeout = timeout
        agent.write(data)
        agent.flush()
        return
