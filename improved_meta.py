
from Functions import dictionary, random_swap, plot_penalty, gantt_chart_list, resultaten_naar_excel_list
import pandas as pd
import random
import math as m

t_max = 1000
cooling_factor = 0.99
cooling_it = 1000
temp = 1000

# Data inladen
df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)
df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

di_orders = dictionary(df_orders)
di_machines = dictionary(df_machines)
di_setups = dictionary(df_setups)
di_orders.sort(key=lambda job: job['Deadline'])

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
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
    orders = {order['Order']: order for order in di_orders}

    for order_nummer in volgorde:
        order = orders[order_nummer]
        kleur = order['Colour']
        laagste_tijd = min(tijden)
        mogelijke_machines = [i for i in range(aantal_machines) if tijden[i] == laagste_tijd]
        machine_index = max(mogelijke_machines, key=lambda i: di_machines[i]['Speed'])
        setup_tijd = 0

        if vorige_kleuren[machine_index] is not None and kleur != vorige_kleuren[machine_index]:
            setup_gevonden = False
            for setup in di_setups:
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    setup_tijd = setup['Setup time']
                    setup_gevonden = True
                    break
            if not setup_gevonden:
                raise ValueError(f"Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}")

        tijden[machine_index] += setup_tijd
        begintijd = tijden[machine_index]
        productietijd = order['Surface'] / di_machines[machine_index]['Speed']
        tijden[machine_index] += productietijd
        eindtijd = tijden[machine_index]
        sequence_numbers[machine_index] += 1
        tardiness = max(0, eindtijd - order['Deadline'])
        penalty_order = tardiness * order['Penalty']

        machines_per_order.append(machine_index)
        seqno_per_order.append(sequence_numbers[machine_index])
        setup_per_order.append(setup_tijd)
        begintijden.append(begintijd)
        procestijden.append(productietijd)
        eindtijden.append(eindtijd)
        tardiness_per_order.append(tardiness)
        penalty_per_order.append(penalty_order)
        total_tardiness += tardiness
        penalty += penalty_order
        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order

def SA(df_orders, t_max, cooling_factor, cooling_it, temp):
    current = df_orders['Order'].tolist()
    random.shuffle(current)
    current_penalty = calculate_tard_pen(current, di_orders, di_machines, di_setups)[1]
    best = current.copy()
    best_penalty = current_penalty

    for i in range(t_max):
        new_current = random_swap(current)
        new_penalty = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)[1]
        verschil = current_penalty - new_penalty

        if verschil > 0 or random.random() < m.exp(verschil / temp):
            current = new_current.copy()
            current_penalty = new_penalty

        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty

        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor

    return best, best_penalty

def meta_improving_search(sa_volgorde):
    beste_volgorde = sa_volgorde.copy()
    best_tot_tard, best_penalty = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)[:2]
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
                current_tard, current_penalty = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)[:2]
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

# Stap 1: Simulated Annealing
sa_volgorde, sa_penalty = SA(df_orders, t_max, cooling_factor, cooling_it, temp)
print(f'Penalty na SA: {sa_penalty:.2f}')

# Stap 2: Improving Search op de SA-oplossing
best_tot_tard, best_penalty, beste_volgorde, penalty_per_iteratie, beste_penalty_per_iteratie = meta_improving_search(sa_volgorde)
print(f'Penalty na Improving Search: {best_penalty:.2f}')

# Resultaten
plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie)
tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)
print(f'De beste lijst is {beste_volgorde}, met een totale tardiness van {tard:.2f} en {pen:.2f} aan penalty')

resultaten_naar_excel_list(beste_volgorde, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, 'Results_SA_improved.xlsx')
gantt_chart_list(beste_volgorde, di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, pen)
