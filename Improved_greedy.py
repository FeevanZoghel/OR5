from Functions import (gantt_chart, resultaten_naar_excel, random_swap, swap)

import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

random.seed(42)

df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name = None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups= df['Setups']


def dictionary(df):

    '''
    Zet de dataframes over naar een dictionary

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
    if vorige_kleur != None and kleur != vorige_kleur:
        setup_gevonden = False

        for setup in di_setups:
            if setup['From colour'] == vorige_kleur and setup['To colour'] == kleur:
                setup_tijd = setup['Setup time']
                tijd += setup_tijd
                setup_gevonden = True
                break

        if setup_gevonden == False:
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

    Orders worden gesorteerd op deadline.
    Elke order wordt toegewezen aan de machine met de laagste huidige tijd.
    Bij gelijke tijden wordt de snelste machine gekozen.

    Return:
        volgordes          : De volgorde van orders per machine
        machines_per_order : De gekozen machine per order
    '''

    aantal_machines = len(di_machines)

    # Huidige tijd per machine
    tijden = [0] * aantal_machines

    # Laatste kleur per machine
    vorige_kleuren = [None] * aantal_machines

    # Orders per machine
    volgordes = [[] for _ in range(aantal_machines)]

    # Machine waarop elke order wordt geplaatst
    machines_per_order = []

    for order in di_orders:

        # Machine met de laagste huidige tijd
        laagste_tijd = min(tijden)

        # Machines met dezelfde laagste tijd
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

        # Kleur van de huidige order
        kleur = order['Colour']

        # Setup time bij een kleurverandering
        if vorige_kleuren[machine_index] != None and kleur != vorige_kleuren[machine_index]:
            setup_gevonden = False

            for setup in di_setups:
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if setup_gevonden == False:
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

def improving_search(di_orders):
    # Beginvolgorde
    current = di_orders.copy()
    beste_volgorde = current.copy()

    # Eerste greedy planning
    volgordes, _ = greedy_schedule(beste_volgorde.copy(), di_machines, di_setups)
    gegevens     = calculate_results(volgordes, beste_volgorde, di_machines, di_setups)
    best_tot_tard = gegevens[0]
    best_penalty = gegevens[1]

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    verbetering = True

    while verbetering:
        verbetering = False

        # Beste resultaat van deze ronde
        ronde_beste_volgorde = beste_volgorde.copy()
        ronde_beste_penalty = best_penalty
        ronde_beste_tard = best_tot_tard

        # Alle mogelijke swaps controleren
        for i in range(len(beste_volgorde)):
            for j in range(i + 1, len(beste_volgorde)):
                # Nieuwe ordervolgorde maken
                new_current = beste_volgorde.copy()
                new_current[i], new_current[j] = new_current[j], new_current[i]

                # Greedy planning maken en doorrekenen
                volgordes, _ = greedy_schedule(new_current.copy(), di_machines, di_setups)
                gegevens = calculate_results(volgordes, new_current, di_machines, di_setups)
                current_tard = gegevens[0]
                current_penalty = gegevens[1]

                # Iedere geteste penalty opslaan
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

    return best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie

(best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie) = improving_search(di_orders)

# Beste planning opnieuw maken
beste_volgordes, _ = greedy_schedule(beste_volgorde.copy(), di_machines, di_setups)

# Alle gegevens van de beste planning berekenen
(total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order,penalty_per_order) = calculate_results(beste_volgordes, beste_volgorde, di_machines, di_setups)

resultaten_naar_excel(beste_volgorde, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order,'Results_greedy_improved.xlsx')

gantt_chart(beste_volgorde,di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty)