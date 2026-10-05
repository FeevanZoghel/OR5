from Functions import (dictionary, random_swap, plot_penalty, gantt_chart_list, resultaten_naar_excel_list)

import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

# Data inladen
df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

# Dataframes omzetten naar dictionaries
di_orders_org = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups_org = dictionary(df_setups)

di_orders = di_orders_org.copy()
di_machines = di_machines_org.copy()
di_setups = di_setups_org.copy()

# Orders sorteren op deadline
di_orders.sort(key=lambda job: job['Deadline'])


def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    '''
    Berekent de tardiness en penalty van een gegeven ordervolgorde.
    Orders worden verdeeld over de machines op basis van de
    laagste huidige machinetijd.
    '''

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    sequence_numbers = [0] * aantal_machines

    total_tardiness = 0
    penalty = 0

    machines_per_order = []
    seqno_per_order = []
    setup_per_order = []
    begintijden = []
    procestijden = []
    eindtijden = []
    tardiness_per_order = []
    penalty_per_order = []

    orders = {}
    for order in di_orders:
        orders[order['Order']] = order

    for order_nummer in volgorde:
        order = orders[order_nummer]
        kleur = order['Colour']

        # Machine met de laagste huidige tijd zoeken
        laagste_tijd = min(tijden)
        mogelijke_machines = []

        for i in range(aantal_machines):
            if tijden[i] == laagste_tijd:
                mogelijke_machines.append(i)

        # Bij gelijke tijd: snelste machine
        machine_index = mogelijke_machines[0]
        for i in mogelijke_machines:
            if di_machines[i]['Speed'] > di_machines[machine_index]['Speed']:
                machine_index = i

        # Setup time bij een kleurverandering
        setup_tijd = 0

        if vorige_kleuren[machine_index] is not None and kleur != vorige_kleuren[machine_index]:
            setup_gevonden = False

            for setup in di_setups:
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    setup_tijd = setup['Setup time']
                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if not setup_gevonden:
                raise ValueError(f'Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}')

        # Productietijd
        productietijd = order['Surface'] / di_machines[machine_index]['Speed']
        begintijd = tijden[machine_index]
        tijden[machine_index] += productietijd
        eindtijd = tijden[machine_index]

        # Sequence number
        sequence_numbers[machine_index] += 1
        seqno = sequence_numbers[machine_index]

        machines_per_order.append(machine_index)
        seqno_per_order.append(seqno)
        setup_per_order.append(setup_tijd)
        begintijden.append(begintijd)
        procestijden.append(productietijd)
        eindtijden.append(eindtijd)

        # Tardiness en penalty
        tardiness = max(0, eindtijd - order['Deadline'])
        penalty_order = tardiness * order['Penalty']

        tardiness_per_order.append(tardiness)
        penalty_per_order.append(penalty_order)

        total_tardiness += tardiness
        penalty += penalty_order

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return (total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order)

# Begin Improving Search

def SA(df_orders, t_max, cooling_factor, cooling_it, temp):
    current = df_orders['Order'].tolist()
    random.shuffle(current)

    _, current_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_penalty = current_penalty

    for i in range(t_max):
        new_current = random_swap(current)
        _, new_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)

        verschil = current_penalty - new_penalty

        if verschil > 0:
            current = new_current.copy()
            current_penalty = new_penalty
        else:
            kans = m.exp(verschil / temp)
            getal = random.choices([0, 1], weights=[1 - kans, kans])[0]

            if getal == 1:
                current = new_current.copy()
                current_penalty = new_penalty

        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty

        if (i + 1) % cooling_it == 0:
            temp = temp * cooling_factor

    return best, best_penalty


t_max = 1000000
cooling_factor = 0.99
cooling_it = 1000
temp = 1000


def meta_improving_search(df_orders, iterations):
    beste_volgorde, best_penalty = SA(df_orders, t_max, cooling_factor, cooling_it, temp)

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []

    for _ in range(iterations):
        current = random_swap(beste_volgorde)

        _, current_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

        penalty_per_iteratie.append(current_penalty)

        if current_penalty < best_penalty:
            best_penalty = current_penalty
            beste_volgorde = current.copy()

        beste_penalty_per_iteratie.append(best_penalty)

    return best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie


best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie = meta_improving_search(df_orders, 1000)

plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie)

tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)

print(f'De beste lijst is {beste_volgorde}, met een totale tardiness van {tard:.2f} en {pen:.2f} aan penalty')

resultaten_naar_excel_list(beste_volgorde, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, 'Results_SA_improved.xlsx')

gantt_chart_list(beste_volgorde, di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, pen)