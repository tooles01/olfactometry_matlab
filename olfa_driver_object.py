import serial, time
from serial import SerialException
from serial.tools import list_ports

class TeensyOlfa():

    def __init__(self, mfc_config):
        super().__init__()
        self.dummyvial = 4
        
        self.mfc_config = mfc_config
        self.mfc1_capacity = int(mfc_config['capacity'])

        # Get all config variables
        self.slaveindex = int(mfc_config['slave_index'])
        self.mfc_type = mfc_config['MFC_type']
        self.capacity = int(mfc_config['capacity'])
        self.gas = mfc_config['gas']
        if self.mfc_type.startswith('alicat_digital'):
            self.address = mfc_config['address']
        if 'arduino_port_num' in list(mfc_config.keys()):  # this is only needed for Teensy olfactometers. This is the device ID
            self.arduino_port = int(mfc_config['arduino_port_num'])
    
    
    # CONNECT TO TEENSY
    def connect_olfa(self, com_settings):
        ''' Get all config variables and create serial object '''
        
        # Convert port & baudrate to int
        com_settings['com_port'] = int(com_settings['com_port'])
        com_settings['baudrate'] = int(com_settings['baudrate'])
        
        # Create serial object
        self.serial = self.connect_serial(port=com_settings['com_port'], baudrate=com_settings['baudrate'], timeout=1, writeTimeout=1)
        
    def connect_serial(self, port, baudrate, timeout=1, writeTimeout=-1):
        """
        Return Serial object after making sure that the port is accessible and that the port is expressed as a string.

        :param port: str or int (ie "COM4" or 4 for Windows).
        :param baudrate: baudrate.
        :param timeout: read timeout in seconds, default 1 sec.
        :param writeTimeout: write timeout in seconds, default 1 sec.
        :return: serial port object.
        :rtype: serial.Serial
        """
        
        if isinstance(port, int):
            port = "COM{0}".format(port)
        
        # Get list of available ports
        names_list = list()
        for i in list_ports.comports():
            names_list.append(i[0])
        
        # Check that port entered is in list of available ports
        if port not in names_list:
            print(("ERROR: Serial not found on {0} (--> Please enter correct COM port number in COM settings)".format(port)))
            print('\tListing current serial ports with devices:')
            for ser in list_ports.comports():
                ser_str = '\t\t{0}: {1}'.format(ser[0], ser[1])
                print(ser_str)
            time.sleep(.01)     # just to let the above lines print before the exemption is raised. cleans console output.
        else:
            print('Successfully connected to {0}'.format(port))
            return serial.Serial(port, baudrate=baudrate, timeout=timeout, writeTimeout=writeTimeout)
    
    
    # SET MFC
    def set_flowrate(self, flowrate):
        """

        :param flowrate: flowrate in units of self.capacity (usually ml/min)
        :param args:
        :param kwargs:
        :return:
        """        
        
        success = False
        start_time = time.time()
        
        if flowrate > self.mfc1_capacity or flowrate < 0:
            return success
        
        flownum = (flowrate * 1. / self.mfc1_capacity)*64000
        flownum = int(flownum)
        
        command = "DMFC {0:d} {1:d} A{2:d}".format(self.slaveindex, self.arduino_port, flownum)
        confirmation = self.send_command(command)

        if(confirmation != 'MFC set\r\n'):
            print("Error setting MFC: ", confirmation)
        else:
            # Attempt to read back
            success = True
            command = "DMFC {0:d} {1:d}".format(self.slaveindex, self.arduino_port)
            returnstring = self.send_command(command)
            while (returnstring is None or returnstring.startswith(b'Error -2')) and time.time() - start_time < .2:
                returnstring = self.send_command(command)
        
        return success

    def send_command(self, command, tries=1):
        ''' Copied from TeensyOlfa class'''
        
        self.serial.flushInput()
        for i in range(tries):
            #print("sending command:", command)
            self.serial.write(bytes("{0}\r".format(command), 'utf8'))
            line = self.read_line()
            line = self.read_line()
            morebytes = self.serial.inWaiting()
            if morebytes:
                extrabytes = self.serial.read(morebytes)
            if line:
                return line
    
    def read_line(self):
        ''' Copied from TeensyOlfa class'''

        line = None
        try:
            line = self.serial.readline()
            line = line.decode("utf-8")
            line = line.rstrip('\r\n')
            print("Received line:", repr(line))
        except SerialException as e:
            print('pySerial exception: Exception that is raised on write timeouts')
        return line

    
    # SET VIAL
    def set_valveset(self, vial_num, valvestate=1, suppress_errors=False):
        ''' Copied from TeensyOlfa class'''
        
        vial_num = int(vial_num)
        
        if vial_num == self.dummyvial:
            self.set_dummy_vial(valvestate)

        try:
            if valvestate:
                command = "vialOn {0} {1}".format(self.slaveindex, vial_num)
                print('opening vial', vial_num)
            else:
                command = "vialOff {0} {1}".format(self.slaveindex, vial_num)
                print('closing vial', vial_num)
            line = self.send_command(command)

            if not line.split()[0] == 'Error':
                #print('return true')
                return True
            elif not suppress_errors:
                print('ERROR: Cannot set valveset for vial ', vial_num)
                print(repr(line))
                return False
            
        except AttributeError as err:
            print('WARNING: cannot set valve, not connected to olfactometer (AttributeError: {0})', err)
        
    def set_dummy_vial(self, valvestate=1):
        ''' Copied from TeensyOlfa class'''
        """
        Sets the dummy vial.

        Valvestate means the state of the valve. This is inversed from a normal valve!!

        * A valvestate of 0 means to *close* the dummy by powering the solenoid.
        * A valvestate of 1 means to *open* the dummy by closing other open valves (if any) and depower the dummy valves.

        Usually, you want to pass valvestate with a 1 to close open valves and set the dummy open.

        :param valvestate: Desired state of the dummy (0 closed, 1 open). Default is 1.
        :return: True if successful setting.
        :rtype : bool
        """
        print('set_dummy_vial')

        success = False
        if self.checked_id == self.dummyvial and not valvestate:  # dummy is "off" (this means open as it is normally open),
            command = "vial {0} {1} on".format(self.slaveindex, self.dummyvial)
            print(command)
            line = self.send_command(command)
            print(line)
            if not line.split()[0] == "Error":
                print('Dummy ON.')
                self.vialChanged.emit(self.dummyvial)
                self.checked_id = 0
            else:
                print('ERROR: Cannot set dummy vial.')
                print(line)
        elif self.checked_id == self.dummyvial and valvestate:  # valve is already open, do nothing and return success!
            success = True
        elif self.checked_id == 0 and valvestate:  # dummy is already (closed)
            command = "vial {0} {1} off".format(self.slaveindex, self.dummyvial)
            print(command)
            line = self.send_command(command)
            print(line)
            if not line.split()[0] == "Error":
                print('Dummy OFF.')
                self.vialChanged.emit(self.dummyvial)
                self.checked_id = self.dummyvial
                success = True
                self.vialChanged.emit(self.dummyvial)
        elif self.checked_id != self.dummyvial and valvestate:  # another valve is open. close it.
            success = self._set_valveset(self.checked_id, 0)  # close open vial.
            if success:
                self.vialChanged.emit(self.dummyvial)
                #QtCore.QTimer.singleShot(1000, self._valve_lockout_clear)
                self.checked_id = self.dummyvial
        else:
            print("THIS SHOULDN'T HAPPEN!!!")
        return success
    