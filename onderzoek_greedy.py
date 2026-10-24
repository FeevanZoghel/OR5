
import pandas as pd

# Instellingen
verhogingen = [0, 10, 20, 30, 50]

# Data inladen
df = pd.read_excel('PaintShop-September2026.xlsx', sheet_name=None)

df_orders = df['Orders']
df_machines = df['Machines']
df_setups = df['Setups']


def dictionary(df):
    """
    Zet een DataFrame om naar een lijst met dictionaries.
    """
    jobs = []

    for i in range(len(df)):
        job = {}

        for column in df.columns:
            job[column] = df.iloc[i][column]

        jobs.append(job)

    return jobs


di_orders = dictionary(df_orders)
di_machines_org = dictionary(df_machines)
di_setups = dictionary(df_setups)

# Orders sorteren op deadline (EDD)
di_orders.sort(key=lambda job: job['Deadline'])


def plan_order(machine, order, tijd, vorige_kleur, di_setups):
    """
    Plant één order op een machine.
    """

    kleur = order['Colour']
    setup_tijd = 0

    # Extra tijd bij kleurverandering
    if vorige_kleur is not None and kleur != vorige_kleur:

        setup_gevonden = False

        for setup in di_setups:
            if (
                setup['From colour'] == vorige_kleur
                and setup['To colour'] == kleur
            ):
                setup_tijd = setup['Setup time']
                tijd += setup_tijd
                setup_gevonden = True
                break

        if not setup_gevonden:
            raise ValueError(
                f'Geen setup gevonden van {vorige_kleur} naar {kleur}'
            )

    # Begintijd
    begintijd = tijd

    # Productietijd
    procestijd = order['Surface'] / machine['Speed']
    tijd += procestijd

    # Eindtijd
    eindtijd = tijd

    # Tardiness en penalty
    tardiness = max(0, eindtijd - order['Deadline'])
    penaltyorder = order['Penalty'] * tardiness

    return (
        tijd,
        kleur,
        tardiness,
        penaltyorder,
        setup_tijd,
        begintijd,
        procestijd,
        eindtijd
    )


def greedy_schedule(di_orders, di_machines, di_setups):
    """
    Maakt een planning met behulp van de greedy heuristic.

    Elke order wordt toegewezen aan de machine met de laagste huidige tijd.
    Bij gelijke tijden wordt de snelste machine gekozen.
    """

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines

    volgordes = [[] for _ in range(aantal_machines)]
    machines_per_order = []

    for order in di_orders:

        # Machine met de laagste huidige tijd
        laagste_tijd = min(tijden)

        mogelijke_machines = []

        for i in range(aantal_machines):
            if tijden[i] == laagste_tijd:
                mogelijke_machines.append(i)

        # Bij gelijke tijd: snelste machine kiezen
        machine_index = mogelijke_machines[0]

        for i in mogelijke_machines:
            if (
                di_machines[i]['Speed']
                > di_machines[machine_index]['Speed']
            ):
                machine_index = i

        machines_per_order.append(machine_index)

        kleur = order['Colour']

        # Setup time bij kleurverandering
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
        tijden[machine_index] += (
            order['Surface'] / di_machines[machine_index]['Speed']
        )

        vorige_kleuren[machine_index] = kleur

        volgordes[machine_index].append(order['Order'])

    return volgordes, machines_per_order


def calculate_results(volgordes, di_orders, di_machines, di_setups):
    """
    Berekent de totale tardiness en totale penalty.
    """

    aantal_machines = len(di_machines)

    tijden = [0] * aantal_machines
    vorige_kleuren = [None] * aantal_machines

    total_tardiness = 0
    total_penalty = 0

    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    for machine_index in range(aantal_machines):

        for order_nummer in volgordes[machine_index]:

            order = orders[order_nummer]

            (
                tijd,
                kleur,
                tardiness,
                penaltyorder,
                setup_tijd,
                begintijd,
                procestijd,
                eindtijd
            ) = plan_order(
                di_machines[machine_index],
                order,
                tijden[machine_index],
                vorige_kleuren[machine_index],
                di_setups
            )

            tijden[machine_index] = tijd
            vorige_kleuren[machine_index] = kleur

            total_tardiness += tardiness
            total_penalty += penaltyorder

    return total_tardiness, total_penalty


def improving_search(di_orders, di_machines, di_setups):
    """
    Verbetert de greedy-planning door alle mogelijke
    swaps tussen twee orders te onderzoeken.

    Per ronde wordt de swap met de laagste penalty gekozen.
    Het proces stopt als er geen verbetering meer mogelijk is.
    """

    current = di_orders.copy()
    beste_volgorde = current.copy()

    # Eerste greedy-planning
    volgordes, _ = greedy_schedule(
        beste_volgorde,
        di_machines,
        di_setups
    )

    best_tot_tard, best_penalty = calculate_results(
        volgordes,
        beste_volgorde,
        di_machines,
        di_setups
    )

    penalty_per_iteratie = []
    beste_penalty_per_iteratie = []

    verbetering = True

    while verbetering:

        verbetering = False

        # Beste resultaat van deze ronde
        ronde_beste_volgorde = beste_volgorde.copy()
        ronde_beste_penalty = best_penalty
        ronde_beste_tard = best_tot_tard

        # Alle mogelijke swaps controleren
        for i in range(len(beste_volgorde)):

            for j in range(i + 1, len(beste_volgorde)):

                # Nieuwe ordervolgorde maken
                new_current = beste_volgorde.copy()

                new_current[i], new_current[j] = (
                    new_current[j],
                    new_current[i]
                )

                # Greedy-planning maken
                volgordes, _ = greedy_schedule(
                    new_current,
                    di_machines,
                    di_setups
                )

                # Resultaten berekenen
                current_tard, current_penalty = calculate_results(
                    volgordes,
                    new_current,
                    di_machines,
                    di_setups
                )

                # Iedere geteste penalty opslaan
                penalty_per_iteratie.append(current_penalty)

                # Beste swap van deze ronde opslaan
                if current_penalty < ronde_beste_penalty:

                    ronde_beste_penalty = current_penalty
                    ronde_beste_tard = current_tard

                    ronde_beste_volgorde = new_current.copy()

                    verbetering = True

        # Beste oplossing van de ronde accepteren
        if verbetering:

            best_penalty = ronde_beste_penalty
            best_tot_tard = ronde_beste_tard

            beste_volgorde = ronde_beste_volgorde.copy()

        beste_penalty_per_iteratie.append(best_penalty)

    return (
        best_tot_tard,
        best_penalty,
        beste_volgorde,
        penalty_per_iteratie,
        beste_penalty_per_iteratie
    )


# Experiment uitvoeren

resultaten_greedy = []
resultaten_improved = []

aantal_machines = len(di_machines_org)

for verhoging in verhogingen:

    rij_greedy = {
        'Snelheidsverhoging (%)': verhoging
    }

    rij_improved = {
        'Snelheidsverhoging (%)': verhoging
    }

    for machine_index in range(aantal_machines):

        # Oorspronkelijke machines kopiëren
        di_machines = [
            machine.copy()
            for machine in di_machines_org
        ]

        # Alleen de geselecteerde machine versnellen
        di_machines[machine_index]['Speed'] *= (
            1 + verhoging / 100
        )

        # Greedy-planning
        volgordes, _ = greedy_schedule(
            di_orders,
            di_machines,
            di_setups
        )

        total_tardiness, total_penalty = calculate_results(
            volgordes,
            di_orders,
            di_machines,
            di_setups
        )

        # Improving Search
        (
            best_tot_tard,
            best_penalty,
            beste_volgorde,
            penalty_per_iteratie,
            beste_penalty_per_iteratie
        ) = improving_search(
            di_orders,
            di_machines,
            di_setups
        )

        # Resultaten opslaan
        kolomnaam = f'M{machine_index + 1} - Penalty'

        rij_greedy[kolomnaam] = total_penalty
        rij_improved[kolomnaam] = best_penalty

        print(
            f'M{machine_index + 1} | '
            f'+{verhoging}% | '
            f'Greedy: {total_penalty:.2f} | '
            f'Improved: {best_penalty:.2f}'
        )

    resultaten_greedy.append(rij_greedy)
    resultaten_improved.append(rij_improved)


# Resultaten naar Excel

df_greedy = pd.DataFrame(resultaten_greedy)
df_improved = pd.DataFrame(resultaten_improved)

with pd.ExcelWriter('onderzoek_greedy.xlsx', engine='openpyxl') as writer:

    df_greedy.to_excel(
        writer,
        sheet_name='Greedy',
        index=False
    )

    df_improved.to_excel(
        writer,
        sheet_name='Improved Greedy',
        index=False
    )

print('\nOnderzoek machinesnelheden afgerond!')
print('\nGreedy:')
print(df_greedy.to_string(index=False))

print('\nImproved Greedy:')
print(df_improved.to_string(index=False))

print('\nResultaten opgeslagen in onderzoek_greedy.xlsx')
