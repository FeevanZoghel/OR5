
from Functions import dictionary, random_swap
import pandas as pd
import random
import math as m
import time


# --------------------------------------------------
# INSTELLINGEN
# --------------------------------------------------

t_max = 700000
cooling_it = 700
k = t_max / cooling_it
cooling_factor = 0.01 ** (1 / k)
temp = 500

seeds = [1, 4, 9, 14, 88, 1040440]


# --------------------------------------------------
# DATA INLADEN
# --------------------------------------------------

df = pd.read_excel(
    'PaintShop-september2026.xlsx',
    sheet_name=None
)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']

di_orders = dictionary(df_orders)
di_machines = dictionary(df_machines)
di_setups = dictionary(df_setups)

# EDD-volgorde voor Greedy
di_orders.sort(key=lambda job: job['Deadline'])

orders_dict = {
    order['Order']: order
    for order in di_orders
}


# --------------------------------------------------
# PLANNING EN PENALTY BEREKENEN
# --------------------------------------------------

def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    """
    Plant orders op de machine met de laagste huidige tijd.
    Bij gelijke tijden wordt de snelste machine gekozen.

    Return:
        total_tardiness
        penalty
    """

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
# DISCRETE IMPROVING SEARCH
# --------------------------------------------------

def improving_search(volgorde, di_orders, di_machines, di_setups):
    """
    Best-improvement search met pairwise swaps.
    """

    beste_volgorde = volgorde.copy()

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
# SIMULATED ANNEALING
# --------------------------------------------------

def SA(df_orders, di_orders, di_machines, di_setups,
       t_max, cooling_factor, cooling_it, temp):

    current = df_orders['Order'].tolist()
    random.shuffle(current)

    current_tard, current_penalty = calculate_tard_pen(
        current,
        di_orders,
        di_machines,
        di_setups
    )

    best = current.copy()
    best_penalty = current_penalty
    best_tard = current_tard

    for i in range(t_max):

        new_current = random_swap(current)

        new_tard, new_penalty = calculate_tard_pen(
            new_current,
            di_orders,
            di_machines,
            di_setups
        )

        verschil = current_penalty - new_penalty

        if (
            verschil > 0
            or random.random() < m.exp(verschil / temp)
        ):

            current = new_current.copy()
            current_penalty = new_penalty
            current_tard = new_tard

        if current_penalty < best_penalty:

            best = current.copy()
            best_penalty = current_penalty
            best_tard = current_tard

        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor

    return best, best_tard, best_penalty


# --------------------------------------------------
# RESULTATEN OPSLAAN
# --------------------------------------------------

resultaten = []


# --------------------------------------------------
# EXPERIMENT 1: GREEDY
# --------------------------------------------------

print('Greedy uitvoeren...')

# EDD-volgorde
greedy_volgorde = [
    order['Order']
    for order in di_orders
]

start_greedy = time.perf_counter()

greedy_tard, greedy_penalty = calculate_tard_pen(
    greedy_volgorde,
    di_orders,
    di_machines,
    di_setups
)

rekentijd_greedy = time.perf_counter() - start_greedy


# Greedy + Improving Search
start_improving = time.perf_counter()

greedy_improved_tard, greedy_improved_penalty, _ = improving_search(
    greedy_volgorde,
    di_orders,
    di_machines,
    di_setups
)

rekentijd_greedy_improving = (
    time.perf_counter() - start_improving
)


resultaten.append({
    'Methode': 'Greedy',
    'Seed': None,
    'Penalty voor Improving': greedy_penalty,
    'Penalty na Improving': greedy_improved_penalty,
    'Tardiness voor Improving': greedy_tard,
    'Tardiness na Improving': greedy_improved_tard,
    'Rekentijd methode (s)': rekentijd_greedy,
    'Rekentijd Improving (s)': rekentijd_greedy_improving,
    'Totale rekentijd (s)': (
        rekentijd_greedy + rekentijd_greedy_improving
    ),
    'Verbetering penalty': (
        greedy_penalty - greedy_improved_penalty
    )
})


print(
    f'Greedy: {greedy_penalty:.2f} -> '
    f'{greedy_improved_penalty:.2f}'
)


# --------------------------------------------------
# EXPERIMENT 2: SIMULATED ANNEALING
# --------------------------------------------------

for seed in seeds:

    print(f'\nSimulated Annealing met seed {seed}...')

    random.seed(seed)

    # SA uitvoeren
    start_sa = time.perf_counter()

    sa_volgorde, sa_tard, sa_penalty = SA(
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

    # Improving Search na SA
    start_improving = time.perf_counter()

    sa_improved_tard, sa_improved_penalty, _ = improving_search(
        sa_volgorde,
        di_orders,
        di_machines,
        di_setups
    )

    rekentijd_sa_improving = (
        time.perf_counter() - start_improving
    )

    resultaten.append({
        'Methode': 'Simulated Annealing',
        'Seed': seed,
        'Penalty voor Improving': sa_penalty,
        'Penalty na Improving': sa_improved_penalty,
        'Tardiness voor Improving': sa_tard,
        'Tardiness na Improving': sa_improved_tard,
        'Rekentijd methode (s)': rekentijd_sa,
        'Rekentijd Improving (s)': rekentijd_sa_improving,
        'Totale rekentijd (s)': (
            rekentijd_sa + rekentijd_sa_improving
        ),
        'Verbetering penalty': (
            sa_penalty - sa_improved_penalty
        )
    })

    print(
        f'Seed {seed}: '
        f'SA {sa_penalty:.2f} -> '
        f'Improved {sa_improved_penalty:.2f}'
    )


# --------------------------------------------------
# DATAFRAMES MAKEN
# --------------------------------------------------

df_resultaten = pd.DataFrame(resultaten)


# --------------------------------------------------
# GEMIDDELDEN EN STANDAARDDEVIATIES
# --------------------------------------------------

df_samenvatting = (
    df_resultaten
    .groupby('Methode')
    .agg(
        Aantal_runs=('Penalty voor Improving', 'count'),

        Gem_penalty_voor=('Penalty voor Improving', 'mean'),
        Std_penalty_voor=('Penalty voor Improving', 'std'),
        Beste_penalty_voor=('Penalty voor Improving', 'min'),

        Gem_penalty_na=('Penalty na Improving', 'mean'),
        Std_penalty_na=('Penalty na Improving', 'std'),
        Beste_penalty_na=('Penalty na Improving', 'min'),

        Gem_tardiness_voor=('Tardiness voor Improving', 'mean'),
        Gem_tardiness_na=('Tardiness na Improving', 'mean'),

        Gem_rekentijd_methode=('Rekentijd methode (s)', 'mean'),
        Gem_rekentijd_improving=('Rekentijd Improving (s)', 'mean'),
        Gem_totale_rekentijd=('Totale rekentijd (s)', 'mean'),

        Gem_verbetering_penalty=('Verbetering penalty', 'mean')
    )
    .reset_index()
)

# Standaarddeviatie is niet van toepassing bij één Greedy-run
df_samenvatting[
    ['Std_penalty_voor', 'Std_penalty_na']
] = df_samenvatting[
    ['Std_penalty_voor', 'Std_penalty_na']
].fillna(0)


# --------------------------------------------------
# TABEL VOOR GRAFIEKEN
# --------------------------------------------------

grafiek_resultaten = []

for _, rij in df_samenvatting.iterrows():

    methode = rij['Methode']

    grafiek_resultaten.append({
        'Methode': methode,
        'Fase': 'Voor Improving',
        'Gemiddelde penalty': rij['Gem_penalty_voor'],
        'Standaarddeviatie': rij['Std_penalty_voor'],
        'Gemiddelde rekentijd (s)': rij['Gem_rekentijd_methode']
    })

    grafiek_resultaten.append({
        'Methode': methode,
        'Fase': 'Na Improving',
        'Gemiddelde penalty': rij['Gem_penalty_na'],
        'Standaarddeviatie': rij['Std_penalty_na'],
        'Gemiddelde rekentijd (s)': rij['Gem_totale_rekentijd']
    })

df_grafieken = pd.DataFrame(grafiek_resultaten)


# --------------------------------------------------
# INSTELLINGEN OPSLAAN
# --------------------------------------------------

df_instellingen = pd.DataFrame({
    'Parameter': [
        'Dataset',
        't_max',
        'cooling_it',
        'cooling_factor',
        'temp',
        'Seeds',
        'Aantal machines'
    ],
    'Waarde': [
        'PaintShop-september2026.xlsx',
        t_max,
        cooling_it,
        cooling_factor,
        temp,
        ', '.join(str(seed) for seed in seeds),
        len(di_machines)
    ]
})


# --------------------------------------------------
# ALLES EXPORTEREN NAAR EXCEL
# --------------------------------------------------

with pd.ExcelWriter(
    'Vergelijking_oplossingsmethoden.xlsx',
    engine='openpyxl'
) as writer:

    df_resultaten.to_excel(
        writer,
        sheet_name='Alle runs',
        index=False
    )

    df_samenvatting.to_excel(
        writer,
        sheet_name='Samenvatting',
        index=False
    )

    df_grafieken.to_excel(
        writer,
        sheet_name='Grafieken',
        index=False
    )

    df_instellingen.to_excel(
        writer,
        sheet_name='Instellingen',
        index=False
    )


# --------------------------------------------------
# RESULTATEN WEERGEVEN
# --------------------------------------------------

print('\nOnderzoek afgerond!')

print('\nAlle runs:')
print(df_resultaten.to_string(index=False))

print('\nSamenvatting:')
print(df_samenvatting.to_string(index=False))

print(
    '\nResultaten opgeslagen in '
    'Vergelijking_oplossingsmethoden.xlsx'
)
