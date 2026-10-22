
from Functions import gantt_chart, resultaten_naar_excel, random_swap, swap
import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt
import time

# Instellingen
random_seed_values = [1, 5, 10, 42, 100]
max_swaps_values = [100, 500, 1000, 5000, 10000]
max_rondes_values = [1, 2, 5, 10, 20]

random_seed = 5
max_swaps = None
max_rondes = None

# Data inladen
df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)
df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

def dictionary(df):
    '''
    Zet de dataframes over naar een dictionary.

    Return:
        Een lijst met dictionaries
    '''
    jobs = []

    for i in range(len(df)):
        job = {}
        for column in df.columns:
            job[column] = df[column][i]
        jobs.append(job)

    return jobs

# Dataframes omzetten naar dictionaries
di_orders_org = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups_org = dictionary(df_setups)

di_orders = di_orders_org.copy()
di_machines = di_machines_org.copy()
di_setups = di_setups_org.copy()

di_orders.sort(key=lambda job: job['Deadline'])

def plan_order(machine, order, tijd, vorige_kleur, di_setups):
    '''
    Plant één order op een machine.

    Return:
        tijd
        kleur
        tardiness
        penaltyorder
        setup_tijd
        begintijd
        procestijd
        eindtijd
    '''
    kleur = order['Colour']
    setup_tijd = 0

    # Extra tijd voor kleurverandering
    if vorige_kleur is not None and kleur != vorige_kleur:
        setup_gevonden = False

        for setup in di_setups:
            if setup['From colour'] == vorige_kleur and setup['To colour'] == kleur:
                setup_tijd = setup['Setup time']
                tijd += setup_tijd
                setup_gevonden = True
                break

        if not setup_gevonden:
            raise ValueError(f'Geen setup gevonden van {vorige_kleur} naar {kleur}')

    # Begintijd
    begintijd = tijd

    # Productietijd
    procestijd = order['Surface'] / machine['Speed']
    tijd += procestijd

    # Eindtijd
    eindtijd = tijd

    # Tardiness en penalty
    tardiness = max(0, eindtijd - order['Deadline'])
    penaltyorder = order['Penalty'] * tardiness

    return tijd, kleur, tardiness, penaltyorder, setup_tijd, begintijd, procestijd, eindtijd

def greedy_schedule(di_orders, di_machines, di_setups):
    '''
    Maakt een planning met behulp van de greedy heuristic.

    Orders worden verwerkt in de aangeleverde volgorde.
    Elke order wordt toegewezen aan de machine met de laagste huidige tijd.
    Bij gelijke tijden wordt de snelste machine gekozen.

    Return:
        volgordes
        machines_per_order
    '''
    aantal_machines = len(di_machines)
    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    volgordes = [[] for _ in range(aantal_machines)]
    machines_per_order = []

    for order in di_orders:

        # Machine met de laagste huidige tijd
        laagste_tijd = min(tijden)
        mogelijke_machines = []

        for i in range(aantal_machines):
            if tijden[i] == laagste_tijd:
                mogelijke_machines.append(i)

        # Bij gelijke tijd: snelste machine kiezen
        machine_index = mogelijke_machines[0]

        for i in mogelijke_machines:
            if di_machines[i]['Speed'] > di_machines[machine_index]['Speed']:
                machine_index = i

        machines_per_order.append(machine_index)
        kleur = order['Colour']

        # Setup time bij een kleurverandering
        if vorige_kleuren[machine_index] is not None and kleur != vorige_kleuren[machine_index]:
            setup_gevonden = False

            for setup in di_setups:
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if not setup_gevonden:
                raise ValueError(f"Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}")

        # Productietijd
        tijden[machine_index] += order['Surface'] / di_machines[machine_index]['Speed']

        # Laatste kleur opslaan
        vorige_kleuren[machine_index] = kleur

        # Order toevoegen aan de machine
        volgordes[machine_index].append(order['Order'])

    return volgordes, machines_per_order

def calculate_results(volgordes, di_orders, di_machines, di_setups):
    '''
    Berekent alle resultaten van een gegeven planning.
    '''
    aantal_machines = len(di_machines)
    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    total_tardiness = 0
    penalty = 0
    resultaten = {}

    orders = {}
    for order in di_orders:
        orders[order['Order']] = order

    for machine_index in range(aantal_machines):
        for i in range(len(volgordes[machine_index])):
            order_nummer = volgordes[machine_index][i]
            order = orders[order_nummer]

            tijd, kleur, tardiness, penaltyorder, setup_tijd, begintijd, procestijd, eindtijd = plan_order(
                di_machines[machine_index],
                order,
                tijden[machine_index],
                vorige_kleuren[machine_index],
                di_setups
            )

            tijden[machine_index] = tijd
            vorige_kleuren[machine_index] = kleur
            total_tardiness += tardiness
            penalty += penaltyorder

            resultaten[order_nummer] = {
                'machine': machine_index,
                'seqno': i + 1,
                'setup': setup_tijd,
                'start': begintijd,
                'process': procestijd,
                'end': eindtijd,
                'tardiness': tardiness,
                'cost': penaltyorder
            }

    machines_per_order = []
    seqno_per_order = []
    setup_per_order = []
    begintijden = []
    procestijden = []
    eindtijden = []
    tardiness_per_order = []
    penalty_per_order = []

    for order in di_orders:
        order_nummer = order['Order']

        machines_per_order.append(resultaten[order_nummer]['machine'])
        seqno_per_order.append(resultaten[order_nummer]['seqno'])
        setup_per_order.append(resultaten[order_nummer]['setup'])
        begintijden.append(resultaten[order_nummer]['start'])
        procestijden.append(resultaten[order_nummer]['process'])
        eindtijden.append(resultaten[order_nummer]['end'])
        tardiness_per_order.append(resultaten[order_nummer]['tardiness'])
        penalty_per_order.append(resultaten[order_nummer]['cost'])

    return total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order

def improving_search(di_orders, max_swaps=None, max_rondes=None):
    # Beginvolgorde overnemen
    current = di_orders.copy()
    beste_volgorde = current.copy()

    # Eerste greedy planning
    volgordes, _ = greedy_schedule(beste_volgorde.copy(), di_machines, di_setups)
    gegevens = calculate_results(volgordes, beste_volgorde, di_machines, di_setups)
    best_tot_tard = gegevens[0]
    best_penalty = gegevens[1]
    begin_penalty = best_penalty

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    verbetering = True
    aantal_swaps = 0
    aantal_rondes = 0

    while verbetering:
        if max_rondes is not None and aantal_rondes >= max_rondes:
            break

        if max_swaps is not None and aantal_swaps >= max_swaps:
            break

        verbetering = False
        aantal_rondes += 1

        # Beste resultaat van deze ronde
        ronde_beste_volgorde = beste_volgorde.copy()
        ronde_beste_penalty = best_penalty
        ronde_beste_tard = best_tot_tard

        # Alle mogelijke swaps controleren
        for i in range(len(beste_volgorde)):
            if max_swaps is not None and aantal_swaps >= max_swaps:
                break

            for j in range(i + 1, len(beste_volgorde)):
                if max_swaps is not None and aantal_swaps >= max_swaps:
                    break

                # Nieuwe ordervolgorde maken
                new_current = beste_volgorde.copy()
                new_current[i], new_current[j] = new_current[j], new_current[i]

                # Greedy planning maken en doorrekenen
                volgordes, _ = greedy_schedule(new_current.copy(), di_machines, di_setups)
                gegevens = calculate_results(volgordes, new_current, di_machines, di_setups)
                current_tard = gegevens[0]
                current_penalty = gegevens[1]

                aantal_swaps += 1
                penalty_per_iteratie.append(current_penalty)

                # Beste swap van deze ronde opslaan
                if current_penalty < ronde_beste_penalty:
                    ronde_beste_penalty = current_penalty
                    ronde_beste_tard = current_tard
                    ronde_beste_volgorde = new_current.copy()
                    verbetering = True

        # Beste oplossing van deze ronde accepteren
        if verbetering:
            best_penalty = ronde_beste_penalty
            best_tot_tard = ronde_beste_tard
            beste_volgorde = ronde_beste_volgorde.copy()

        beste_penalty_per_iteratie.append(best_penalty)

    return best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie, begin_penalty, aantal_swaps, aantal_rondes

def voer_experiment_uit(random_seed, max_swaps, max_rondes, random_start=False):
    random.seed(random_seed)

    # Beginvolgorde bepalen
    start_volgorde = di_orders.copy()

    if random_start:
        random.shuffle(start_volgorde)

    print(f'\nExperiment: seed={random_seed}, max_swaps={max_swaps}, max_rondes={max_rondes}, random_start={random_start}')

    # Improving Search uitvoeren
    start = time.perf_counter()

    best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie, begin_penalty, aantal_swaps, aantal_rondes = improving_search(
        start_volgorde, max_swaps, max_rondes
    )

    rekentijd = time.perf_counter() - start

    # Resultaten verzamelen
    resultaat = {
        'Random seed': random_seed if random_start else None,
        'Random start': random_start,
        'Max swaps': max_swaps,
        'Max rondes': max_rondes,
        'Begin penalty': begin_penalty,
        'Total penalty': best_penalty,
        'Total tardiness': best_tot_tard,
        'Verbetering': begin_penalty - best_penalty,
        'Aantal swaps': aantal_swaps,
        'Aantal rondes': aantal_rondes,
        'Rekentijd (s)': rekentijd
    }

    print(f'Begin penalty: {begin_penalty:.2f}')
    print(f'Penalty na Improving Search: {best_penalty:.2f}')
    print(f'Verbetering: {begin_penalty - best_penalty:.2f}')
    print(f'Aantal swaps: {aantal_swaps}')
    print(f'Aantal rondes: {aantal_rondes}')
    print(f'Rekentijd: {rekentijd:.2f} seconden')

    return resultaat, beste_volgorde

# Experimenten uitvoeren
experimenten = {
    'random_seed': [],
    'max_swaps': [],
    'max_rondes': []
}

beste_resultaat = float('inf')
beste_volgorde_totaal = None
beste_instellingen = None

def bewaar_beste_resultaat(resultaat, volgorde):
    global beste_resultaat, beste_volgorde_totaal, beste_instellingen

    if resultaat['Total penalty'] < beste_resultaat:
        beste_resultaat = resultaat['Total penalty']
        beste_volgorde_totaal = volgorde.copy()
        beste_instellingen = resultaat.copy()

# Random seed experimenten
for waarde in random_seed_values:
    resultaat, beste_volgorde = voer_experiment_uit(
        waarde, max_swaps, max_rondes, random_start=True
    )
    experimenten['random_seed'].append(resultaat)
    bewaar_beste_resultaat(resultaat, beste_volgorde)

# Maximum aantal swaps experimenten
for waarde in max_swaps_values:
    resultaat, beste_volgorde = voer_experiment_uit(
        random_seed, waarde, max_rondes
    )
    experimenten['max_swaps'].append(resultaat)
    bewaar_beste_resultaat(resultaat, beste_volgorde)

# Maximum aantal rondes experimenten
for waarde in max_rondes_values:
    resultaat, beste_volgorde = voer_experiment_uit(
        random_seed, max_swaps, waarde
    )
    experimenten['max_rondes'].append(resultaat)
    bewaar_beste_resultaat(resultaat, beste_volgorde)

# Alle experimenten opslaan in Excel
with pd.ExcelWriter('Experimenten_Greedy.xlsx', engine='openpyxl') as writer:
    for sheetnaam, resultaten in experimenten.items():
        pd.DataFrame(resultaten).to_excel(writer, sheet_name=sheetnaam, index=False)

print('\nAlle experimenten zijn opgeslagen in Experimenten_Greedy.xlsx')

# Beste resultaat van alle experimenten
print(f'\nBeste penalty van alle experimenten: {beste_resultaat:.2f}')
print(f'Bijbehorende instellingen: {beste_instellingen}')

# Beste planning opnieuw maken
beste_volgordes, _ = greedy_schedule(beste_volgorde_totaal.copy(), di_machines, di_setups)

# Alle gegevens van de beste planning berekenen
total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_results(
    beste_volgordes, beste_volgorde_totaal, di_machines, di_setups
)

print(f'De beste planning heeft een totale tardiness van {total_tardiness:.2f} en {penalty:.2f} aan penalty')

# Beste planning exporteren naar Excel
resultaten_naar_excel(
    beste_volgorde_totaal, di_machines, machines_per_order, seqno_per_order,
    setup_per_order, begintijden, procestijden, eindtijden,
    tardiness_per_order, penalty_per_order, 'Results_greedy_improved.xlsx'
)

# Gantt-chart van de beste planning
gantt_chart(
    beste_volgorde_totaal, di_machines, machines_per_order, setup_per_order,
    begintijden, procestijden, eindtijden, tardiness_per_order, penalty
)
