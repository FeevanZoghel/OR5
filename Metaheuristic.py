from Functions import (dictionary, random_swap, gantt_chart_list, resultaten_naar_excel_list)

import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

di_orders_org = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups_org = dictionary(df_setups)

di_orders = di_orders_org.copy()
di_machines = di_machines_org.copy()
di_setups = di_setups_org.copy()

di_orders.sort(key=lambda job: job['Deadline'])

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    '''
    Berekent de totale tardiness en penalty van een gegeven ordervolgorde.
    Orders worden verdeeld over de machines op basis van de
    laagste huidige machinetijd.
    '''

    aantal_machines = len(di_machines)

    # Huidige tijd per machine
    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    sequence_numbers = [0] * aantal_machines

    # Resultaten
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

    # Orders opzoeken via Order-nummer
    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    # Door de volledige ordervolgorde lopen
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

        if (vorige_kleuren[machine_index] is not None
                and kleur != vorige_kleuren[machine_index]):

            setup_gevonden = False

            for setup in di_setups:
                if (setup['From colour'] == vorige_kleuren[machine_index]
                        and setup['To colour'] == kleur):

                    setup_tijd = setup['Setup time']
                    setup_gevonden = True
                    break

            if not setup_gevonden:
                raise ValueError(
                    f"Geen setup gevonden van "
                    f"{vorige_kleuren[machine_index]} naar {kleur}"
                )

        # Setup toevoegen aan de machinetijd
        tijden[machine_index] += setup_tijd

        # Productietijd
        productietijd = order['Surface'] / di_machines[machine_index]['Speed']
        begintijd = tijden[machine_index]

        tijden[machine_index] += productietijd

        # Eindtijd
        eindtijd = tijden[machine_index]

        # Volgnummer op de gekozen machine
        sequence_numbers[machine_index] += 1
        seqno = sequence_numbers[machine_index]

        # Tardiness
        tardiness = max(0, eindtijd - order['Deadline'])

        # Penalty van deze order
        penalty_order = tardiness * order['Penalty']

        # Totalen
        total_tardiness += tardiness
        penalty += penalty_order

        # Resultaten opslaan
        machines_per_order.append(machine_index)
        seqno_per_order.append(seqno)
        setup_per_order.append(setup_tijd)
        begintijden.append(begintijd)
        procestijden.append(productietijd)
        eindtijden.append(eindtijd)
        tardiness_per_order.append(tardiness)
        penalty_per_order.append(penalty_order)

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order


# begin SA

def SA(df_orders, t_max, cooling_factor, cooling_it, temp):
    
    current = df_orders['Order'].tolist()

    random.shuffle(current)
    current_tard, current_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_tardiness = current_tard
    best_penalty   = current_penalty

    for i in range(t_max):

        new_current = random_swap(current)
        new_tard, new_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
        verschil    = current_penalty-new_penalty
        
        kans = m.exp(verschil / temp)

        if verschil > 0:
            current              = new_current.copy()
            current_penalty         = new_penalty
        else:
            getal = np.random.choice([0, 1], p=[1-kans, kans])

            # Slechtere oplossing toch accepteren
            if getal == 1:
                current = new_current.copy()
                current_penalty = new_penalty

        # Is current de beste oplossing van alles?
        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty

        # Temperatuur na 1000 iteraties verlagen
        if (i + 1) % cooling_it == 0:
            temp = temp * cooling_factor
    return(best, best_penalty)


t_max = 10000
cooling_factor =0.99
cooling_it = 1000
temp = 1000

oefen, oefen_pen = SA(df_orders, t_max, cooling_factor, cooling_it,temp)

tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(oefen, di_orders, di_machines, di_setups)

print(f'de beste lijst is {oefen}, met een totaletardiness van {tard} en {pen} aan penalty' )

resultaten_naar_excel_list(oefen, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden,tardiness_per_order, penalty_per_order, 'Results_SA.xlsx')

gantt_chart_list(oefen, di_orders, di_machines, machines_per_order,setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order,
pen)
