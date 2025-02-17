import math

# import numpy as np
from pandas import isna


from calcs.unit_conversions import colesterol_mgdl_to_mmol, hba1c_to_mmol_mol


def score_type_algorithm(score, age, has_diabetes, cvd):
    if isna(score):
        return None
    if cvd:
        return "CVD establecida"
    elif age >= 70:
        return "SCORE2_OP"
    elif has_diabetes:
        return "SCORE2_DM"
    elif age >= 40 and age < 70:  # and isna(has_diabetes):
        return "SCORE2"
    else:
        return None


def score2_LDL_no_alvo(ldl, cvd, risco_cv):
    # 55, 70, 100, 116

    ldl_no_alvo = None

    if isna(ldl) or isna(risco_cv):
        return None

    if cvd or risco_cv == "Muito alto":
        if ldl > 55:
            ldl_no_alvo = "Acima do alvo"
        elif ldl <= 55:
            ldl_no_alvo = "Dentro do alvo"
        else:
            ldl_no_alvo = None

    elif risco_cv == "Alto":
        if ldl > 70:
            ldl_no_alvo = "Acima do alvo"
        elif ldl <= 70:
            ldl_no_alvo = "Dentro do alvo"
        else:
            ldl_no_alvo = None

    elif risco_cv == "Baixo a Moderado" or risco_cv == "Moderado":
        if ldl > 100:
            ldl_no_alvo = "Acima do alvo"
        elif ldl <= 100:
            ldl_no_alvo = "Dentro do alvo"
        else:
            ldl_no_alvo = None

    elif risco_cv == "Baixo":
        if ldl > 116:
            ldl_no_alvo = "Acima do alvo"
        elif ldl <= 116:
            ldl_no_alvo = "Dentro do alvo"
        else:
            ldl_no_alvo = None

    # print("LDL:", ldl, "CVD:", cvd, "Risco CV:", risco_cv, "LDL no alvo:", ldl_no_alvo)

    return ldl_no_alvo


def alvo_ldl(risco_cv):
    if risco_cv == "Baixo":
        return 116
    if risco_cv == "Baixo a Moderado":
        return 100
    if risco_cv == "Alto":
        return 70
    if risco_cv == "Muito alto":
        return 55


def score2_interpretation(cvd, score, score_type, age):
    if cvd:
        return "Muito alto"
    if isna(score):
        return None

    # score_type = score_type_algorithm(age, has_diabetes)

    if score_type == "SCORE2":
        if age < 50:
            # Score < 2,5%: grau BAIXO A MODERADO
            # Score 2,5 - 7,4%: grau ALTO
            # Score ≥ 7,5%: grau MUITO ALTO
            if score < 2.5:
                return "Baixo a Moderado"
            elif score >= 2.5 and score < 7.5:
                return "Alto"
            elif score >= 7.5:
                return "Muito alto"
            else:
                return None
        else:
            # Score < 5%: grau BAIXO A MODERADO
            # Score 5 - 10%: grau ALTO
            # Score ≥ 7,5%: grau MUITO ALTO
            if score < 5:
                return "Baixo a Moderado"
            elif score >= 5 and score < 10:
                return "Alto"
            elif score >= 10:
                return "Muito alto"
            else:
                return None

    elif score_type == "SCORE2_OP":
        # Score 7,5%: grau BAIXO A MODERADO
        # Score 7,5 - 14,9%: grau ALTO
        # Score ≥ 15%: grau MUITO ALTO
        if score < 7.5:
            return "Baixo a Moderado"
        elif score >= 7.5 and score < 15:
            return "Alto"
        elif score >= 15:
            return "Muito alto"
        else:
            return None

    elif score_type == "SCORE2_DM":
        # <5%: Risco baixo
        # 5 a <10%: Risco moderado
        # 10 < 20%: Risco alto
        # >= 20%: Risco muito alto
        if score < 5:
            return "Baixo"
        elif score >= 5 and score < 10:
            return "Moderado"
        elif score >= 10 and score < 20:
            return "Alto"
        elif score >= 20:
            return "Muito alto"
        else:
            return None
    else:
        return None


def score2_algorithm(
    sex,
    age,
    has_diabetes,
    age_at_diagnosis,
    smoker,
    systolic_blood_pressure,
    total_cholesterol,
    hdl_cholesterol,
    hba1c,
    gfr,
    region_risk,
    cvd,
):
    if cvd:
        return None

    if age < 40 or total_cholesterol < 50:
        return None

    if (
        isna(sex)
        or isna(age)
        or isna(systolic_blood_pressure)
        or isna(total_cholesterol)
        or isna(hdl_cholesterol)
    ):
        return None

    if has_diabetes and (
        isna(age_at_diagnosis) or isna(hba1c) or isna(gfr) or hba1c > 20 or gfr < 10
    ):
        return None

    # validate data

    if total_cholesterol < 50 or total_cholesterol > 400:
        return None
    if hdl_cholesterol < 10 or hdl_cholesterol > 150:
        return None
    if hba1c < 3 or hba1c > 20:
        return None
    if gfr < 0 or gfr > 200:
        return None
    if systolic_blood_pressure < 50 or systolic_blood_pressure > 300:
        return None

    # print("###")
    # print("Sex:", sex)
    # print("Age:", age)
    # print("Diabetes:", has_diabetes)
    # print("Age at diagnosis:", age_at_diagnosis)
    # print("Smoker:", smoker)
    # print("Systolic blood pressure:", systolic_blood_pressure, "mmHg")
    # print("Total cholesterol:", total_cholesterol, "mg/dL")
    # print("HDL cholesterol:", hdl_cholesterol, "mg/dL")
    # print("HbA1c:", hba1c)
    # print("GFR:", gfr)
    # print("Region risk:", region_risk)

    score_type = score_type_algorithm("1", age, has_diabetes, cvd)

    if isna(score_type):
        return None

    # Convert cholesterol from mg/dL to mmol/L
    total_cholesterol = colesterol_mgdl_to_mmol(total_cholesterol)
    hdl_cholesterol = colesterol_mgdl_to_mmol(hdl_cholesterol)
    hba1c = hba1c_to_mmol_mol(hba1c)

    # print("HbA1c in mmol/mol:", hba1c)

    # Example coefficients (replace with actual values from SCORE2 paper)
    coefficients = {
        "SCORE2": {
            "Homem": {
                "Age": 0.3742,
                "Smoking": 0.6012,
                "SBP": 0.2777,
                "Total cholesterol": 0.1458,
                "HDL": -0.2698,
                "Smoking_Age": -0.0755,
                "SBP_age": -0.0255,
                "Total cholesterol_age": -0.0281,
                "HDL_age": 0.0426,
                "Baseline_survival": 0.9605,
            },
            "Mulher": {
                "Age": 0.4648,
                "Smoking": 0.7744,
                "SBP": 0.3131,
                "Total cholesterol": 0.1002,
                "HDL": -0.2606,
                "Smoking_Age": -0.1088,
                "SBP_age": -0.0277,
                "Total cholesterol_age": -0.0226,
                "HDL_age": 0.0613,
                "Baseline_survival": 0.9776,
            },
        },
        "SCORE2_OP": {
            "Homem": {
                "Age": 0.0634,
                "Diabetes": 0.4245,
                "Smoking": 0.3524,
                "SBP": 0.0094,
                "Total cholesterol": 0.0850,
                "HDL": -0.3564,
                "Diabetes_Age": -0.0174,
                "Smoking_Age": -0.0247,
                "SBP_age": -0.0005,
                "Total cholesterol_age": 0.0073,
                "HDL_age": 0.0091,
                "Baseline_survival": 0.7576,
                "Mean linear predictor": 0.0929,
            },
            "Mulher": {
                "Age": 0.0789,
                "Diabetes": 0.6010,
                "Smoking": 0.4921,
                "SBP": 0.0102,
                "Total cholesterol": 0.0605,
                "HDL": -0.3040,
                "Diabetes_Age": -0.0107,
                "Smoking_Age": -0.0255,
                "SBP_age": -0.0004,
                "Total cholesterol_age": -0.0009,
                "HDL_age": 0.0154,
                "Baseline_survival": 0.8082,
                "Mean linear predictor": 0.2290,
            },
        },
        "SCORE2_DM": {
            "Homem": {
                "Age": 0.5368,
                "Smoking": 0.4774,
                "SBP": 0.1322,
                "Diabetes": 0.6457,
                "Total cholesterol": 0.1102,
                "HDL": -0.1087,
                "Smoking_Age": -0.0672,
                "SBP_age": -0.0268,
                "Diabetes_Age": -0.0983,
                "Total cholesterol_age": -0.0181,
                "HDL_age": 0.0095,
                "Age_at_diagnosis": -0.0998,
                "HbA1c": 0.0955,
                "GFR": -0.0591,
                "GFR2": 0.0058,
                "Hba1c_age": -0.0134,
                "gfr_age": 0.0115,
                "Baseline_survival": 0.9605,
            },
            "Mulher": {
                "Age": 0.6624,
                "Smoking": 0.6139,
                "SBP": 0.1421,
                "Diabetes": 0.8096,
                "Total cholesterol": 0.1127,
                "HDL": -0.1568,
                "Smoking_Age": -0.1122,
                "SBP_age": -0.0167,
                "Diabetes_Age": -0.1272,
                "Total cholesterol_age": -0.0200,
                "HDL_age": 0.0186,
                "Age_at_diagnosis": -0.1180,
                "HbA1c": 0.1173,
                "GFR": -0.0640,
                "GFR2": 0.0062,
                "Hba1c_age": -0.0196,
                "gfr_age": 0.0169,
                "Baseline_survival": 0.9776,
            },
        },
    }

    region_risk_coeficients = {
        "SCORE2": {
            "Homem": {
                "Low": {
                    "Scale1": -0.5699,
                    "Scale2": 0.7476,
                },
                "Moderate": {
                    "Scale1": -0.1565,
                    "Scale2": 0.8009,
                },
                "High": {
                    "Scale1": 0.3207,
                    "Scale2": 0.9360,
                },
                "Very high": {
                    "Scale1": 0.5836,
                    "Scale2": 0.8294,
                },
            },
            "Mulher": {
                "Low": {
                    "Scale1": -0.7380,
                    "Scale2": 0.7019,
                },
                "Moderate": {
                    "Scale1": -0.3143,
                    "Scale2": 0.7701,
                },
                "High": {
                    "Scale1": 0.5710,
                    "Scale2": 0.9369,
                },
                "Very high": {
                    "Scale1": 0.9369,
                    "Scale2": 0.8329,
                },
            },
        },
        "SCORE2_OP": {
            "Homem": {
                "Low": {
                    "Scale1": -0.34,
                    "Scale2": 1.19,
                },
                "Moderate": {
                    "Scale1": 0.01,
                    "Scale2": 1.25,
                },
                "High": {
                    "Scale1": 0.08,
                    "Scale2": 1.15,
                },
                "Very high": {
                    "Scale1": 0.05,
                    "Scale2": 0.70,
                },
            },
            "Mulher": {
                "Low": {
                    "Scale1": -0.52,
                    "Scale2": 1.01,
                },
                "Moderate": {
                    "Scale1": -0.10,
                    "Scale2": 1.10,
                },
                "High": {
                    "Scale1": 0.38,
                    "Scale2": 1.09,
                },
                "Very high": {
                    "Scale1": 0.38,
                    "Scale2": 0.69,
                },
            },
        },
        "SCORE2_DM": {
            "Homem": {
                "Low": {
                    "Scale1": -0.5699,
                    "Scale2": 0.7476,
                },
                "Moderate": {
                    "Scale1": -0.1565,
                    "Scale2": 0.8009,
                },
                "High": {
                    "Scale1": 0.3207,
                    "Scale2": 0.9360,
                },
                "Very high": {
                    "Scale1": 0.5836,
                    "Scale2": 0.8294,
                },
            },
            "Mulher": {
                "Low": {
                    "Scale1": -0.7380,
                    "Scale2": 0.7019,
                },
                "Moderate": {
                    "Scale1": -0.3143,
                    "Scale2": 0.7701,
                },
                "High": {
                    "Scale1": 0.5710,
                    "Scale2": 0.9369,
                },
                "Very high": {
                    "Scale1": 0.9412,
                    "Scale2": 0.8329,
                },
            },
        },
    }

    ten_year_risk = None

    if score_type == "SCORE2":
        cage = (age - 60) / 5
        smoking = 1 if smoker else 0
        csbp = (systolic_blood_pressure - 120) / 20
        ctchol = total_cholesterol - 6
        chdl = (hdl_cholesterol - 1.3) / 0.5
        somking_age = smoking * cage
        sbp_age = csbp * cage
        tchol_age = ctchol * cage
        chdl_age = chdl * cage

        # Calculate x (Σ[β * transformed variables])
        x = (
            coefficients[score_type][sex]["Age"] * cage
            + coefficients[score_type][sex]["Smoking"] * smoking
            + coefficients[score_type][sex]["SBP"] * csbp
            + coefficients[score_type][sex]["Total cholesterol"] * ctchol
            + coefficients[score_type][sex]["HDL"] * chdl
            + coefficients[score_type][sex]["Smoking_Age"] * somking_age
            + coefficients[score_type][sex]["SBP_age"] * sbp_age
            + coefficients[score_type][sex]["Total cholesterol_age"] * tchol_age
            + coefficients[score_type][sex]["HDL_age"] * chdl_age
        )

        ten_year_risk = 1 - (
            coefficients[score_type][sex]["Baseline_survival"]
        ) ** math.exp(x)

    elif score_type == "SCORE2_OP":
        cage = age - 73
        diabetes = 1 if has_diabetes else 0
        smoking = 1 if smoker else 0
        csbp = systolic_blood_pressure - 150
        ctchol = total_cholesterol - 6
        chdl = hdl_cholesterol - 1.4
        diabetes_age = diabetes * cage
        smoking_age = smoking * cage
        sbp_age = csbp * cage
        tchol_age = ctchol * cage
        chdl_age = chdl * cage

        # Calculate x (Σ[β * transformed variables])
        x = (
            coefficients[score_type][sex]["Age"] * cage
            + coefficients[score_type][sex]["Diabetes"] * diabetes
            + coefficients[score_type][sex]["Smoking"] * smoking
            + coefficients[score_type][sex]["SBP"] * csbp
            + coefficients[score_type][sex]["Total cholesterol"] * ctchol
            + coefficients[score_type][sex]["HDL"] * chdl
            + coefficients[score_type][sex]["Diabetes_Age"] * diabetes_age
            + coefficients[score_type][sex]["Smoking_Age"] * smoking_age
            + coefficients[score_type][sex]["SBP_age"] * sbp_age
            + coefficients[score_type][sex]["Total cholesterol_age"] * tchol_age
            + coefficients[score_type][sex]["HDL_age"] * chdl_age
        )

        ten_year_risk = 1 - (
            coefficients[score_type][sex]["Baseline_survival"]
        ) ** math.exp(x - coefficients[score_type][sex]["Mean linear predictor"])

    elif score_type == "SCORE2_DM":
        ### This formula is not correct, it is just an aproximation due to faulty references
        cage_dm = (age - 60) / 5
        smoking_dm = 1 if smoker else 0
        csbp_dm = (systolic_blood_pressure - 120) / 20
        diabetes_dm = 1 if has_diabetes else 0
        ctchol_dm = total_cholesterol - 6
        chdl_dm = (hdl_cholesterol - 1.3) / 0.5

        somking_age_dm = smoking_dm * cage_dm
        sbp_age_dm = csbp_dm * cage_dm
        diabetes_age_dm = diabetes_dm * cage_dm
        ctchol_age_dm = ctchol_dm * cage_dm
        chdl_age_dm = chdl_dm * cage_dm

        cagediab_dm = diabetes_dm * (age_at_diagnosis - 50) / 5

        ca1c_dm = (hba1c - 31) / 9.34
        cegfr_dm = (math.log(gfr) - 4.5) / 0.15
        cegfr2_dm = cegfr_dm**2

        ca1c_age_dm = ca1c_dm * cage_dm
        cegfr_age_dm = cegfr_dm * cage_dm

        # Calculate x (Σ[β * transformed variables])
        x = (
            coefficients[score_type][sex]["Age"] * cage_dm
            + coefficients[score_type][sex]["Smoking"] * smoking_dm
            + coefficients[score_type][sex]["SBP"] * csbp_dm
            + coefficients[score_type][sex]["Diabetes"] * diabetes_dm
            + coefficients[score_type][sex]["Total cholesterol"] * ctchol_dm
            + coefficients[score_type][sex]["HDL"] * chdl_dm
            + coefficients[score_type][sex]["Smoking_Age"] * somking_age_dm
            + coefficients[score_type][sex]["SBP_age"] * sbp_age_dm
            + coefficients[score_type][sex]["Diabetes_Age"] * diabetes_age_dm
            + coefficients[score_type][sex]["Total cholesterol_age"] * ctchol_age_dm
            + coefficients[score_type][sex]["HDL_age"] * chdl_age_dm
            + coefficients[score_type][sex]["Age_at_diagnosis"] * cagediab_dm
            + coefficients[score_type][sex]["HbA1c"] * ca1c_dm
            + coefficients[score_type][sex]["GFR"] * cegfr_dm
            + coefficients[score_type][sex]["GFR2"] * cegfr2_dm
            + coefficients[score_type][sex]["Hba1c_age"] * ca1c_age_dm
            + coefficients[score_type][sex]["gfr_age"] * cegfr_age_dm
        )

        ten_year_risk = 1 - (
            coefficients[score_type][sex]["Baseline_survival"]
        ) ** math.exp(x)

    if isna(ten_year_risk):
        return None

    # [1 – exp(-exp(scale1 + scale2*ln(-ln(1 – 10-year risk))))]*100
    calibrated_ten_year_risk = (
        1
        - math.exp(
            -math.exp(
                region_risk_coeficients[score_type][sex][region_risk]["Scale1"]
                + region_risk_coeficients[score_type][sex][region_risk]["Scale2"]
                * math.log(-math.log(1 - ten_year_risk))
            )
        )
    ) * 100

    calibrated_ten_year_risk = round(calibrated_ten_year_risk, 2)

    return calibrated_ten_year_risk


# if __name__ == "__main__":
#     sexo = "Homem"
#     idade = 69
#     tem_diabetes = True
#     idade_diagnostico = 60
#     fumador = True
#     pressao_arterial_sistolica = 150
#     colesterol_total = 300
#     colesterol_hdl = 40
#     hba1c = 12
#     gfr = 30
#     risco_regiao = "Moderate"
#     cvd = False

#     # sexo = "Mulher"
#     # idade = 40
#     # tem_diabetes = True
#     # idade_diagnostico = 2023
#     # fumador = False
#     # pressao_arterial_sistolica = 120
#     # colesterol_total = 150
#     # colesterol_hdl = 70
#     # hba1c = 6.5
#     # gfr = 90
#     # risco_regiao = "Moderado"
#     # cvd = False

#     score = score2_algorithm(
#         sex=sexo,
#         age=idade,
#         has_diabetes=tem_diabetes,
#         age_at_diagnosis=idade_diagnostico,
#         smoker=fumador,
#         systolic_blood_pressure=pressao_arterial_sistolica,
#         total_cholesterol=colesterol_total,
#         hdl_cholesterol=colesterol_hdl,
#         hba1c=hba1c,
#         gfr=gfr,
#         region_risk=risco_regiao,
#         cvd=cvd,
#     )

#     risco_cv = score2_interpretation(cvd, score, "SCORE2", idade)

#     score_aplicado = score_type_algorithm(score, idade, tem_diabetes, cvd)

#     print("Idade:", idade)
#     print("Sexo:", sexo)
#     print("Diabetes:", tem_diabetes)
#     print("Idade diagnóstico:", idade_diagnostico)
#     print("Fumador:", fumador)
#     print("Pressão arterial sistólica:", pressao_arterial_sistolica)
#     print("Colesterol total:", colesterol_total)
#     print("Colesterol HDL:", colesterol_hdl)
#     print("HbA1c:", hba1c)
#     print("GFR:", gfr)
#     print("Risco região:", risco_regiao)
#     print("CVD:", cvd)

#     print("###")
#     print("Score", score)
#     print("Score aplicado:", score_aplicado)
#     print("Risco CV", risco_cv)
