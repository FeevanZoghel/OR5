
"""PaintShop dashboard met donker thema en originele algoritmes."""

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


# ============================================================
# PAGINA EN DONKER THEMA
# ============================================================

st.set_page_config(
    page_title="PaintShop Experiments",
    page_icon="🎨",
    layout="wide"
)

st.markdown("""
<style>
:root {
    color-scheme: dark;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #080f1e !important;
    color: #edf3ff !important;
}

[data-testid="stHeader"] {
    background: #080f1e !important;
}

.block-container {
    max-width: 1540px;
    padding: 1.35rem 1.7rem 3rem;
}

/* ZIJBALK */

[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background: linear-gradient(170deg, #151f35, #0c1526) !important;
    border-right: 1px solid #2b3853;
}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label {
    color: #e6eeff !important;
}

[data-testid="stSidebar"] h3 {
    color: #9fc4ff !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] {
    background: #192741 !important;
    border: 1px solid #374a6b !important;
    border-radius: 12px !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
    color: #dfeaff !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: #1a2944 !important;
    border: 1px solid #344766 !important;
    border-radius: 9px !important;
    padding: 8px 10px !important;
    margin-bottom: 5px !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(90deg, #6438ed, #442bb0) !important;
    border-color: #aa8aff !important;
    box-shadow: 0 0 12px #7655fa55;
}

[data-testid="stSidebar"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-baseweb="input"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
    background: #111d33 !important;
    color: #fff !important;
}

[data-testid="stSidebar"] [data-baseweb="input"] * {
    color: #fff !important;
}

[data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(95deg, #8c4dff, #5929e8) !important;
    color: white !important;
    border: 1px solid #ad83ff !important;
    border-radius: 12px !important;
    font-weight: 750;
    min-height: 52px;
}

[data-testid="stSidebar"] button[kind="primary"] * {
    color: white !important;
}

/* HOOFDPAGINA */

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color: #edf3ff;
}

[data-testid="stMain"] [data-testid="stExpander"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #111c30 !important;
    border-color: #2b3a57 !important;
    border-radius: 14px !important;
}

[data-testid="stMain"] [data-testid="stTabs"] button {
    color: #bbc9e7 !important;
}

[data-testid="stMain"] [data-testid="stTabs"] button[aria-selected="true"] {
    color: #bd9cff !important;
}

[data-testid="stMain"] [data-baseweb="tab-highlight"] {
    background: #9155ff !important;
}

[data-testid="stMain"] [data-testid="stDataFrame"] {
    border: 1px solid #344462 !important;
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stMain"] [data-baseweb="input"],
[data-testid="stMain"] [data-baseweb="input"] input {
    background: #18263d !important;
    color: #fff !important;
}

[data-testid="stMain"] button {
    border-radius: 10px;
}

/* HEADER */

.hero {
    background: linear-gradient(
        112deg,
        #121e34 40%,
        #211b47 75%,
        #102c43 100%
    );
    border: 1px solid #31415e;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}

.hero:after {
    content: "🎨";
    position: absolute;
    right: 35px;
    top: 12px;
    font-size: 78px;
    opacity: .22;
}

.hero h1 {
    color: #f5f6ff;
    font-size: clamp(1.7rem, 3vw, 2.6rem);
    margin: 0 0 8px;
}

.hero h1 span {
    color: #ae83ff;
}

.hero p {
    color: #b7c6e3;
    margin: 0;
}

/* STATISTIEKKAARTEN */

.kpi {
    border: 1px solid var(--stroke);
    border-radius: 14px;
    padding: 15px 14px;
    min-height: 124px;
    background: linear-gradient(140deg, var(--bg), #111c31);
    box-shadow: 0 6px 20px #00000022;
}

.kpi-icon {
    font-size: 1.5rem;
    margin-bottom: 7px;
}

.kpi-name {
    font-size: .78rem;
    color: #d7e3f9;
    font-weight: 600;
}

.kpi-value {
    font-size: clamp(1.15rem, 1.7vw, 1.75rem);
    font-weight: 800;
    color: white;
    margin-top: 5px;
    overflow-wrap: anywhere;
}

.kpi-blue {
    --bg: #193566;
    --stroke: #285bb5;
}

.kpi-green {
    --bg: #124c45;
    --stroke: #178a75;
}

.kpi-yellow {
    --bg: #594420;
    --stroke: #987027;
}

.kpi-pink {
    --bg: #54263c;
    --stroke: #ab436a;
}

.kpi-purple {
    --bg: #3e2869;
    --stroke: #7046b7;
}

.kpi-cyan {
    --bg: #14465a;
    --stroke: #197c9e;
}

.section-heading {
    font-weight: 750;
    font-size: 1.2rem;
    color: #eaf0ff;
    margin: 16px 0 12px;
}

@media(max-width: 900px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 18px;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎨 PaintShop | <span>Experiments</span></h1>
    <p>
        Experimenteer met jullie oorspronkelijke
        Greedy- en Simulated Annealing-functies.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BESTANDEN EN KOLOMMEN
# ============================================================

FILES = {
    "Greedy": "Greedy.py",
    "Improved Greedy": "Improved_greedy.py",
    "Simulated Annealing": "Metaheuristic.py",
    "Improved Simulated Annealing": "Improved_metaheuristic.py",
}

COLUMNS = [
    "Order", "Machine", "SeqNo", "Setup",
    "Start", "Process", "End", "Deadline",
    "Tardiness", "Penalty", "Cost"
]

REQUIRED = {
    "Orders": [
        "Order", "Surface", "Colour", "Deadline", "Penalty"
    ],
    "Machines": [
        "Machine", "Speed"
    ],
    "Setups": [
        "From colour", "To colour", "Setup time"
    ],
}


# ============================================================
# ORIGINELE FUNCTIES INLADEN
# ============================================================

def original_functions(filename, globals_for_functions):
    """
    Laadt alleen de functiedefinities uit jullie scripts.
    De vaste Excel-inleesregels worden niet uitgevoerd.
    """

    path = Path(__file__).resolve().parent / filename

    source = path.read_text(encoding="utf-8-sig")

    tree = ast.parse(source, filename=str(path))

    definitions = [
        node for node in tree.body
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
    ]

    module = ast.fix_missing_locations(
        ast.Module(body=definitions, type_ignores=[])
    )

    namespace = {
        "__builtins__": __builtins__,
        "pd": pd,
        "np": np,
        "random": random,
        "m": m,
        "plt": plt,
        "dictionary": dictionary,
        "random_swap": random_swap,
        "swap": swap,
    }

    namespace.update(globals_for_functions)

    exec(
        compile(module, str(path), "exec"),
        namespace
    )

    return namespace


# ============================================================
# EXCEL VALIDATIE
# ============================================================

def validate(sheets):

    for sheet, columns in REQUIRED.items():

        if sheet not in sheets:
            raise ValueError(
                f"Tabblad '{sheet}' ontbreekt."
            )

        missing = [
            col for col in columns
            if col not in sheets[sheet].columns
        ]

        if missing:
            raise ValueError(
                f"Ontbrekende kolommen in {sheet}: "
                f"{', '.join(missing)}"
            )

        if sheets[sheet][columns].isna().any().any():
            raise ValueError(
                f"Lege waarden in {sheet}."
            )

    if sheets["Orders"].empty or sheets["Machines"].empty:
        raise ValueError(
            "Orders en Machines mogen niet leeg zijn."
        )

    if sheets["Orders"]["Order"].duplicated().any():
        raise ValueError(
            "Order-nummers moeten uniek zijn."
        )

    speeds = pd.to_numeric(
        sheets["Machines"]["Speed"],
        errors="coerce"
    )

    if speeds.isna().any() or (speeds <= 0).any():
        raise ValueError(
            "Machine speed must be greater than zero."
        )


# ============================================================
# RESULTATEN OMZETTEN NAAR TABEL
# ============================================================

def schedule_table(order_sequence, result, orders, machines):

    (
        _, _, machine_indices, seqnos, setups,
        starts, processes, ends, tardiness, costs
    ) = result

    order_lookup = {
        order["Order"]: order
        for order in orders
    }

    rows = []

    for i, number in enumerate(order_sequence):

        order = order_lookup[number]

        rows.append({
            "Order": number,
            "Machine": machines[machine_indices[i]]["Machine"],
            "SeqNo": seqnos[i],
            "Setup": setups[i],
            "Start": starts[i],
            "Process": processes[i],
            "End": ends[i],
            "Deadline": order["Deadline"],
            "Tardiness": tardiness[i],
            "Penalty": order["Penalty"],
            "Cost": costs[i],
            "Colour": order["Colour"]
        })

    return pd.DataFrame(rows)


# ============================================================
# DONKERE GANTT-CHART
# ============================================================

def gantt(schedule, machines):
    """
    Donkere Gantt-chart.
    Planningsberekeningen blijven ongewijzigd.
    """

    palette = {
        "Red": "#fb5473",
        "Blue": "#238dff",
        "Green": "#22cc85",
        "Yellow": "#ffcf3b",
        "Orange": "#ff9b24",
        "Purple": "#a36cff",
        "Pink": "#ff8ccf",
        "Black": "#596378",
        "White": "#d8e8ff",
        "Grey": "#a7b1c6"
    }

    fig, ax = plt.subplots(
        figsize=(12, max(4.4, len(machines) * 0.85 + 1)),
        facecolor="#111c30"
    )

    ax.set_facecolor("#111c30")

    names = [
        machine["Machine"]
        for machine in machines
    ]

    setup_seen = False
    late_seen = False

    for row in schedule.to_dict("records"):

        y = names.index(row["Machine"])

        if row["Setup"] > 0:

            ax.barh(
                y,
                row["Setup"],
                left=row["Start"] - row["Setup"],
                height=.63,
                color="#66738a",
                edgecolor="#c6d0e3",
                hatch="///",
                label="Setup tijd" if not setup_seen else None
            )

            setup_seen = True

        late = row["Tardiness"] > 0

        ax.barh(
            y,
            row["Process"],
            left=row["Start"],
            height=.63,
            color=palette.get(
                str(row["Colour"]), "#8a7be4"
            ),
            edgecolor="#ff456b" if late else "#24334e",
            linewidth=2.1 if late else .8,
            label=(
                "Order met penalty"
                if late and not late_seen
                else None
            )
        )

        late_seen |= late

        if row["Process"] > 0:

            ax.text(
                row["Start"] + row["Process"] / 2,
                y,
                str(row["Order"]),
                ha="center",
                va="center",
                fontsize=7.5,
                fontweight="bold",
                color="#071120",
                clip_on=True
            )

    ax.set_yticks(
        range(len(names)),
        names
    )

    ax.invert_yaxis()

    ax.set_xlabel(
        "Tijd",
        color="#dce6fa"
    )

    ax.set_ylabel(
        "Machine",
        color="#dce6fa"
    )

    ax.set_title(
        "Gantt-chart planning",
        color="#f0f4ff",
        fontweight="bold",
        pad=14
    )

    ax.tick_params(colors="#dce6fa")

    ax.grid(
        axis="x",
        color="#354562",
        alpha=.6
    )

    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#354562")

    if setup_seen or late_seen:

        legend = ax.legend(
            facecolor="#182640",
            edgecolor="#3b4b69"
        )

        for label in legend.get_texts():
            label.set_color("#eaf0ff")

    fig.tight_layout()

    return fig


# ============================================================
# DONKERE OPTIMALISATIEGRAFIEK
# ============================================================

def penalty_chart(tested, best):

    fig, ax = plt.subplots(
        figsize=(8, 4.4),
        facecolor="#111c30"
    )

    ax.set_facecolor("#111c30")

    if tested:

        ax.plot(
            range(1, len(tested) + 1),
            tested,
            color="#55b6ff",
            linewidth=1.2,
            alpha=.85,
            label="Geteste penalty"
        )

    if best:

        ax.plot(
            range(1, len(best) + 1),
            best,
            color="#9d55ff",
            linewidth=2.3,
            label="Beste penalty"
        )

    ax.set_xlabel(
        "Iteratie",
        color="#dce6fa"
    )

    ax.set_ylabel(
        "Penalty",
        color="#dce6fa"
    )

    ax.tick_params(colors="#dce6fa")

    ax.grid(
        color="#33425f",
        alpha=.6
    )

    for spine in ax.spines.values():
        spine.set_color("#354562")

    legend = ax.legend(
        facecolor="#182640",
        edgecolor="#3b4b69"
    )

    for label in legend.get_texts():
        label.set_color("#eaf0ff")

    fig.tight_layout()

    return fig


# ============================================================
# EXCEL DOWNLOAD
# ============================================================

def excel_file(schedule, settings, penalty, tardiness, duration):

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        schedule[COLUMNS].to_excel(
            writer,
            sheet_name="Schedule",
            index=False
        )

        pd.DataFrame([{
            "Total penalty": penalty,
            "Total tardiness": tardiness,
            "Runtime (s)": duration,
            **settings
        }]).to_excel(
            writer,
            sheet_name="Experiment",
            index=False
        )

    return buffer.getvalue()


# ============================================================
# ZIJBALK
# ============================================================

with st.sidebar:

    st.markdown("### 🎨 PaintShop")
    st.caption("**Experiments**")

    st.markdown("#### 1. Excelbestand uploaden")

    upload = st.file_uploader(
        "Excelbestand",
        type="xlsx",
        label_visibility="collapsed"
    )

    st.markdown("#### 2. Kies methode")

    method = st.radio(
        "Optimalisatiemethode",
        list(FILES),
        index=3,
        label_visibility="collapsed"
    )

    uses_sa = method in (
        "Simulated Annealing",
        "Improved Simulated Annealing"
    )

    if uses_sa:

        st.markdown("#### 3. Parameters")
        st.markdown("**Simulated Annealing**")

        t_max = st.number_input(
            "t_max (aantal iteraties)",
            min_value=1,
            value=1000,
            step=100
        )

        cooling_factor = st.number_input(
            "cooling_factor",
            min_value=.0001,
            max_value=1.0,
            value=.99,
            format="%.4f"
        )

        cooling_it = st.number_input(
            "cooling_it",
            min_value=1,
            value=1000,
            step=100
        )

        temp = st.number_input(
            "temp (starttemperatuur)",
            min_value=.0001,
            value=1000.0,
            step=100.0
        )

        seed = st.number_input(
            "Random seed",
            min_value=0,
            value=42,
            step=1
        )

    if method == "Improved Simulated Annealing":

        st.markdown("**Improving Search**")

        improve_iterations = st.number_input(
            "Aantal verbeteriteraties",
            min_value=0,
            value=1000,
            step=100
        )

    with st.expander("⚙️ Geavanceerd"):

        st.caption(
            "Gebruik dezelfde seed om "
            "experimenten te vergelijken."
        )

    solve = st.button(
        "🚀 Solve ▶",
        type="primary",
        use_container_width=True,
        disabled=upload is None
    )


# ============================================================
# DATA INLADEN
# ============================================================

if upload is None:

    st.info(
        "Upload een Excelbestand met Orders, Machines en Setups."
    )

    st.stop()


try:

    sheets = pd.read_excel(
        upload,
        sheet_name=None
    )

    validate(sheets)

    orders = dictionary(sheets["Orders"])
    machines = dictionary(sheets["Machines"])
    setups = dictionary(sheets["Setups"])

except Exception as exc:

    st.error(f"Invoerfout: {exc}")
    st.stop()


# ============================================================
# INGEVOERDE GEGEVENS
# ============================================================

with st.expander("📁 Ingevoerde gegevens"):

    for sheet in REQUIRED:

        st.markdown(f"**{sheet}**")

        st.dataframe(
            sheets[sheet],
            hide_index=True,
            use_container_width=True
        )


# ============================================================
# STATISTIEKKAARTEN
# ============================================================

def kpi(name, value, emoji, theme):

    st.markdown(
        f'<div class="kpi kpi-{theme}">'
        f'<div class="kpi-icon">{emoji}</div>'
        f'<div class="kpi-name">{name}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# INSTELLINGEN
# ============================================================

settings = {
    "Methode": method
}

if uses_sa:

    settings.update({
        "t_max": int(t_max),
        "cooling_factor": float(cooling_factor),
        "cooling_it": int(cooling_it),
        "temp": float(temp),
        "seed": int(seed)
    })

if method == "Improved Simulated Annealing":

    settings["improve_iterations"] = int(
        improve_iterations
    )

run_key = (
    upload.getvalue(),
    tuple(settings.items())
)


# ============================================================
# ALGORITME UITVOEREN
# ============================================================

if solve:

    try:

        started = time.perf_counter()

        di_orders = sorted(
            orders,
            key=lambda order: order["Deadline"]
        )

        namespace = original_functions(
            FILES[method],
            {
                "di_orders": di_orders,
                "di_machines": machines,
                "di_setups": setups,
                "t_max": int(t_max) if uses_sa else None,
                "cooling_factor": (
                    float(cooling_factor) if uses_sa else None
                ),
                "cooling_it": (
                    int(cooling_it) if uses_sa else None
                ),
                "temp": float(temp) if uses_sa else None
            }
        )

        history_tested = []
        history_best = []

        if method == "Greedy":

            order_list = di_orders.copy()

            per_machine, _ = namespace[
                "greedy_schedule"
            ](
                order_list,
                machines,
                setups
            )

            result = namespace[
                "calculate_results"
            ](
                per_machine,
                order_list,
                machines,
                setups
            )

            sequence = [
                order["Order"]
                for order in order_list
            ]

        elif method == "Improved Greedy":

            (
                _, _,
                best_orders,
                history_tested,
                history_best
            ) = namespace[
                "improving_search"
            ](di_orders)

            order_list = best_orders.copy()

            per_machine, _ = namespace[
                "greedy_schedule"
            ](
                order_list.copy(),
                machines,
                setups
            )

            result = namespace[
                "calculate_results"
            ](
                per_machine,
                order_list,
                machines,
                setups
            )

            sequence = [
                order["Order"]
                for order in order_list
            ]

        else:

            random.seed(int(seed))
            np.random.seed(int(seed))

            if method == "Simulated Annealing":

                sequence, _ = namespace["SA"](
                    sheets["Orders"],
                    int(t_max),
                    float(cooling_factor),
                    int(cooling_it),
                    float(temp)
                )

            else:
                sa_volgorde, _ = namespace["SA"](
                    sheets["Orders"],
                    int(t_max),
                    float(cooling_factor),
                    int(cooling_it),
                    float(temp)
                )
                (
                    _,
                    _,
                    sequence,
                    history_tested,
                    history_best
                ) = namespace["meta_improving_search"](sa_volgorde)
                

            result = namespace[
                "calculate_tard_pen"
            ](
                sequence,
                di_orders,
                machines,
                setups
            )

        schedule = schedule_table(
            sequence,
            result,
            di_orders,
            machines
        )

        duration = time.perf_counter() - started

        st.session_state["paintshop_result"] = {
            "key": run_key,
            "schedule": schedule,
            "machines": machines,
            "penalty": result[1],
            "tardiness": result[0],
            "duration": duration,
            "sequence": sequence,
            "tested": history_tested,
            "best": history_best,
            "settings": settings
        }

    except Exception as exc:

        st.error(f"Oplossen mislukt: {exc}")
        st.stop()


# ============================================================
# EXPERIMENTOVERZICHT
# ============================================================

result = st.session_state.get(
    "paintshop_result"
)

st.markdown(
    '<div class="section-heading">'
    '📊 Experimentoverzicht'
    '</div>',
    unsafe_allow_html=True
)

cards = [
    (
        "Orders",
        str(len(orders)),
        "📄",
        "blue"
    ),
    (
        "Machines",
        str(len(machines)),
        "⚙️",
        "green"
    ),
    (
        "Setup-overgangen",
        str(len(setups)),
        "🔁",
        "yellow"
    ),
    (
        "Totale penalty",
        f"{result['penalty']:,.2f}" if result else "—",
        "🎯",
        "pink"
    ),
    (
        "Totale tardiness",
        f"{result['tardiness']:,.2f}" if result else "—",
        "🕒",
        "purple"
    ),
    (
        "Rekentijd",
        f"{result['duration']:.3f} s" if result else "—",
        "⏱️",
        "cyan"
    )
]

for col, card in zip(
    st.columns(6, gap="small"),
    cards
):

    with col:

        kpi(*card)


# ============================================================
# RESULTATEN WEERGEVEN
# ============================================================

if result is None:

    st.info(
        "Upload een Excelbestand, kies een methode "
        "en klik op Solve."
    )

else:

    if result["key"] != run_key:

        st.warning(
            "De instellingen zijn gewijzigd. "
            "Klik opnieuw op Solve."
        )

    st.write("")

    tab_gantt, tab_schedule, tab_history, tab_orders = st.tabs([
        "📊 Planning (Gantt-chart)",
        "📋 Schedule (tabel)",
        "📈 Optimalisatieverloop",
        "☷ Ordervolgorde"
    ])

    with tab_gantt:

        left, right = st.columns(
            [1.6, 1],
            gap="medium"
        )

        with left:

            with st.container(border=True):

                st.markdown(
                    "#### 📊 Gantt-chart planning"
                )

                fig = gantt(
                    result["schedule"],
                    result["machines"]
                )

                st.pyplot(
                    fig,
                    use_container_width=True
                )

                plt.close(fig)

        with right:

            with st.container(border=True):

                st.markdown(
                    "#### 📈 Optimalisatieverloop"
                )

                if result["tested"] or result["best"]:

                    fig = penalty_chart(
                        result["tested"],
                        result["best"]
                    )

                    st.pyplot(
                        fig,
                        use_container_width=True
                    )

                    plt.close(fig)

                else:

                    st.info(
                        "Dit algoritme registreert "
                        "geen iteratiegeschiedenis."
                    )

        st.markdown("#### 📋 Schedule")

        st.dataframe(
            result["schedule"][COLUMNS],
            hide_index=True,
            use_container_width=True,
            height=320
        )

    with tab_schedule:

        st.markdown(
            "#### Volledige planning"
        )

        search = st.text_input(
            "🔎 Zoek order",
            placeholder="Bijvoorbeeld ORD13"
        )

        table = result["schedule"][COLUMNS]

        if search:

            table = table[
                table["Order"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    regex=False
                )
            ]

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            height=490
        )

    with tab_history:

        st.markdown(
            "#### Optimalisatieverloop"
        )

        if result["tested"] or result["best"]:

            fig = penalty_chart(
                result["tested"],
                result["best"]
            )

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

        else:

            st.info(
                "Dit oorspronkelijke algoritme registreert "
                "geen iteratiegeschiedenis."
            )

    with tab_orders:

        st.markdown(
            "#### Ordervolgorde"
        )

        st.write(
            " → ".join(
                map(str, result["sequence"])
            )
        )

    st.download_button(
        "⬇ Download Excel",
        data=excel_file(
            result["schedule"],
            result["settings"],
            result["penalty"],
            result["tardiness"],
            result["duration"]
        ),
        file_name="PaintShop_Experiment_Results.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )
