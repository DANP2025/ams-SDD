import pytest
import pandas as pd

from app import (
    MBD_DIRECTIONS,
    MissingRequiredColumnsError,
    build_mbd_forest_plot,
    build_mbd_player_matrix,
    build_z_score_matrix,
    build_z_score_radar,
    calculate_mbd_hopkins,
    calculate_z_scores,
    summarize_mbd_changes,
    build_mbd_player_matrix_html,
    canonicalize_headers,
    classify_mbd_clarity,
    classify_mbd_certainty,
    classify_z_score,
    lookup_mbd_direction,
    missing_secret_settings,
    normalize_header,
    prepare_monthly_measurements,
    standardize_sheet,
    summarize_mbd_probabilities,
    z_score_color,
    z_score_cell_style,
)


def test_mbd_hopkins_calculates_change_uncertainty_and_neutral_probabilities():
    measurements = pd.DataFrame(
        [
            ["p1", "Ana Uno", "2026-01-10", "U18", "Sprint", 10.0],
            ["p2", "Beto Dos", "2026-01-10", "U18", "Sprint", 14.0],
            ["p1", "Ana Uno", "2026-02-10", "U18", "Sprint", 13.0],
            ["p2", "Beto Dos", "2026-02-10", "U18", "Sprint", 15.0],
        ],
        columns=[
            "player_id",
            "player_name",
            "date",
            "category",
            "metric",
            "value",
        ],
    )
    measurements["date"] = pd.to_datetime(measurements["date"])

    results = calculate_mbd_hopkins(
        measurements,
        ["p1"],
        "U18",
        pd.Period("2026-01", freq="M"),
        pd.Period("2026-02", freq="M"),
    )

    result = results.iloc[0]
    reference_sd = 2**0.5 * 2
    expected_te = reference_sd * (1 - 0.90) ** 0.5
    assert result["change"] == pytest.approx(3.0)
    assert result["reference_n"] == 2
    assert result["reference_sd"] == pytest.approx(reference_sd)
    assert result["swc"] == pytest.approx(0.2 * reference_sd)
    assert result["effect_size"] == pytest.approx(3 / reference_sd)
    assert result["typical_error"] == pytest.approx(expected_te)
    assert result["se_change"] == pytest.approx(expected_te * 2**0.5)
    assert result["ci_lower"] == pytest.approx(
        3 - 1.96 * expected_te * 2**0.5
    )
    assert result["ci_upper"] == pytest.approx(
        3 + 1.96 * expected_te * 2**0.5
    )
    assert (
        result["p_below_swc"]
        + result["p_trivial"]
        + result["p_above_swc"]
    ) == pytest.approx(1.0)
    assert pd.isna(result["p_benefit"])
    assert result["certainty"] == "Sin dirección validada"
    assert result["availability"] == "Disponible"

    figure = build_mbd_forest_plot(results)
    assert figure.data[0].x[0] == pytest.approx(
        result["change"] / result["reference_sd"]
    )
    assert figure.layout.xaxis.title.text == (
        "Tamaño del efecto (SD) · SWC = ±0.2"
    )
    assert figure.data[0].error_x.array[0] == pytest.approx(
        result["ci_upper"] / result["reference_sd"]
        - result["change"] / result["reference_sd"]
    )
    assert len(figure.layout.shapes) == 6
    assert {
        shape.x0
        for shape in figure.layout.shapes
        if shape.type == "line"
    } == {-0.2, 0, 0.2}


def test_mbd_matrix_groups_metrics_by_source_and_shows_neutral_probabilities():
    results = pd.DataFrame(
        [
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "source": "Rendimiento",
                "metric": "VO2 max",
                "change": 2.0,
                "p_below_swc": 0.1,
                "p_trivial": 0.2,
                "p_above_swc": 0.7,
                "availability": "Disponible",
            },
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "source": "Plat de fuerza",
                "metric": "Fuerza CMJ",
                "change": float("nan"),
                "p_below_swc": float("nan"),
                "p_trivial": float("nan"),
                "p_above_swc": float("nan"),
                "availability": "Falta una medición Pre o Post.",
            },
        ]
    )

    matrix = build_mbd_player_matrix(results)

    assert matrix.index.name == "JUGADOR"
    assert matrix.columns.tolist() == [
        ("RENDIMIENTO", "VO2 max"),
        ("PLATAFORMA DE FUERZA", "Fuerza CMJ"),
    ]
    assert matrix.iloc[0, 0] == "Sin dirección validada"
    assert matrix.iloc[0, 1] == "No disponible"


def test_mbd_matrix_html_colors_will_hopkins_labels_without_inner_scrolling():
    results = pd.DataFrame(
        [
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "source": "Rendimiento",
                "metric": "VO2 max",
                "change": 2.0,
                "p_benefit": 0.97,
                "p_harm": 0.01,
                "certainty": "Muy Probable Beneficioso",
                "clarity": "CLARO",
                "availability": "Disponible",
                "p_below_swc": 0.01,
                "p_trivial": 0.02,
                "p_above_swc": 0.97,
            },
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "source": "Plat de fuerza",
                "metric": "Alt. Salto",
                "change": -0.5,
                "p_benefit": 0.10,
                "p_harm": 0.70,
                "certainty": "Probable Perjudicial",
                "clarity": "NO CLARO",
                "availability": "Disponible",
                "p_below_swc": 0.70,
                "p_trivial": 0.20,
                "p_above_swc": 0.10,
            },
        ]
    )

    table = build_mbd_player_matrix_html(results)

    assert 'class="ams-mbd-table-wrap"' in table
    assert 'rowspan="2">JUGADOR</th>' in table
    assert 'colspan="1">RENDIMIENTO (1)</th>' in table
    assert 'colspan="1">PLATAFORMA DE FUERZA (1)</th>' in table
    assert "Muy Probable Beneficioso<br>CLARO" in table
    assert "Probable Perjudicial<br>NO CLARO" in table
    assert "70% / 20% / 10%" not in table
    assert "Δ " not in table
    assert 'background:#166534;color:#ffffff' in table
    assert 'background:#fee2e2;color:#991b1b' in table
    assert "Alt. Salto" in table


def test_mbd_matrix_html_has_players_as_rows_and_variables_as_columns():
    results = pd.DataFrame(
        [
            {
                "player_id": player_id,
                "player_name": player_name,
                "source": "Rendimiento",
                "metric": "VO2 max",
                "change": 0.1,
                "p_benefit": 0.8,
                "p_harm": 0.01,
                "certainty": "Probable Beneficioso",
                "clarity": "CLARO",
                "availability": "Disponible",
                "p_below_swc": 0.01,
                "p_trivial": 0.19,
                "p_above_swc": 0.8,
            }
            for player_id, player_name in (("p1", "Ana Uno"), ("p2", "Beto Dos"))
        ]
    )

    table = build_mbd_player_matrix_html(results)

    assert table.count("<tr>") == 4
    assert table.count('class="ams-mbd-cell ') == 2
    assert "Ana Uno" in table and "Beto Dos" in table
    assert "Δ" not in table


def test_mbd_direction_catalog_normalizes_metrics_and_leaves_ambiguous_neutral():
    assert lookup_mbd_direction("ALT. Salto (cm)", MBD_DIRECTIONS) == "mayor"
    assert lookup_mbd_direction("Vmax (m/s)", MBD_DIRECTIONS) == "mayor"
    assert lookup_mbd_direction("F0 (N/kg)", MBD_DIRECTIONS) == "mayor"
    assert lookup_mbd_direction("DRF", MBD_DIRECTIONS) is None
    assert lookup_mbd_direction("RFD Dec", MBD_DIRECTIONS) is None


def test_mbd_forest_plot_bounds_extreme_effects_and_marks_them():
    results = pd.DataFrame(
        [
            {
                "player_name": "Jugador",
                "metric": "Variable extrema",
                "change": 20.0,
                "reference_sd": 1.0,
                "swc": 0.2,
                "ci_lower": 18.0,
                "ci_upper": 22.0,
                "p_below_swc": 0.0,
                "p_trivial": 0.0,
                "p_above_swc": 1.0,
            }
        ]
    )

    figure = build_mbd_forest_plot(results)

    assert tuple(figure.layout.xaxis.range) == (-4.5, 6.8)
    assert figure.data[0].x[0] == 4.5
    assert figure.data[0].marker.symbol[0] == "triangle-right"
    assert figure.data[0].customdata[0][1] == 20.0
    assert figure.data[0].customdata[0][2] == 18.0
    assert figure.data[0].customdata[0][3] == 22.0
    annotations = [annotation.text for annotation in figure.layout.annotations]
    assert "0% · 0% · 100%" in annotations
    assert "Perjudicial" in annotations
    assert "Beneficioso" in annotations


def test_mbd_forest_plot_colors_outcomes_and_grows_to_show_all_rows():
    results = pd.DataFrame(
        [
            {
                "player_name": "Jugador",
                "metric": f"Variable {index}",
                "change": 0.3,
                "reference_sd": 1.0,
                "swc": 0.2,
                "ci_lower": -0.1,
                "ci_upper": 0.7,
                "p_below_swc": 0.1,
                "p_trivial": 0.2,
                "p_above_swc": 0.7,
                "direction": "mayor",
                "certainty": (
                    "Probable Beneficioso"
                    if index % 2
                    else "Probable Perjudicial"
                ),
                "clarity": "NO CLARO" if index % 2 else "CLARO",
                "p_benefit": 0.7 if index % 2 else 0.1,
                "p_harm": 0.1 if index % 2 else 0.7,
                "availability": "Disponible",
            }
            for index in range(1, 19)
        ]
    )

    figure = build_mbd_forest_plot(results)

    trace_by_name = {trace.name: trace for trace in figure.data}
    assert set(trace_by_name) == {
        "Beneficioso · no claro",
        "Perjudicial · claro",
    }
    assert trace_by_name["Beneficioso · no claro"].marker.color == "#86c995"
    assert trace_by_name["Perjudicial · claro"].marker.color == "#b91c1c"
    assert sum(len(trace.x) for trace in figure.data) == len(results)
    assert figure.layout.height > 800
    fills = {
        shape.fillcolor for shape in figure.layout.shapes if shape.type == "rect"
    }
    assert "rgba(220, 38, 38, 0.11)" in fills
    assert "rgba(34, 197, 94, 0.12)" in fills


def test_mbd_change_summary_groups_clear_direction_and_unclear_results():
    results = pd.DataFrame(
        [
            {
                "availability": "Disponible",
                "certainty": "Muy Probable Beneficioso",
                "clarity": "CLARO",
                "p_benefit": 0.97,
                "p_harm": 0.01,
            },
            {
                "availability": "Disponible",
                "certainty": "Probable Perjudicial",
                "clarity": "CLARO",
                "p_benefit": 0.01,
                "p_harm": 0.8,
            },
            {
                "availability": "Disponible",
                "certainty": "Posible Beneficioso",
                "clarity": "NO CLARO",
                "p_benefit": 0.4,
                "p_harm": 0.3,
            },
            {
                "availability": "Disponible",
                "certainty": "Trivial",
                "clarity": "CLARO",
                "p_benefit": 0.2,
                "p_harm": 0.2,
            },
            {
                "availability": "Disponible",
                "certainty": "Sin dirección validada",
                "clarity": "Sin dirección validada",
                "p_benefit": float("nan"),
                "p_harm": float("nan"),
            },
            {
                "availability": "Falta una medición Pre o Post.",
                "certainty": "No disponible",
                "clarity": "No disponible",
                "p_benefit": float("nan"),
                "p_harm": float("nan"),
            },
        ]
    )

    assert summarize_mbd_changes(results) == {
        "Beneficioso": 1,
        "Perjudicial": 1,
        "Trivial / No claro": 3,
    }


def test_mbd_probability_summary_counts_unique_most_likely_zones_and_ties():
    results = pd.DataFrame(
        [
            {
                "availability": "Disponible",
                "p_below_swc": 0.7,
                "p_trivial": 0.2,
                "p_above_swc": 0.1,
            },
            {
                "availability": "Disponible",
                "p_below_swc": 0.1,
                "p_trivial": 0.2,
                "p_above_swc": 0.7,
            },
            {
                "availability": "Disponible",
                "p_below_swc": 0.2,
                "p_trivial": 0.6,
                "p_above_swc": 0.2,
            },
            {
                "availability": "Disponible",
                "p_below_swc": 0.4,
                "p_trivial": 0.2,
                "p_above_swc": 0.4,
            },
            {
                "availability": "No disponible",
                "p_below_swc": float("nan"),
                "p_trivial": float("nan"),
                "p_above_swc": float("nan"),
            },
        ]
    )

    assert summarize_mbd_probabilities(results) == {
        "Menor que −SWC": 1,
        "Dentro de ±SWC": 1,
        "Mayor que +SWC": 1,
        "Empate": 1,
    }


def test_mbd_hopkins_applies_approved_direction_and_clarity_labels():
    measurements = pd.DataFrame(
        [
            ["p1", "Ana Uno", "2026-01-10", "U18", "Sprint", 10.0],
            ["p2", "Beto Dos", "2026-01-10", "U18", "Sprint", 14.0],
            ["p1", "Ana Uno", "2026-02-10", "U18", "Sprint", 13.0],
        ],
        columns=[
            "player_id",
            "player_name",
            "date",
            "category",
            "metric",
            "value",
        ],
    )
    measurements["date"] = pd.to_datetime(measurements["date"])

    result = calculate_mbd_hopkins(
        measurements,
        ["p1"],
        "U18",
        pd.Period("2026-01", freq="M"),
        pd.Period("2026-02", freq="M"),
        directions={"Sprint": "mayor"},
    ).iloc[0]

    assert result["p_benefit"] == pytest.approx(result["p_above_swc"])
    assert result["p_harm"] == pytest.approx(result["p_below_swc"])
    assert result["certainty"].endswith("Beneficioso")
    assert result["clarity"] in {"CLARO", "NO CLARO"}


@pytest.mark.parametrize(
    ("probability_benefit", "probability_harm", "expected"),
    [
        (0.996, 0.001, "Casi Seguro Beneficioso"),
        (0.96, 0.02, "Muy Probable Beneficioso"),
        (0.76, 0.02, "Probable Beneficioso"),
        (0.30, 0.01, "Posible Beneficioso"),
        (0.20, 0.25, "Trivial"),
        (0.01, 0.80, "Probable Perjudicial"),
        (0.995, 0.001, "Muy Probable Beneficioso"),
        (0.95, 0.01, "Probable Beneficioso"),
        (0.75, 0.01, "Posible Beneficioso"),
        (0.25, 0.01, "Trivial"),
    ],
)
def test_mbd_certainty_classification_uses_specified_thresholds(
    probability_benefit,
    probability_harm,
    expected,
):
    assert (
        classify_mbd_certainty(probability_benefit, probability_harm)
        == expected
    )


@pytest.mark.parametrize(
    ("probability_benefit", "probability_harm", "expected"),
    [
        (0.051, 0.051, "NO CLARO"),
        (0.05, 0.9, "CLARO"),
        (0.9, 0.05, "CLARO"),
        (0.049, 0.051, "CLARO"),
    ],
)
def test_mbd_clarity_uses_strict_five_percent_threshold(
    probability_benefit,
    probability_harm,
    expected,
):
    assert (
        classify_mbd_clarity(probability_benefit, probability_harm)
        == expected
    )


def test_mbd_hopkins_marks_missing_values_and_zero_reference_sd_unavailable():
    measurements = pd.DataFrame(
        [
            ["p1", "Ana Uno", "2026-01-10", "U18", "Metric A", 10.0],
            ["p1", "Ana Uno", "2026-02-10", "U18", "Metric A", 12.0],
            ["p1", "Ana Uno", "2026-01-11", "U18", "Metric B", 10.0],
            ["p2", "Beto Dos", "2026-01-11", "U18", "Metric B", 10.0],
            ["p1", "Ana Uno", "2026-02-11", "U18", "Metric B", 12.0],
            ["p1", "Ana Uno", "2026-01-12", "U18", "Metric C", 10.0],
        ],
        columns=[
            "player_id",
            "player_name",
            "date",
            "category",
            "metric",
            "value",
        ],
    )
    measurements["date"] = pd.to_datetime(measurements["date"])

    results = calculate_mbd_hopkins(
        measurements,
        ["p1"],
        "U18",
        pd.Period("2026-01", freq="M"),
        pd.Period("2026-02", freq="M"),
    ).set_index("metric")

    assert "al menos dos mediciones" in results.loc["Metric A", "availability"]
    assert "es cero" in results.loc["Metric B", "availability"]
    assert "Falta una medición" in results.loc["Metric C", "availability"]
    assert pd.isna(results.loc["Metric A", "change"])
    assert pd.isna(results.loc["Metric B", "ci_lower"])
    assert pd.isna(results.loc["Metric C", "change"])


def test_normalize_header_ignores_accents_case_and_separators():
    assert normalize_header("  Fecha_de NACIMIENTO ") == "fecha de nacimiento"


def test_missing_secret_settings_lists_incomplete_private_configuration():
    assert missing_secret_settings({}) == [
        "[auth]",
        "[app]",
        "[gcp_service_account]",
    ]


def test_missing_secret_settings_accepts_complete_configuration():
    secrets = {
        "auth": {
            "redirect_uri": "https://ams.streamlit.app/oauth2callback",
            "cookie_secret": "generated-secret",
            "client_id": "oauth-client-id",
            "client_secret": "oauth-client-secret",
            "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        },
        "app": {
            "google_sheet_id": "spreadsheet-id",
            "authorized_emails": ["one@example.com", "two@example.com"],
        },
        "gcp_service_account": {
            key: "configured"
            for key in (
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
        },
    }

    assert missing_secret_settings(secrets) == []


def test_base_sheet_accepts_current_headers():
    frame = standardize_sheet(
        "Base de datos",
        [
            [
                "DNI",
                "Nombre",
                "Apellido",
                "Fecha de Nacimiento",
                "Posicion",
                "Categoria",
                "URL foto",
            ],
            ["123", "Ana", "Ejemplo", "2008-05-01", "Delantera", "U18", ""],
        ],
    )

    assert frame.columns.tolist() == [
        "player_id",
        "first_name",
        "last_name",
        "birth_date",
        "position",
        "category",
        "photo_url",
    ]
    assert frame.loc[0, "player_id"] == "123"


def test_measurement_sheet_accepts_a_user_mapped_required_header():
    frame = standardize_sheet(
        "Rendimiento",
        [
            ["DNI", "Día de test", "Categoría", "VO2 max"],
            ["123", "2026-03-01", "U18", "52.4"],
        ],
        {"Día de test": "date"},
    )

    assert "date" in frame.columns


def test_measurement_sheet_accepts_common_header_variants():
    frame = standardize_sheet(
        "Rendimiento",
        [
            ["Dni", "Fecha de evaluación", "Categoría", "VO2 max"],
            ["123", "2026-03-01", "U18", "52.4"],
        ],
    )

    assert frame.columns.tolist() == ["player_id", "date", "category", "VO2 max"]
    assert frame.loc[0, "VO2 max"] == "52.4"


def test_unrecognized_required_header_reports_a_clear_error():
    with pytest.raises(MissingRequiredColumnsError) as error:
        standardize_sheet(
            "Rendimiento",
            [["DNI", "Fecha", "Grupo"], ["123", "2026-03-01", "U18"]],
        )
    assert error.value.missing_columns == ["category"]
    assert error.value.candidate_headers == ["Grupo"]


def test_duplicate_headers_that_resolve_to_same_field_are_rejected():
    with pytest.raises(ValueError, match="más de una columna"):
        canonicalize_headers(["DNI", "ID jugador"])


def test_classify_z_score_uses_documented_boundaries():
    assert classify_z_score(2) == "Muy Bueno"
    assert classify_z_score(2.01) == "Excelente"
    assert classify_z_score(-0.5) == "Promedio (Estable)"
    assert classify_z_score(-1) == "Debajo del Promedio"
    assert classify_z_score(-3) == "Muy Pobre"
    assert classify_z_score(-3.01) == "Extremadamente Pobre"


def test_z_score_colors_follow_the_documented_boundaries():
    assert z_score_color(2) == "#4CAF50"
    assert z_score_color(2.01) == "#1A6E1A"
    assert z_score_color(-0.5) == "#EEEEEE"
    assert z_score_color(-1) == "#FFD600"
    assert z_score_color(-3) == "#E53935"
    assert z_score_color(-3.01) == "#8B0000"


def test_z_score_matrix_keeps_full_precision_for_display_formatting():
    results = pd.DataFrame(
        [
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "metric": "VO2 max",
                "z_score": 1.234,
            },
            {
                "player_id": "p1",
                "player_name": "Ana Uno",
                "metric": "Fuerza",
                "z_score": -0.456,
            },
        ]
    )

    matrix = build_z_score_matrix(results)

    assert matrix.columns.tolist() == ["Jugador", "Fuerza", "VO2 max"]
    assert matrix.loc[0, "Fuerza"] == pytest.approx(-0.456)
    assert matrix.loc[0, "VO2 max"] == pytest.approx(1.234)


def test_z_score_cell_style_uses_classification_colors_and_readable_text():
    assert "background-color: #4CAF50" in z_score_cell_style(1.5)
    assert "color: #FFFFFF" in z_score_cell_style(1.5)
    assert "background-color: #E9ECEF" in z_score_cell_style(float("nan"))


def test_z_score_radar_shows_zero_reference_and_one_decimal_hover_values():
    player_results = pd.DataFrame(
        [
            {"metric": "VO2 max", "z_score": 1.234},
            {"metric": "Fuerza", "z_score": -0.456},
            {"metric": "Velocidad", "z_score": 0.75},
        ]
    )

    figure = build_z_score_radar(
        player_results,
        "Ana Uno",
        "Primera",
        "2026-01",
    )

    assert len(figure.data) == 2
    assert list(figure.data[0].r) == [3.0, 3.0, 3.0, 3.0]
    assert list(figure.data[1].customdata) == [-0.456, 1.234, 0.75, -0.456]
    assert figure.data[1].hovertemplate.find("%{customdata:.1f}") >= 0
    assert list(figure.layout.polar.radialaxis.ticktext) == [
        "-3",
        "-2",
        "-1",
        "0",
        "+1",
        "+2",
        "+3",
    ]


def test_prepare_measurements_uses_latest_value_per_player_and_month():
    sheets = {
        "Base de datos": standardize_sheet(
            "Base de datos",
            [
                ["DNI", "Nombre", "Apellido", "Categoria"],
                ["001", "Ana", "Uno", "U18"],
                ["002", "Beto", "Dos", "U18"],
            ],
        ),
        "Rendimiento": standardize_sheet(
            "Rendimiento",
            [
                ["DNI", "Fecha", "Categoria", "VO2 max"],
                ["001", "2026-03-01", "U18", "40"],
                ["001", "2026-03-20", "U18", "50"],
                ["002", "2026-03-15", "U18", "60"],
                ["002", "", "U18", "80"],
            ],
        ),
        "Plat de fuerza": standardize_sheet(
            "Plat de fuerza",
            [
                ["DNI", "Fecha", "Categoria", "Fuerza"],
                ["001", "2026-03-10", "U18", "100"],
                ["002", "2026-03-10", "U18", "120"],
            ],
        ),
    }

    frame, excluded_rows, diagnostics = prepare_monthly_measurements(sheets)

    ana_vo2 = frame.loc[
        (frame["player_id"] == "001") & (frame["metric"] == "VO2 max"),
        "value",
    ].item()
    assert ana_vo2 == 50
    assert excluded_rows == 1
    assert frame.loc[frame["metric"].eq("VO2 max"), "source"].unique().tolist() == [
        "Rendimiento"
    ]
    assert frame.loc[frame["metric"].eq("Fuerza"), "source"].unique().tolist() == [
        "Plat de fuerza"
    ]
    assert diagnostics["Rendimiento"] == {
        "rows": 4,
        "excluded": 1,
        "missing_player": 0,
        "invalid_date": 1,
        "missing_category": 0,
        "multiple_issues": 0,
    }


def test_prepare_measurements_reports_overlapping_missing_fields_and_ignores_blank_rows():
    sheets = {
        "Base de datos": standardize_sheet(
            "Base de datos",
            [
                ["DNI", "Nombre", "Apellido", "Categoria"],
                ["001", "Ana", "Uno", "U18"],
            ],
        ),
        "Rendimiento": standardize_sheet(
            "Rendimiento",
            [
                ["DNI", "Fecha", "Categoria", "VO2 max"],
                ["", "", "", ""],
                ["", "2026-03-01", "U18", "52"],
                ["002", "fecha inválida", "", "53"],
                ["003", "2026-03-05", "U18", "54"],
            ],
        ),
        "Plat de fuerza": standardize_sheet(
            "Plat de fuerza",
            [
                ["DNI", "Fecha", "Categoria", "Fuerza"],
                ["  ", "  ", "  ", "  "],
            ],
        ),
    }

    measurements, excluded_rows, diagnostics = prepare_monthly_measurements(
        sheets
    )

    assert excluded_rows == 2
    assert len(measurements) == 1
    assert diagnostics["Rendimiento"] == {
        "rows": 3,
        "excluded": 2,
        "missing_player": 1,
        "invalid_date": 1,
        "missing_category": 1,
        "multiple_issues": 1,
    }
    assert diagnostics["Plat de fuerza"] == {
        "rows": 0,
        "excluded": 0,
        "missing_player": 0,
        "invalid_date": 0,
        "missing_category": 0,
        "multiple_issues": 0,
    }


def test_calculate_z_scores_excludes_zero_and_reports_insufficient_reference():
    measurements = pd.DataFrame(
        [
            {"player_id": "p1", "player_name": "Ana Uno", "category": "U18",
             "metric": "VO2 max", "value": 50},
            {"player_id": "r1", "player_name": "Ref Uno", "category": "U21",
             "metric": "VO2 max", "value": 40},
            {"player_id": "r2", "player_name": "Ref Dos", "category": "U21",
             "metric": "VO2 max", "value": 60},
            {"player_id": "r3", "player_name": "Ref Tres", "category": "U21",
             "metric": "VO2 max", "value": 0},
            {"player_id": "p1", "player_name": "Ana Uno", "category": "U18",
             "metric": "Fuerza", "value": 100},
            {"player_id": "r1", "player_name": "Ref Uno", "category": "U21",
             "metric": "Fuerza", "value": 100},
        ]
    )

    result = calculate_z_scores(measurements, ["p1"], "U21")

    vo2 = result.loc[result["metric"] == "VO2 max"].iloc[0]
    strength = result.loc[result["metric"] == "Fuerza"].iloc[0]
    assert vo2["z_score"] == pytest.approx(0)
    assert vo2["reference_count"] == 2
    assert pd.isna(strength["z_score"])
    assert strength["classification"] == "No disponible"