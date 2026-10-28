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

    st.title("AMS · Athletic Management System")
    st.caption("Acceso restringido al equipo autorizado.")

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
        st.warning(
            f"Se excluyeron {excluded_rows} filas de medición sin jugador, "
            "fecha o categoría válida."
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
            selected_month = st.selectbox(
                "Mes y año",
                available_months,
                format_func=lambda period: period.strftime("%m/%Y"),
            )
            month_data = measurements.loc[
                measurements["date"].dt.to_period("M").eq(selected_month)
            ]
            categories = sorted(month_data["category"].dropna().unique())
            if not categories:
                st.warning("No hay categorías en el mes seleccionado.")
            else:
                filters = st.columns(2)
                with filters[0]:
                    player_category = st.selectbox(
                        "Categoría de jugadores", categories
                    )
                    player_options = (
                        month_data.loc[month_data["category"].eq(player_category)]
                        .drop_duplicates("player_id")
                        .sort_values("player_name")
                    )
                    display_names = dict(
                        zip(player_options["player_id"], player_options["player_name"])
                    )
                    selected_player_ids = st.multiselect(
                        "Jugador o jugadores",
                        player_options["player_id"].tolist(),
                        format_func=lambda player_id: display_names[player_id],
                    )
                with filters[1]:
                    reference_category = st.selectbox(
                        "Categoría de referencia", categories
                    )

                if not selected_player_ids:
                    st.info("Selecciona al menos un jugador para ver su comparación.")
                else:
                    results = calculate_z_scores(
                        month_data,
                        selected_player_ids,
                        reference_category,
                        player_category,
                    )
                    st.caption(
                        "Los colores muestran la distancia respecto de la media de "
                        "referencia. Un valor por encima de la media no significa "
                        "automáticamente que sea mejor en términos deportivos."
                    )
                    table = results[
                        [
                            "player_name",
                            "metric",
                            "value",
                            "reference_mean",
                            "z_score",
                            "classification",
                        ]
                    ].rename(
                        columns={
                            "player_name": "Jugador",
                            "metric": "Variable",
                            "value": "Valor",
                            "reference_mean": "Media de referencia",
                            "z_score": "Z-Score",
                            "classification": "Clasificación",
                        }
                    )
                    classification_colors = {
                        "Excelente": ("#1A6E1A", "#FFFFFF"),
                        "Muy Bueno": ("#4CAF50", "#FFFFFF"),
                        "Bueno": ("#A8D08D", "#1B1B1B"),
                        "Promedio (Estable)": ("#FFFFFF", "#1B1B1B"),
                        "Debajo del Promedio": ("#FFD600", "#1B1B1B"),
                        "Pobre": ("#FF9800", "#1B1B1B"),
                        "Muy Pobre": ("#E53935", "#FFFFFF"),
                        "Extremadamente Pobre": ("#8B0000", "#FFFFFF"),
                        "No disponible": ("#E9ECEF", "#1B1B1B"),
                    }

                    def style_classification(row: pd.Series) -> list[str]:
                        background, foreground = classification_colors[
                            row["Clasificación"]
                        ]
                        return [
                            ""
                            if column != "Clasificación"
                            else (
                                f"background-color: {background}; "
                                f"color: {foreground}"
                            )
                            for column in row.index
                        ]

                    st.dataframe(
                        table.style.apply(style_classification, axis=1),
                        hide_index=True,
                        use_container_width=True,
                    )

                    figure = go.Figure()
                    for player_id in selected_player_ids:
                        player_results = results.loc[
                            results["player_id"].eq(str(player_id))
                            & results["z_score"].notna()
                        ]
                        if not player_results.empty:
                            figure.add_trace(
                                go.Scatterpolar(
                                    r=player_results["z_score"],
                                    theta=player_results["metric"],
                                    fill="toself",
                                    name=display_names[str(player_id)],
                                    marker={
                                        "color": [
                                            z_score_color(value)
                                            for value in player_results["z_score"]
                                        ],
                                        "size": 9,
                                    },
                                )
                            )
                    if figure.data:
                        figure.update_layout(
                            polar={"radialaxis": {"visible": True}},
                            showlegend=True,
                            margin={"t": 30, "b": 30},
                        )
                        st.plotly_chart(figure, use_container_width=True)
                    else:
                        st.info(
                            "No hay suficientes datos de referencia para dibujar el radar."
                        )

    with mbd_tab:
        st.info("MBD Hopkins: Próximamente.")

    with swc_tab:
        st.info("SWC: Próximamente.")


if __name__ == "__main__":
    main()
