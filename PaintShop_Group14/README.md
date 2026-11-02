# PaintShop Scheduling – OR5 | Groep 14

**Studenten:** Fee van Zoghel (5835704) en Matthijs van Meeuwen (5797799)  
**Onderdeel:** Operations Research 5 (OR5)

## 1. Project

In dit project optimaliseren we de planning van verfopdrachten over meerdere machines. Het doel is de **totale kosten door het overschrijden van deadlines (total penalty)** te minimaliseren. Bij het plannen houden de algoritmen rekening met machinesnelheden, kleuren en omsteltijden (*setup times*).

We hebben twee oplossingsmethoden ontwikkeld:

1. **Greedy Constructive Heuristic (EDD)**, gevolgd door **Discrete Improving Search**.
2. **Simulated Annealing (SA)**, gevolgd door **Discrete Improving Search**.

De Improving Search gebruikt swaps en de *Best Improvement*-strategie en stopt wanneer binnen de gekozen swap-neighbourhood geen verbeterende swap meer overblijft.

## 2. Inhoud van het portfolio

| Map / bestand | Inhoud |
| --- | --- |
| `01_Verslag/` | Verantwoordingsverslag als PDF, inclusief ontwerp, implementatie, validatie, experimenten, eigen onderzoek en bijlagen (waaronder de Implementation Checklist en documentatie van AI-gebruik). |
| `02_Python_Code/` | Python-implementatie van de twee oplossingsmethoden en gedeelde functies. |
| `03_Input_Data/` | De originele PaintShop-datasets van september en november 2026. |
| `04_Validatie/` | Testplan, testdatasets en scripts voor de validatietests. |
| `05_Experimenten/` | Vastgelegde experimentele resultaten en eventueel bijbehorende scripts. |
| `06_Resultaten/` | Geselecteerde Excel-planningen, waaronder de definitieve planning voor de novemberdataset. |
| `README.md` | Deze handleiding. |

### Python-bestanden

| Bestand | Functie |
| --- | --- |
| `Greedy.py` | Bouwt de initiële planning op met de EDD-regel. |
| `Improved_greedy.py` | Voert Discrete Improving Search uit op de greedy-oplossing. |
| `Metaheuristic.py` | Voert Simulated Annealing uit. |
| `Improved_metaheuristic.py` | Voert Simulated Annealing uit, verbetert de gevonden oplossing met Discrete Improving Search en toont het zoekverloop. |
| `Functions.py` | Gedeelde functies voor onder andere swaps, Gantt-charts en Excel-export. |

## 3. Benodigdheden

- Python 3
- Python-pakketten `pandas`, `numpy`, `matplotlib` en `openpyxl`

Installeer de benodigde pakketten via een terminal:

```
python -m pip install pandas numpy matplotlib openpyxl
```

## 4. Python-code uitvoeren

1. Pak het volledige portfolio uit. **Behoud de mappenstructuur.**
2. Open de hoofdmap van het portfolio in Visual Studio Code of een andere Python-omgeving.
3. Zorg dat `Functions.py` in dezelfde map staat als de overige implementatiescripts.
4. Controleer bovenaan het gewenste script de geselecteerde dataset en, bij Simulated Annealing, de parameters en random seed.
5. Voer vanuit de hoofdmap het gewenste script uit, bijvoorbeeld:

```
python 02_Python_Code/Greedy.py
python 02_Python_Code/Improved_greedy.py
python 02_Python_Code/Metaheuristic.py
python 02_Python_Code/Improved_metaheuristic.py
```

**Let op:** elk commando start een afzonderlijke uitvoering. Het is niet nodig alle vier de scripts na elkaar te starten om één methode te testen. Bij Simulated Annealing kan de rekentijd aanzienlijk oplopen, afhankelijk van de ingestelde parameters.

De scripts gebruiken Excel-invoer met de werkbladen `Orders`, `Machines` en `Setups`. Voor de definitieve inlevering is de **novemberdataset** de vereiste tweede probleeminstantie. De datasets staan in `03_Input_Data/`.

## 5. Uitvoer

Afhankelijk van het gekozen script worden de resultaten afgedrukt in de terminal, als **Excel-planning** geëxporteerd en als **Gantt-chart** weergegeven. `Improved_metaheuristic.py` kan bovendien het verloop van de penalty en temperatuur tijdens Simulated Annealing visualiseren.

De Excel-planning wordt gegenereerd met één werkblad, `Schedule`, en de kolommen:

`Order`, `Machine`, `SeqNo`, `Setup`, `Start`, `Process`, `End`, `Deadline`, `Tardiness`, `Penalty`, `Cost`.

De **geselecteerde definitieve planning voor november 2026** staat in `06_Resultaten/`. Deze planning is het verplichte eindresultaat voor de tweede dataset.

## 6. Validatie en experimenten

Voor de validatie zijn 13 tests opgesteld en uitgevoerd, onderverdeeld in *Happy Flow*, *Error Cases* en *Boundary Cases*. De testopzet, verwachte resultaten en uitkomsten zijn vastgelegd in het testplan en besproken in het verantwoordingsverslag.

Bij de experimenten zijn de oplossingskwaliteit en rekentijd van beide methoden vergeleken. Voor Simulated Annealing is daarnaast de invloed van parameterinstellingen en random seeds onderzocht. De resultaten staan in `05_Experimenten/`; de analyses en conclusies in het verantwoordingsverslag.

## 7. Verantwoording

De ontwerpkeuzes, validatie, experimenten, tijdscomplexiteitsanalyses, de eigen onderzoeksvraag en de documentatie van het gebruik van generatieve AI zijn opgenomen in het verantwoordingsverslag in `01_Verslag/`.

De bijgevoegde Python-code en Excelresultaten vormen samen met het verslag het beoordeelbare portfolio.
