
"""PaintShop dashboard dat de originele algoritmes gebruikt."""

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
# PAGINA EN OPMAAK
# ============================================================

st.set_page_config(
    page_title="PaintShop Experiments",
    page_icon="🎨",
    layout="wide"
)


# ============================================================
# EXTRA LIGHT MODE STYLING
# ============================================================

st.markdown("""
<style>

/* Algemene achtergrond */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #f7f9ff !important;
    color: #172448 !important;
}

/* Geüploade Excelbestanden */
[data-testid="stFileUploaderFile"],
[data-testid="stFileUploaderFile"] > div,
[data-testid="stFileUploaderFile"] section {
    background-color: #ffffff !important;
    color: #172448 !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploaderFile"] * {
    color: #172448 !important;
}

/* Invoervelden */
[data-baseweb="input"],
[data-baseweb="select"],
[data-baseweb="textarea"] {
    background-color: #ffffff !important;
    color: #172448 !important;
}

[data-baseweb="input"] input {
    background-color: #ffffff !important;
    color: #172448 !important;
}

/* Tabellen */
[data-testid="stDataFrame"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f4 !important;
    border-radius: 12px !important;
}

/* Tabel-toolbar */
[data-testid="stElementToolbar"] {
    background-color: #ffffff !important;
    color: #172448 !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background-color: transparent !important;
}

[data-baseweb="tab"] {
    color: #344263 !important;
}

/* Knoppen */
[data-testid="stMain"] button {
    border-radius: 9px;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #ffffff !important;
}

/* Meldingen */
[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* Zijbalk */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background: #edf1ff !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
:root {
    color-scheme: light;
}

html, body, .stApp,
[data-testid="stAppViewContainer"] {
    background: #f7f9ff !important;
    color: #18244a !important;
}

[data-testid="stHeader"] {
    background: #f7f9ff !important;
}

.block-container {
    max-width: 1550px;
    padding: 1.7rem 2rem 3rem;
}

/* ZIJBALK */

[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background: linear-gradient(
        180deg, #f0f3ff, #e8edff
    ) !important;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #dce3f6;
}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #1d2a53 !important;
}

[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 1.5px dashed #b5c1e7 !important;
    border-radius: 13px !important;
}

[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzone"] * {
    color: #28375f !important;
}

[data-testid="stSidebar"]
[data-testid="stFileUploaderFile"] {
    background: #ffffff !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"]
[data-testid="stRadio"] label {
    background: #ffffff !important;
    border: 1px solid #dfe5f7 !important;
    border-radius: 10px !important;
    padding: 9px 11px !important;
    margin-bottom: 4px !important;
}

[data-testid="stSidebar"]
[data-testid="stRadio"] label:has(input:checked) {
    background: #eee8ff !important;
    border-color: #8b6af6 !important;
}

[data-testid="stSidebar"] input[type="number"],
[data-testid="stSidebar"] input[type="text"],
[data-testid="stSidebar"] [data-baseweb="input"] {
    background: #ffffff !important;
    color: #172448 !important;
    border-radius: 9px !important;
}

[data-testid="stSidebar"]
[data-baseweb="input"] * {
    color: #172448 !important;
}

[data-testid="stSidebar"]
[data-testid="stNumberInput"] button {
    background: #ffffff !important;
    color: #26365d !important;
}

[data-testid="stSidebar"]
[data-testid="stNumberInput"] button * {
    color: #26365d !important;
}

/* HOOFDPAGINA */

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color: #172448;
}

.hero {
    background: linear-gradient(
        110deg,
        #ffffff 35%,
        #fff0f7 75%,
        #e0f3ff 100%
    );
    border: 1px solid #e3e8f7;
    border-radius: 20px;
    padding: 26px 30px;
    margin-bottom: 20px;
}

.hero h1 {
    color: #101b49;
    font-size: 2.4rem;
    margin: 0 0 6px;
    line-height: 1.25;
}

.hero p {
    color: #64708d;
    margin: 0;
    font-size: 1rem;
}

/* STATISTIEKKAARTEN */

.metric-card {
    min-height: 136px;
    border: 1px solid #e2e8f5;
    border-radius: 16px;
    padding: 17px 15px;
    box-shadow: 0 3px 10px rgba(29,46,99,.04);
}

.metric-card .name {
    font-size: .81rem;
    font-weight: 650;
    color: #344263;
}

.metric-card .value {
    font-size: clamp(1.2rem,1.7vw,1.8rem);
    font-weight: 800;
    color: #101b49;
    margin-top: 9px;
    overflow-wrap: anywhere;
}

.metric-card .emoji {
    font-size: 1.35rem;
    margin-bottom: 9px;
}

.metric-blue {
    background: #e8f0ff;
}

.metric-green {
    background: #e7f8ee;
}

.metric-yellow {
    background: #fff5dc;
}

.metric-pink {
    background: #ffeaf0;
}

.metric-purple {
    background: #efe9ff;
}

.metric-cyan {
    background: #e3f7f8;
}

.section-title {
    font-size: 1.22rem;
    font-weight: 750;
    color: #172448;
    margin: 18px 0 14px;
}

/* CONTAINERS EN TABBLADEN */

[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #e1e7f4 !important;
    border-radius: 16px !important;
    background: #ffffff !important;
}

[data-testid="stMain"]
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f4 !important;
    border-radius: 12px !important;
}

[data-testid="stMain"]
[data-testid="stExpander"] * {
    color: #23335c !important;
}

[data-testid="stMain"]
[data-testid="stTabs"] button {
    color: #52617f !important;
    font-weight: 600 !important;
}

[data-testid="stMain"]
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #6943e8 !important;
}

[data-testid="stMain"]
[data-baseweb="tab-highlight"] {
    background: #7650ef !important;
}

[data-testid="stMain"]
[data-testid="stDataFrame"] {
    background: #ffffff !important;
}

[data-testid="stMain"]
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #172448 !important;
}

/* SOLVE KNOP */

[data-testid="stSidebar"]
div.stButton > button[kind="primary"] {
    background: linear-gradient(
        95deg, #7955fa, #6435ea
    ) !important;
    border: 0 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    font-weight: 750 !important;
    min-height: 50px !important;
}

[data-testid="stSidebar"]
div.stButton > button[kind="primary"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"]
div.stButton > button[kind="primary"]:hover {
    background: #5c2cdb !important;
}

@media(max-width:1000px) {
    .block-container {
        padding: 1rem;
    }

    .hero h1 {
        font-size: 1.8rem;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🎨 PaintShop | Experiments</h1>
    <p>
        Experimenteer met jullie oorspronkelijke
        Greedy- en Simulated Annealing-functies.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# ALGORITMES EN BENODIGDE KOLOMMEN
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
        "Order", "Surface", "Colour",
        "Deadline", "Penalty"
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
    Laadt alleen de oorspronkelijke functiedefinities.
    De vaste Excel-inleesregels en uitvoerregels
    worden niet uitgevoerd.
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
        ast.Module(
            body=definitions,
            type_ignores=[]
        )
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
# GANTT-CHART
# ============================================================

def gantt(schedule, machines):

    colours = {
        "Red": "#ff6464",
        "Blue": "blue",
        "Green": "green",
        "Yellow": "yellow",
        "Orange": "orange",
        "Purple": "purple",
        "Pink": "pink",
        "Black": "black",
        "White": "white",
        "Grey": "grey"
    }

    fig, ax = plt.subplots(
        figsize=(12, max(4.4, len(machines) * 0.85 + 1)),
        facecolor="white"
    )

    ax.set_facecolor("#ffffff")

    machine_names = [
        machine["Machine"]
        for machine in machines
    ]

    setup_seen = False
    late_seen = False

    for row in schedule.to_dict("records"):

        y = machine_names.index(row["Machine"])

        if row["Setup"] > 0:

            ax.barh(
                y,
                row["Setup"],
                left=row["Start"] - row["Setup"],
                height=0.6,
                color="lightgrey",
                edgecolor="black",
                hatch="//",
                label="Setup tijd" if not setup_seen else None
            )

            setup_seen = True

        late = row["Tardiness"] > 0

        ax.barh(
            y,
            row["Process"],
            left=row["Start"],
            height=0.6,
            color=colours.get(
                str(row["Colour"]), "#8ca8d6"
            ),
            edgecolor="red" if late else "black",
            linewidth=2 if late else 1,
            label=(
                "Order met penalty"
                if late and not late_seen
                else None
            )
        )

        late_seen |= late

        ax.text(
            row["Start"] + row["Process"] / 2,
            y,
            str(row["Order"]),
            ha="center",
            va="center",
            fontsize=8
        )

    ax.set_yticks(
        range(len(machine_names)),
        machine_names
    )

    ax.set_xlabel("Tijd")
    ax.set_ylabel("Machine")

    ax.set_title(
        "Gantt-chart planning",
        color="#172448",
        fontsize=12,
        fontweight="bold",
        pad=14
    )

    ax.grid(axis="x", alpha=0.15)
    ax.tick_params(colors="#243454", labelsize=9)

    ax.xaxis.label.set_color("#243454")
    ax.yaxis.label.set_color("#243454")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax.set_axisbelow(True)

    if setup_seen or late_seen:
        ax.legend()

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

    st.markdown("### 🎨 PaintShop Experiments")

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
            "t_max",
            min_value=1,
            value=1000,
            step=100
        )

        cooling_factor = st.number_input(
            "cooling_factor",
            min_value=0.0001,
            max_value=1.0,
            value=0.99,
            format="%.4f"
        )

        cooling_it = st.number_input(
            "cooling_it",
            min_value=1,
            value=1000,
            step=100
        )

        temp = st.number_input(
            "temp",
            min_value=0.0001,
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
            "Gebruik dezelfde random seed om "
            "experimenten reproduceerbaar te vergelijken."
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
# STATISTIEKKAARTEN
# ============================================================

def metric_card(name, value, emoji, style):

    st.markdown(
        f'<div class="metric-card metric-{style}">'
        f'<div class="emoji">{emoji}</div>'
        f'<div class="name">{name}</div>'
        f'<div class="value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


with st.expander("📁 Ingevoerde gegevens"):

    for sheet in REQUIRED:

        st.markdown(f"**{sheet}**")

        st.dataframe(
            sheets[sheet],
            hide_index=True,
            use_container_width=True
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

                (
                    _,
                    sequence,
                    history_tested,
                    history_best
                ) = namespace[
                    "meta_improving_search"
                ](
                    sheets["Orders"],
                    int(improve_iterations)
                )

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
    '<div class="section-title">'
    '📊 Experimentoverzicht'
    '</div>',
    unsafe_allow_html=True
)

metrics = st.columns(
    6,
    gap="small"
)

values = [
    ("Orders", str(len(orders)), "📄", "blue"),
    ("Machines", str(len(machines)), "⚙️", "green"),
    ("Setup-overgangen", str(len(setups)), "🔁", "yellow"),
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

for column, (name, value, emoji, style) in zip(
    metrics, values
):

    with column:

        metric_card(
            name,
            value,
            emoji,
            style
        )


# ============================================================
# RESULTATEN WEERGEVEN
# ============================================================

if result is None:

    st.info(
        "Stel links de parameters in en klik op "
        "🚀 Solve om de planning te berekenen."
    )

else:

    if result["key"] != run_key:

        st.warning(
            "De instellingen zijn gewijzigd. "
            "Klik opnieuw op Solve om nieuwe "
            "resultaten te berekenen."
        )

    st.write("")

    tab_plan, tab_table, tab_history, tab_orders = st.tabs([
        "📊 Planning (Gantt-chart)",
        "📋 Schedule (tabel)",
        "📈 Optimalisatieverloop",
        "☷ Ordervolgorde"
    ])

    with tab_plan:

        left, right = st.columns(
            [1.65, 1],
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

                    data = {}

                    if result["tested"]:

                        data["Geteste penalty"] = pd.Series(
                            result["tested"],
                            dtype=float
                        )

                    if result["best"]:

                        data["Beste penalty"] = pd.Series(
                            result["best"],
                            dtype=float
                        )

                    st.line_chart(
                        pd.DataFrame(data),
                        height=370,
                        x_label="Iteratie",
                        y_label="Penalty"
                    )

                    st.caption(
                        "Bij Improved Greedy wordt de beste "
                        "penalty per ronde opgeslagen; bij "
                        "Improved SA komt de historie uit "
                        "de improving search."
                    )

                else:

                    st.info(
                        "Deze methode registreert geen "
                        "optimalisatiegeschiedenis."
                    )

        st.markdown("#### 📋 Schedule")

        st.dataframe(
            result["schedule"][COLUMNS],
            hide_index=True,
            use_container_width=True,
            height=300
        )

    with tab_table:

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

            data = {}

            if result["tested"]:

                data["Geteste penalty"] = pd.Series(
                    result["tested"],
                    dtype=float
                )

            if result["best"]:

                data["Beste penalty"] = pd.Series(
                    result["best"],
                    dtype=float
                )

            st.line_chart(
                pd.DataFrame(data),
                x_label="Iteratie",
                y_label="Penalty"
            )

        else:

            st.info(
                "De oorspronkelijke methode slaat "
                "geen penaltygeschiedenis per iteratie op."
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

        st.caption(
            "De volgorde is overgenomen uit "
            "jullie oorspronkelijke algoritme."
        )

    st.download_button(
        "⬇️ Download Excel",
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
