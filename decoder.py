from datetime import date, timedelta, time
import sys
from bitarray import bitarray
from bitarray.util import ba2int

CODE_NATURE_STR = {
    0: '-',
    1: 'bus',
    3: 'metro',
    4: 'tramway',
}

CODE_TYPE_STR = {
    0: '-',
    1: 'entry validation',
    6: 'connection entry validation',
}

GEO_ROUTE_DIRECTION_STR = {
    0: '-',
    1: 'outward',
    2: 'inward',
}

class Chunk:
    head = 0
    
    def __init__(self, hex_str:str=None, bytes_reversed:bool=False):
        self.bits = bitarray()
        if hex_str:
            self.bits.frombytes(bytes.fromhex(hex_str))
            if bytes_reversed:
                self.bits.bytereverse()
                self.bits.reverse()
        
    def __repr__(self):
        return str(self.bits)
    
    def __add__(self, obj2: "Chunk"):
        new_chunk = Chunk()
        new_chunk.bits = self.bits + obj2.bits
        return new_chunk
    
    def read(self, count: int) -> "Chunk":
        self.head += count
        sub_chunk = Chunk()
        sub_chunk.bits = self.bits[self.head-count:self.head]
        return sub_chunk
    
    def datediff(self, end_date: date) -> date:
        return end_date - timedelta(days = self.int)
    
    @property
    def bytes(self) -> bytes:
        return self.bits.tobytes()
    
    @property
    def int(self) -> int:
        return ba2int(self.bits)
    
    @property
    def bytes_str(self) -> str:
        return self.bytes.hex(" ", 1).upper()
    
    @property
    def time(self) -> time:
        return time(hour=self.int // 60, minute=self.int % 60)
    
    @property
    def date(self) -> date:
        return date(1997, 1, 1) + timedelta(days = self.int)
    


class Ticket:
    UID: Chunk = None
    blocks: list[Chunk] = []
    
    def __init__(self, flipper_file_path: str):
        with open(flipper_file_path) as file:
            for line in file:
                if "UID:" in line:
                    uid = line.split(":")[1]
                    self.UID = Chunk(uid)
                if "Block" in line:
                    reversed_bytes_str = line.split(":")[1]
                    self.blocks.append(Chunk(reversed_bytes_str, True))
    
    def __str__(self):
        str = f"UID: {self.UID.bytes_str}\n"
        for i in range(len(self.blocks)):
            str += f"Block {i}: {self.blocks[i].bytes_str}\n"
        return str
    
    def get_system_data(self) -> dict:
        system_chunk = self.blocks[0]
        
        system_chunk.read(23)
        KEY_ID = system_chunk.read(4)
        PARTITION_ID = system_chunk.read(5)
        
        return {
            "Key ID": hex(KEY_ID.int),
            "Partition ID": hex(PARTITION_ID.int),
            "UID (hex)": self.UID.bytes_str,
            "UID (decimal)": self.UID.int,
        }
    
    def get_distribution(self) -> dict:
        distribution_chunk = self.blocks[1] + self.blocks[2] + self.blocks[0]
        
        COUNTRY_CODE = hex(distribution_chunk.read(12).int)
        ORGANIZATIONAL_AUTHORITY = hex(distribution_chunk.read(12).int)
        CONTRACT_APP_VERSION_NUMBER = distribution_chunk.read(6).int
        CONTRACT_PROVIDER = distribution_chunk.read(8).int
        CONTRACT_TARIFF = distribution_chunk.read(16).int
        CONTRACT_MEDIUM_END_DATE = distribution_chunk.read(14).date
        CONTRACT_BITMAP = distribution_chunk.read(5)
        CONTRACT_SALE_BITMAP = distribution_chunk.read(2)
        CONTRACT_SALE_AGENT = distribution_chunk.read(8).int
        
        return {
            "Certificate": self.blocks[15].bytes_str,
            "ContractApplicationVersionNumber": CONTRACT_APP_VERSION_NUMBER,
            "ContractMediumEndDate": CONTRACT_MEDIUM_END_DATE,
            "ContractProvider": CONTRACT_PROVIDER,
            "ContractSaleAgent": CONTRACT_SALE_AGENT,
            "ContractTariff": CONTRACT_TARIFF,
            "CountryCode": COUNTRY_CODE,
            "OrganizationalAuthority": ORGANIZATIONAL_AUTHORITY,
        }
    
    def get_usage(self, usage_b=False) -> dict:
        if not usage_b:
            chunk = self.blocks[3] + self.blocks[4] + self.blocks[7] + self.blocks[8] + self.blocks[9]
        else:
            chunk = self.blocks[10] + self.blocks[11] + self.blocks[12] + self.blocks[13] + self.blocks[14]
            
        distribution = self.get_distribution()
        CONTRACT_MEDIUM_END_DATE = distribution["ContractMediumEndDate"]
        
        EVENT_DATE_STAMP = chunk.read(10).datediff(CONTRACT_MEDIUM_END_DATE)
        EVENT_TIME_STAMP = chunk.read(11).time
        EVENT_PROVIDER = chunk.read(8).int
        EVENT_CODE_NATURE = CODE_NATURE_STR[chunk.read(5).int]
        EVENT_CODE_TYPE = CODE_TYPE_STR[chunk.read(5).int]
        EVENT_BITMAP = chunk.read(5)
        EVENT_GEO_BITMAP = chunk.read(6)
        EVENT_GEO_ROUTE_ID = chunk.read(14).int
        EVENT_GEO_ROUTE_DIRECTION = GEO_ROUTE_DIRECTION_STR[chunk.read(2).int]
        
        IS_EVENT_GEO_LOCATION_ID = EVENT_GEO_BITMAP.bits[4:5] == bitarray('1')
        if IS_EVENT_GEO_LOCATION_ID:
            EVENT_GEO_LOCATION_ID = chunk.read(16).int
        else:
            EVENT_GEO_LOCATION_ID = "-"
            
        EVENT_ROUTE_BITMAP = chunk.read(2)
        EVENT_ROUTE_ID_1 = chunk.read(14).int
        EVENT_ROUTE_ID_2 = chunk.read(14).int
        EVENT_VALIDITY_BITMAP = chunk.read(4)
        EVENT_VALIDITY_TIME_FIRST_STAMP = chunk.read(11).time
        EVENT_COUNT_BITMAP = chunk.read(3)
        EVENT_COUNT_PASSENGERS = chunk.read(4).int
        EVENT_COUNT = chunk.read(6).int
        EVENT_COUNT_INTERCHANGES = chunk.read(3).int
        
        return {
            "EventCode/Nature": EVENT_CODE_NATURE,
            "EventCode/Type": EVENT_CODE_TYPE,
            "EventProvider": EVENT_PROVIDER,
            "EventDateStamp": EVENT_DATE_STAMP,
            "EventTimeStamp": EVENT_TIME_STAMP,
            "EventGeoRouteDirection": EVENT_GEO_ROUTE_DIRECTION,
            "EventGeoRouteId": EVENT_GEO_ROUTE_ID,
            "EventRouteId1": EVENT_ROUTE_ID_1,
            "EventRouteId2": EVENT_ROUTE_ID_2,
            "EventValidityTimeFirstStamp": EVENT_VALIDITY_TIME_FIRST_STAMP,
            "EventCount": EVENT_COUNT,
            "EventCountInterchanges": EVENT_COUNT_INTERCHANGES,
            "EventCountPassengers": EVENT_COUNT_PASSENGERS,
            "EventGeoLocationId": EVENT_GEO_LOCATION_ID,
        }
        
    def get_counters(self) -> dict:
        cnt1 = self.blocks[5]
        cnt2 = self.blocks[6]
        
        LOADED = cnt1.read(8)
        AVAILABLE = cnt1.read(24)
        SWAP = cnt2.read(32)
        NEXT_USAGE = 'Usage A' if SWAP.int % 2 else 'Usage B'
        
        return {
            "Next usage":NEXT_USAGE,
            "Swap count": 0xFFFFFFFF - SWAP.int,
            "Tickets available": AVAILABLE.int,
            "Loadings": 255 - LOADED.int,
        }

def print_dict_pretty(title: str, dict_to_print: dict) -> None:
    print(title)
    print(''.join(['-' for _ in range(len(title))]))
    for key, value in dict_to_print.items():
        print(f"{key:40}\t{value}")
    print()

if(len(sys.argv) != 2):
    raise Exception("Filename missing")

ticket = Ticket(sys.argv[1])
print_dict_pretty("Distribution", ticket.get_distribution())
print_dict_pretty("System data", ticket.get_system_data())
print_dict_pretty("Counters", ticket.get_counters())
print_dict_pretty("Usage A", ticket.get_usage(False))
print_dict_pretty("Usage B", ticket.get_usage(True))