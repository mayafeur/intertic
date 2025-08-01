# Décodeur de titres de transports rechargeables

Cet outil décode les titres de transport rechargerables du réseau Tisséo de Toulouse afin
de permettre aux client.e.s de connaître leur solde et toutes les informations annexes stockées sur le titre
étant donné que l'application Tisséo ne permet pas de lire les titres rechargeables.

- Le fichier d'entrée prend plusieurs formats, notamment les dumps du Flipper Zero (cf. les exemples)
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
Système
-------
Clé                           0x1
Partition                     0x10
UID (hex)                     D0 02 33 80 B7 6B 24 B4
UID (décimal)                 14988599137768514740

Distribution
------------
Certificat                    C3 54 76 4B
Version du contrat            9
Date de fin du contrat        2028-04-20
Fournisseur                   1
Exploitant                    1
Tarif                         1 déplacement
Pays                          France
Autorité organisatrice        Tisséo

Compteurs
---------
Prochain usage                Usage B
Swap                          3
Titres disponibles            0
Chargements effectués         1

Usage A
-------
Moyen de transport            Autobus
Action                        Validation en correspondance
Exploitant                    1
Date                          2025-07-15
Heure                         11:51:00
Direction                     Aller
Ligne empruntée               19
Ligne précédente              Métro A
Ligne encore précédente       -
Heure de 1e validation        11:03:00
Nombre de trajets             1
Nombre de correspondances     1
Nombre de passagers           1
Station                       -

Usage B
-------
Moyen de transport            Métro
Action                        Validation
Exploitant                    1
Date                          2025-07-15
Heure                         11:03:00
Direction                     -
Ligne empruntée               Métro A
Ligne précédente              -
Ligne encore précédente       -
Heure de 1e validation        11:03:00
Nombre de trajets             0
Nombre de correspondances     0
Nombre de passagers           1
Station                       25
```

## Voir aussi

- [ST25TB series NFC tags for fun in French public transports](https://raw.githubusercontent.com/gentilkiwi/st25tb_kiemul/main/ST25TB_transport.pdf) par gentilkiwi [PDF]
- [ST25TB datasheet](https://www.st.com/resource/en/datasheet/st25tb04k.pdf) [PDF]
- [FAQ tickets rechargeables Tisséo](https://www.tisseo.fr/FAQ?thematic=generalites)
