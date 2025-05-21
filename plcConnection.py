import time
import snap7
from threading import Thread
from settings import WHITE, DARK_GRAY


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

    def run(self):
        while self.running:
            self.sim.read_thread_count += 1
            if not self.connected:
                try:
                    print(f"Attempting to connect to PLC at {self.sim.plc_address} (Attempt {self.connection_attempts + 1}/{self.max_connection_attempts})")
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        # Reset connection attempts on successful connection
                        self.connection_attempts = 0
                        self.sim.plc_write_thread = PLCWrite(self.sim)
                        self.sim.plc_status_thread = PLCStatus(self.sim)
                        self.sim.plc_write_thread.start()
                        self.sim.plc_status_thread.start()
                        self.cpu_info = self.plc.get_cpu_info()
                        self.sim.texts[1][1] = self.sim.render_text("PLC connected: " + str(self.connected), 15, WHITE)
                        self.sim.texts[1][2] = self.sim.render_text("PLC name: " + self.cpu_info.ModuleName.decode(), 15, WHITE)
                        self.sim.texts[1][3] = self.sim.render_text("PLC type: " + self.cpu_info.ModuleTypeName.decode(), 15, WHITE)
                        print(f"Successfully connected to PLC: {self.cpu_info.ModuleName.decode()}")
                        self.time_mem = time.time()
                    else:
                        # If connect() didn't raise an exception but we're still not connected
                        self.connection_attempts += 1
                        if self.connection_attempts >= self.max_connection_attempts:
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
                    if self.connection_attempts >= self.max_connection_attempts:
                        print("Max connection attempts reached. Simulator requires a PLC connection to run.")
                        self.running = False
                        break
                    time.sleep(2)
            else:
                if not self.data_to_update:
                    try:
                        # read form PLC
                        self.sim.read_operation_count += 1
                        self.pps += 1
                        self.data = self.plc.mb_read(0, 5)
                        if self.result:
                            self.data = bin(int.from_bytes(self.data, byteorder='little'))
                            self.data = self.data[::-1]
                            while self.data.__len__() < 37:
                                self.data += "0"
                            self.data_to_update = True
                    except Exception as e:
                        try:
                            e_str = e.args[0].decode()
                        except:
                            e_str = str(e)
                        
                        if e_str[0:4] == " ISO" or "connection" in e_str.lower():
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
                    for i in range(37):
                        if self.data[i] == '1':
                            self.sim.inputs[i] = True
                        else:
                            self.sim.inputs[i] = False
                    self.data_to_update = False
                    self.sim.io_lock = False
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

    def run(self):
        while self.running:
            self.sim.write_thread_count += 1
            if not self.connected:
                try:
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        self.connection_attempts = 0
                        self.time_mem = time.time()
                    else:
                        self.connection_attempts += 1
                        if self.connection_attempts >= self.max_connection_attempts:
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
                    if self.connection_attempts >= self.max_connection_attempts:
                        print(f"{self.name}: Max connection attempts reached. Exiting.")
                        self.running = False
                        break
                    time.sleep(2)
            else:
                if not self.sim.io_lock:
                    self.sim.io_lock = True
                    self.data = self.sim.outputs
                    self.sim.io_lock = False
                    outputs_bin = ''
                    for i in range(24):
                        if self.data[i]:
                            outputs_bin += '1'
                        else:
                            outputs_bin += '0'
                    outputs_bytes = int(outputs_bin[::-1], 2).to_bytes((len(outputs_bin) + 7) // 8, byteorder='little')
                    try:
                        # write to PLC
                        self.sim.write_operation_count += 1
                        self.pps += 1
                        self.result = self.plc.mb_write(5, 3, outputs_bytes)
                    except Exception as e:
                        try:
                            e_str = e.args[0].decode()
                        except:
                            e_str = str(e)
                        
                        if e_str[0:4] == " ISO" or "connection" in e_str.lower():
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

    def run(self):
        while self.running:
            self.sim.status_thread_count += 1
            if not self.connected:
                try:
                    self.plc.connect(self.sim.plc_address, self.sim.plc_rack, self.sim.plc_slot, self.sim.plc_port)
                    self.connected = self.plc.get_connected()
                    if self.connected:
                        self.connection_attempts = 0
                    else:
                        self.connection_attempts += 1
                        if self.connection_attempts >= self.max_connection_attempts:
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
                    if self.connection_attempts >= self.max_connection_attempts:
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
                except Exception as e:
                    try:
                        e_str = e.args[0].decode()
                    except:
                        e_str = str(e)
                        
                    if e_str[0:4] == " ISO" or "connection" in e_str.lower():
                        self.plc.disconnect()
                        self.connected = False
                        print(self.name + ":")
                        print(e_str)
                        print(" Lost connection to PLC. Simulator will stop as PLC connection is required.")
                time.sleep(1)
        if self.connected:
            self.plc.disconnect()
