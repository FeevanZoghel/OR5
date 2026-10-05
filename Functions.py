import pandas as pd
import matplotlib.pyplot as plt
import random 

random.seed(42)

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

def gantt_chart(di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty):
    '''
    Maakt een Gantt-chart van de greedy planning.

    Elke horizontale rij stelt een machine voor.
    De setup-tijd en procestijd worden weergegeven.
    '''

    fig, ax = plt.subplots(figsize=(16, 7))

    kleur_dict = {
        'Red'   : 'red',
        'Blue'  : 'blue',
        'Green' : 'green',
        'Yellow': 'yellow',
        'Orange': 'orange',
        'Purple': 'purple',
        'Pink'  : 'pink',
        'Black' : 'black',
        'White' : 'white',
        'Grey'  : 'grey'
    }

    for i in range(len(di_orders)):

        machine = machines_per_order[i]
        begintijd = begintijden[i]
        eindtijd = eindtijden[i]
        procestijd = procestijden[i]
        setup_tijd = setup_per_order[i]

        kleur_order = di_orders[i]['Colour']

        # Setup begint voor de productiestart
        setup_start = begintijd - setup_tijd

        # Setup-tijd tekenen
        if setup_tijd > 0:
            ax.barh(machine, setup_tijd, left=setup_start, height=0.6, color='lightgrey', edgecolor='black', hatch='//')

        # Rode rand als de order te laat is
        if tardiness_per_order[i] > 0:
            edgecolor = "#FF8888"
            linewidth = 2
        else:
            edgecolor = 'black'
            linewidth = 1

        # Productietijd tekenen
        ax.barh(machine, procestijd, left=begintijd, height=0.6, color=kleur_dict[kleur_order], edgecolor=edgecolor, linewidth=linewidth)

        # Ordernummer in de balk zetten
        ax.text(begintijd + procestijd / 2, machine, str(di_orders[i]['Order']), ha='center', va='center', fontsize=9)

    # Machine-namen op de y-as
    ax.set_yticks(range(len(di_machines)))
    ax.set_yticklabels([di_machines[i]['Machine'] for i in range(len(di_machines))])

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    ax.set_xlabel('Tijd')
    ax.set_ylabel('Machine')
    ax.set_title('Gantt-chart Greedy planning')

    # Totale resultaten rechtsboven
    ax.text(1, 1, f'Totale penalty: {penalty:.2f}\nTotale tardiness: {sum(tardiness_per_order):.2f}', transform=ax.transAxes, ha='right', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.show()

def resultaten_naar_excel(di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, bestandsnaam='Results_Greedy.xlsx'):
    '''
    Zet de planning in het vereiste Excel-format.

    Het Excel-bestand bevat één tabblad:
        Schedule
    '''

    orders_lijst = []
    machine_lijst = []
    deadline_lijst = []
    penalty_lijst = []

    for i in range(len(di_orders)):
        orders_lijst.append(di_orders[i]['Order'])
        machine_lijst.append(di_machines[machines_per_order[i]]['Machine'])
        deadline_lijst.append(di_orders[i]['Deadline'])
        penalty_lijst.append(di_orders[i]['Penalty'])

    df_schedule = pd.DataFrame({
        'Order': orders_lijst,
        'Machine': machine_lijst,
        'SeqNo': seqno_per_order,
        'Setup': setup_per_order,
        'Start': begintijden,
        'Process': procestijden,
        'End': eindtijden,
        'Deadline': deadline_lijst,
        'Tardiness': tardiness_per_order,
        'Penalty': penalty_lijst,
        'Cost': penalty_per_order
    })

    # Excel bestand maken
    with pd.ExcelWriter(bestandsnaam) as writer:
        df_schedule.to_excel(writer, sheet_name='Schedule', index=False)

def random_swap(current):
    nieuwe_volgorde = current.copy()
    a = random.randint(0, len(nieuwe_volgorde) - 1)
    b = random.randint(0, len(nieuwe_volgorde) - 1)

    while a == b:
        b = random.randint(0, len(nieuwe_volgorde) - 1)

    nieuwe_volgorde[a], nieuwe_volgorde[b] = (nieuwe_volgorde[b], nieuwe_volgorde[a])

    return nieuwe_volgorde

def swap(volgorde, i, j):
    nieuwe_volgorde = volgorde.copy()
    nieuwe_volgorde[i], nieuwe_volgorde[j] = nieuwe_volgorde[j], nieuwe_volgorde[i]
    return nieuwe_volgorde

def plot_penalty(penalty_per_iteratie, beste_penalty_per_iteratie):
    plt.figure(figsize=(12, 6))

    plt.plot(penalty_per_iteratie, label='Penalty geteste swap')

    plt.plot(beste_penalty_per_iteratie, label='Beste penalty')

    plt.xlabel('Iteratie')
    plt.ylabel('Totale penalty')
    plt.title('Simulated Annealing')

    plt.legend()
    plt.grid()

    plt.show()

def gantt_chart_list(volgorde, di_orders, di_machines, machines_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty):
    '''
    Maakt een Gantt-chart van de planning.

    Elke horizontale rij stelt een machine voor.
    De setup-tijd en procestijd worden weergegeven.
    '''

    fig, ax = plt.subplots(figsize=(16, 7))

    kleur_dict = {
        'Red'   : 'red',
        'Blue'  : 'blue',
        'Green' : 'green',
        'Yellow': 'yellow',
        'Orange': 'orange',
        'Purple': 'purple',
        'Pink'  : 'pink',
        'Black' : 'black',
        'White' : 'white',
        'Grey'  : 'grey'
    }

    # Orders opzoeken via ordernummer
    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    for i in range(len(volgorde)):

        machine = machines_per_order[i]
        begintijd = begintijden[i]
        eindtijd = eindtijden[i]
        procestijd = procestijden[i]
        setup_tijd = setup_per_order[i]

        # Juiste order ophalen uit de volgorde
        order = orders[volgorde[i]]
        kleur_order = order['Colour']

        # Setup begint voor de productiestart
        setup_start = begintijd - setup_tijd

        # Setup-tijd tekenen
        if setup_tijd > 0:
            ax.barh(machine, setup_tijd, left=setup_start, height=0.6, color='lightgrey', edgecolor='black', hatch='//')

        # Rode rand als de order te laat is
        if tardiness_per_order[i] > 0:
            edgecolor = '#FF8888'
            linewidth = 2
        else:
            edgecolor = 'black'
            linewidth = 1

        # Productietijd tekenen
        ax.barh(machine, procestijd, left=begintijd, height=0.6, color=kleur_dict[kleur_order], edgecolor=edgecolor, linewidth=linewidth)

        # Ordernummer in de balk zetten
        ax.text(begintijd + procestijd / 2, machine, str(order['Order']), ha='center', va='center', fontsize=9)

    # Machine-namen op de y-as
    ax.set_yticks(range(len(di_machines)))
    ax.set_yticklabels([di_machines[i]['Machine'] for i in range(len(di_machines))])

    ax.grid(axis='x', linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    ax.set_xlabel('Tijd')
    ax.set_ylabel('Machine')
    ax.set_title('Gantt-chart planning')

    # Totale resultaten rechtsboven
    ax.text(1, 1, f'Totale penalty: {penalty:.2f}\nTotale tardiness: {sum(tardiness_per_order):.2f}', transform=ax.transAxes, ha='right', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.show()

def resultaten_naar_excel_list(volgorde, di_orders, di_machines, machines_per_order, seqno_per_order, setup_per_order, begintijden, procestijden, eindtijden, tardiness_per_order, penalty_per_order, bestandsnaam='Results_SA.xlsx'):
    '''
    Zet de Simulated Annealing planning in het vereiste Excel-format.

    Het Excel-bestand bevat één tabblad:
        Schedule
    '''

    # Orders opzoeken via ordernummer
    orders = {}

    for order in di_orders:
        orders[order['Order']] = order

    orders_lijst = []
    machine_lijst = []
    deadline_lijst = []
    penalty_lijst = []

    for i in range(len(volgorde)):

        # Juiste order ophalen uit de SA-volgorde
        order = orders[volgorde[i]]

        orders_lijst.append(order['Order'])
        machine_lijst.append(di_machines[machines_per_order[i]]['Machine'])
        deadline_lijst.append(order['Deadline'])
        penalty_lijst.append(order['Penalty'])

    df_schedule = pd.DataFrame({
        'Order': orders_lijst,
        'Machine': machine_lijst,
        'SeqNo': seqno_per_order,
        'Setup': setup_per_order,
        'Start': begintijden,
        'Process': procestijden,
        'End': eindtijden,
        'Deadline': deadline_lijst,
        'Tardiness': tardiness_per_order,
        'Penalty': penalty_lijst,
        'Cost': penalty_per_order
    })

    with pd.ExcelWriter(bestandsnaam) as writer:
        df_schedule.to_excel(writer, sheet_name='Schedule', index=False)