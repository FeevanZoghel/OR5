from Functions import (dictionary, random_swap, gantt_chart_list, resultaten_naar_excel_list)

import pandas as pd
import numpy as np
import random
import math as m
import matplotlib.pyplot as plt

df = pd.read_excel('Data_test_sets/Test09_Penalty_ExpectedResults.xlsx', sheet_name=None)

df_orders = df['Orders']
#Test 9: Controleren of het programma de ontbrekenden kolom 'deadline' herkent
if 'Deadline' not in df_orders.columns:
    print("De kolom 'Deadline' ontbreekt in Orders")

df_machines = df['Machines']
#Test 10: Controleren of een machinesnelheid van 0 correct wordt afgehandeld
if (df_machines['Speed'] <= 0).any():
    print("Machine speed must be greater than zero")
df_setups = df['Setups']

di_orders_org = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups_org = dictionary(df_setups)

di_orders = di_orders_org.copy()
di_machines = di_machines_org.copy()
di_setups = di_setups_org.copy()

di_orders.sort(key=lambda job: job['Deadline'])

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    '''
    Berekent de totale tardiness en penalty van een gegeven ordervolgorde.
    Orders worden verdeeld over de machines op basis van de
    laagste huidige machinetijd.
    '''

    aantal_machines = len(di_machines)

    # Huidige tijd per machine
    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines
    sequence_numbers = [0] * aantal_machines

    # Resultaten
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
        setup_tijd = 0

        if (vorige_kleuren[machine_index] is not None
                and kleur != vorige_kleuren[machine_index]):

            setup_gevonden = False

            for setup in di_setups:
                if (setup['From colour'] == vorige_kleuren[machine_index]
                        and setup['To colour'] == kleur):

                    setup_tijd = setup['Setup time']
                    setup_gevonden = True
                    break

            #Test 11: Controleren of een ontbrekende setup wordt herkent
            if not setup_gevonden:
                print(
                    f"Geen setup gevonden van "
                    f"{vorige_kleuren[machine_index]} naar {kleur}"
                )

        # Setup toevoegen aan de machinetijd
        tijden[machine_index] += setup_tijd

        # Productietijd
        productietijd = order['Surface'] / di_machines[machine_index]['Speed']
        begintijd = tijden[machine_index]

        tijden[machine_index] += productietijd

        # Eindtijd
        eindtijd = tijden[machine_index]

        # Volgnummer op de gekozen machine
        sequence_numbers[machine_index] += 1
        seqno = sequence_numbers[machine_index]

        # Tardiness
        tardiness = max(0, eindtijd - order['Deadline'])

        # Penalty van deze order
        penalty_order = tardiness * order['Penalty']

        # Totalen
        total_tardiness += tardiness
        penalty += penalty_order

        # Resultaten opslaan
        machines_per_order.append(machine_index)
        seqno_per_order.append(seqno)
        setup_per_order.append(setup_tijd)
        begintijden.append(begintijd)
        procestijden.append(productietijd)
        eindtijden.append(eindtijd)
        tardiness_per_order.append(tardiness)
        penalty_per_order.append(penalty_order)

        # Kleur opslaan
        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order


# begin SA

def SA(df_orders, t_max, cooling_factor, cooling_it, temp):
    
    current = df_orders['Order'].tolist()

    random.shuffle(current)
    current_tard, current_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(current, di_orders, di_machines, di_setups)

    best = current.copy()
    best_tardiness = current_tard
    best_penalty   = current_penalty

    for i in range(t_max):

        new_current = random_swap(current)
        new_tard, new_penalty, _, _, _, _, _, _, _, _ = calculate_tard_pen(new_current, di_orders, di_machines, di_setups)
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

        # Is current de beste oplossing van alles?
        if current_penalty < best_penalty:
            best = current.copy()
            best_penalty = current_penalty

        # Temperatuur na 1000 iteraties verlagen
        if (i + 1) % cooling_it == 0:
            temp = temp * cooling_factor
    return(best, best_penalty)


t_max = 10000
cooling_factor =0.99
cooling_it = 1000
temp = 1000

oefen, oefen_pen = SA(df_orders, t_max, cooling_factor, cooling_it,temp)

tard, pen, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order = calculate_tard_pen(oefen, di_orders, di_machines, di_setups)

print(f'de beste lijst is {oefen}, met een totaletardiness van {tard} en {pen} aan penalty' )

resultaten_naar_excel_list(oefen, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden,tardiness_per_order, penalty_per_order, 'Results_SA.xlsx')

gantt_chart_list(oefen, di_orders, di_machines, machines_per_order,setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order,
pen)

#---------------------------------------------------------------------------------------
# Test 6: controleer of de beste SA-penalty klopt

# opnieuw_berekende_penalty = calculate_tard_pen(
#     oefen, di_orders, di_machines, di_setups
# )[1]

# print("Best penalty SA:", oefen_pen)
# print("Opnieuw berekende penalty:", opnieuw_berekende_penalty)

# if abs(oefen_pen - opnieuw_berekende_penalty) < 1e-9:
#     print("Test 6: PASS")
# else:
#     print("Test 6: FAIL")

#---------------------------------------------------------------------------------------
# Test 7: geen setup bij dezelfde kleur

# print("Setup-tijden:", setup_per_order)

# if all(setup == 0 for setup in setup_per_order):
#     print("Test 7: PASS")
# else:
#     print("Test 7: FAIL")

#---------------------------------------------------------------------------------------
# Test 12: order eindigt exact op deadline

# test_volgorde = ['O3', 'O1', 'O2']

# resultaten = calculate_tard_pen(
#     test_volgorde, di_orders, di_machines, di_setups
# )

# eindtijd = resultaten[7][0]
# tardiness = resultaten[8][0]
# cost = resultaten[9][0]

# print("Eindtijd O3:", eindtijd)
# print("Deadline O3:", 7.2)
# print("Tardiness O3:", tardiness)
# print("Cost O3:", cost)

# if (abs(eindtijd - 7.2) < 1e-9
#     and abs(tardiness) < 1e-9
#     and abs(cost) < 1e-9):

#     print("Test 12: PASS")
# else:
#     print("Test 12: FAIL")

#---------------------------------------------------------------------------------------
# Test 13: order eindigt 1 tijdseenheid na deadline

# test_volgorde = ['O1', 'O2', 'O3']

# resultaten = calculate_tard_pen(
#     test_volgorde, di_orders, di_machines, di_setups
# )

# eindtijd = resultaten[7][2]
# tardiness = resultaten[8][2]
# cost = resultaten[9][2]

# print("Eindtijd O3:", eindtijd)
# print("Deadline O3:", 15.2)
# print("Tardiness O3:", tardiness)
# print("Cost O3:", cost)

# if (abs(eindtijd - 16.2) < 1e-9
#     and abs(tardiness - 1) < 1e-9
#     and abs(cost - 8) < 1e-9):

#     print("Test 13: PASS")
# else:
#     print("Test 13: FAIL")

#---------------------------------------------------------------------------------------
# Test 2: snelste machine kiezen bij gelijke machinetijd

# test_volgorde = ['O1', 'O2', 'O3']

# resultaten = calculate_tard_pen(
#     test_volgorde, di_orders, di_machines, di_setups
# )

# machines_per_order = resultaten[2]

# print("Machines per order:", machines_per_order)
# print("Machine voor O3:", di_machines[machines_per_order[2]]['Machine'])

# if machines_per_order == [1, 0, 1]:
#     print("Test 2: PASS")
# else:
#     print("Test 2: FAIL")

#---------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------
#Test 4: penalty per order
# test_volgorde = ['O1', 'O2', 'O3']

# resultaten = calculate_tard_pen(
#     test_volgorde, di_orders, di_machines, di_setups
# )

# tardiness = resultaten[8][2]
# cost = resultaten[9][2]
# totale_penalty = resultaten[1]

# print("Tardiness O3:", tardiness)
# print("Cost O3:", cost)
# print("Totale penalty:", totale_penalty)

# if (abs(tardiness - 5) < 1e-9
#     and abs(cost - 50) < 1e-9
#     and abs(totale_penalty - 50) < 1e-9):

#     print("Test 4: PASS")
# else:
#     print("Test 4: FAIL")
#---------------------------------------------------------------------------------------