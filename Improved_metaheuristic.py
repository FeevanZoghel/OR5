
from Functions import dictionary, random_swap, gantt_chart_list, resultaten_naar_excel_list
import pandas as pd
import random
import math as m
import matplotlib.pyplot as plt
import time

# Instellingen
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
di_orders.sort(key=lambda job: job['Deadline'])

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    '''Berekent de tardiness en penalty van een gegeven ordervolgorde.'''
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
                    tijden[machine_index] += setup_tijd
                    setup_gevonden = True
                    break
            if not setup_gevonden:
                raise ValueError(f"Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}")

        productietijd = order['Surface'] / di_machines[machine_index]['Speed']
        begintijd = tijden[machine_index]
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
    current_history = []
    best_history = []
    temperature_history = []

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

        current_history.append(current_penalty)
        best_history.append(best_penalty)
        temperature_history.append(temp)

        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor

        if (i + 1) % 1000 == 0:
            print(f"\rIteration: {i + 1:6d}  Temperature: {temp:10.4f}  Current penalty: {current_penalty:10.2f}  Best penalty: {best_penalty:10.2f}", end="", flush=True)

    print()
    return best, best_penalty, current_history, best_history, temperature_history

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

def plot_sa_progress(current_history, best_history, temperature_history):
    iterations = range(1, len(current_history) + 1)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Penalty op linker y-as
    ax1.plot(iterations, current_history, label='Current solution', color='tab:blue', linewidth=0.8, alpha=0.7)
    ax1.plot(iterations, best_history, label='Best solution', color='tab:orange', linewidth=1.8)
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Total penalty')
    ax1.grid(alpha=0.3)

    # Temperatuur op rechter y-as
    ax2 = ax1.twinx()
    ax2.plot(iterations, temperature_history, label='Temperature', color='tab:red', linewidth=1.5)
    ax2.set_ylabel('Temperature', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Legenda combineren
    lijnen1, labels1 = ax1.get_legend_handles_labels()
    lijnen2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lijnen1 + lijnen2, labels1 + labels2, loc='upper right')

    plt.title('Simulated Annealing objective values and temperature')
    plt.tight_layout()
    plt.show()

# Simulated Annealing uitvoeren
random.seed(1)
start_sa = time.perf_counter()
sa_volgorde, sa_penalty, current_history, best_history, temperature_history = SA(df_orders, t_max, cooling_factor, cooling_it, temp)
rekentijd_sa = time.perf_counter() - start_sa

# Improving Search uitvoeren op de beste SA-volgorde
start_improving = time.perf_counter()
best_tot_tard, best_penalty, beste_volgorde, dis_penalties, dis_beste_penalties = meta_improving_search(sa_volgorde)
rekentijd_improving = time.perf_counter() - start_improving

# Resultaten weergeven
print(f'Penalty na Simulated Annealing: {sa_penalty:.2f}')
print(f'Penalty na Improving Search: {best_penalty:.2f}')
print(f'Verbetering door Improving Search: {sa_penalty - best_penalty:.2f}')
print(f'Rekentijd SA: {rekentijd_sa:.2f} seconden')
print(f'Rekentijd Improving Search: {rekentijd_improving:.2f} seconden')
print(f'Totale rekentijd: {rekentijd_sa + rekentijd_improving:.2f} seconden')

# Grafiek van Simulated Annealing
plot_sa_progress(current_history, best_history, temperature_history)

# Definitieve planning na Improving Search
tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(beste_volgorde, di_orders, di_machines, di_setups)

print(f'De beste lijst is {beste_volgorde}, met een totale tardiness van {tard:.2f} en {pen:.2f} aan penalty')

# Definitieve planning exporteren naar Excel
resultaten_naar_excel_list(beste_volgorde, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, 'Results_SA_improved.xlsx')

# Gantt-chart van de definitieve planning
gantt_chart_list(beste_volgorde, di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, pen)
