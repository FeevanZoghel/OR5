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
    Berekening voor de tardiness

    Return:
        Tijd        : productietijd
        Kleur       : De volgorde van kleuren in de orders
        Tardiness   : De tardiness
        Penaltyorder: Penaltyscore van de tardiness.
    '''

    kleur = order['Colour']
    setup_gevonden = False

    # Extra tijd voor kleur verandering
    if vorige_kleur != None and kleur != vorige_kleur:
        for setup in di_setups:
            if setup['From colour'] == vorige_kleur and setup['To colour'] == kleur:
                tijd += setup['Setup time']
                setup_gevonden = True
                break
        if setup_gevonden == False:
            raise ValueError(f'Geen setup gevonden van {vorige_kleur} naar {kleur}')

    #begintijd en productie tijd
    begintijd = tijd
    tijd += order['Surface'] / machine['Speed']
    eindtijd = tijd

    # Tardiness --> Alleen de vertragingen worden meegenomen
    tardiness       = max(0, tijd - order['Deadline'])
    penaltyorder    = order['Penalty']*tardiness

    return tijd, kleur, tardiness, penaltyorder, begintijd, eindtijd

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

    # Orders sorteren op deadline
    di_orders.sort(key=lambda order: order['Deadline'])

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

def improving_search(di_orders, iterations):
    # Beginvolgorde
    current = di_orders.copy()
    beste_volgorde = current.copy()

    # Eerste greedy uitvoeren
    gegevens = greedy_schedule(current, di_machines, di_setups)

    best_penalty = gegevens[4]
    best_tot_tard = gegevens[3]
    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    order_lijst = []

    for _ in range(iterations):
        # Swap vanaf beste oplossing
        current = random_swap(beste_volgorde)

        # Planning opnieuw maken met greedy
        gegevens = greedy_schedule(current, di_machines, di_setups)
        current_penalty = gegevens[4]

        # Penalty van ELKE geteste swap opslaan
        penalty_per_iteratie.append(current_penalty)

        # Alleen accepteren als deze beter is
        if current_penalty < best_penalty:
            best_penalty = current_penalty
            best_tot_tard = gegevens[3]
            beste_volgorde = current.copy()
            order_lijst.append([order['Order'] for order in beste_volgorde])

        # Beste penalty na iedere iteratie opslaan
        beste_penalty_per_iteratie.append(best_penalty)

    return (best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie)

(best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie) = improving_search(di_orders, 1000)

def plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie):
    plt.figure(figsize=(12, 6))

    plt.plot(penalty_per_iteratie, label='Penalty huidige swap')

    plt.plot(beste_penalty_per_iteratie, label='Beste penalty')

    plt.xlabel('Iteratie')
    plt.ylabel('Totale penalty')
    plt.title('Improving Search')

    plt.legend()
    plt.grid()

    plt.show()

plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie)

resultaten_naar_excel(di_orders,di_machines,di_setups, [order['Order'] for order in di_orders], total_tardiness, penalty, tardiness_per_order, penalty_per_order, machines_per_order, begintijden, eindtijden, 'Results_greedy_improved.xlsx')


gantt_chart(di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty)