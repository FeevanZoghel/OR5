import pandas as pd
import numpy as np
import random
import math as m

random.seed(42)

df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name = None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

def dictionary(df):

    jobs = []

    for i in range(len(df)):
        job = {}

        for column in df.columns:
            job[column] = df[column][i]

        jobs.append(job)

    return jobs

di_orders = dictionary(df_orders)
di_machines = dictionary(df_machines)
di_setups = dictionary(df_setups)


di_orders.sort(key=lambda job: job['Deadline'])
di_machines.sort(key=lambda machine: machine['Speed'], reverse=True)

#####################DEFENITIE##################################

def plan_order(machine, order, tijd, vorige_kleur):

    kleur = order['Colour']

    # Extra tijd voor kleur verandering
    if vorige_kleur != None and kleur != vorige_kleur:
        for setup in di_setups:
            if setup['From colour'] == vorige_kleur and setup['To colour'] == kleur:
                tijd += setup['Setup time']
                break

    # Productietijd
    tijd += order['Surface'] / machine['Speed']

    # Tardiness --> Alleen de vertragingen worden meegenomen
    tardiness       = max(0, tijd - order['Deadline'])
    penaltyorder    = order['Penalty']*tardiness

    return tijd, kleur, tardiness, penaltyorder

######################################################################

aantal_machines     = len(di_machines)
tijden              = [0]* aantal_machines
tardiness           = [0]*aantal_machines
penalty_per_order   = []
tardiness_per_order = []
machines_per_order  = []
vorige_kleuren      = [None]*aantal_machines
volgordes           = [[] for _ in range(aantal_machines)]
total_tardiness     = 0
penalty             = 0

di_orders.sort(key=lambda order: order['Deadline'])

for order in di_orders:

    # Machine met laagste huidige tijd
    laagste_tijd = min(tijden)


    # Machines die de order kunnen uitvoeren

    mogelijke_machines = []

    for i in range(len(di_machines)):
    
        if tijden[i] == laagste_tijd:
            mogelijke_machines.append(i)

    # Bij gelijke tijd: snelste machine
    machine_index = mogelijke_machines[0]

    for i in mogelijke_machines:
        if di_machines[i]['Speed'] > di_machines[machine_index]['Speed']:
            machine_index = i
    machines_per_order.append(int(machine_index))

    # Order op gekozen machine plannen
    tijden[machine_index], vorige_kleuren[machine_index], tard , penaltyorder = plan_order(
        di_machines[machine_index],
        order,
        tijden[machine_index],
        vorige_kleuren[machine_index]
    )

    # Resultaten opslaan
    penalty  += penaltyorder
    volgordes[machine_index].append(order['Order'])
    tardiness[machine_index] += tard
    tot_penalty_order = penaltyorder*tard
    penalty_per_order.append(tot_penalty_order)
    tardiness_per_order.append(tard)


for i in range(len(di_machines)):
    print(f'Machine {i+1}:')
    print('Order volgorde:', volgordes[i])
for i in range(len(di_machines)):
    total_tardiness += tardiness[i]

print(f'De totale vertraging is {total_tardiness:.2f} tijdseenheden')
print(f'De totale penalty is {penalty:.2f}')
print(f'{'Order':<8} {'Tardiness':>10} {'Penalty/tijd':>14} {'Tot_penalty':>14} {'Machine':>10}')
for i in range(len(tardiness_per_order)):
    print(f'{di_orders[i]['Order']:<8} {tardiness_per_order[i]:>10.2f} {di_orders[i]['Penalty']:>14.2f} {penalty_per_order[i]:>14.2f} {machines_per_order[i]:>10.0f}') 
