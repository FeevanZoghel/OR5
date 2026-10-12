from Functions import (dictionary, random_swap, plot_penalty, gantt_chart_list, resultaten_naar_excel_list)

import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

t_max = 500000
cooling_factor = 0.99
cooling_it = 1000
temp = 1000

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
    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    temperatuur_per_iteratie = []

    for i in range(t_max):
        new_current = random_swap(current)
        _, new_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
        penalty_per_iteratie.append(new_penalty)
        temperatuur_per_iteratie.append(temp)
        verschil = current_penalty - new_penalty

        if verschil > 0:
            current = new_current.copy()
            current_penalty = new_penalty
        else:
            kans = m.exp(verschil / temp)
            if random.random() < kans:
                current = new_current.copy()
                current_penalty = new_penalty

        penalty_per_iteratie.append(current_penalty)

        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty


        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor

    return best, best_penalty, penalty_per_iteratie, penalty_per_iteratie, temperatuur_per_iteratie


def meta_improving_search(sa_volgorde):
    beste_volgorde = sa_volgorde.copy()

    gegevens = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)
    best_tot_tard = gegevens[0]
    best_penalty = gegevens[1]

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    verbetering = True

    while verbetering:
        verbetering = False

        ronde_beste_volgorde = beste_volgorde.copy()
        ronde_beste_penalty = best_penalty
        ronde_beste_tard = best_tot_tard

        for i in range(len(beste_volgorde)):
            for j in range(i + 1, len(beste_volgorde)):
                new_current = beste_volgorde.copy()
                new_current[i], new_current[j] = new_current[j], new_current[i]

                gegevens = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
                current_tard = gegevens[0]
                current_penalty = gegevens[1]

                penalty_per_iteratie.append(current_penalty)

                if current_penalty < ronde_beste_penalty:
                    ronde_beste_penalty = current_penalty
                    ronde_beste_tard = current_tard
                    ronde_beste_volgorde = new_current.copy()
                    verbetering = True

                beste_penalty_per_iteratie.append(ronde_beste_penalty)

        if verbetering:
            best_penalty = ronde_beste_penalty
            best_tot_tard = ronde_beste_tard
            beste_volgorde = ronde_beste_volgorde.copy()

    return best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie



# Simulated Annealing uitvoeren
sa_volgorde, sa_penalty, sa_penalties, sa_beste_penalties, sa_temperaturen = SA(df_orders, t_max, cooling_factor, cooling_it, temp)

# Improving Search uitvoeren, maar niet in de grafiek tonen
best_tot_tard, best_penalty, beste_volgorde, dis_penalties, dis_beste_penalties = meta_improving_search(sa_volgorde)

# Grafiek van alleen Simulated Annealing
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(sa_penalties, color='tab:blue', alpha=0.5, linewidth=0.8, label='Geteste penalty')
ax1.plot(sa_beste_penalties, color='tab:orange', linewidth=2, label='Beste penalty')
ax1.set_xlabel('Iteratie')
ax1.set_ylabel('Penalty')
ax1.grid(True, alpha=0.3)

# Temperatuur op de rechter y-as
ax2 = ax1.twinx()
ax2.plot(sa_temperaturen, color='tab:red', linewidth=1.5, label='Temperatuur')
ax2.set_ylabel('Temperatuur', color='tab:red')
ax2.tick_params(axis='y', labelcolor='tab:red')

# Legenda's combineren
lijnen1, labels1 = ax1.get_legend_handles_labels()
lijnen2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lijnen1 + lijnen2, labels1 + labels2, loc='upper right')

plt.title('Simulated Annealing: penalty en temperatuur')
plt.tight_layout()
plt.show()


tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)

print(f'De beste lijst is {beste_volgorde}, met een totale tardiness van {tard:.2f} en {pen:.2f} aan penalty')

resultaten_naar_excel_list(beste_volgorde, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, 'Results_SA_improved.xlsx')

gantt_chart_list(beste_volgorde, di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, pen)
