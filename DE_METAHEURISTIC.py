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
    Berekent de totale tardiness van een gegeven ordervolgorde.
    Orders worden verdeeld over de machines op basis van de
    laagste huidige machinetijd.
    '''

    aantal_machines = len(di_machines)

    # Huidige tijd per machine
    tijden = [0] * aantal_machines

    # Laatste kleur per machine
    vorige_kleuren = [None] * aantal_machines

    # Totale tardiness
    total_tardiness = 0
    penalty = 0
    machines_per_order = []
    begintijden = []
    eindtijden = []

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

        # Tardiness+ penalty
        tardiness = max(0, eindtijd - order['Deadline'])
        if eindtijd - order['Deadline'] >0:
            penalty+= tardiness*order['Penalty']

        

        # Totale tardiness
        total_tardiness += tardiness

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty, machines_per_order, begintijden, eindtijden


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
    current_tard, current_penalty, _,_, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_tardiness = current_tard
    best_penalty   = current_penalty

    for i in range(t_max):

        new_current = random_swap(current)
        new_tard, new_penalty ,_,_,_    = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
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
    return(best, best_penalty)


t_max = 1000000
cooling_factor =0.99
cooling_it = 1000
temp = 1000

oefen, oefen_pen = SA(df_orders, t_max, cooling_factor, cooling_it,temp)




tard, pen,machines_per_order,begintijden,eindtijden = calculate_tard_pen(oefen, di_orders, di_machines, di_setups)
print(f'de beste lijst is {oefen}, met een totaletardiness van {tard} en {pen} aan penalty' )


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

gantt_chart_list(oefen, di_orders, di_machines, machines_per_order, begintijden, eindtijden)
