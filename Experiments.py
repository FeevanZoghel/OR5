"""PaintShop dashboard that executes the ORIGINAL function definitions from the four scripts.
Run from your OR5 directory: python -m streamlit run Experiments.py
"""
import ast
from io import BytesIO
from pathlib import Path
import math as m
import random
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from Functions import dictionary, random_swap, swap

st.set_page_config(page_title='PaintShop Experiments', page_icon='🎨', layout='wide')
st.markdown("""
<style>
.stApp {background: #f8faff; color: #142044;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#eef2ff 0%,#e5eafe 100%);}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {color:#16204b;}
.block-container {max-width: 1600px; padding-top: 1.7rem; padding-bottom: 2rem;}
.hero {background: linear-gradient(115deg,#fff 50%,#fbe6f4 74%,#dff5ff 100%);
       border:1px solid #e8e9f8;border-radius:20px;padding:24px 28px;margin-bottom:18px;}
.hero h1 {color:#101a47; font-size:2.45rem; margin:0 0 4px 0;}
.hero p {color:#576582; margin:0; font-size:1rem;}
.metric-card {min-height:114px;border:1px solid #e3e9f5;border-radius:15px;
              padding:17px 15px; box-shadow:0 2px 8px rgba(33,50,110,.025);}
.metric-card .name {font-size:.84rem;font-weight:650;color:#344165;}
.metric-card .value {font-size:1.85rem;font-weight:800;color:#101a47;margin-top:8px;}
.metric-card .emoji {font-size:1.3rem;margin-bottom:4px;}
.metric-blue {background:#eaf2ff;} .metric-green {background:#e9faef;}
.metric-yellow {background:#fff6df;} .metric-pink {background:#ffebf0;}
.metric-purple {background:#f0eaff;} .metric-cyan {background:#e6f9fa;}
.section-title {font-size:1.2rem;font-weight:750;color:#14204b;margin:10px 0 12px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:#e5eaf6!important;border-radius:16px!important;}
div.stButton > button[kind="primary"] {background:linear-gradient(100deg,#7350ff,#6936f2);border:0;
       color:white;border-radius:11px;font-weight:700;min-height:49px;}
div.stButton > button[kind="primary"]:hover {background:#5c2cdb;color:white;}
[data-testid="stTabs"] button[aria-selected="true"] {color:#6d40ef!important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:#6d40ef!important;}
[data-testid="stFileUploader"] {border-radius:13px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><h1>🎨 PaintShop | Experiments</h1>
<p>Experimenteer met jullie oorspronkelijke Greedy- en Simulated Annealing-functies.</p>
</div>""", unsafe_allow_html=True)

FILES = {
    'Greedy': 'Greedy.py',
    'Improved Greedy': 'Improved_greedy.py',
    'Simulated Annealing': 'Metaheuristic.py',
    'Improved Simulated Annealing': 'Improved_metaheuristic.py',
}
COLUMNS = ['Order', 'Machine', 'SeqNo', 'Setup', 'Start', 'Process', 'End',
           'Deadline', 'Tardiness', 'Penalty', 'Cost']
REQUIRED = {
    'Orders': ['Order', 'Surface', 'Colour', 'Deadline', 'Penalty'],
    'Machines': ['Machine', 'Speed'],
    'Setups': ['From colour', 'To colour', 'Setup time'],
}


def original_functions(filename, globals_for_functions):
    """Load only original function definitions; skip fixed Excel reads and script execution."""
    path = Path(__file__).resolve().parent / filename
    source = path.read_text(encoding='utf-8-sig')
    tree = ast.parse(source, filename=str(path))
    definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    module = ast.fix_missing_locations(ast.Module(body=definitions, type_ignores=[]))
    namespace = {'__builtins__': __builtins__, 'pd': pd, 'np': np, 'random': random,
                 'm': m, 'plt': plt, 'dictionary': dictionary,
                 'random_swap': random_swap, 'swap': swap}
    namespace.update(globals_for_functions)
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace


def validate(sheets):
    for sheet, columns in REQUIRED.items():
        if sheet not in sheets:
            raise ValueError(f"Tabblad '{sheet}' ontbreekt.")
        missing = [col for col in columns if col not in sheets[sheet].columns]
        if missing:
            raise ValueError(f"Ontbrekende kolommen in {sheet}: {', '.join(missing)}")
        if sheets[sheet][columns].isna().any().any():
            raise ValueError(f"Lege waarden in {sheet}.")
    if sheets['Orders'].empty or sheets['Machines'].empty:
        raise ValueError('Orders en Machines mogen niet leeg zijn.')
    if sheets['Orders']['Order'].duplicated().any():
        raise ValueError('Order-nummers moeten uniek zijn.')
    if (pd.to_numeric(sheets['Machines']['Speed'], errors='coerce') <= 0).any():
        raise ValueError('Machine speed must be greater than zero.')


def schedule_table(order_sequence, result, orders, machines):
    _, _, machine_indices, seqnos, setups, starts, processes, ends, tardiness, costs = result
    order_lookup = {order['Order']: order for order in orders}
    rows = []
    for i, number in enumerate(order_sequence):
        order = order_lookup[number]
        rows.append({'Order': number, 'Machine': machines[machine_indices[i]]['Machine'],
                     'SeqNo': seqnos[i], 'Setup': setups[i], 'Start': starts[i],
                     'Process': processes[i], 'End': ends[i], 'Deadline': order['Deadline'],
                     'Tardiness': tardiness[i], 'Penalty': order['Penalty'], 'Cost': costs[i],
                     'Colour': order['Colour']})
    return pd.DataFrame(rows)


def gantt(schedule, machines):
    colours = {'Red': '#ff6464', 'Blue': 'blue', 'Green': 'green', 'Yellow': 'yellow',
               'Orange': 'orange', 'Purple': 'purple', 'Pink': 'pink', 'Black': 'black',
               'White': 'white', 'Grey': 'grey'}
    fig, ax = plt.subplots(figsize=(13, max(4, len(machines) * 0.8 + 1)))
    machine_names = [machine['Machine'] for machine in machines]
    setup_seen = late_seen = False
    for row in schedule.to_dict('records'):
        y = machine_names.index(row['Machine'])
        if row['Setup'] > 0:
            ax.barh(y, row['Setup'], left=row['Start'] - row['Setup'], height=.6,
                    color='lightgrey', edgecolor='black', hatch='//',
                    label='Setup tijd' if not setup_seen else None)
            setup_seen = True
        late = row['Tardiness'] > 0
        ax.barh(y, row['Process'], left=row['Start'], height=.6,
                color=colours.get(str(row['Colour']), '#8ca8d6'),
                edgecolor='red' if late else 'black', linewidth=2 if late else 1,
                label='Order met penalty' if late and not late_seen else None)
        late_seen |= late
        ax.text(row['Start'] + row['Process'] / 2, y, str(row['Order']),
                ha='center', va='center', fontsize=8)
    ax.set_yticks(range(len(machine_names)), machine_names)
    ax.set_xlabel('Tijd')
    ax.set_ylabel('Machine')
    ax.set_title('Gantt-chart planning')
    ax.grid(axis='x', alpha=.3)
    ax.set_axisbelow(True)
    if setup_seen or late_seen:
        ax.legend()
    fig.tight_layout()
    return fig


def excel_file(schedule, settings, penalty, tardiness, duration):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        schedule[COLUMNS].to_excel(writer, sheet_name='Schedule', index=False)
        pd.DataFrame([{'Total penalty': penalty, 'Total tardiness': tardiness,
                       'Runtime (s)': duration, **settings}]).to_excel(
                           writer, sheet_name='Experiment', index=False)
    return buffer.getvalue()


with st.sidebar:
    st.markdown('### 🎨 PaintShop Experiments')
    st.markdown('#### 1. Excelbestand uploaden')
    upload = st.file_uploader('Excelbestand', type='xlsx', label_visibility='collapsed')
    st.markdown('#### 2. Kies methode')
    method = st.radio('Optimalisatiemethode', list(FILES), index=3, label_visibility='collapsed')
    uses_sa = method in ('Simulated Annealing', 'Improved Simulated Annealing')
    if uses_sa:
        st.markdown('#### 3. Parameters')
        st.markdown('**Simulated Annealing**')
        t_max = st.number_input('t_max', min_value=1, value=1000, step=100)
        cooling_factor = st.number_input('cooling_factor', min_value=0.0001,
                                         max_value=1.0, value=0.99, format='%.4f')
        cooling_it = st.number_input('cooling_it', min_value=1, value=1000, step=100)
        temp = st.number_input('temp', min_value=0.0001, value=1000.0, step=100.0)
        seed = st.number_input('Random seed', min_value=0, value=42, step=1)
    if method == 'Improved Simulated Annealing':
        st.markdown('**Improving Search**')
        improve_iterations = st.number_input('Aantal verbeteriteraties',
                                             min_value=0, value=1000, step=100)
    with st.expander('⚙️ Geavanceerd'):
        st.caption('Gebruik dezelfde random seed om experimenten reproduceerbaar te vergelijken.')
    solve = st.button('🚀 Solve  ▶', type='primary', use_container_width=True,
                      disabled=upload is None)

if upload is None:
    st.info('Upload een Excelbestand met Orders, Machines en Setups.')
    st.stop()

try:
    sheets = pd.read_excel(upload, sheet_name=None)
    validate(sheets)
    orders = dictionary(sheets['Orders'])
    machines = dictionary(sheets['Machines'])
    setups = dictionary(sheets['Setups'])
except Exception as exc:
    st.error(f'Invoerfout: {exc}')
    st.stop()

def metric_card(name, value, emoji, style):
    st.markdown(f'<div class="metric-card metric-{style}">'
                f'<div class="emoji">{emoji}</div><div class="name">{name}</div>'
                f'<div class="value">{value}</div></div>', unsafe_allow_html=True)


with st.expander('📁 Ingevoerde gegevens'):
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
        di_orders = sorted(orders, key=lambda order: order['Deadline'])
        namespace = original_functions(FILES[method], {
            'di_orders': di_orders, 'di_machines': machines, 'di_setups': setups,
            't_max': int(t_max) if uses_sa else None,
            'cooling_factor': float(cooling_factor) if uses_sa else None,
            'cooling_it': int(cooling_it) if uses_sa else None,
            'temp': float(temp) if uses_sa else None,
        })
        history_tested, history_best = [], []
        if method == 'Greedy':
            order_list = di_orders.copy()
            per_machine, _ = namespace['greedy_schedule'](order_list, machines, setups)
            result = namespace['calculate_results'](per_machine, order_list, machines, setups)
            sequence = [order['Order'] for order in order_list]
        elif method == 'Improved Greedy':
            _, _, best_orders, history_tested, history_best = namespace['improving_search'](di_orders)
            order_list = best_orders.copy()
            per_machine, _ = namespace['greedy_schedule'](order_list.copy(), machines, setups)
            result = namespace['calculate_results'](per_machine, order_list, machines, setups)
            sequence = [order['Order'] for order in order_list]
        else:
            random.seed(int(seed))
            np.random.seed(int(seed))
            if method == 'Simulated Annealing':
                sequence, _ = namespace['SA'](sheets['Orders'], int(t_max),
                                              float(cooling_factor), int(cooling_it), float(temp))
            else:
                _, sequence, history_tested, history_best = namespace['meta_improving_search'](
                    sheets['Orders'], int(improve_iterations))
            result = namespace['calculate_tard_pen'](sequence, di_orders, machines, setups)
        schedule = schedule_table(sequence, result, di_orders, machines)
        duration = time.perf_counter() - started
        st.session_state['paintshop_result'] = {
            'key': run_key, 'schedule': schedule, 'machines': machines,
            'penalty': result[1], 'tardiness': result[0], 'duration': duration,
            'sequence': sequence, 'tested': history_tested, 'best': history_best,
            'settings': settings,
        }
    except Exception as exc:
        st.error(f'Oplossen mislukt: {exc}')
        st.stop()

result = st.session_state.get('paintshop_result')

st.markdown('<div class="section-title">📊 Experimentoverzicht</div>', unsafe_allow_html=True)
metrics = st.columns(6, gap='small')
values = [
    ('Orders', str(len(orders)), '📄', 'blue'),
    ('Machines', str(len(machines)), '⚙️', 'green'),
    ('Setup-overgangen', str(len(setups)), '🔁', 'yellow'),
    ('Totale penalty', f"{result['penalty']:,.2f}" if result else '—', '🎯', 'pink'),
    ('Totale tardiness', f"{result['tardiness']:,.2f}" if result else '—', '🕒', 'purple'),
    ('Rekentijd', f"{result['duration']:.3f} s" if result else '—', '⏱️', 'cyan'),
]
for column, (name, value, emoji, style) in zip(metrics, values):
    with column:
        metric_card(name, value, emoji, style)

if result is None:
    st.info('Stel links de parameters in en klik op 🚀 Solve om de planning te berekenen.')
else:
    if result['key'] != run_key:
        st.warning('De instellingen zijn gewijzigd. Klik opnieuw op Solve om nieuwe resultaten te berekenen.')
    st.write('')
    tab_plan, tab_table, tab_history, tab_orders = st.tabs([
        '📊 Planning (Gantt-chart)', '📋 Schedule (tabel)',
        '📈 Optimalisatieverloop', '☷ Ordervolgorde'
    ])
    with tab_plan:
        left, right = st.columns([1.65, 1], gap='medium')
        with left:
            with st.container(border=True):
                st.markdown('#### 📊 Gantt-chart planning')
                fig = gantt(result['schedule'], result['machines'])
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)
        with right:
            with st.container(border=True):
                st.markdown('#### 📈 Optimalisatieverloop')
                if result['tested'] or result['best']:
                    data = {}
                    if result['tested']:
                        data['Geteste penalty'] = pd.Series(result['tested'], dtype=float)
                    if result['best']:
                        data['Beste penalty'] = pd.Series(result['best'], dtype=float)
                    st.line_chart(pd.DataFrame(data), height=370,
                                  x_label='Iteratie', y_label='Penalty')
                    st.caption('Bij Improved Greedy wordt de beste penalty per ronde opgeslagen; '
                               'bij Improved SA komt de historie uit de improving search.')
                else:
                    st.info('Deze methode registreert geen optimalisatiegeschiedenis.')
        st.markdown('#### 📋 Schedule')
        st.dataframe(result['schedule'][COLUMNS], hide_index=True,
                     use_container_width=True, height=300)
    with tab_table:
        st.markdown('#### Volledige planning')
        search = st.text_input('🔎 Zoek order', placeholder='Bijvoorbeeld ORD13')
        table = result['schedule'][COLUMNS]
        if search:
            table = table[table['Order'].astype(str).str.contains(search, case=False, regex=False)]
        st.dataframe(table, hide_index=True, use_container_width=True, height=490)
    with tab_history:
        st.markdown('#### Optimalisatieverloop')
        if result['tested'] or result['best']:
            data = {}
            if result['tested']:
                data['Geteste penalty'] = pd.Series(result['tested'], dtype=float)
            if result['best']:
                data['Beste penalty'] = pd.Series(result['best'], dtype=float)
            st.line_chart(pd.DataFrame(data), x_label='Iteratie', y_label='Penalty')
        else:
            st.info('De oorspronkelijke methode slaat geen penaltygeschiedenis per iteratie op.')
    with tab_orders:
        st.markdown('#### Ordervolgorde')
        st.write(' → '.join(map(str, result['sequence'])))
        st.caption('De volgorde is overgenomen uit het resultaat van jullie oorspronkelijke algoritme.')
    st.download_button('⬇️ Download Excel', data=excel_file(
        result['schedule'], result['settings'], result['penalty'],
        result['tardiness'], result['duration']),
        file_name='PaintShop_Experiment_Results.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
