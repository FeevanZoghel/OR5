from Functions import dictionary, random_swap
from itertools import combinations, product

import pandas as pd
import random
import math as m
import time


# --------------------------------------------------
# INSTELLINGEN
# --------------------------------------------------

t_max = 70000
cooling_it = 700
k = t_max / cooling_it
cooling_factor = 0.01 ** (1 / k)
temp = 500

seed = 4

# Snelheidsverhogingen
verhogingen = [0]


# --------------------------------------------------
# DATA INLADEN
# --------------------------------------------------

df = pd.read_excel(
    'PaintShop-September2026_kopie.xlsx',
    sheet_name=None
)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

di_orders_org = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups_org = dictionary(df_setups)

di_orders = di_orders_org.copy()
di_setups = di_setups_org.copy()

di_orders.sort(key=lambda job: job['Deadline'])

aantal_machines = len(di_machines_org)

originele_snelheden = [
    machine['Speed']
    for machine in di_machines_org
]


# --------------------------------------------------
# TARDINESS EN PENALTY BEREKENEN
# --------------------------------------------------

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines

    total_tardiness = 0
    penalty = 0

    orders = {
        order['Order']: order
        for order in di_orders
    }

    for order_nummer in volgorde:

        order = orders[order_nummer]
        kleur = order['Colour']

        laagste_tijd = min(tijden)

        mogelijke_machines = [
            i for i in range(aantal_machines)
            if tijden[i] == laagste_tijd
        ]

        machine_index = max(
            mogelijke_machines,
            key=lambda i: di_machines[i]['Speed']
        )

        # Setup bij kleurverandering
        if (
            vorige_kleuren[machine_index] is not None
            and kleur != vorige_kleuren[machine_index]
        ):

            setup_gevonden = False

            for setup in di_setups:

                if (
                    setup['From colour'] == vorige_kleuren[machine_index]
                    and setup['To colour'] == kleur
                ):

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
            order['Surface']
            / di_machines[machine_index]['Speed']
        )

        tijden[machine_index] += productietijd

        # Tardiness en penalty
        tardiness = max(
            0,
            tijden[machine_index] - order['Deadline']
        )

        penalty_order = tardiness * order['Penalty']

        total_tardiness += tardiness
        penalty += penalty_order

        vorige_kleuren[machine_index] = kleur

    return total_tardiness, penalty


# --------------------------------------------------
# SIMULATED ANNEALING
# --------------------------------------------------

def SA(df_orders, di_orders, di_machines, di_setups,
       t_max, cooling_factor, cooling_it, temp):

    current = df_orders['Order'].tolist()

    random.shuffle(current)

    current_penalty = calculate_tard_pen(
        current,
        di_orders,
        di_machines,
        di_setups
    )[1]

    best = current.copy()
    best_penalty = current_penalty

    for i in range(t_max):

        new_current = random_swap(current)

        new_penalty = calculate_tard_pen(
            new_current,
            di_orders,
            di_machines,
            di_setups
        )[1]

        verschil = current_penalty - new_penalty

        if (
            verschil > 0
            or random.random() < m.exp(verschil / temp)
        ):

            current = new_current.copy()
            current_penalty = new_penalty

        if current_penalty < best_penalty:

            best = current.copy()
            best_penalty = current_penalty

        # Stop zodra een penalty van 0 is gevonden
        if best_penalty <= 0:
            print(f'Penalty 0 gevonden na {i + 1} iteraties!')
            break

        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor

    return best, best_penalty


# --------------------------------------------------
# IMPROVING SEARCH NA SA
# --------------------------------------------------

def meta_improving_search(
    sa_volgorde,
    di_orders,
    di_machines,
    di_setups
):

    beste_volgorde = sa_volgorde.copy()

    best_tot_tard, best_penalty = calculate_tard_pen(
        beste_volgorde,
        di_orders,
        di_machines,
        di_setups
    )

    verbetering = True

    while verbetering:

        verbetering = False

        ronde_beste_volgorde = beste_volgorde.copy()
        ronde_beste_penalty = best_penalty
        ronde_beste_tard = best_tot_tard

        for i in range(len(beste_volgorde)):

            for j in range(i + 1, len(beste_volgorde)):

                new_current = beste_volgorde.copy()

                new_current[i], new_current[j] = (
                    new_current[j],
                    new_current[i]
                )

                current_tard, current_penalty = calculate_tard_pen(
                    new_current,
                    di_orders,
                    di_machines,
                    di_setups
                )

                if current_penalty < ronde_beste_penalty:

                    ronde_beste_penalty = current_penalty
                    ronde_beste_tard = current_tard
                    ronde_beste_volgorde = new_current.copy()

                    verbetering = True

        if verbetering:

            best_penalty = ronde_beste_penalty
            best_tot_tard = ronde_beste_tard
            beste_volgorde = ronde_beste_volgorde.copy()

    return best_tot_tard, best_penalty, beste_volgorde


# --------------------------------------------------
# MACHINESNELHEDEN AANPASSEN
# --------------------------------------------------

def maak_machines(verhoging_per_machine):

    di_machines = [
        machine.copy()
        for machine in di_machines_org
    ]

    for i in range(aantal_machines):

        di_machines[i]['Speed'] = (
            originele_snelheden[i]
            * (1 + verhoging_per_machine[i] / 100)
        )

    return di_machines


# --------------------------------------------------
# EXPERIMENT UITVOEREN
# --------------------------------------------------


def voer_experiment_uit(verhoging_per_machine):

    # Zelfde seed voor ieder experiment
    random.seed(seed)

    di_machines = maak_machines(verhoging_per_machine)

    # Simulated Annealing
    start_sa = time.perf_counter()

    sa_volgorde, penalty_sa = SA(
        df_orders,
        di_orders,
        di_machines,
        di_setups,
        t_max,
        cooling_factor,
        cooling_it,
        temp
    )

    rekentijd_sa = time.perf_counter() - start_sa

    # Improving Search alleen uitvoeren als penalty > 0
    if penalty_sa <= 0:
        penalty_improved = penalty_sa
        rekentijd_improving = 0

    else:
        start_improving = time.perf_counter()

        _, penalty_improved, beste_volgorde = meta_improving_search(
            sa_volgorde,
            di_orders,
            di_machines,
            di_setups
        )

        rekentijd_improving = (
            time.perf_counter() - start_improving
        )

    return (
        penalty_sa,
        penalty_improved,
        rekentijd_sa,
        rekentijd_improving
    )


resultaten = []

for verhoging in verhogingen:

    # Alle drie de machines krijgen dezelfde verhoging
    verhoging_per_machine = [verhoging] * aantal_machines

    # Simulated Annealing + Improving Search uitvoeren
    (
        penalty_sa,
        penalty_improved,
        rekentijd_sa,
        rekentijd_improving
    ) = voer_experiment_uit(verhoging_per_machine)

    resultaten.append({
        'Snelheidsverhoging (%)': verhoging,
        'M1 (%)': verhoging,
        'M2 (%)': verhoging,
        'M3 (%)': verhoging,
        'Penalty SA': penalty_sa,
        'Penalty SA Improved': penalty_improved,
        'Rekentijd SA (s)': rekentijd_sa,
        'Rekentijd Improving (s)': rekentijd_improving,
        'Totale rekentijd (s)': rekentijd_sa + rekentijd_improving
    })

    print(
        f'Alle machines +{verhoging}% | '
        f'SA: {penalty_sa:.2f} | '
        f'Improved: {penalty_improved:.2f} | '
        f'Tijd: {rekentijd_sa + rekentijd_improving:.2f} s'
    )

    # Stop met experimenteren als de penalty 0 is
    if penalty_improved <= 0:
        print(
            f'\nPenalty 0 bereikt bij een snelheidsverhoging '
            f'van {verhoging}% voor alle machines!'
        )
        break


# --------------------------------------------------
# RESULTATEN VERWERKEN
# --------------------------------------------------

df_resultaten = pd.DataFrame(resultaten)

# Nulmeting
penalty_sa_0 = df_resultaten.loc[0, 'Penalty SA']
penalty_improved_0 = df_resultaten.loc[0, 'Penalty SA Improved']

# Procentuele verbetering ten opzichte van 0%
if penalty_sa_0 != 0:
    df_resultaten['Verbetering SA (%)'] = (
        (penalty_sa_0 - df_resultaten['Penalty SA'])
        / penalty_sa_0 * 100
    )

if penalty_improved_0 != 0:
    df_resultaten['Verbetering Improved (%)'] = (
        (penalty_improved_0 - df_resultaten['Penalty SA Improved'])
        / penalty_improved_0 * 100
    )


# --------------------------------------------------
# RESULTATEN NAAR APART EXCELBESTAND
# --------------------------------------------------

bestandsnaam = 'onderzoek_meta_alle_machines.xlsx'

df_resultaten.to_excel(
    bestandsnaam,
    sheet_name='Alle machines',
    index=False
)

print('\nOnderzoek afgerond!')
print(df_resultaten.to_string(index=False))
print(f'\nResultaten opgeslagen in {bestandsnaam}')
