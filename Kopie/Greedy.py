from Functions import (gantt_chart, resultaten_naar_excel)

import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']


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
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    tijden[machine_index] += setup['Setup time']
                    setup_gevonden = True
                    break

            if setup_gevonden == False:
                raise ValueError(f"Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}")

        # Productietijd
        tijden[machine_index] += order['Surface'] / di_machines[machine_index]['Speed']

        # Laatste kleur opslaan
        vorige_kleuren[machine_index] = kleur

        # Order toevoegen aan de machine
        volgordes[machine_index].append(order['Order'])

    return volgordes, machines_per_order


def calculate_results(volgordes, di_orders, di_machines, di_setups):
    '''
    Berekent alle resultaten van de greedy planning.

    Return:
        total_tardiness
        total_penalty
        machines_per_order
        seqno_per_order
        setup_per_order
        begintijden
        procestijden
        eindtijden
        tardiness_per_order
        penalty_per_order
    '''

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines

    total_tardiness = 0
    total_penalty = 0

    resultaten = {}

    # Orders opzoeken via ordernummer
    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    # Iedere machine apart doorlopen
    for machine_index in range(aantal_machines):

        for i in range(len(volgordes[machine_index])):

            order_nummer = volgordes[machine_index][i]
            order = orders[order_nummer]
            kleur = order['Colour']

            # Volgnummer op de machine
            seqno = i + 1

            # Setup-tijd
            setup_tijd = 0

            if vorige_kleuren[machine_index] != None and kleur != vorige_kleuren[machine_index]:
                setup_gevonden = False

                for setup in di_setups:
                    if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                        setup_tijd = setup['Setup time']
                        setup_gevonden = True
                        break

                if setup_gevonden == False:
                    raise ValueError(f"Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}")

            # Setup uitvoeren
            tijden[machine_index] += setup_tijd

            # Starttijd schilderen
            begintijd = tijden[machine_index]

            # Procestijd
            procestijd = order['Surface'] / di_machines[machine_index]['Speed']

            # Productie uitvoeren
            tijden[machine_index] += procestijd

            # Eindtijd
            eindtijd = tijden[machine_index]

            # Tardiness
            tardiness = max(0, eindtijd - order['Deadline'])

            # Cost
            cost = tardiness * order['Penalty']

            total_tardiness += tardiness
            total_penalty += cost

            resultaten[order_nummer] = {
                'machine': machine_index,
                'seqno': seqno,
                'setup': setup_tijd,
                'start': begintijd,
                'process': procestijd,
                'end': eindtijd,
                'tardiness': tardiness,
                'cost': cost
            }

            vorige_kleuren[machine_index] = kleur

    # Resultaten in dezelfde volgorde als di_orders zetten
    machines_per_order = []
    seqno_per_order = []
    setup_per_order = []
    begintijden = []
    procestijden = []
    eindtijden = []
    tardiness_per_order = []
    penalty_per_order = []

    for order in di_orders:

        order_nummer = order['Order']

        machines_per_order.append(resultaten[order_nummer]['machine'])
        seqno_per_order.append(resultaten[order_nummer]['seqno'])
        setup_per_order.append(resultaten[order_nummer]['setup'])
        begintijden.append(resultaten[order_nummer]['start'])
        procestijden.append(resultaten[order_nummer]['process'])
        eindtijden.append(resultaten[order_nummer]['end'])
        tardiness_per_order.append(resultaten[order_nummer]['tardiness'])
        penalty_per_order.append(resultaten[order_nummer]['cost'])

    return total_tardiness, total_penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order


# Greedy uitvoeren
volgordes, machines_greedy = greedy_schedule(di_orders, di_machines, di_setups)

# Resultaten berekenen
total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_results(volgordes, di_orders, di_machines, di_setups)


# Resultaten printen
for i in range(len(di_machines)):
    print(f'{di_machines[i]["Machine"]}:')
    print('Order volgorde:', volgordes[i])

print(f'De totale vertraging is {total_tardiness:.2f} tijdseenheden')
print(f'De totale penalty is {penalty:.2f}')


resultaten_naar_excel(di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, 'Results_Greedy.xlsx')

gantt_chart(di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty)