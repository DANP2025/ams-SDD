import pytest
import pandas as pd

from app import (
    MissingRequiredColumnsError,
    calculate_z_scores,
    canonicalize_headers,
    classify_z_score,
    missing_secret_settings,
    normalize_header,
    prepare_monthly_measurements,
    standardize_sheet,
    z_score_color,
)


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

    frame, excluded_rows = prepare_monthly_measurements(sheets)

    ana_vo2 = frame.loc[
        (frame["player_id"] == "001") & (frame["metric"] == "VO2 max"),
        "value",
    ].item()
    assert ana_vo2 == 50
    assert excluded_rows == 1


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