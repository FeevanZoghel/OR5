import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

"""PaintShop experiment dashboard, based on the four original OR5 algorithms.
Run from OR5: python -m streamlit run Experiments.py
"""
from io import BytesIO
import math
import random
import time


st.set_page_config(page_title='PaintShop Experiments', page_icon='🎨', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.8rem;max-width:1450px}
[data-testid="stMetric"]{background:#f3f5f9;padding:14px;border-radius:10px}</style>''', unsafe_allow_html=True)

REQUIRED = {
    'Orders': ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty'],
    'Machines': ['Machine', 'Speed'],
    'Setups': ['From colour', 'To colour', 'Setup time'],
}
COLUMNS = ['Order', 'Machine', 'SeqNo', 'Setup', 'Start', 'Process', 'End',
           'Deadline', 'Tardiness', 'Penalty', 'Cost']


def load_workbook(upload):
    sheets = pd.read_excel(upload, sheet_name=None)
    for sheet, columns in REQUIRED.items():
        if sheet not in sheets:
            raise ValueError(f"Tabblad '{sheet}' ontbreekt.")
        missing = [c for c in columns if c not in sheets[sheet].columns]
        if missing:
            raise ValueError(f"Ontbrekende kolommen in {sheet}: {', '.join(missing)}")
        if sheets[sheet][columns].isna().any().any():
            raise ValueError(f"Lege waarden gevonden in tabblad '{sheet}'.")
    orders = sheets['Orders'][REQUIRED['Orders']].to_dict('records')
    machines = sheets['Machines'][REQUIRED['Machines']].to_dict('records')
    setups = sheets['Setups'][REQUIRED['Setups']].to_dict('records')
    if not orders or not machines:
        raise ValueError('Er moet minstens één order en machine zijn.')
    if len(set(o['Order'] for o in orders)) != len(orders):
        raise ValueError('Order-nummers moeten uniek zijn.')
    for o in orders:
        for col in ['Surface', 'Deadline', 'Penalty']:
            if not math.isfinite(float(o[col])):
                raise ValueError(f'Ongeldige {col} bij order {o["Order"]}.')
        if float(o['Surface']) < 0 or float(o['Penalty']) < 0:
            raise ValueError('Surface en Penalty mogen niet negatief zijn.')
    for machine in machines:
        if not math.isfinite(float(machine['Speed'])) or float(machine['Speed']) <= 0:
            raise ValueError(f"Machine speed must be greater than zero: {machine['Machine']}")
    for setup in setups:
        if not math.isfinite(float(setup['Setup time'])) or float(setup['Setup time']) < 0:
            raise ValueError('Setup time moet niet-negatief zijn.')
    return sheets, orders, machines, setups


def calculate_tard_pen(volgorde, di_orders, di_machines, di_setups):
    """Same machine selection, setup, tardiness and penalty as Metaheuristic.py."""
    tijden = [0.0] * len(di_machines)
    vorige_kleuren = [None] * len(di_machines)
    sequence_numbers = [0] * len(di_machines)
    orders = {order['Order']: order for order in di_orders}
    resultaten = []
    for nummer in volgorde:
        order = orders[nummer]
        laagste_tijd = min(tijden)
        mogelijke_machines = [i for i in range(len(di_machines)) if tijden[i] == laagste_tijd]
        machine_index = mogelijke_machines[0]
        for i in mogelijke_machines:
            if di_machines[i]['Speed'] > di_machines[machine_index]['Speed']:
                machine_index = i
        kleur = order['Colour']
        setup_tijd = 0.0
        if vorige_kleuren[machine_index] is not None and kleur != vorige_kleuren[machine_index]:
            for setup in di_setups:
                if setup['From colour'] == vorige_kleuren[machine_index] and setup['To colour'] == kleur:
                    setup_tijd = float(setup['Setup time'])
                    break
            else:
                raise ValueError(f'Geen setup gevonden van {vorige_kleuren[machine_index]} naar {kleur}')
        tijden[machine_index] += setup_tijd
        begintijd = tijden[machine_index]
        procestijd = float(order['Surface']) / float(di_machines[machine_index]['Speed'])
        tijden[machine_index] += procestijd
        eindtijd = tijden[machine_index]
        sequence_numbers[machine_index] += 1
        tardiness = max(0.0, eindtijd - float(order['Deadline']))
        cost = tardiness * float(order['Penalty'])
        resultaten.append({
            'Order': nummer, 'Machine': di_machines[machine_index]['Machine'],
            'SeqNo': sequence_numbers[machine_index], 'Setup': setup_tijd,
            'Start': begintijd, 'Process': procestijd, 'End': eindtijd,
            'Deadline': order['Deadline'], 'Tardiness': tardiness,
            'Penalty': order['Penalty'], 'Cost': cost, 'Colour': kleur,
        })
        vorige_kleuren[machine_index] = kleur
    return pd.DataFrame(resultaten)


def greedy_sequence(orders):
    return [o['Order'] for o in sorted(orders, key=lambda o: o['Deadline'])]


def swap(sequence, i, j):
    candidate = sequence.copy()
    candidate[i], candidate[j] = candidate[j], candidate[i]
    return candidate


def random_swap(sequence, rng):
    if len(sequence) < 2:
        return sequence.copy()
    i, j = rng.sample(range(len(sequence)), 2)
    return swap(sequence, i, j)


def improved_greedy(orders, penalty_of):
    """Exhaustive best-improvement swaps, matching Improved_greedy.py."""
    best = greedy_sequence(orders)
    best_penalty = penalty_of(best)
    tested, best_history = [], []
    while True:
        round_best = best.copy()
        round_penalty = best_penalty
        improved = False
        for i in range(len(best)):
            for j in range(i + 1, len(best)):
                candidate = swap(best, i, j)
                penalty = penalty_of(candidate)
                tested.append(penalty)
                if penalty < round_penalty:
                    round_penalty = penalty
                    round_best = candidate.copy()
                    improved = True
        best_history.append(round_penalty)
        if not improved:
            break
        best, best_penalty = round_best, round_penalty
    return best, tested, best_history


def simulated_annealing(orders, penalty_of, t_max, cooling_factor, cooling_it, temp, rng):
    """Acceptance and cooling rules of Metaheuristic.py / Improved_metaheuristic.py."""
    current = [o['Order'] for o in orders]
    rng.shuffle(current)
    current_penalty = penalty_of(current)
    best = current.copy()
    best_penalty = current_penalty
    tested, best_history = [], []
    for i in range(t_max):
        candidate = random_swap(current, rng)
        new_penalty = penalty_of(candidate)
        tested.append(new_penalty)
        verschil = current_penalty - new_penalty
        if verschil > 0:
            current, current_penalty = candidate.copy(), new_penalty
        else:
            kans = math.exp(verschil / temp)
            if rng.random() < kans:
                current, current_penalty = candidate.copy(), new_penalty
        if current_penalty < best_penalty:
            best, best_penalty = current.copy(), current_penalty
        best_history.append(best_penalty)
        if (i + 1) % cooling_it == 0:
            temp *= cooling_factor
    return best, best_penalty, tested, best_history


def improved_metaheuristic(best, best_penalty, penalty_of, iterations, rng):
    """Random improving swaps, matching Improved_metaheuristic.py (not hill climbing)."""
    tested, best_history = [], []
    for _ in range(iterations):
        candidate = random_swap(best, rng)
        penalty = penalty_of(candidate)
        tested.append(penalty)
        if penalty < best_penalty:
            best, best_penalty = candidate.copy(), penalty
        best_history.append(best_penalty)
    return best, best_penalty, tested, best_history


def gantt(schedule, machines):
    fig, ax = plt.subplots(figsize=(14, max(4, len(machines) * 0.8 + 1)))
    names = [m['Machine'] for m in machines]
    colour_map = {'Red': '#ff6464', 'Blue': 'blue', 'Green': 'green',
                  'Yellow': 'yellow', 'Orange': 'orange', 'Purple': 'purple',
                  'Pink': 'pink', 'Black': 'black', 'White': 'white', 'Grey': 'grey'}
    setup_labeled = late_labeled = False
    for row in schedule.to_dict('records'):
        y = names.index(row['Machine'])
        if row['Setup'] > 0:
            ax.barh(y, row['Setup'], left=row['Start'] - row['Setup'], height=0.6,
                    color='lightgrey', edgecolor='black', hatch='//',
                    label='Setup tijd' if not setup_labeled else None)
            setup_labeled = True
        late = row['Tardiness'] > 0
        ax.barh(y, row['Process'], left=row['Start'], height=0.6,
                color=colour_map.get(str(row['Colour']), '#8ca8d6'),
                edgecolor='red' if late else 'black', linewidth=2 if late else 1,
                label='Order met penalty' if late and not late_labeled else None)
        late_labeled |= late
        ax.text(row['Start'] + row['Process'] / 2, y, str(row['Order']),
                ha='center', va='center', fontsize=8)
    ax.set_yticks(range(len(names)), [str(n) for n in names])
    ax.set_xlabel('Tijd')
    ax.set_ylabel('Machine')
    ax.set_title('Gantt-chart planning')
    ax.grid(axis='x', linestyle='--', alpha=0.35)
    ax.set_axisbelow(True)
    if setup_labeled or late_labeled:
        ax.legend()
    fig.tight_layout()
    return fig


def to_excel(schedule, method, total_penalty, total_tardiness, runtime, settings):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        schedule[COLUMNS].to_excel(writer, sheet_name='Schedule', index=False)
        summary = {'Method': method, 'Total penalty': total_penalty,
                   'Total tardiness': total_tardiness, 'Runtime (s)': runtime, **settings}
        pd.DataFrame([summary]).to_excel(writer, sheet_name='Experiment', index=False)
    return buffer.getvalue()


st.title('🎨 PaintShop | Optimization Experiments')
st.caption('Experimenteer met de vier algoritmes uit jullie Operations Research-project.')
with st.sidebar:
    st.header('Instellingen')
    upload = st.file_uploader('Upload PaintShop Excel', type='xlsx')
    method = st.selectbox('Methode', ['Greedy', 'Improved Greedy', 'Simulated Annealing', 'Improved Simulated Annealing'])
    uses_sa = 'Simulated Annealing' in method
    if uses_sa:
        st.subheader('Simulated Annealing')
        t_max = st.number_input('t_max', min_value=1, value=1000, step=100)
        cooling_factor = st.number_input('cooling_factor', min_value=0.0001, max_value=1.0, value=0.99, step=0.01, format='%.4f')
        cooling_it = st.number_input('cooling_it', min_value=1, value=1000, step=100)
        temp = st.number_input('temp', min_value=0.0001, value=1000.0, step=100.0)
        seed = st.number_input('Random seed', min_value=0, value=42, step=1,
                               help='Gebruik dezelfde seed om instellingen eerlijk te vergelijken.')
    if method == 'Improved Simulated Annealing':
        improve_iterations = st.number_input('Improving search iteraties', min_value=0, value=1000, step=100)
    solve = st.button('▶ Solve', type='primary', use_container_width=True, disabled=upload is None)

if upload is None:
    st.info('Upload een Excelbestand met de tabbladen Orders, Machines en Setups.')
    st.stop()
try:
    sheets, orders, machines, setups = load_workbook(upload)
except Exception as exc:
    st.error(str(exc))
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric('Orders', len(orders))
c2.metric('Machines', len(machines))
c3.metric('Setup-overgangen', len(setups))
with st.expander('Bekijk de ingevoerde gegevens'):
    for sheet in REQUIRED:
        st.markdown(f'**{sheet}**')
        st.dataframe(sheets[sheet], hide_index=True, use_container_width=True)

settings = {'Methode': method}
if uses_sa:
    settings.update({'t_max': int(t_max), 'cooling_factor': float(cooling_factor),
                     'cooling_it': int(cooling_it), 'temp': float(temp), 'seed': int(seed)})
if method == 'Improved Simulated Annealing':
    settings['improve_iterations'] = int(improve_iterations)
run_key = (upload.getvalue(), tuple(settings.items()))

if solve:
    try:
        started = time.perf_counter()
        def penalty_of(sequence):
            return float(calculate_tard_pen(sequence, orders, machines, setups)['Cost'].sum())
        rng = random.Random(int(seed)) if uses_sa else None
        if method == 'Greedy':
            best = greedy_sequence(orders)
            tested, best_history = [], [penalty_of(best)]
        elif method == 'Improved Greedy':
            best, tested, best_history = improved_greedy(orders, penalty_of)
        else:
            best, best_penalty, tested, best_history = simulated_annealing(
                orders, penalty_of, int(t_max), float(cooling_factor), int(cooling_it), float(temp), rng)
            if method == 'Improved Simulated Annealing':
                best, best_penalty, extra_tested, extra_best = improved_metaheuristic(
                    best, best_penalty, penalty_of, int(improve_iterations), rng)
                tested += extra_tested
                best_history += extra_best
        schedule = calculate_tard_pen(best, orders, machines, setups)
        duration = time.perf_counter() - started
        st.session_state['result'] = {
            'key': run_key, 'schedule': schedule, 'machines': machines,
            'penalty': float(schedule['Cost'].sum()),
            'tardiness': float(schedule['Tardiness'].sum()),
            'duration': duration, 'method': method, 'sequence': best,
            'tested': tested, 'best_history': best_history, 'settings': settings,
        }
    except Exception as exc:
        st.error(f'Oplossen mislukt: {exc}')
        st.stop()

result = st.session_state.get('result')
if result:
    if result['key'] != run_key:
        st.warning('De invoer of instellingen zijn gewijzigd. Klik opnieuw op Solve.')
    st.divider()
    st.subheader('Resultaten')
    a, b, c = st.columns(3)
    a.metric('Totale penalty', f"{result['penalty']:.2f}")
    b.metric('Totale tardiness', f"{result['tardiness']:.2f}")
    c.metric('Rekentijd', f"{result['duration']:.3f} s")
    st.caption('Beste ordervolgorde: ' + ' → '.join(map(str, result['sequence'])))
    tab_gantt, tab_schedule, tab_history = st.tabs(['Gantt-chart', 'Schedule', 'Optimalisatieverloop'])
    with tab_gantt:
        fig = gantt(result['schedule'], result['machines'])
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    with tab_schedule:
        st.dataframe(result['schedule'][COLUMNS], hide_index=True, use_container_width=True)
    with tab_history:
        if result['tested']:
            st.line_chart(pd.DataFrame({'Geteste penalty': result['tested']}))
        if result['best_history']:
            st.line_chart(pd.DataFrame({'Beste penalty': result['best_history']}))
        else:
            st.info('Greedy heeft geen iteratief optimalisatieverloop.')
    st.download_button('⬇ Download resultaten als Excel',
        data=to_excel(result['schedule'], result['method'], result['penalty'],
                      result['tardiness'], result['duration'], result['settings']),
        file_name='PaintShop_Experiment_Results.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
else:
    st.info('Kies een methode en klik op Solve.')
