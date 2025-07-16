# Décodeur de titres de transports rechargeables

- Décode uniquement les titres rechargeables du réseau Tisséo de Toulouse (pour le moment)
- Le fichier d'entrée est un dump de Flipper Zero (cf. les exemples)
- Inspiré de [intertic.py](https://github.com/RfidResearchGroup/proxmark3/blob/master/client/pyscripts/intertic.py) du projet [proxmark3](https://github.com/RfidResearchGroup/proxmark3/)

## Dépendances

- [bitarray](https://pypi.org/project/bitarray/)

## Usage

```
python3 decoder.py fichier.txt
```

## Exemple

```
$ python3 decoder.py tisseo_24b4.txt
Distribution
------------
Certificate                             	C3 54 76 4B
ContractApplicationVersionNumber        	9
ContractMediumEndDate                   	2028-04-20
ContractProvider                        	1
ContractSaleAgent                       	1
ContractTariff                          	2005
CountryCode                             	0x250
OrganizationalAuthority                 	0x916

System data
-----------
Key ID                                  	0x1
Partition ID                            	0x10
UID (hex)                               	D0 02 33 80 B7 6B 24 B4
UID (decimal)                           	14988599137768514740

Counters
--------
Next usage                              	Usage B
Swap count                              	3
Tickets available                       	0
Loadings                                	1

Usage A
-------
EventCode/Nature                        	bus
EventCode/Type                          	connection entry validation
EventProvider                           	1
EventDateStamp                          	2025-07-15
EventTimeStamp                          	11:51:00
EventGeoRouteDirection                  	outward
EventGeoRouteId                         	19
EventRouteId1                           	1001
EventRouteId2                           	0
EventValidityTimeFirstStamp             	11:03:00
EventCount                              	1
EventCountInterchanges                  	1
EventCountPassengers                    	1
EventGeoLocationId                      	-

Usage B
-------
EventCode/Nature                        	metro
EventCode/Type                          	entry validation
EventProvider                           	1
EventDateStamp                          	2025-07-15
EventTimeStamp                          	11:03:00
EventGeoRouteDirection                  	-
EventGeoRouteId                         	1001
EventRouteId1                           	0
EventRouteId2                           	0
EventValidityTimeFirstStamp             	11:03:00
EventCount                              	0
EventCountInterchanges                  	0
EventCountPassengers                    	1
EventGeoLocationId                      	25
```

## Voir aussi

- [ST25TB series NFC tags for fun in French public transports](https://raw.githubusercontent.com/gentilkiwi/st25tb_kiemul/main/ST25TB_transport.pdf) par gentilkiwi [PDF]
- [ST25TB datasheet](https://www.st.com/resource/en/datasheet/st25tb04k.pdf)
- [FAQ tickets rechargeables Tisséo](https://www.tisseo.fr/FAQ?thematic=generalites)
