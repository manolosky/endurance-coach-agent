"""Migrate a v1 data folder (Spanish columns/values) to the v2 schema (English).

  python3 scripts/migrate_v1_to_v2.py <v1_dir> <v2_dir>

Rows are kept 1:1. Free-text fields are copied as they are (translate them afterwards if needed).
"""

import csv
import os
import sys

import _bootstrap  # noqa: F401

from coach.schema import COLUMNS

FILES = {
    "sesiones.csv": "sessions.csv", "intervalos.csv": "intervals.csv", "fuerza.csv": "strength.csv",
    "semanas.csv": "weeks.csv", "diario.csv": "daily.csv", "tests.csv": "tests.csv",
    "medidas.csv": "measurements.csv", "material.csv": "gear.csv",
}

COLS = {
    "sesion_id": "session_id", "fecha": "date", "semana": "week", "fase": "phase",
    "deporte": "sport", "tipo": "type", "estado": "status", "motivo_cambio": "change_reason",
    "plan_nombre": "plan_name", "plan_duracion_min": "plan_duration_min",
    "plan_techo_fc_lpm": "plan_hr_cap_bpm", "plan_potencia_min_w": "plan_power_min_w",
    "plan_potencia_max_w": "plan_power_max_w", "fuente": "source", "actividad_id": "activity_id",
    "hora_inicio": "start_time", "superficie": "surface", "material_id": "gear_id",
    "temperatura_c": "temperature_c", "duracion_min": "duration_min",
    "duracion_total_min": "elapsed_min", "distancia_km": "distance_km",
    "desnivel_m": "elevation_gain_m", "fc_media_lpm": "hr_avg_bpm", "fc_max_lpm": "hr_max_bpm",
    "potencia_media_w": "power_avg_w", "potencia_normalizada_w": "power_np_w",
    "ritmo_medio_s_km": "pace_avg_s_km", "velocidad_media_kmh": "speed_avg_kmh",
    "cadencia_media": "cadence_avg", "tiempo_contacto_ms": "ground_contact_ms",
    "oscilacion_vertical_cm": "vertical_osc_cm", "longitud_zancada_m": "stride_length_m",
    "rigidez_pierna_kn_m": "leg_stiffness_kn_m", "tipo_tss": "tss_type",
    "desacoplamiento_pct": "decoupling_pct", "pct_tiempo_sobre_techo": "pct_time_over_cap",
    "techo_respetado": "cap_respected", "recuperacion_fallida": "failed_recovery",
    "carga_coros": "coros_load", "esfuerzo_relativo_strava": "strava_relative_effort",
    "molestias": "issues", "cho_g_h": "carbs_g_h", "fuerza_hecha": "strength_done",
    "zonas_version": "zones_version", "notas": "notes",
    # intervals
    "duracion_s": "duration_s", "distancia_m": "distance_m", "fc_final_lpm": "hr_end_bpm",
    "techo_superado": "cap_exceeded",
    # strength
    "bloque": "block", "ejercicio": "exercise", "series": "sets", "segundos": "seconds",
    "carga_kg": "load_kg", "banda": "band",
    # weeks
    "fecha_inicio": "start_date", "semana_fase": "phase_week", "es_descarga": "is_deload",
    "sesiones_plan": "sessions_planned", "sesiones_hechas": "sessions_done",
    "cumplimiento_pct": "compliance_pct", "min_carrera": "run_min", "km_carrera": "run_km",
    "min_bici": "bike_min", "km_bici": "bike_km", "sesiones_fuerza": "strength_sessions",
    "tss_carrera": "tss_run", "tss_bici": "tss_bike", "var_km_carrera_pct": "run_km_change_pct",
    "ef_rodaje_control": "ef_control_run", "desacoplamiento_tirada_pct": "long_run_decoupling_pct",
    "hrv_media": "hrv_avg_ms", "fc_reposo_media_lpm": "rhr_avg_bpm", "sueno_medio_h": "sleep_avg_h",
    "dias_verde": "days_green", "dias_amarillo": "days_yellow", "dias_rojo": "days_red",
    "dolor_tibia_max": "pain_max", "peso_kg": "weight_kg", "sensaciones_1_5": "feeling_1_5",
    "motivo": "rationale", "integracion": "integration",
    # daily
    "hrv_rango_min_ms": "hrv_range_min_ms", "hrv_rango_max_ms": "hrv_range_max_ms",
    "hrv_media_7d_ms": "hrv_7d_avg_ms", "fc_reposo_lpm": "rhr_bpm",
    "fc_reposo_media_30d_lpm": "rhr_30d_avg_bpm", "sueno_h": "sleep_h",
    "sueno_puntuacion": "sleep_score", "temperatura_desv_c": "temp_dev_c",
    "ratio_carga": "load_ratio", "semaforo": "light", "sesion_prevista": "planned_session",
    "accion": "action",
    # tests
    "parametro": "parameter", "valor": "value", "unidad": "unit",
    "valor_anterior": "previous_value", "condiciones": "conditions", "valido": "valid",
    # measurements
    "rango_referencia": "reference_range",
    # gear
    "modelo": "model", "uso": "use", "fecha_alta": "start_date", "km_iniciales": "initial_km",
    "km_limite": "limit_km", "fecha_baja": "retired_date",
}

VALUES = {
    "phase": {"readaptacion": "return_to_run", "base": "base", "desarrollo": "build",
              "especifica": "specific", "puesta_a_punto": "taper", "transicion": "transition"},
    "sport": {"carrera": "run", "bici": "bike", "fuerza": "strength"},
    "status": {"completada": "completed", "modificada": "modified", "no_realizada": "missed",
               "extra": "extra"},
    "surface": {"cesped": "grass", "tierra": "dirt", "pista": "track", "asfalto": "asphalt",
                "mixto": "mixed", "carretera": "road"},
    "decision": {"apretar": "push", "mantener": "hold", "aflojar": "ease"},
    "integration": {"ok": "ok", "parcial": "partial", "fallback": "fallback"},
    "light": {"verde": "green", "amarillo": "yellow", "rojo": "red", "sin_datos": "no_data"},
    "unit": {"lpm": "bpm"},
    "use": {"rodaje": "easy", "calidad": "quality", "competicion": "race", "trail": "trail"},
}

TYPE_VALUES = {
    "sessions.csv": {"rodaje_z1": "easy_z1", "trote_caminar": "run_walk",
                     "umbral_noruego": "norwegian_threshold", "tirada_larga": "long_run",
                     "ritmo_maraton": "marathon_pace", "factor_x": "x_factor",
                     "recuperacion": "recovery", "test": "test", "fuerza": "strength",
                     "competicion": "race"},
    "intervals.csv": {"calentamiento": "warmup", "trabajo": "work", "recuperacion": "recovery",
                      "vuelta_calma": "cooldown"},
    "measurements.csv": {"peso": "weight", "altura": "height", "grasa_pct": "body_fat_pct",
                         "hemoglobina": "haemoglobin"},
    "gear.csv": {"zapatilla": "shoe", "bici": "bike"},
}

TEST_VALUES = {"deriva_bici": "bike_drift", "rodaje_control": "control_run",
               "umbral_30min": "threshold_30min", "cp_3_9": "cp_3_9", "carrera": "race"}
PARAM_VALUES = {"lthr": "lthr", "ritmo_umbral": "threshold_pace",
                "potencia_umbral": "threshold_power", "cp": "cp", "techo_z1": "z1_cap",
                "ef": "ef", "fc_max": "hr_max"}


def convert_row(old_name, new_name, row):
    out = {c: "" for c in COLUMNS[new_name]}
    for k, v in row.items():
        if k == "dolor_tibia_0_10":
            out["pain_0_10"] = v
            if v != "":
                out["pain_site"] = "shin"
            continue
        key = COLS.get(k, k)
        if key == "type" and new_name in TYPE_VALUES:
            v = TYPE_VALUES[new_name].get(v, v)
        elif key == "test":
            v = TEST_VALUES.get(v, v)
        elif key == "parameter":
            v = PARAM_VALUES.get(v, v)
        elif key == "source" and new_name == "measurements.csv" and v == "atleta":
            v = "athlete"
        elif key in VALUES:
            v = VALUES[key].get(v, v)
        if key in out:
            out[key] = v
        else:
            raise KeyError(f"{old_name}: no v2 column for {k!r}")
    return out


def migrate(src, dst):
    os.makedirs(dst, exist_ok=True)
    report = {}
    for old, new in FILES.items():
        p = os.path.join(src, old)
        rows = list(csv.DictReader(open(p, encoding="utf-8"))) if os.path.exists(p) else []
        with open(os.path.join(dst, new), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLUMNS[new], lineterminator="\n")
            w.writeheader()
            for r in rows:
                w.writerow(convert_row(old, new, r))
        report[new] = len(rows)
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    for name, n in migrate(sys.argv[1], sys.argv[2]).items():
        print(f"{name}: {n} row(s)")
