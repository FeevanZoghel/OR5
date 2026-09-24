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


def calculate_tardiness1(volgorde, di_orders, di_machines, di_setups):
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
        productietijd = (
            order['Surface'] / di_machines[machine_index]['Speed']
        )

        tijden[machine_index] += productietijd

        # Eindtijd
        eindtijd = tijden[machine_index]

        # Tardiness
        tardiness = max(0, eindtijd - order['Deadline'])

        # Totale tardiness
        total_tardiness += tardiness

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return total_tardiness


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
    current_tard = calculate_tardiness1(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_tardiness = current_tard

    for i in range(t_max):

        new_current = random_swap(current)
        new_tard    = calculate_tardiness1(new_current, di_orders, di_machines, di_setups)
        verschil    = current_tard-new_tard
        
        kans = m.exp(verschil / temp)

        if verschil > 0:
            current             = new_current.copy()
            current_tard         = new_tard
        else:
            getal = np.random.choice([0, 1], p=[1-kans, kans])

            # Slechtere oplossing toch accepteren
            if getal == 1:
                current = new_current.copy()
                current_tard = new_tard

        # Is current de beste oplossing die we ooit hebben gezien?
        if current_tard < best_tardiness:
            best = current.copy()
            best_tardiness = current_tard

        # Temperatuur na 1000 iteraties verlagen
        if (i + 1) % cooling_it == 0:
            temp = temp * cooling_factor
    return(best, best_tardiness)


t_max = 100000
cooling_factor =0.99
cooling_it = 100
temp = 1000

print(SA(df_orders, t_max, cooling_factor,cooling_it,temp))

