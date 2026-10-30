
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
verhogingen = [0, 10, 20, 30, 50]


# --------------------------------------------------
# DATA INLADEN
# --------------------------------------------------

df = pd.read_excel(
    'PaintShop-September2026.xlsx',
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

    # Improving Search
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


# --------------------------------------------------
# DEEL 1: MACHINES AFZONDERLIJK VERSNELLEN
# --------------------------------------------------

resultaten_sa = []
resultaten_improved = []

for verhoging in verhogingen:

    rij_sa = {
        'Snelheidsverhoging (%)': verhoging
    }

    rij_improved = {
        'Snelheidsverhoging (%)': verhoging
    }

    for machine_index in range(aantal_machines):

        verhoging_per_machine = [0] * aantal_machines

        verhoging_per_machine[machine_index] = verhoging

        penalty_sa, penalty_improved, _, _ = voer_experiment_uit(
            verhoging_per_machine
        )

        kolomnaam = f'M{machine_index + 1} - Penalty'

        rij_sa[kolomnaam] = penalty_sa
        rij_improved[kolomnaam] = penalty_improved

        print(
            f'Afzonderlijk | M{machine_index + 1} '
            f'+{verhoging}% | '
            f'SA: {penalty_sa:.2f} | '
            f'Improved: {penalty_improved:.2f}'
        )

    resultaten_sa.append(rij_sa)
    resultaten_improved.append(rij_improved)


df_sa = pd.DataFrame(resultaten_sa)
df_improved = pd.DataFrame(resultaten_improved)


# --------------------------------------------------
# DEEL 2: MEERDERE MACHINES TEGELIJK VERSNELLEN
# --------------------------------------------------

resultaten_combinaties = []

# Nulmeting
penalty_sa_0, penalty_improved_0, _, _ = voer_experiment_uit(
    [0] * aantal_machines
)

resultaten_combinaties.append({
    'Combinatie': 'Geen verhoging',
    'M1 (%)': 0,
    'M2 (%)': 0,
    'M3 (%)': 0,
    'Totale verhoging (%)': 0,
    'Penalty SA': penalty_sa_0,
    'Penalty SA Improved': penalty_improved_0
})


# Combinaties van 2 en 3 machines
for aantal in range(2, aantal_machines + 1):

    for machine_combinatie in combinations(
        range(aantal_machines), aantal
    ):

        for percentages in product(
            verhogingen[1:],
            repeat=aantal
        ):

            verhoging_per_machine = [0] * aantal_machines

            for machine_index, percentage in zip(
                machine_combinatie,
                percentages
            ):

                verhoging_per_machine[machine_index] = percentage

            (
                penalty_sa,
                penalty_improved,
                rekentijd_sa,
                rekentijd_improving
            ) = voer_experiment_uit(
                verhoging_per_machine
            )

            combinatie_naam = ' + '.join(
                f'M{i + 1}'
                for i in machine_combinatie
            )

            resultaten_combinaties.append({
                'Combinatie': combinatie_naam,
                'M1 (%)': verhoging_per_machine[0],
                'M2 (%)': verhoging_per_machine[1],
                'M3 (%)': verhoging_per_machine[2],
                'Totale verhoging (%)': sum(
                    verhoging_per_machine
                ),
                'Penalty SA': penalty_sa,
                'Penalty SA Improved': penalty_improved,
                'Rekentijd SA (s)': rekentijd_sa,
                'Rekentijd Improving (s)': rekentijd_improving
            })

            print(
                f'Combinatie | {combinatie_naam} | '
                f'{verhoging_per_machine} | '
                f'SA: {penalty_sa:.2f} | '
                f'Improved: {penalty_improved:.2f}'
            )


# --------------------------------------------------
# DEEL 3: RESULTATEN VERWERKEN
# --------------------------------------------------

df_combinaties = pd.DataFrame(resultaten_combinaties)

if penalty_sa_0 != 0:

    df_combinaties['Verbetering SA (%)'] = (
        (penalty_sa_0 - df_combinaties['Penalty SA'])
        / penalty_sa_0 * 100
    )

else:
    df_combinaties['Verbetering SA (%)'] = 0


if penalty_improved_0 != 0:

    df_combinaties['Verbetering Improved (%)'] = (
        (penalty_improved_0 - df_combinaties['Penalty SA Improved'])
        / penalty_improved_0 * 100
    )

else:
    df_combinaties['Verbetering Improved (%)'] = 0


# Beste combinatie per groep
df_beste_combinaties = (
    df_combinaties
    .sort_values(
        by=[
            'Penalty SA Improved',
            'Totale verhoging (%)'
        ]
    )
    .drop_duplicates(subset=['Combinatie'])
    .reset_index(drop=True)
)


# --------------------------------------------------
# DEEL 4: RESULTATEN NAAR EXCEL
# --------------------------------------------------

with pd.ExcelWriter(
    'onderzoek_meta.xlsx',
    engine='openpyxl'
) as writer:

    df_sa.to_excel(
        writer,
        sheet_name='SA',
        index=False
    )

    df_improved.to_excel(
        writer,
        sheet_name='SA Improved',
        index=False
    )

    df_combinaties.to_excel(
        writer,
        sheet_name='Alle combinaties',
        index=False
    )

    df_beste_combinaties.to_excel(
        writer,
        sheet_name='Beste combinaties',
        index=False
    )


print('\nOnderzoek Simulated Annealing afgerond!')

print('\nSA:')
print(df_sa.to_string(index=False))

print('\nSA Improved:')
print(df_improved.to_string(index=False))

print('\nBeste combinaties:')
print(df_beste_combinaties.to_string(index=False))

print('\nResultaten opgeslagen in onderzoek_meta.xlsx')
