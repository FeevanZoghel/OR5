import pandas as pd
import numpy as np
import random
import math as m

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
di_machines.sort(key=lambda machine: machine['Speed'], reverse=True)

#####################DEFENITIE##################################

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

    # Productietijd
    tijd += order['Surface'] / machine['Speed']

    # Tardiness --> Alleen de vertragingen worden meegenomen
    tardiness       = max(0, tijd - order['Deadline'])
    penaltyorder    = order['Penalty']*tardiness

    return tijd, kleur, tardiness, penaltyorder

######################################################################


def greedy_schedule(di_orders, di_machines, di_setups):
    '''
    Maakt een planning met behulp van de greedy methode.

    De orders worden gesorteerd op deadline.
    Elke order wordt toegewezen aan de machine met de laagste huidige tijd.
    Bij gelijke tijden wordt de snelste machine gekozen.

    Return:
        Volgordes           : De volgorde van orders per machine
        Tijden              : De eindtijd per machine
        Tardiness           : De totale tardiness per machine
        Total_tardiness     : De totale tardiness van alle orders
        Penalty             : De totale penalty
        Penalty_per_order   : De penalty per order
        Tardiness_per_order : De tardiness per order
        Machines_per_order  : De gekozen machine per order
    '''

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


        # Machines met de laagste huidige eindtijd, die we de order laten uitvoeren
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
        tijden[machine_index], vorige_kleuren[machine_index], tard , penalty_order = plan_order(
            di_machines[machine_index],
            order,
            tijden[machine_index],
            vorige_kleuren[machine_index],
            di_setups
        )

        # Resultaten opslaan
        penalty  += penalty_order
        total_tardiness += tard

        volgordes[machine_index].append(order['Order'])
        tardiness[machine_index] += tard
        penalty_per_order.append(penalty_order)
        tardiness_per_order.append(tard)

    return (volgordes, tijden, tardiness, total_tardiness, penalty, penalty_per_order, tardiness_per_order, machines_per_order)

(volgordes, tijden, tardiness, total_tardiness, penalty, penalty_per_order, tardiness_per_order, machines_per_order) = greedy_schedule(di_orders, di_machines, di_setups)

df1_1 = []
df1_2 = []

for i in range(len(di_machines)):
    df1_1.append(i + 1)
    df1_2.append(' -> '.join(volgordes[i]))

    print(f'Machine {i+1}:')
    print('Order volgorde:', volgordes[i])


df0 = pd.DataFrame({
    'Machine_number': df1_1,
    'Order machine': df1_2
})


# Totale resultaten
print(f'De totale vertraging is {total_tardiness:.2f} tijdseenheden')
print(f'De totale penalty is {penalty:.2f}')


# Tabel
print(f'{'Order':<8} {'Tardiness':>10} {'Penalty/tijd':>14} {'Tot_penalty':>14} {'Machine':>10}')

order = [] 
for i in range(len(tardiness_per_order)):
    print(f'{di_orders[i]['Order']:<8} {tardiness_per_order[i]:>10.2f} {di_orders[i]['Penalty']:>14.2f} {penalty_per_order[i]:>14.2f} {machines_per_order[i]+1:>10.0f}') 

orders_lijst = []
tardiness_lijst = []
penalty_tijd_lijst = []
tot_penalty_lijst = []
machine_lijst = []

for i in range(len(tardiness_per_order)):

    orders_lijst.append(di_orders[i]['Order'])
    tardiness_lijst.append(round(tardiness_per_order[i],4))
    penalty_tijd_lijst.append(di_orders[i]['Penalty'])
    tot_penalty_lijst.append(round(penalty_per_order[i],4))
    machine_lijst.append(machines_per_order[i] + 1)

df1 = pd.DataFrame({
    'Order': orders_lijst,
    'tardiness': tardiness_lijst,
    'Penalty': penalty_tijd_lijst,
    'Tot_penalty': tot_penalty_lijst,   #penalty x tardiness
    'Machine': machine_lijst
})

with pd.ExcelWriter('Resuls.xlsx') as writer:
    df1.to_excel(writer, sheet_name = 'Gegevens', index = False)  
    df0.to_excel(writer, sheet_name = 'Volgorde_m', index = False)
