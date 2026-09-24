import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

random.seed(42)

df = pd.read_excel('PaintShop_Test.xlsx', sheet_name = None)

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

    #begintijd van de order
    begintijd = tijd

    # Productietijd
    tijd += order['Surface'] / machine['Speed']

    eindtijd = tijd

    # Tardiness --> Alleen de vertragingen worden meegenomen
    tardiness       = max(0, tijd - order['Deadline'])
    penaltyorder    = order['Penalty']*tardiness

    return tijd, kleur, tardiness, penaltyorder, begintijd, eindtijd

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

    begintijden         = []
    eindtijden          = []
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
        tijden[machine_index], vorige_kleuren[machine_index], tard , penalty_order, begintijd, eindtijd = plan_order(
            di_machines[machine_index],
            order,
            tijden[machine_index],
            vorige_kleuren[machine_index],
            di_setups
        )

        begintijden.append(begintijd)
        eindtijden.append(eindtijd) 

        # Resultaten opslaan
        penalty  += penalty_order
        total_tardiness += tard

        volgordes[machine_index].append(order['Order'])
        tardiness[machine_index] += tard
        penalty_per_order.append(penalty_order)
        tardiness_per_order.append(tard)

    return (volgordes, tijden, tardiness, total_tardiness, penalty, penalty_per_order, tardiness_per_order, machines_per_order, begintijden, eindtijden)

(volgordes, 
 tijden, 
 tardiness, 
 total_tardiness, 
 penalty, 
 penalty_per_order, 
 tardiness_per_order, 
 machines_per_order, 
 begintijden, eindtijden) = greedy_schedule(di_orders, di_machines, di_setups)

current_order = volgordes
best_order = volgordes












def resultaten_naar_excel(di_orders, di_machines, volgordes, total_tardiness, penalty, tardiness_per_order, penalty_per_order, machines_per_order, bestandsnaam='Results.xlsx'):
    '''
    Zet de resultaten van de planning in een Excel-bestand.

    Het Excel-bestand bevat drie tabbladen:
        1. Resultaten orders
        2. Volgorde machines
        3. Totale resultaten
    '''

    #Volgorde per machine
    machine_nummers = []
    order_volgorde = []

    for i in range(len(di_machines)):
        machine_nummers.append(i + 1)
        order_volgorde.append(' -> '.join(volgordes[i]))

    df_MachineOrder = pd.DataFrame({
        'Machine_number': machine_nummers,
        'Order machine': order_volgorde
    })

    #Totale resultaten
    df_totalen = pd.DataFrame({
        'Resultaat': [
            'Totale vertraging',
            'Totale penalty'
        ],
        'Waarde': [
            round(total_tardiness, 4),
            round(penalty,4)
        ]
    })

    #Resultaten per order
    orders_lijst = []
    tardiness_lijst = []
    penalty_tijd_lijst = []
    tot_penalty_lijst = []
    machine_lijst = []

    for i in range(len(tardiness_per_order)):

        orders_lijst.append(di_orders[i]['Order'])
        tardiness_lijst.append(round(tardiness_per_order[i],2))
        penalty_tijd_lijst.append(di_orders[i]['Penalty'])
        tot_penalty_lijst.append(round(penalty_per_order[i],2))
        machine_lijst.append(machines_per_order[i] + 1)

    df_resultaten = pd.DataFrame({
        'Order': orders_lijst,
        'tardiness': tardiness_lijst,
        'Penalty': penalty_tijd_lijst,
        'Tot_penalty': tot_penalty_lijst, #pen x tard
        'Machine': machine_lijst,
        'begintijd': [round(tijd, 2) for tijd in begintijden],
        'eindtijd': [round(tijd, 2) for tijd in eindtijden]
    })


    #Excel bestan maken
    with pd.ExcelWriter('Resuls.xlsx') as writer:
        df_resultaten.to_excel(writer, sheet_name = 'Resultaten orders', index = False)  
        df_MachineOrder.to_excel(writer, sheet_name = 'Volgorde machines', index = False)
        df_totalen.to_excel(writer, sheet_name = 'Totale resulaten', index = False)

resultaten_naar_excel(di_orders, di_machines, volgordes, total_tardiness, penalty, tardiness_per_order, penalty_per_order, machines_per_order)

def gantt_chart(di_orders, di_machines, machines_per_order, begintijden, eindtijden):
    '''
    Maakt een Gantt-chart van de planning.

    Elke horizontale rij stelt een machine voor.
    Elke balk stelt een order voor van begintijd tot eindtijd.
    '''

    fig, ax = plt.subplots(figsize=(13, 7))

    kleur_dict = {
        'Red': 'red',
        'Blue': 'blue',
        'Green': 'green',
        'Yellow': 'yellow',
        'Orange': 'orange',
        'Purple': 'purple',
        'Pink': 'pink',
        'Black': 'black',
        'White': 'white',
        'Grey': 'grey'
    }

    for i in range(len(di_orders)):

        machine = machines_per_order[i]
        begintijd = begintijden[i]
        eindtijd = eindtijden[i]

        duur = eindtijd - begintijd

        kleur_order = di_orders[i]['Colour']

        # Balk tekenen
        ax.barh(machine, duur, left=begintijd, height = 0.6,color = kleur_dict[kleur_order], edgecolor = 'black')

        # Ordernummer in de balk zetten
        ax.text(begintijd + duur / 2, machine, str(di_orders[i]['Order']), ha='center', va='center', fontsize = 9)

    # Machine-namen op de y-as
    ax.set_yticks(range(len(di_machines)))
    ax.set_yticklabels([f'Machine {i + 1}' for i in range(len(di_machines))])

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    ax.set_xlabel('Tijd')
    ax.set_ylabel('Machine')
    ax.set_title('Gantt-chart planning')

    plt.tight_layout()
    plt.show()

gantt_chart(di_orders, di_machines, machines_per_order, begintijden, eindtijden)