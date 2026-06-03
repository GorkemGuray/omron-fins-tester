import logging
from typing import Tuple, Optional, Any
from fins.udp import UDPFinsConnection

logger = logging.getLogger(__name__)

class OmronFinsClient:
    def __init__(self):
        self.client: Optional[Any] = None
        self.ip_address = ""
        self.port = 9600
        self.connected = False

    def connect(self, ip_address: str, port: int = 9600, dest_node: int = 0, src_node: int = 0, dest_net: int = 0, src_net: int = 0, protocol: str = "UDP") -> Tuple[bool, str]:
        try:
            if protocol == "TCP":
                from fins.tcp import TCPFinsConnection
                self.client = TCPFinsConnection()
                self.client.connect(ip_address, port=port, connection_timeout=2.0)
            else:
                self.client = UDPFinsConnection()
                self.client.connect(ip_address, port=port)

            # Set short timeout to prevent UI freezes
            if hasattr(self.client, 'fins_socket'):
                self.client.fins_socket.settimeout(2.0)

            if dest_node != 0:
                self.client.dest_node_add = dest_node
            if src_node != 0:
                self.client.srce_node_add = src_node
            if dest_net != 0:
                self.client.dest_net_add = dest_net
            if src_net != 0:
                self.client.srce_net_add = src_net
            
            # For UDP, the socket connects immediately even if PLC is offline.
            # We must send a ping command to verify the PLC is reachable and nodes are correct.
            if protocol == "UDP":
                self.client.cpu_unit_status_read()
            
            self.ip_address = ip_address
            self.port = port
            self.connected = True
            logger.info(f"Connected to {ip_address}:{port} over {protocol} (DestNode={self.client.dest_node_add}, SrcNode={self.client.srce_node_add})")
            return True, "Connected successfully"
        except Exception as e:
            self.connected = False
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def disconnect(self):
        if self.client:
            if hasattr(self.client, 'fins_socket') and self.client.fins_socket:
                try:
                    self.client.fins_socket.close()
                except Exception:
                    pass
            del self.client
            self.client = None
        self.connected = False
        logger.info("Disconnected")

    def read_variable(self, memory_area: str, address_str: str, data_type: str = 'w', number_of_values: int = 1) -> Tuple[bool, Any, str]:
        if not self.connected or not self.client:
            return False, None, "Not connected"
        try:
            if "." in address_str:
                parts = address_str.split(".")
                word_address = int(parts[0])
                bit_address = int(parts[1])
            else:
                word_address = int(address_str)
                bit_address = 0

            # Handle Bool explicitly because FINS library wrapper is incomplete for 'b'
            if data_type.lower() == 'b':
                import fins.fins_common
                memory_areas = fins.fins_common.FinsPLCMemoryAreas()
                ma = memory_area.lower()
                if ma == 'w': read_area = memory_areas.WORK_BIT
                elif ma == 'c': read_area = memory_areas.CIO_BIT
                elif ma == 'd': read_area = memory_areas.DATA_MEMORY_BIT
                elif ma == 'h': read_area = memory_areas.HOLDING_BIT
                else: read_area = memory_areas.DATA_MEMORY_BIT
                
                begin_address = word_address.to_bytes(2, 'big') + bit_address.to_bytes(1, 'big')
                response = self.client.memory_area_read(read_area, begin_address, number_of_values)
                
                fins_response = fins.fins_common.FinsResponseFrame()
                fins_response.from_bytes(response)
                
                if not fins_response.end_code.startswith(b'\x00'):
                    return False, None, f"End Code: {fins_response.end_code}"
                
                data = fins_response.text
                return True, int.from_bytes(data, 'big'), "Read success"

            # Memory area mapping: 'd' (DM), 'w' (WR), 'c' (CIO), 'h' (HR)
            result = self.client.read(memory_area=memory_area.lower(), word_address=word_address, data_type=data_type.lower(), number_of_values=number_of_values)
            return True, result, "Read success"
        except Exception as e:
            error_msg = f"Read failed: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg

    def write_variable(self, value: Any, memory_area: str, address_str: str, data_type: str = 'w') -> Tuple[bool, str]:
        if not self.connected or not self.client:
            return False, "Not connected"
        try:
            if "." in address_str:
                parts = address_str.split(".")
                word_address = int(parts[0])
                bit_address = int(parts[1])
            else:
                word_address = int(address_str)
                bit_address = 0

            # Handle Bool explicitly
            if data_type.lower() == 'b':
                import fins.fins_common
                memory_areas = fins.fins_common.FinsPLCMemoryAreas()
                ma = memory_area.lower()
                if ma == 'w': write_area = memory_areas.WORK_BIT
                elif ma == 'c': write_area = memory_areas.CIO_BIT
                elif ma == 'd': write_area = memory_areas.DATA_MEMORY_BIT
                elif ma == 'h': write_area = memory_areas.HOLDING_BIT
                else: write_area = memory_areas.DATA_MEMORY_BIT
                
                begin_address = word_address.to_bytes(2, 'big') + bit_address.to_bytes(1, 'big')
                write_bytes = int(value).to_bytes(1, 'big')
                
                response = self.client.memory_area_write(write_area, begin_address, write_bytes, 1)
                fins_response = fins.fins_common.FinsResponseFrame()
                fins_response.from_bytes(response)
                
                if not fins_response.end_code.startswith(b'\x00'):
                    return False, f"End Code: {fins_response.end_code}"
                return True, "Write success"

            # Convert value to list if writing multiple values, else single
            self.client.write(value=value, memory_area=memory_area.lower(), word_address=word_address, data_type=data_type.lower())
            return True, "Write success"
        except Exception as e:
            error_msg = f"Write failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
