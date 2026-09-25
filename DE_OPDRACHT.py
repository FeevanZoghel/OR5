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
di_machines.sort(key=lambda machine: machine['Speed'], reverse=True)



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
                if (setup['From colour'] == vorige_kleuren[machine_index]
                        and setup['To colour'] == kleur):

                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if setup_gevonden == False:
                raise ValueError(
                    f"Geen setup gevonden van "
                    f"{vorige_kleuren[machine_index]} naar {kleur}"
                )

        # Productietijd
        tijden[machine_index] += (
            order['Surface'] / di_machines[machine_index]['Speed']
        )

        # Laatste kleur van de machine opslaan
        vorige_kleuren[machine_index] = kleur

        # Order toevoegen aan de volgorde van de machine
        volgordes[machine_index].append(order['Order'])

    return volgordes, machines_per_order


def calculate_tardiness(volgordes, di_orders, di_machines, di_setups):
    '''
    Berekent de tardiness van een gegeven volgorde.

    Return:
        total_tardiness     : Totale tardiness
        tardiness_per_order : Tardiness per order
        begintijden         : Begintijd per order
        eindtijden          : Eindtijd per order
    '''

    aantal_machines = len(di_machines)

    # Huidige tijd per machine
    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    total_tardiness = 0
    tardiness_per_order = []
    begintijden = []
    eindtijden = []

    # Orders opzoeken via Order-nummer
    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    # Door iedere machine lopen
    for machine_index in range(aantal_machines):

        # Door de gegeven volgorde van de machine lopen
        for order_nummer in volgordes[machine_index]:

            order = orders[order_nummer]
            kleur = order['Colour']

            # Setup time bij een kleurverandering
            if vorige_kleuren[machine_index] != None and kleur != vorige_kleuren[machine_index]:

                setup_gevonden = False

                for setup in di_setups:
                    if (setup['From colour'] == vorige_kleuren[machine_index]
                            and setup['To colour'] == kleur):

                        tijden[machine_index] += setup['Setup time']
                        setup_gevonden = True
                        break

                # geeft een foutmelding als er niet tussen bepaalde kleuren kan worden geswapt
                if setup_gevonden == False:
                    raise ValueError(
                        f"Geen setup gevonden van "
                        f"{vorige_kleuren[machine_index]} naar {kleur}"
                    )

            # Begintijd
            begintijd = tijden[machine_index]

            # Productietijd
            tijden[machine_index] += (
                order['Surface'] / di_machines[machine_index]['Speed']
            )

            # Eindtijd
            eindtijd = tijden[machine_index]

            # Tardiness
            tardiness = max(0, eindtijd - order['Deadline'])

            # Resultaten opslaan
            total_tardiness += tardiness
            tardiness_per_order.append(tardiness)
            begintijden.append(begintijd)
            eindtijden.append(eindtijd)

            # Kleur opslaan
            vorige_kleuren[machine_index] = kleur

    return total_tardiness, tardiness_per_order, begintijden, eindtijden

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

    #----------------------------------------

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

    #----------------------------------------

    #Resultaten per order
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

    df_resultaten = pd.DataFrame({
        'Order': orders_lijst,
        'tardiness': tardiness_lijst,
        'Penalty': penalty_tijd_lijst,
        'Tot_penalty': tot_penalty_lijst,   #penalty x tardiness
        'Machine': machine_lijst,
        'begintijd': begintijden,
        'eindtijd': eindtijden
    })

    #----------------------------------------

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

    fig, ax = plt.subplots(figsize=(16, 7))

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