import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt



random.seed(42)

df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']


def dictionary(df):
    '''
    Zet een dataframe om naar een lijst van dictionaries.
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


def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    '''
    Berekent de tardiness en penalty van een gegeven ordervolgorde.
    Orders worden verdeeld over de machines op basis van de
    laagste huidige machinetijd.

    Return:
        total_tardiness    : Totale tardiness
        penalty            : Totale penalty
        machines_per_order : Machine per order
        begintijden        : Begintijd per order
        eindtijden         : Eindtijd per order
        tard_per_order     : Tardiness per order
        penalty_per_order  : Penalty per order
    '''

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines


    # Totale tardiness
    total_tardiness = 0
    penalty = 0
    machines_per_order = []
    begintijden = []
    eindtijden = []
    penalty_per_order = []
    tard_per_order = []

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
        if (vorige_kleuren[machine_index] is not None
                and kleur != vorige_kleuren[machine_index]):

            setup_gevonden = False

            for setup in di_setups:

                if (setup['From colour'] == vorige_kleuren[machine_index]
                        and setup['To colour'] == kleur):

                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if not setup_gevonden:
                raise ValueError(
                    f"Geen setup gevonden van "
                    f"{vorige_kleuren[machine_index]} naar {kleur}"
                )

        # Productietijd
        productietijd = (order['Surface'] / di_machines[machine_index]['Speed'])
        begintijd     = tijden[machine_index]

        tijden[machine_index] += productietijd

        # Eindtijd
        eindtijd = tijden[machine_index]
        machines_per_order.append(machine_index)
        begintijden.append(begintijd)
        eindtijden.append(eindtijd)

        # Tardiness
        tardiness = max(0, eindtijd - order['Deadline'])

        # Penalty van deze specifieke order
        penalty_order = tardiness * order['Penalty']

        # Per order opslaan
        tard_per_order.append(tardiness)
        penalty_per_order.append(penalty_order)

        # Totalen
        total_tardiness += tardiness
        penalty += penalty_order

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty, machines_per_order, begintijden, eindtijden, tard_per_order, penalty_per_order

# begin SA

def swap(volgorde, i, j):

    nieuwe_volgorde = volgorde.copy()
    nieuwe_volgorde[i], nieuwe_volgorde[j] = (
        nieuwe_volgorde[j],
        nieuwe_volgorde[i]
    )

    return nieuwe_volgorde


def random_swap(current):

    a = random.randint(0, len(current) - 1)
    b = random.randint(0, len(current) - 1)

    while a == b:
        b = random.randint(0, len(current) - 1)
    new_current = swap(current, a, b)

    return new_current



def SA(df_orders, t_max, cooling_factor, cooling_it, temp):
    
    current = df_orders['Order'].tolist()

    random.shuffle(current)
    current_tard, current_penalty, _,_, _, _, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_tardiness = current_tard
    best_penalty   = current_penalty

    for i in range(t_max):

        new_current = random_swap(current)
        new_tard, new_penalty ,_,_,_ ,_ ,_   = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
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

        # Is current de beste oplossing die we ooit hebben gezien?
        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty

        # Temperatuur na 1000 iteraties verlagen
        if (i + 1) % cooling_it == 0:
            temp = temp * cooling_factor

    # Tardiness van de beste gevonden volgorde opnieuw berekenen
    best_tardiness, _, _, _, _, _, _ = calculate_tard_pen(
        best,
        di_orders,
        di_machines,
        di_setups
    )
    return(best, best_penalty, best_tardiness)


t_max = 1000000
cooling_factor =0.99
cooling_it = 1000
temp = 1000

oefen, oefen_pen, oefen_tard = SA(df_orders, t_max, cooling_factor, cooling_it, temp)

def meta_improving_search(df_orders, iterations):

    # Beginvolgorde als lijst met ordernummers
    current = df_orders['Order'].tolist()

    # SA gegevens
    t_max = 1000000
    cooling_factor = 0.99
    cooling_it = 1000
    temp = 1000

    # Eerst SA uitvoeren
    beste_volgorde, best_penalty, best_tot_tard = SA(
        df_orders,
        t_max,
        cooling_factor,
        cooling_it,
        temp
    )

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []
    order_lijst = []

    for _ in range(iterations):

        # Swap uitvoeren op de beste gevonden volgorde
        current = random_swap(beste_volgorde)

        # Planning van deze nieuwe volgorde berekenen
        (
            current_tard,
            current_penalty,
            _,
            _,
            _,
            _,
            _
        ) = calculate_tard_pen(
            current,
            di_orders,
            di_machines,
            di_setups
        )

        # Penalty van deze swap bewaren
        penalty_per_iteratie.append(current_penalty)

        # Alleen accepteren als de nieuwe volgorde beter is
        if current_penalty < best_penalty:

            best_penalty = current_penalty
            best_tot_tard = current_tard
            beste_volgorde = current.copy()

            order_lijst.append(beste_volgorde.copy())

        # Beste penalty tot nu toe bewaren
        beste_penalty_per_iteratie.append(best_penalty)

    return (
        best_tot_tard,
        best_penalty,
        beste_volgorde,
        penalty_per_iteratie,
        beste_penalty_per_iteratie
    )
(
    best_tardiness,
    best_penalty,
    beste_volgorde,
    penalty_per_iteratie,
    beste_penalty_per_iteratie
) = meta_improving_search(df_orders, 1000)

def plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie):

    plt.figure(figsize=(12, 6))

    plt.plot(
        penalty_per_iteratie,
        label='Penalty huidige swap'
    )

    plt.plot(
        beste_penalty_per_iteratie,
        label='Beste penalty'
    )

    plt.xlabel('Iteratie')
    plt.ylabel('Totale penalty')
    plt.title('Improving Search')

    plt.legend()
    plt.grid()

    plt.show()

plot_penalty(
    penalty_per_iteratie,
    beste_penalty_per_iteratie
)

tard, pen, machines_per_order, begintijden, eindtijden, tard_per_order, penalty_per_order = calculate_tard_pen(
    beste_volgorde,
    di_orders,
    di_machines,
    di_setups
)

print(
    f'De beste lijst is {beste_volgorde}, '
    f'met een totale tardiness van {tard} '
    f'en {pen} aan penalty'
)

def resultaten_naar_excel_list(
    di_orders,
    di_machines,
    volgordes,
    total_tardiness,
    penalty,
    tardiness_per_order,
    penalty_per_order,
    machines_per_order,
    bestandsnaam='Results.xlsx'
):
    '''
    Zet de resultaten van de planning in een Excel-bestand.

    Het Excel-bestand bevat drie tabbladen:
        1. Resultaten orders
        2. Volgorde machines
        3. Totale resultaten
    '''

    # Volgorde per machine
    machine_nummers = []
    order_volgorde = []

    for machine in range(len(di_machines)):

        orders_machine = []

        for i in range(len(volgordes)):

            if machines_per_order[i] == machine:
                orders_machine.append(volgordes[i])

        machine_nummers.append(machine + 1)
        order_volgorde.append(' -> '.join(orders_machine))

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

    orders_dict = {}

    for order in di_orders:
        orders_dict[order['Order']] = order

    for i in range(len(tardiness_per_order)):

        order_nummer = volgordes[i]
        order = orders_dict[order_nummer]

        orders_lijst.append(order_nummer)
        tardiness_lijst.append(round(tardiness_per_order[i], 2))
        penalty_tijd_lijst.append(order['Penalty'])
        tot_penalty_lijst.append(round(penalty_per_order[i], 2))
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
    with pd.ExcelWriter(bestandsnaam) as writer:
        df_resultaten.to_excel(writer, sheet_name = 'Resultaten orders', index = False)  
        df_MachineOrder.to_excel(writer, sheet_name = 'Volgorde machines', index = False)
        df_totalen.to_excel(writer, sheet_name = 'Totale resulaten', index = False)

resultaten_naar_excel_list(di_orders, di_machines, oefen, tard, pen, tard_per_order, penalty_per_order, machines_per_order, 'Results_Metaheuristic.xlsx')

resultaten_naar_excel_list(
    di_orders,
    di_machines,
    beste_volgorde,
    tard,
    pen,
    tard_per_order,
    penalty_per_order,
    machines_per_order,
    'Results_Metaheuristic_improved.xlsx'
)


def gantt_chart_list(volgorde, di_orders, di_machines, machines_per_order, begintijden, eindtijden):
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
    orders = {} 
    for order in di_orders: 
        orders[order['Order']] = order

    for i in range(len(volgorde)):

        machine = machines_per_order[i]
        begintijd = begintijden[i]
        eindtijd = eindtijden[i]

        duur = eindtijd - begintijd
        order = orders[volgorde[i]]
        kleur_order = order['Colour']

        # Balk tekenen
        ax.barh(machine, duur, left=begintijd, height = 0.6,color = kleur_dict[kleur_order], edgecolor = 'black')

        # Ordernummer in de balk zetten
        ax.text(begintijd + duur / 2, machine, str(order['Order']), ha='center', va='center', fontsize = 9)

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

gantt_chart_list(
    beste_volgorde,
    di_orders,
    di_machines,
    machines_per_order,
    begintijden,
    eindtijden
)
