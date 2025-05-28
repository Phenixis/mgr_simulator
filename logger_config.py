import logging
import os
from datetime import datetime

def setup_logger():
    """Setup logging configuration for the PLC simulator"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"plc_simulator_{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create specific loggers for different components
    main_logger = logging.getLogger('MAIN')
    plc_read_logger = logging.getLogger('PLC_READ')
    plc_write_logger = logging.getLogger('PLC_WRITE')
    plc_status_logger = logging.getLogger('PLC_STATUS')
    simulator_logger = logging.getLogger('SIMULATOR')
    
    main_logger.info(f"Logging initialized. Log file: {log_filename}")
    
    return {
        'main': main_logger,
        'plc_read': plc_read_logger,
        'plc_write': plc_write_logger,
        'plc_status': plc_status_logger,
        'simulator': simulator_logger
    }

def log_plc_data(logger, data, data_type="UNKNOWN"):
    """Helper function to log PLC data in a readable format"""
    if data:
        if isinstance(data, (bytes, bytearray)):
            # hex_data = ' '.join([f'{b:02X}' for b in data])
            binary_data = ' '.join([f'{b:08b}' for b in data])
            # logger.info(f"{data_type} - HEX: {hex_data}")
            logger.info(f"{data_type} - BIN: {binary_data}")
        else:
            logger.info(f"{data_type}: {data}")

def log_connection_attempt(logger, address, rack, slot, port, attempt, max_attempts):
    """Helper function to log connection attempts"""
    logger.info(f"Connection attempt {attempt}/{max_attempts} to PLC at {address}:{port} (Rack:{rack}, Slot:{slot})")

def log_io_operation(logger, operation_type, area, db_number, start, size, success=True, error=None):
    """Helper function to log I/O operations"""
    if success:
        logger.info(f"{operation_type} operation successful - Area:{area}, DB:{db_number}, Start:{start}, Size:{size}")
    else:
        logger.error(f"{operation_type} operation failed - Area:{area}, DB:{db_number}, Start:{start}, Size:{size}, Error: {error}")
