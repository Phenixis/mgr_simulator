import time
import snap7
from threading import Thread
from settings import WHITE, DARK_GRAY
from logger_config import log_plc_data, log_connection_attempt, log_io_operation
import logging


class PLCRead(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCReadThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.cpu_info = ''
        self.data = ''
        self.data_to_update = False
        self.sim = sim
        self.result = 1
        self.time_mem = 0
        self.time_set = 1
        self.pps = 0
        self.connection_attempts = 0
        self.max_connection_attempts = 5  # Maximum number of attempts before giving up
        
        # Initialize logger
        self.logger = logging.getLogger('PLC_READ')
        self.logger.info("PLCRead thread initialized")

    def run(self):
        while self.running:
            self.sim.read_thread_count += 1
            if not self.connected:
                try:
                    self.logger.info(f"Attempting to connect to PLC at {self.sim.plc_address} (Attempt {self.connection_attempts + 1}/{self.max_connection_attempts})")
                    log_connection_attempt(self.logger, self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port, self.connection_attempts + 1, self.max_connection_attempts)
                    print(f"Attempting to connect to PLC at {self.sim.plc_address} (Attempt {self.connection_attempts + 1}/{self.max_connection_attempts})")
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        # Reset connection attempts on successful connection
                        self.connection_attempts = 0
                        self.logger.info("Successfully connected to PLC")
                        
                        # Start other PLC threads
                        self.sim.plc_write_thread = PLCWrite(self.sim)
                        self.sim.plc_status_thread = PLCStatus(self.sim)
                        self.sim.plc_write_thread.start()
                        self.sim.plc_status_thread.start()
                        self.logger.info("PLC Write and Status threads started")
                        
                        self.cpu_info = self.plc.get_cpu_info()
                        self.logger.info(f"PLC CPU Info - Name: {self.cpu_info.ModuleName.decode()}, Type: {self.cpu_info.ModuleTypeName.decode()}")
                        
                        self.sim.texts[1][1] = self.sim.render_text("PLC connected: " + str(self.connected), 15, WHITE)
                        self.sim.texts[1][2] = self.sim.render_text("PLC name: " + self.cpu_info.ModuleName.decode(), 15, WHITE)
                        self.sim.texts[1][3] = self.sim.render_text("PLC type: " + self.cpu_info.ModuleTypeName.decode(), 15, WHITE)
                        print(f"Successfully connected to PLC: {self.cpu_info.ModuleName.decode()}")
                        self.time_mem = time.time()
                    else:
                        # If connect() didn't raise an exception but we're still not connected
                        self.connection_attempts += 1
                        self.logger.warning(f"Connection attempt {self.connection_attempts} failed - not connected after connect() call")
                        if self.connection_attempts >= self.max_connection_attempts:
                            self.logger.error("Max connection attempts reached. Simulator requires a PLC connection to run.")
                            print("Max connection attempts reached. Simulator requires a PLC connection to run.")
                            self.running = False
                            break
                except Exception as e:
                    print(self.name + ":")
                    try:
                        print(e.args[0].decode())
                    except:
                        print(str(e))
                    print(" Connection failed. Trying to connect again in 2 sec.")
                    self.connection_attempts += 1
                    self.logger.error(f"Connection attempt {self.connection_attempts} failed: {str(e)}")
                    if self.connection_attempts >= self.max_connection_attempts:
                        self.logger.error("Max connection attempts reached. Simulator requires a PLC connection to run.")
                        print("Max connection attempts reached. Simulator requires a PLC connection to run.")
                        self.running = False
                        break
                    time.sleep(2)
            else:
                if not self.data_to_update:
                    try:
                        # read from PLC - Read 5 bytes from Merker area starting at MW0
                        self.sim.read_operation_count += 1
                        self.pps += 1
                        self.data = self.plc.read_area(snap7.types.Areas.MK, 0, 0, 5)
                        if self.data:
                            self.data_to_update = True
                            self.logger.debug(f"Read operation successful - {len(self.data)} bytes")
                            log_plc_data(self.logger, self.data, "READ_DATA")
                            log_io_operation(self.logger, "READ", "MK", 0, 0, 5, success=True)
                    except Exception as e:
                        try:
                            e_str = e.args[0].decode()
                        except:
                            e_str = str(e)
                        
                        self.logger.error(f"Read operation failed: {e_str}")
                        log_io_operation(self.logger, "READ", "MK", 0, 0, 5, success=False, error=e_str)
                        
                        if e_str[0:4] == " ISO" or "connection" in e_str.lower():
                            self.logger.warning("Connection lost detected during read operation")
                            self.plc.disconnect()
                            self.connected = False
                            self.pps = 0
                            self.sim.texts[1][1] = self.sim.render_text("PLC connected: " + str(self.connected), 15, WHITE)
                            if self.sim.plc_write_thread and self.sim.plc_write_thread.running:
                                self.sim.plc_write_thread.running = False
                                self.sim.plc_write_thread.join()
                            if self.sim.plc_status_thread and self.sim.plc_status_thread.running:
                                self.sim.plc_status_thread.running = False
                                self.sim.plc_status_thread.join()
                            print(self.name + ":")
                            print(e_str)
                            print(" Lost connection to PLC. Simulator will stop as PLC connection is required.")
                if not self.sim.io_lock and self.data_to_update:
                    self.sim.io_lock = True
                    # Extract individual bits from the read data
                    self.logger.debug("Processing read data - extracting bits")
                    for byte_idx in range(5):  # 5 bytes = 40 bits, but you use 37
                        for bit_idx in range(8):
                            if byte_idx * 8 + bit_idx < 37:  # Limit to 37 inputs
                                bit_value = snap7.util.get_bool(self.data, byte_idx, bit_idx)
                                self.sim.inputs[byte_idx * 8 + bit_idx] = bit_value
                    self.data_to_update = False
                    self.sim.io_lock = False
                    self.logger.debug("Data processing completed - inputs updated")
                now = time.time()
                if now - self.time_mem >= self.time_set:
                    self.sim.read_pps = self.pps
                    text = "Dow/Up rate: " + str(self.pps) + "/" + str(self.sim.write_pps) + " p/s"
                    self.sim.texts[1][5] = self.sim.render_text(text, 15, WHITE)
                    self.pps = 0
                    self.time_mem = now
        if self.connected:
            self.plc.disconnect()
            if self.sim.plc_write_thread.running:
                self.sim.plc_write_thread.running = False
                self.sim.plc_write_thread.join()
            if self.sim.plc_status_thread.running:
                self.sim.plc_status_thread.running = False
                self.sim.plc_status_thread.join()


class PLCWrite(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCWriteThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.data = ''
        self.sim = sim
        self.result = 1
        self.time_mem = 0
        self.time_set = 1
        self.pps = 0
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # Initialize logger
        self.logger = logging.getLogger('PLC_WRITE')
        self.logger.info("PLCWrite thread initialized")

    def run(self):
        while self.running:
            self.sim.write_thread_count += 1
            if not self.connected:
                try:
                    self.logger.info(f"Write thread attempting to connect to PLC at {self.sim.plc_address}")
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        self.connection_attempts = 0
                        self.logger.info("Write thread successfully connected to PLC")
                        self.time_mem = time.time()
                    else:
                        self.connection_attempts += 1
                        self.logger.warning(f"Write thread connection attempt {self.connection_attempts} failed")
                        if self.connection_attempts >= self.max_connection_attempts:
                            self.logger.error(f"{self.name}: Max connection attempts reached. Exiting.")
                            print(f"{self.name}: Max connection attempts reached. Exiting.")
                            self.running = False
                            break
                except Exception as e:
                    print(self.name + ":")
                    try:
                        print(e.args[0].decode())
                    except:
                        print(str(e))
                    print(" Connection failed. Trying to connect again in 2 sec.")
                    self.connection_attempts += 1
                    self.logger.error(f"Write thread connection attempt {self.connection_attempts} failed: {str(e)}")
                    if self.connection_attempts >= self.max_connection_attempts:
                        self.logger.error(f"{self.name}: Max connection attempts reached. Exiting.")
                        print(f"{self.name}: Max connection attempts reached. Exiting.")
                        self.running = False
                        break
                    time.sleep(2)
            else:
                if not self.sim.io_lock:
                    self.sim.io_lock = True
                    self.data = self.sim.outputs.copy()
                    self.sim.io_lock = False
                    
                    # Prepare 3 bytes for 24 outputs
                    output_data = bytearray(3)
                    for i in range(24):
                        byte_idx = i // 8
                        bit_idx = i % 8
                        if self.data[i]:
                            snap7.util.set_bool(output_data, byte_idx, bit_idx, True)
                    
                    try:
                        # write to PLC - Write to Merker area starting at MW5
                        self.sim.write_operation_count += 1
                        self.pps += 1
                        self.result = self.plc.write_area(snap7.types.Areas.MK, 0, 5, output_data)
                        self.logger.debug(f"Write operation successful - {len(output_data)} bytes")
                        log_plc_data(self.logger, output_data, "WRITE_DATA")
                        log_io_operation(self.logger, "WRITE", "MK", 0, 5, len(output_data), success=True)
                    except Exception as e:
                        try:
                            e_str = e.args[0].decode()
                        except:
                            e_str = str(e)
                        
                        self.logger.error(f"Write operation failed: {e_str}")
                        log_io_operation(self.logger, "WRITE", "MK", 0, 5, len(output_data), success=False, error=e_str)
                        
                        if e_str[0:4] == " ISO" or "connection" in e_str.lower():
                            self.logger.warning("Connection lost detected during write operation")
                            self.plc.disconnect()
                            self.connected = False
                            self.pps = 0
                            print(self.name + ":")
                            print(e_str)
                            print(" Lost connection to PLC. Simulator will stop as PLC connection is required.")
                now = time.time()
                if now - self.time_mem >= self.time_set:
                    self.sim.write_pps = self.pps
                    self.pps = 0
                    self.time_mem = now
        if self.connected:
            self.plc.disconnect()


class PLCStatus(Thread):
    def __init__(self, sim):
        Thread.__init__(self)
        self.name = 'PLCStatusThread'
        self.running = True
        self.plc = snap7.client.Client()
        self.connected = False
        self.cpu_state = ''
        self.sim = sim
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # Initialize logger
        self.logger = logging.getLogger('PLC_STATUS')
        self.logger.info("PLCStatus thread initialized")

    def run(self):
        while self.running:
            self.sim.status_thread_count += 1
            if not self.connected:
                try:
                    self.logger.info(f"Status thread attempting to connect to PLC at {self.sim.plc_address}")
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        self.connection_attempts = 0
                        self.logger.info("Status thread successfully connected to PLC")
                    else:
                        self.connection_attempts += 1
                        self.logger.warning(f"Status thread connection attempt {self.connection_attempts} failed")
                        if self.connection_attempts >= self.max_connection_attempts:
                            self.logger.error(f"{self.name}: Max connection attempts reached. Exiting.")
                            print(f"{self.name}: Max connection attempts reached. Exiting.")
                            self.running = False
                            break
                except Exception as e:
                    print(self.name + ":")
                    try:
                        print(e.args[0].decode())
                    except:
                        print(str(e))
                    print(" Connection failed. Trying to connect again in 2 sec.")
                    self.connection_attempts += 1
                    self.logger.error(f"Status thread connection attempt {self.connection_attempts} failed: {str(e)}")
                    if self.connection_attempts >= self.max_connection_attempts:
                        self.logger.error(f"{self.name}: Max connection attempts reached. Exiting.")
                        print(f"{self.name}: Max connection attempts reached. Exiting.")
                        self.running = False
                        break
                    time.sleep(2)
            else:
                try:
                    # read status form PLC
                    self.sim.status_operation_count += 1
                    self.cpu_state = self.plc.get_cpu_state()
                    self.sim.texts[1][4] = self.sim.render_text("CPU state: " + str(self.cpu_state), 15, WHITE)
                    self.logger.debug(f"CPU state read successfully: {self.cpu_state}")
                except Exception as e:
                    try:
                        e_str = e.args[0].decode()
                    except:
                        e_str = str(e)
                    
                    self.logger.error(f"Status operation failed: {e_str}")
                    
                    if e_str[0:4] == " ISO" or "connection" in e_str.lower():
                        self.logger.warning("Connection lost detected during status operation")
                        self.plc.disconnect()
                        self.connected = False
                        print(self.name + ":")
                        print(e_str)
                        print(" Lost connection to PLC. Simulator will stop as PLC connection is required.")
                time.sleep(1)
        if self.connected:
            self.plc.disconnect()
