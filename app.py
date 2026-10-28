import html
import re
import unicodedata
from collections.abc import Mapping, Sequence

import gspread
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


WORKSHEETS = ("Base de datos", "Rendimiento", "Plat de fuerza")
REQUIRED_AUTH_SETTINGS = (
    "redirect_uri",
    "cookie_secret",
    "client_id",
    "client_secret",
    "server_metadata_url",
)
REQUIRED_SERVICE_ACCOUNT_SETTINGS = (
    "type",
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "auth_uri",
    "token_uri",
    "auth_provider_x509_cert_url",
    "client_x509_cert_url",
)

COLUMN_ALIASES = {
    "player_id": {
        "dni",
        "id",
        "id jugador",
        "identificacion",
        "identificacion jugador",
        "documento",
        "documento de identidad",
    },
    "first_name": {"nombre", "nombres"},
    "last_name": {"apellido", "apellidos"},
    "birth_date": {"fecha de nacimiento", "nacimiento"},
    "position": {"posicion", "puesto"},
    "category": {"categoria", "cat"},
    "photo_url": {"url foto", "foto", "url fotografia", "url de la foto"},
    "father_height": {"altura padre", "estatura padre", "altura del padre"},
    "mother_height": {"altura madre", "estatura madre", "altura de la madre"},
    "date": {
        "fecha",
        "fecha test",
        "fecha evaluacion",
        "fecha de evaluacion",
        "fecha de medicion",
        "date",
    },
    "age": {"edad", "edad decimal"},
}

REQUIRED_COLUMNS = {
    "Base de datos": ("player_id", "first_name", "last_name", "category"),
    "Rendimiento": ("player_id", "date", "category"),
    "Plat de fuerza": ("player_id", "date", "category"),
}


class MissingRequiredColumnsError(ValueError):
    def __init__(
        self,
        worksheet_name: str,
        missing_columns: Sequence[str],
        candidate_headers: Sequence[str],
    ) -> None:
        self.worksheet_name = worksheet_name
        self.missing_columns = list(missing_columns)
        self.candidate_headers = list(candidate_headers)
        super().__init__(
            f"No reconocí los campos {', '.join(self.missing_columns)} "
            f"en “{worksheet_name}”."
        )


def missing_secret_settings(secrets: Mapping[str, object]) -> list[str]:
    missing = []

    for section, required_keys in (
        ("auth", REQUIRED_AUTH_SETTINGS),
        ("app", ("google_sheet_id", "authorized_emails")),
        ("gcp_service_account", REQUIRED_SERVICE_ACCOUNT_SETTINGS),
    ):
        section_settings = secrets.get(section)
        if not isinstance(section_settings, Mapping):
            missing.append(f"[{section}]")
            continue

        missing.extend(
            f"[{section}].{key}"
            for key in required_keys
            if key not in section_settings or not section_settings[key]
        )

    app_config = secrets.get("app")
    if isinstance(app_config, Mapping):
        authorized_emails = app_config.get("authorized_emails")
        if not isinstance(authorized_emails, Sequence) or isinstance(
            authorized_emails, str
        ):
            missing.append("[app].authorized_emails (debe ser una lista)")
        elif not any(str(email).strip() for email in authorized_emails):
            missing.append("[app].authorized_emails (agrega al menos una cuenta)")

    return missing


def normalize_header(value: object) -> str:
    decomposed = unicodedata.normalize("NFKD", str(value))
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents.casefold()).strip()


def canonicalize_headers(
    headers: Sequence[object],
    column_mappings: Mapping[str, str] | None = None,
) -> list[str]:
    aliases = {
        normalize_header(alias): canonical
        for canonical, names in COLUMN_ALIASES.items()
        for alias in names | {canonical.replace("_", " ")}
    }
    mapping_by_header = {
        normalize_header(header): canonical
        for header, canonical in (column_mappings or {}).items()
    }
    canonical_headers = []
    seen = set()

    for index, header in enumerate(headers, start=1):
        display_header = str(header).strip()
        if not display_header:
            raise ValueError(f"La columna {index} no tiene nombre.")

        normalized_header = normalize_header(display_header)
        if normalized_header in mapping_by_header:
            canonical = mapping_by_header[normalized_header]
            if canonical not in COLUMN_ALIASES:
                raise ValueError(f"El campo asignado “{canonical}” no es válido.")
        else:
            canonical = aliases.get(normalized_header, display_header)
        if canonical in seen:
            raise ValueError(
                f"Hay más de una columna que corresponde a “{canonical}”. "
                "Revisa los encabezados de la hoja."
            )
        seen.add(canonical)
        canonical_headers.append(canonical)

    return canonical_headers


def standardize_sheet(
    worksheet_name: str,
    values: Sequence[Sequence[str]],
    column_mappings: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    if not values:
        raise ValueError(f"La pestaña “{worksheet_name}” está vacía.")

    headers = canonicalize_headers(values[0], column_mappings)
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS[worksheet_name]
        if column not in headers
    ]
    if missing_columns:
        candidate_headers = [
            str(raw_header).strip()
            for raw_header, canonical in zip(values[0], headers)
            if canonical == str(raw_header).strip()
            and str(raw_header).strip()
        ]
        raise MissingRequiredColumnsError(
            worksheet_name,
            missing_columns,
            candidate_headers,
        )

    rows = [list(row[: len(headers)]) for row in values[1:] if any(row)]
    padded_rows = [row + [""] * (len(headers) - len(row)) for row in rows]
    frame = pd.DataFrame(padded_rows, columns=headers)
    frame["player_id"] = frame["player_id"].astype("string").str.strip()
    return frame


def classify_z_score(value: float) -> str:
    if value > 2:
        return "Excelente"
    if value > 1:
        return "Muy Bueno"
    if value > 0.5:
        return "Bueno"
    if value >= -0.5:
        return "Promedio (Estable)"
    if value >= -1:
        return "Debajo del Promedio"
    if value >= -2:
        return "Pobre"
    if value >= -3:
        return "Muy Pobre"
    return "Extremadamente Pobre"


def z_score_color(value: float) -> str:
    if pd.isna(value):
        return "#E9ECEF"
    if value > 2:
        return "#1A6E1A"
    if value > 1:
        return "#4CAF50"
    if value > 0.5:
        return "#A8D08D"
    if value >= -0.5:
        return "#EEEEEE"
    if value >= -1:
        return "#FFD600"
    if value >= -2:
        return "#FF9800"
    if value >= -3:
        return "#E53935"
    return "#8B0000"


def z_score_cell_style(value: float) -> str:
    if pd.isna(value):
        return "background-color: #E9ECEF; color: #1B1B1B"
    text_color = "#FFFFFF" if value > 1 or value <= -2 else "#1B1B1B"
    return f"background-color: {z_score_color(value)}; color: {text_color}"


def build_z_score_matrix(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame(columns=["Jugador"])

    metrics = sorted(results["metric"].dropna().unique())
    players = results[["player_id", "player_name"]].drop_duplicates("player_id")
    scores = results.pivot(index="player_id", columns="metric", values="z_score")
    matrix = players.merge(scores, on="player_id", how="left")
    matrix = matrix.rename(columns={"player_name": "Jugador"}).drop(
        columns="player_id"
    )
    matrix.columns.name = None
    return matrix[["Jugador", *metrics]]


def build_z_score_radar(
    player_results: pd.DataFrame,
    player_name: str,
    reference_category: str,
    month_label: str,
) -> go.Figure:
    valid_results = player_results.loc[
        player_results["z_score"].notna()
    ].sort_values("metric")
    metrics = valid_results["metric"].astype(str).tolist()
    z_scores = valid_results["z_score"].astype(float).tolist()
    closed_metrics = [*metrics, metrics[0]]
    closed_radii = [3.0] * len(closed_metrics)
    player_radii = [max(-3.0, min(3.0, score)) + 3.0 for score in z_scores]
    player_radii.append(player_radii[0])
    custom_scores = [*z_scores, z_scores[0]]

    figure = go.Figure()
    figure.add_trace(
        go.Scatterpolar(
            r=closed_radii,
            theta=closed_metrics,
            name="Media (Z=0)",
            mode="lines",
            line={"color": "#DC3545", "dash": "dash", "width": 2},
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatterpolar(
            r=player_radii,
            theta=closed_metrics,
            customdata=custom_scores,
            name=player_name,
            mode="lines+markers",
            fill="toself",
            fillcolor="rgba(39, 78, 123, 0.18)",
            line={"color": "#274E7B", "width": 2.5},
            marker={"color": "#274E7B", "size": 7},
            hovertemplate=(
                "%{theta}<br>Z-Score: %{customdata:.1f}<extra>%{fullData.name}</extra>"
            ),
        )
    )
    figure.update_layout(
        title={
            "text": f"Perfil Z-Score vs {reference_category} | {month_label}",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 18, "color": "#17212B"},
        },
        template="plotly_white",
        font={
            "family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            "color": "#344256",
        },
        paper_bgcolor="rgba(0,0,0,0)",
        polar={
            "bgcolor": "#FFFFFF",
            "radialaxis": {
                "visible": True,
                "range": [0, 6],
                "tickmode": "array",
                "tickvals": list(range(7)),
                "ticktext": ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
                "gridcolor": "#E5E7EB",
                "linecolor": "#D1D5DB",
            },
            "angularaxis": {
                "rotation": 90,
                "direction": "clockwise",
                "gridcolor": "#E5E7EB",
                "linecolor": "#D1D5DB",
            },
        },
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.12,
            "font": {"size": 12, "color": "#536176"},
        },
        margin={"t": 70, "b": 65, "l": 60, "r": 60},
        height=620,
    )
    return figure


def _select_all_players(player_ids: Sequence[str]) -> None:
    st.session_state["selected_player_ids"] = list(player_ids)


def render_dashboard_header() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #f7f8fa;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1440px;
            padding-top: 3.5rem;
            padding-bottom: 4rem;
        }
        [data-testid="stTabs"] [role="tablist"] {
            gap: 1.4rem;
            border-bottom: 1px solid #e4e8ee;
        }
        [data-testid="stTabs"] [role="tab"] {
            height: 3rem;
            padding: 0 0.15rem;
            color: #64748b;
            font-weight: 550;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            color: #274e7b;
            font-weight: 700;
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #e3e8ef;
            border-radius: 14px;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.035);
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            border-color: #d7dee8;
            border-radius: 9px;
            background: #ffffff;
        }
        [data-testid="stButton"] button {
            min-height: 2.65rem;
            border-color: #d7dee8;
            border-radius: 9px;
            color: #274e7b;
            font-weight: 650;
            transition: border-color 140ms ease, background 140ms ease;
        }
        [data-testid="stButton"] button:hover {
            border-color: #274e7b;
            background: #f2f6fb;
            color: #1d3d61;
        }
        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid #e3e8ef;
            border-radius: 11px;
        }
        .ams-brand {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin-bottom: 2.15rem;
        }
        .ams-brand-mark {
            display: grid;
            width: 2.7rem;
            height: 2.7rem;
            place-items: center;
            border: 1px solid #d5dfeb;
            border-radius: 10px;
            background: #ffffff;
            color: #274e7b;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
        }
        .ams-brand-name {
            color: #17212b;
            font-size: 0.94rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .ams-brand-caption {
            margin-top: 0.12rem;
            color: #718096;
            font-size: 0.76rem;
        }
        .ams-access-pill {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            margin-left: auto;
            padding: 0.38rem 0.7rem;
            border: 1px solid #e1e7ed;
            border-radius: 999px;
            background: #ffffff;
            color: #58677a;
            font-size: 0.72rem;
            font-weight: 600;
        }
        .ams-access-dot {
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 50%;
            background: #35a370;
        }
        .ams-hero {
            margin-bottom: 1.65rem;
        }
        .ams-eyebrow {
            margin-bottom: 0.55rem;
            color: #52749b;
            font-size: 0.7rem;
            font-weight: 750;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }
        .ams-hero-title {
            margin: 0;
            color: #17212b;
            font-size: clamp(2rem, 3.2vw, 2.8rem);
            font-weight: 680;
            letter-spacing: -0.055em;
            line-height: 1.12;
        }
        .ams-hero-copy {
            max-width: 48rem;
            margin: 0.65rem 0 0;
            color: #667487;
            font-size: 0.98rem;
            line-height: 1.65;
        }
        .ams-section-heading {
            margin: 0.35rem 0 0.2rem;
            color: #17212b;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }
        .ams-section-copy {
            margin: 0 0 0.8rem;
            color: #758195;
            font-size: 0.83rem;
        }
        .ams-stat {
            min-height: 5.3rem;
            padding: 0.9rem 1rem;
            border: 1px solid #e5e9ef;
            border-radius: 11px;
            background: #ffffff;
        }
        .ams-stat-label {
            color: #718096;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
        }
        .ams-stat-value {
            margin-top: 0.4rem;
            color: #17212b;
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: -0.035em;
        }
        @media (max-width: 640px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1.25rem 1rem 3rem;
            }
            .ams-brand {
                margin-bottom: 1.6rem;
            }
            .ams-access-pill {
                padding: 0.32rem 0.52rem;
                font-size: 0.66rem;
            }
        }
        </style>
        <div class="ams-brand">
          <div class="ams-brand-mark">AMS</div>
          <div>
            <div class="ams-brand-name">Athletic Management System</div>
            <div class="ams-brand-caption">Rendimiento y analítica deportiva</div>
          </div>
          <div class="ams-access-pill">
            <span class="ams-access-dot"></span>
            Equipo privado
          </div>
        </div>
        <section class="ams-hero">
          <div class="ams-eyebrow">Analítica de rendimiento</div>
          <h1 class="ams-hero-title">Rendimiento, con contexto.</h1>
          <p class="ams-hero-copy">
            Explora las mediciones del equipo y compara cada perfil con una
            referencia clara, en un solo lugar.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_stat(label: str, value: str) -> None:
    safe_label = html.escape(label)
    safe_value = html.escape(value)
    st.markdown(
        f"""
        <div class="ams-stat">
          <div class="ams-stat-label">{safe_label}</div>
          <div class="ams-stat-value">{safe_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_monthly_measurements(
    sheets: Mapping[str, pd.DataFrame],
) -> tuple[pd.DataFrame, int]:
    measurement_frames = []
    excluded_rows = 0

    for worksheet_name in ("Rendimiento", "Plat de fuerza"):
        frame = sheets[worksheet_name].copy()
        date_text = frame["date"].astype("string").str.strip()
        iso_dates = date_text.str.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
        parsed_dates = pd.to_datetime(date_text, errors="coerce", dayfirst=True)
        parsed_dates.loc[iso_dates] = pd.to_datetime(
            date_text.loc[iso_dates],
            errors="coerce",
            yearfirst=True,
        )
        frame["date"] = parsed_dates
        frame["category"] = frame["category"].astype("string").str.strip()
        frame["player_id"] = frame["player_id"].astype("string").str.strip()

        valid_keys = (
            frame["player_id"].notna()
            & frame["player_id"].ne("")
            & frame["date"].notna()
            & frame["category"].notna()
            & frame["category"].ne("")
        )
        excluded_rows += int((~valid_keys).sum())
        frame = frame.loc[valid_keys].copy()

        key_columns = {"player_id", "date", "category"}
        metric_columns = []
        for column in frame.columns:
            if column in key_columns:
                continue
            numeric_values = pd.to_numeric(
                frame[column].astype("string").str.replace(",", ".", regex=False),
                errors="coerce",
            )
            if numeric_values.notna().any():
                frame[column] = numeric_values
                metric_columns.append(column)

        if not metric_columns:
            continue

        grouped = (
            frame.groupby(["player_id", "date", "category"], as_index=False)[
                metric_columns
            ]
            .mean()
            .melt(
                id_vars=["player_id", "date", "category"],
                value_vars=metric_columns,
                var_name="metric",
                value_name="value",
            )
            .dropna(subset=["value"])
        )
        measurement_frames.append(grouped)

    columns = ["player_id", "player_name", "date", "category", "metric", "value"]
    if not measurement_frames:
        return pd.DataFrame(columns=columns), excluded_rows

    measurements = pd.concat(measurement_frames, ignore_index=True)
    measurements["_month"] = measurements["date"].dt.to_period("M")
    measurements = (
        measurements.sort_values("date")
        .drop_duplicates(
            ["player_id", "category", "metric", "_month"],
            keep="last",
        )
        .drop(columns="_month")
    )

    roster = sheets["Base de datos"]
    names = (
        roster[["player_id", "first_name", "last_name"]]
        .fillna("")
        .assign(
            player_name=lambda rows: (
                rows["first_name"].astype(str).str.strip()
                + " "
                + rows["last_name"].astype(str).str.strip()
            ).str.strip()
        )
        .drop_duplicates("player_id")
        .set_index("player_id")["player_name"]
    )
    measurements["player_name"] = measurements["player_id"].map(names).fillna("")
    measurements.loc[
        measurements["player_name"].eq(""), "player_name"
    ] = "Jugador sin nombre"
    return measurements[columns], excluded_rows


def calculate_z_scores(
    measurements: pd.DataFrame,
    selected_player_ids: Sequence[str],
    reference_category: str,
    player_category: str | None = None,
) -> pd.DataFrame:
    result_columns = [
        "player_id",
        "player_name",
        "metric",
        "value",
        "reference_mean",
        "reference_sd",
        "reference_count",
        "z_score",
        "classification",
    ]
    selected_ids = {str(player_id) for player_id in selected_player_ids}
    if measurements.empty or not selected_ids:
        return pd.DataFrame(columns=result_columns)

    metrics = sorted(measurements["metric"].dropna().unique())
    target_rows = measurements.loc[
        measurements["player_id"].astype(str).isin(selected_ids)
    ].drop_duplicates(["player_id", "metric"], keep="last")
    if player_category is not None:
        target_rows = target_rows.loc[
            target_rows["category"].eq(player_category)
        ]
    reference_rows = measurements.loc[
        measurements["category"].eq(reference_category)
    ]
    target_names = (
        target_rows
        .drop_duplicates("player_id")
        .set_index("player_id")["player_name"]
        .to_dict()
    )

    results = []
    for player_id in selected_player_ids:
        for metric in metrics:
            player_value_rows = target_rows.loc[
                target_rows["player_id"].astype(str).eq(str(player_id))
                & target_rows["metric"].eq(metric),
                "value",
            ]
            reference_values = pd.to_numeric(
                reference_rows.loc[
                    reference_rows["metric"].eq(metric), "value"
                ],
                errors="coerce",
            )
            reference_values = reference_values.loc[
                reference_values.notna() & reference_values.ne(0)
            ]
            reference_count = len(reference_values)
            reference_mean = (
                float(reference_values.mean()) if reference_count else float("nan")
            )
            reference_sd = (
                float(reference_values.std(ddof=1))
                if reference_count >= 2
                else float("nan")
            )
            player_value = (
                float(player_value_rows.iloc[0])
                if not player_value_rows.empty
                else float("nan")
            )
            if (
                reference_count >= 2
                and pd.notna(reference_sd)
                and reference_sd > 0
                and pd.notna(player_value)
            ):
                z_score = (player_value - reference_mean) / reference_sd
                classification = classify_z_score(z_score)
            else:
                z_score = float("nan")
                classification = "No disponible"

            results.append(
                {
                    "player_id": str(player_id),
                    "player_name": target_names.get(str(player_id), "Jugador"),
                    "metric": metric,
                    "value": player_value,
                    "reference_mean": reference_mean,
                    "reference_sd": reference_sd,
                    "reference_count": reference_count,
                    "z_score": z_score,
                    "classification": classification,
                }
            )

    return pd.DataFrame(results, columns=result_columns)


def _required_secret(name: str) -> object:
    if name not in st.secrets:
        raise ValueError(
            f"Falta configurar “{name}” en los secretos de Streamlit."
        )
    return st.secrets[name]


@st.cache_data(ttl=300, show_spinner="Cargando datos...")
def load_google_sheets() -> dict[str, list[list[str]]]:
    app_config = _required_secret("app")
    if not isinstance(app_config, Mapping):
        raise ValueError("La configuración “app” de Streamlit no es válida.")

    spreadsheet_id = app_config.get("google_sheet_id")
    if not spreadsheet_id:
        raise ValueError(
            "Falta “google_sheet_id” dentro de la configuración “app”."
        )

    service_account = _required_secret("gcp_service_account")
    if not isinstance(service_account, Mapping):
        raise ValueError("La configuración de la cuenta de Google no es válida.")

    client = gspread.service_account_from_dict(dict(service_account))
    spreadsheet = client.open_by_key(str(spreadsheet_id))
    sheets = {}

    for worksheet_name in WORKSHEETS:
        worksheet = spreadsheet.worksheet(worksheet_name)
        sheets[worksheet_name] = worksheet.get_all_values()

    return sheets


def standardize_sheets_with_mapping(
    raw_sheets: Mapping[str, Sequence[Sequence[str]]],
) -> dict[str, pd.DataFrame]:
    saved_mappings = st.session_state.setdefault("column_mappings", {})
    standardized_sheets = {}
    mapping_issues = []

    for worksheet_name in WORKSHEETS:
        try:
            standardized_sheets[worksheet_name] = standardize_sheet(
                worksheet_name,
                raw_sheets[worksheet_name],
                saved_mappings.get(worksheet_name, {}),
            )
        except MissingRequiredColumnsError as error:
            mapping_issues.append(error)
        except ValueError as error:
            st.error(str(error))
            st.stop()

    if not mapping_issues:
        return standardized_sheets

    st.warning(
        "Cambió el nombre de una columna necesaria. Asígnala una vez para "
        "esta sesión; las nuevas mediciones se incorporan automáticamente."
    )
    if st.button("Restablecer asignaciones de columnas"):
        st.session_state["column_mappings"] = {}
        st.rerun()

    if any(
        len(issue.candidate_headers) < len(issue.missing_columns)
        for issue in mapping_issues
    ):
        for issue in mapping_issues:
            st.error(
                f"En “{issue.worksheet_name}” deben existir campos equivalentes a "
                f"{', '.join(issue.missing_columns)}. Encabezados disponibles: "
                f"{', '.join(issue.candidate_headers) or 'ninguno'}."
            )
        st.stop()

    proposed_mappings = {}
    with st.form("column_mapping_form"):
        st.subheader("Asignar columnas")
        for issue in mapping_issues:
            st.write(f"Pestaña: {issue.worksheet_name}")
            used_headers = set()
            for field in issue.missing_columns:
                options = [
                    header
                    for header in issue.candidate_headers
                    if header not in used_headers
                ]
                chosen_header = st.selectbox(
                    f"¿Qué encabezado representa “{field}”?",
                    options,
                    key=f"column_map_{issue.worksheet_name}_{field}",
                )
                used_headers.add(chosen_header)
                proposed_mappings.setdefault(issue.worksheet_name, {})[
                    chosen_header
                ] = field

        submitted = st.form_submit_button("Aplicar asignaciones")

    if submitted:
        for worksheet_name, mappings in proposed_mappings.items():
            saved_mappings.setdefault(worksheet_name, {}).update(mappings)
        st.rerun()

    st.stop()


def require_authorized_user(app_config: Mapping[str, object]) -> None:
    if not st.user.is_logged_in:
        st.title("AMS · Athletic Management System")
        st.write("Inicia sesión con una cuenta autorizada para acceder al sistema.")
        st.button("Iniciar sesión con Google", on_click=st.login)
        st.stop()

    authorized_emails = app_config.get("authorized_emails", [])
    if not isinstance(authorized_emails, Sequence) or isinstance(
        authorized_emails, str
    ):
        st.error("La lista de personas autorizadas no está configurada correctamente.")
        st.stop()

    user_email = str(getattr(st.user, "email", "")).strip().casefold()
    allowed_emails = {str(email).strip().casefold() for email in authorized_emails}
    if not user_email or user_email not in allowed_emails:
        st.error("Esta cuenta no está autorizada para acceder al AMS.")
        st.button("Cerrar sesión", on_click=st.logout)
        st.stop()


def main() -> None:
    st.set_page_config(page_title="AMS", layout="wide")
    try:
        secrets = st.secrets
    except StreamlitSecretNotFoundError:
        st.title("AMS · Athletic Management System")
        st.error("Falta configurar los secretos privados de Streamlit.")
        st.info(
            "En Streamlit Community Cloud, abre la aplicación, entra en "
            "Settings → Secrets y completa la plantilla "
            "`.streamlit/secrets.example.toml`. No pegues claves ni contraseñas "
            "en el chat ni en archivos del repositorio."
        )
        st.stop()

    missing_settings = missing_secret_settings(secrets)
    if missing_settings:
        st.title("AMS · Athletic Management System")
        st.error("La configuración privada del AMS está incompleta.")
        st.write("Faltan estas secciones o campos:")
        st.code("\n".join(missing_settings), language="text")
        st.info(
            "Completa los secretos de la aplicación en Streamlit Community Cloud. "
            "No agregues secretos a archivos versionados."
        )
        st.stop()

    app_config = secrets["app"]
    require_authorized_user(app_config)

    render_dashboard_header()

    try:
        raw_sheets = load_google_sheets()
    except PermissionError:
        st.error(
            "La cuenta de servicio de AMS no puede abrir esta hoja de Google."
        )
        st.info(
            "Comprueba que [app].google_sheet_id sea el ID correcto. Luego, "
            "en Google Sheets pulsa Compartir y agrega como Lector el correo "
            "client_email de [gcp_service_account]. Mantén el acceso general "
            "restringido. Guarda los cambios y vuelve a cargar AMS."
        )
        st.stop()
    except (
        gspread.exceptions.APIError,
        gspread.exceptions.SpreadsheetNotFound,
        gspread.exceptions.WorksheetNotFound,
        ValueError,
    ) as error:
        st.error(f"No se pudieron cargar las hojas de Google Sheets: {error}")
        st.info(
            "Verifica que la hoja sea privada, que el acceso esté configurado "
            "en Streamlit y que sus tres pestañas mantengan los nombres esperados."
        )
        st.stop()

    sheets = standardize_sheets_with_mapping(raw_sheets)
    measurements, excluded_rows = prepare_monthly_measurements(sheets)
    if excluded_rows:
        formatted_excluded_rows = f"{excluded_rows:,}".replace(",", ".")
        st.caption(
            f"Filas incompletas omitidas: {formatted_excluded_rows} "
            "(sin jugador, fecha o categoría)."
        )

    zscore_tab, mbd_tab, swc_tab = st.tabs(
        ["Z-Score / Extrapolar", "MBD Hopkins", "SWC"]
    )
    with zscore_tab:
        if measurements.empty:
            st.warning("No hay mediciones numéricas disponibles para analizar.")
        else:
            available_months = sorted(
                measurements["date"].dt.to_period("M").dropna().unique(),
                reverse=True,
            )
            with st.container(border=True):
                main_filters = st.columns([1, 1.35, 1.35], gap="medium")
                with main_filters[0]:
                    selected_month = st.selectbox(
                        "Mes",
                        available_months,
                        format_func=lambda period: period.strftime("%Y-%m"),
                    )

                month_data = measurements.loc[
                    measurements["date"].dt.to_period("M").eq(selected_month)
                ]
                categories = sorted(month_data["category"].dropna().unique())
                if not categories:
                    st.warning("No hay categorías en el mes seleccionado.")
                else:
                    with main_filters[1]:
                        player_category = st.selectbox(
                            "Categoría", categories
                        )
                    with main_filters[2]:
                        reference_category = st.selectbox(
                            "Comparar con", categories
                        )

                    player_options = (
                        month_data.loc[month_data["category"].eq(player_category)]
                        .drop_duplicates("player_id")
                        .sort_values("player_name")
                    )
                    player_ids = player_options["player_id"].tolist()
                    display_names = dict(
                        zip(player_ids, player_options["player_name"])
                    )
                    current_selection = st.session_state.get(
                        "selected_player_ids", []
                    )
                    st.session_state["selected_player_ids"] = [
                        player_id
                        for player_id in current_selection
                        if player_id in player_ids
                    ]
                    player_filters = st.columns([4, 1], gap="medium")
                    with player_filters[0]:
                        selected_player_ids = st.multiselect(
                            "Jugadores",
                            player_ids,
                            format_func=lambda player_id: display_names.get(
                                player_id, str(player_id)
                            ),
                            key="selected_player_ids",
                            placeholder="Selecciona uno o varios jugadores",
                        )
                    with player_filters[1]:
                        st.caption(" ")
                        st.button(
                            "Todos",
                            help="Seleccionar todos los jugadores de esta categoría.",
                            on_click=_select_all_players,
                            args=(player_ids,),
                            use_container_width=True,
                        )

                    if not selected_player_ids:
                        st.info(
                            "Selecciona uno o varios jugadores para ver su comparación."
                        )
                    else:
                        results = calculate_z_scores(
                            month_data,
                            selected_player_ids,
                            reference_category,
                            player_category,
                        )
                        st.markdown(
                            '<div class="ams-section-heading">'
                            "Resumen de la selección</div>",
                            unsafe_allow_html=True,
                        )
                        summary = st.columns(3, gap="medium")
                        with summary[0]:
                            render_dashboard_stat(
                                "Jugadores analizados",
                                str(len(selected_player_ids)),
                            )
                        with summary[1]:
                            render_dashboard_stat(
                                "Variables disponibles",
                                str(results["metric"].nunique()),
                            )
                        with summary[2]:
                            render_dashboard_stat(
                                "Categoría de referencia",
                                str(reference_category),
                            )

                        st.markdown(
                            '<div class="ams-section-heading">'
                            "Mapa de rendimiento</div>"
                            '<div class="ams-section-copy">'
                            "Cada celda muestra el Z-Score del jugador para esa variable."
                            "</div>",
                            unsafe_allow_html=True,
                        )
                        table = build_z_score_matrix(results)
                        metric_columns = table.columns.drop("Jugador").tolist()
                        styled_table = (
                            table.style.format(
                                {metric: "{:.1f}" for metric in metric_columns},
                                na_rep="—",
                            )
                            .map(z_score_cell_style, subset=metric_columns)
                            .set_properties(
                                subset=["Jugador"],
                                **{
                                    "font-weight": "bold",
                                    "text-align": "left",
                                    "background-color": "#F3F6FA",
                                },
                            )
                            .set_table_styles(
                                [
                                    {
                                        "selector": "th",
                                        "props": [
                                            ("background-color", "#F3F6FA"),
                                            ("color", "#536176"),
                                            ("font-weight", "700"),
                                            ("font-size", "0.72rem"),
                                            ("letter-spacing", "0.04em"),
                                            ("border-bottom", "1px solid #E3E8EF"),
                                        ],
                                    },
                                    {
                                        "selector": "td",
                                        "props": [
                                            ("padding", "0.65rem 0.75rem"),
                                            ("border-color", "#E8EDF2"),
                                        ],
                                    },
                                ]
                            )
                        )
                        with st.container(border=True):
                            st.caption(
                                "Los colores muestran el Z-Score frente a la categoría "
                                "de referencia. Un resultado positivo no significa "
                                "automáticamente que sea mejor en términos deportivos."
                            )
                            st.dataframe(
                                styled_table,
                                hide_index=True,
                                use_container_width=True,
                                height=min(38 + 35 * len(table), 650),
                            )

                        legend_items = [
                            ("> +2.0", "Excelente", 2.1),
                            ("+1.0 a +2.0", "Muy bueno", 1.5),
                            ("+0.5 a +1.0", "Bueno", 0.75),
                            ("-0.5 a +0.5", "Promedio (estable)", 0),
                            ("-1.0 a -0.5", "Debajo del promedio", -0.75),
                            ("-2.0 a -1.0", "Pobre", -1.5),
                            ("-3.0 a -2.0", "Muy pobre", -2.5),
                            ("< -3.0", "Extremadamente pobre", -3.1),
                        ]
                        with st.expander(
                            "Guía de colores del Z-Score", expanded=True
                        ):
                            for start in range(0, len(legend_items), 4):
                                legend_columns = st.columns(4, gap="small")
                                for column, item in zip(
                                    legend_columns, legend_items[start : start + 4]
                                ):
                                    score_range, label, score = item
                                    background = z_score_color(score)
                                    foreground = (
                                        "#FFFFFF"
                                        if score > 1 or score <= -2
                                        else "#1B1B1B"
                                    )
                                    column.markdown(
                                        f"<div style='background:{background};"
                                        f"color:{foreground};padding:.55rem;"
                                        "margin-bottom:.5rem;border-radius:.35rem;"
                                        "text-align:center'>"
                                        f"<strong>{score_range}</strong><br>{label}</div>",
                                        unsafe_allow_html=True,
                                    )

                        radar_candidates = results.loc[
                            results["player_id"].isin(selected_player_ids),
                            ["player_id", "player_name"],
                        ].drop_duplicates("player_id")
                        radar_ids = radar_candidates["player_id"].astype(str).tolist()
                        if (
                            st.session_state.get("radar_player_id")
                            not in radar_ids
                        ):
                            st.session_state["radar_player_id"] = radar_ids[0]
                        radar_names = dict(
                            zip(
                                radar_candidates["player_id"].astype(str),
                                radar_candidates["player_name"],
                            )
                        )
                        with st.container(border=True):
                            st.markdown(
                                '<div class="ams-section-heading">'
                                "Perfil individual</div>"
                                '<div class="ams-section-copy">'
                                "Compara las variables del jugador seleccionado con "
                                "la referencia Z=0."
                                "</div>",
                                unsafe_allow_html=True,
                            )
                            radar_filter, _ = st.columns([1, 2])
                            with radar_filter:
                                radar_player_id = st.selectbox(
                                    "Jugador del radar",
                                    radar_ids,
                                    format_func=lambda player_id: radar_names.get(
                                        player_id, str(player_id)
                                    ),
                                    key="radar_player_id",
                                )

                            player_results = results.loc[
                                results["player_id"].eq(radar_player_id)
                                & results["z_score"].notna()
                            ]
                            if player_results["metric"].nunique() < 3:
                                st.info(
                                    "Se necesitan al menos tres variables con "
                                    "referencia válida para dibujar el radar."
                                )
                            else:
                                figure = build_z_score_radar(
                                    player_results,
                                    radar_names[radar_player_id],
                                    reference_category,
                                    selected_month.strftime("%Y-%m"),
                                )
                                st.plotly_chart(
                                    figure,
                                    use_container_width=True,
                                    config={"displayModeBar": False},
                                )

    with mbd_tab:
        st.info("MBD Hopkins: Próximamente.")

    with swc_tab:
        st.info("SWC: Próximamente.")


if __name__ == "__main__":
    main()
