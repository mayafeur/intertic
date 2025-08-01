from datetime import date, timedelta, time
import sys
from bitarray import bitarray
from bitarray.util import ba2int

CONTRACT_TARIFF_STR = {
    2005: "1 déplacement",
    2007: "1 déplacement dernière minute",
    2010: "10 déplacements",
    2020: "2 déplacements",
    2060: "1 déplacement (SAV)",
    2090: "1 déplacement aéroport",
}

COUNTRY_STR = {
    0x250: "France",
}

ORGANIZATIONAL_AUTHORITY_STR = {
    0x916: "Tisséo"
}

EVENT_CODE_NATURE_STR = {
    1: 'Autobus',
    3: 'Métro',
    4: 'Tramway',
}

EVENT_CODE_TYPE_STR = {
    1: 'Validation',
    6: 'Validation en correspondance',
}

EVENT_GEO_ROUTE_DIRECTION_STR = {
    1: 'Aller',
    2: 'Retour',
}

EVENT_GEO_ROUTE_ID_STR = {
    24: "Navette aéroport",
    262: "Navette cimetières",
    1001: "Métro A",
    1002: "Métro B",
    1003: "Ligne C",
    1005: "Tramway T1",
    1007: "Câble Téléo",
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
                if "Block" in line:   # Flipper dump
                    reversed_bytes_str = line.split(":")[1]
                    self.blocks.append(Chunk(reversed_bytes_str, True))
                if "|     " in line:  # Near Field Chaos dump
                    bytes_str = line.split("|")[2]
                    self.blocks.append(Chunk(bytes_str, False))
    
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
            "Clé": hex(KEY_ID.int),
            "Partition": hex(PARTITION_ID.int),
            "UID (hex)": self.UID.bytes_str,
            "UID (décimal)": self.UID.int,
        }
    
    def get_distribution(self) -> dict:
        distribution_chunk = self.blocks[1] + self.blocks[2] + self.blocks[0]
        
        COUNTRY_CODE = distribution_chunk.read(12).int
        ORGANIZATIONAL_AUTHORITY = distribution_chunk.read(12).int
        CONTRACT_APPLICATION_VERSION_NUMBER = distribution_chunk.read(6).int
        CONTRACT_PROVIDER = distribution_chunk.read(8).int
        CONTRACT_TARIFF = distribution_chunk.read(16).int
        CONTRACT_MEDIUM_END_DATE = distribution_chunk.read(14).date
        CONTRACT_BITMAP = distribution_chunk.read(5)
        CONTRACT_SALE_BITMAP = distribution_chunk.read(2)
        CONTRACT_SALE_AGENT = distribution_chunk.read(8).int
        
        return {
            "Certificat": self.blocks[15].bytes_str,
            "Version du contrat": CONTRACT_APPLICATION_VERSION_NUMBER,
            "Date de fin du contrat": CONTRACT_MEDIUM_END_DATE,
            "Fournisseur": CONTRACT_PROVIDER,
            "Exploitant": CONTRACT_SALE_AGENT,
            "Tarif": print_from_dict(CONTRACT_TARIFF, CONTRACT_TARIFF_STR),
            "Pays": print_from_dict(COUNTRY_CODE, COUNTRY_STR),
            "Autorité organisatrice": print_from_dict(ORGANIZATIONAL_AUTHORITY, ORGANIZATIONAL_AUTHORITY_STR),
        }
    
    def get_usage(self, usage_b=False) -> dict:
        if not usage_b:
            chunk = self.blocks[3] + self.blocks[4] + self.blocks[7] + self.blocks[8] + self.blocks[9]
        else:
            chunk = self.blocks[10] + self.blocks[11] + self.blocks[12] + self.blocks[13] + self.blocks[14]
            
        distribution = self.get_distribution()
        CONTRACT_MEDIUM_END_DATE = distribution["Date de fin du contrat"]
        
        EVENT_DATE_STAMP = chunk.read(10).datediff(CONTRACT_MEDIUM_END_DATE)
        EVENT_TIME_STAMP = chunk.read(11).time
        EVENT_PROVIDER = chunk.read(8).int
        EVENT_CODE_NATURE = chunk.read(5).int
        EVENT_CODE_TYPE = chunk.read(5).int
        EVENT_BITMAP = chunk.read(5)
        
        EVENT_GEO_ROUTE_ID = 0
        EVENT_GEO_ROUTE_DIRECTION = 0
        EVENT_GEO_LOCATION_ID = "-"
        EVENT_ROUTE_ID_1 = 0
        EVENT_ROUTE_ID_2 = 0
        
        IS_EVENT_GEO_AND_ROUTE_IDS = EVENT_BITMAP.bits[1:3] == bitarray('11')
        if IS_EVENT_GEO_AND_ROUTE_IDS:

            EVENT_GEO_BITMAP = chunk.read(6)
            EVENT_GEO_ROUTE_ID = chunk.read(14).int
            EVENT_GEO_ROUTE_DIRECTION = chunk.read(2).int
            
            IS_EVENT_GEO_LOCATION_ID = EVENT_GEO_BITMAP.bits[4:5] == bitarray('1')
            if IS_EVENT_GEO_LOCATION_ID:
                EVENT_GEO_LOCATION_ID = chunk.read(16).int
            
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
            "Moyen de transport": print_from_dict(EVENT_CODE_NATURE, EVENT_CODE_NATURE_STR),
            "Action": print_from_dict(EVENT_CODE_TYPE, EVENT_CODE_TYPE_STR),
            "Exploitant": EVENT_PROVIDER,
            "Date": EVENT_DATE_STAMP,
            "Heure": EVENT_TIME_STAMP,
            "Direction": print_from_dict(EVENT_GEO_ROUTE_DIRECTION, EVENT_GEO_ROUTE_DIRECTION_STR),
            "Ligne empruntée": print_from_dict(EVENT_GEO_ROUTE_ID, EVENT_GEO_ROUTE_ID_STR, True),
            "Ligne précédente": print_from_dict(EVENT_ROUTE_ID_1, EVENT_GEO_ROUTE_ID_STR),
            "Ligne encore précédente": print_from_dict(EVENT_ROUTE_ID_2, EVENT_GEO_ROUTE_ID_STR),
            "Heure de 1e validation": EVENT_VALIDITY_TIME_FIRST_STAMP,
            "Nombre de trajets": EVENT_COUNT,
            "Nombre de correspondances": EVENT_COUNT_INTERCHANGES,
            "Nombre de passagers": EVENT_COUNT_PASSENGERS,
            "Station": EVENT_GEO_LOCATION_ID,
        }
        
    def get_counters(self) -> dict:
        cnt1 = self.blocks[5]
        cnt2 = self.blocks[6]
        
        LOADED = cnt1.read(8)
        AVAILABLE = cnt1.read(24)
        SWAP = cnt2.read(32)
        NEXT_USAGE = 'Usage A' if SWAP.int % 2 else 'Usage B'
        
        return {
            "Prochain usage":NEXT_USAGE,
            "Swap": 0xFFFFFFFF - SWAP.int,
            "Titres disponibles": AVAILABLE.int,
            "Chargements effectués": 255 - LOADED.int,
        }

def print_dict_pretty(title: str, dict_to_print: dict) -> None:
    print(title)
    print(''.join(['-' for _ in range(len(title))]))
    for key, value in dict_to_print.items():
        print(f"{key:30}{value}")
    print()
    
def print_from_dict(raw_value: int, str_dict: dict, just_int=False) -> str:
    raw_value_hex = hex(raw_value)
    if raw_value in str_dict.keys():
        return str_dict[raw_value]
    elif raw_value == 0:
        return "-"
    elif just_int:
        return raw_value
    else:
        return f"?   {raw_value_hex} / {raw_value}"

if(len(sys.argv) != 2):
    raise Exception("Nom de fichier non trouvé")

ticket = Ticket(sys.argv[1])
print_dict_pretty("Système", ticket.get_system_data())
print_dict_pretty("Distribution", ticket.get_distribution())
print_dict_pretty("Compteurs", ticket.get_counters())
print_dict_pretty("Usage A", ticket.get_usage(False))
print_dict_pretty("Usage B", ticket.get_usage(True))
