# igonre W0621
# pylint: disable=W0621

import streamlit as st
import pandas as pd

# import numpy as np

from utils.utils import theme_toggle

theme_toggle()

from calcs.gfr_cki import gfr_cki
from calcs.ldl import ldl_check_and_calc

from calcs.score2_algorithm import (
    score2_algorithm,
    score_type_algorithm,
    score2_interpretation,
    score2_LDL_no_alvo,
    alvo_ldl,
)

from etl.etl import split_metadata_from_df, basic_mimuf_cleaning, process_metadata

# Set the page configuration
# st.set_page_config(
#     page_title="SCORE 2",  # Title of the app on the browser tab
#     page_icon="🧑‍⚕️",  # Icon of the app on the browser tab
#     layout="wide",  # Layout of the app
#     initial_sidebar_state="expanded"  # Initial state of the sidebar
# )


# not_uploaded = "🔴"
not_uploaded = "❓"
not_uplaod_messege = "Not Uploaded"
spining = "🔄"
spining_messege = "Processing"
uploaded = "✅"
uploaded_messege = None
problem = "❌"
problem_messege = "Problem"
warning = "	⚠️"
warning_messege = "Warning"


def update_status():
    for each in st.session_state["status_starting_info"]:
        if each["df"] is not None:
            each["status"] = not_uploaded
            each["message"] = not_uplaod_messege


def upload_status_script():
    for each in st.session_state["status_starting_info"]:
        if each["df"] is None:
            return "not all files uploaded"

    return "all files uploaded!"


def etl_transform(uoload_list):
    df = uoload_list[0]["df"]

    df = df[["Utente", "Nome", "Idade", "Data Nascimento", "Sexo", "Médico Familia"]]

    df["Idade_hoje"] = (
        pd.to_datetime("today").year - pd.to_datetime(df["Data Nascimento"]).dt.year
    )

    df_problemas = uoload_list[1]["df"]

    df_problemas = df_problemas.pivot_table(
        index="Utente",
        columns="ICPC",
        # values="Data",
        aggfunc="size",
        fill_value=0,
    ).reset_index()

    # create column for missing ICPCs

    icpcs = [
        "K74",  # Doença Cardíaca Isquémica sem Angina
        "K75",  # Enfarte Agudo do Miocárdio
        "K76",  # Doença Cardíaca Isquémica sem Angina
        # "K77",  # Insuficiência Cardíaca
        "K89",  # Isquémia Cerbral Transitória
        "K90",  # Acidente Vascular Cerebral
        "K91",  # Doença Vascular Cerebral
        "K92",  # Doença Vascular Periférica
        "T89",
        "T90",
        "P17",
    ]

    for icpc in icpcs:
        if icpc not in df_problemas.columns:
            df_problemas[icpc] = 0

    df = df.merge(df_problemas, on="Utente", how="left")

    # substitute o with Nan
    df.replace(0, None, inplace=True)

    # Colesterol Total

    df_colesterol_total = uoload_list[2]["df"]

    df_colesterol_total.rename(
        columns={
            "Data Último MCDT": "Data Último Colesterol Total",
            "Resultado Último MCDT": "Colesterol Total",
        },
        inplace=True,
    )

    df_colesterol_total["Colesterol Total"] = df_colesterol_total[
        "Colesterol Total"
    ].astype(float)

    df = df.merge(
        df_colesterol_total[
            ["Utente", "Data Último Colesterol Total", "Colesterol Total"]
        ],
        on="Utente",
        how="left",
    )

    # HDL

    df_HDL = uoload_list[3]["df"]

    df_HDL.rename(
        columns={
            "Data Último MCDT": "Data Último HDL",
            "Resultado Último MCDT": "HDL",
        },
        inplace=True,
    )

    df_HDL["HDL"] = df_HDL["HDL"].astype(float)

    df = df.merge(df_HDL[["Utente", "Data Último HDL", "HDL"]], on="Utente", how="left")

    ## Triglicéridos

    df_Triglicéridos = uoload_list[4]["df"]

    df_Triglicéridos.rename(
        columns={
            "Data Último MCDT": "Data Último Triglicéridos",
            "Resultado Último MCDT": "Triglicéridos",
        },
        inplace=True,
    )

    df_Triglicéridos["Triglicéridos"] = df_Triglicéridos["Triglicéridos"].astype(float)

    df = df.merge(
        df_Triglicéridos[["Utente", "Data Último Triglicéridos", "Triglicéridos"]],
        on="Utente",
        how="left",
    )

    ## LDL

    df_LDL = uoload_list[5]["df"]

    df_LDL.rename(
        columns={"Data Último MCDT": "Data Último LDL", "Resultado Último MCDT": "LDL"},
        inplace=True,
    )

    # if is str replace with None then convert to float
    df_LDL["LDL"] = df_LDL["LDL"].apply(lambda x: x if isinstance(x, float) else None)

    df = df.merge(df_LDL[["Utente", "Data Último LDL", "LDL"]], on="Utente", how="left")

    df_Creatinina = uoload_list[6]["df"]

    df_Creatinina.rename(
        columns={
            "Data Último MCDT": "Data Último Creatinina",
            "Resultado Último MCDT": "Creatinina",
        },
        inplace=True,
    )

    df_Creatinina["Creatinina"] = df_Creatinina["Creatinina"].astype(float)

    df = df.merge(
        df_Creatinina[["Utente", "Data Último Creatinina", "Creatinina"]],
        on="Utente",
        how="left",
    )

    df_Hemoglobina_A1c = uoload_list[7]["df"]

    df_Hemoglobina_A1c.rename(
        columns={
            "Data Último MCDT": "Data Último Hemoglobina A1c",
            "Resultado Último MCDT": "Hemoglobina A1c",
        },
        inplace=True,
    )

    df_Hemoglobina_A1c["Hemoglobina A1c"] = df_Hemoglobina_A1c[
        "Hemoglobina A1c"
    ].astype(float)

    df = df.merge(
        df_Hemoglobina_A1c[
            ["Utente", "Data Último Hemoglobina A1c", "Hemoglobina A1c"]
        ],
        on="Utente",
        how="left",
    )

    df_Albuminúria = uoload_list[8]["df"]

    df_Albuminúria.rename(
        columns={
            "Data Último MCDT": "Data Último Albuminúria",
            "Resultado Último MCDT": "Albuminuria",
        },
        inplace=True,
    )

    df_Albuminúria["Albuminuria"] = df_Albuminúria["Albuminuria"].apply(
        lambda x: x if isinstance(x, float) else None
    )

    # df_Albuminúria["Albuminuria"] = df_Albuminúria["Albuminuria"].astype(float)

    df = df.merge(
        df_Albuminúria[["Utente", "Data Último Albuminúria", "Albuminuria"]],
        on="Utente",
        how="left",
    )

    df_TAs = uoload_list[9]["df"]

    df_TAs.rename(
        columns={
            "Data Último Registo": "Data Último TAs",
            "Resultado Último Registo": "TAs",
        },
        inplace=True,
    )

    df_TAs["TAs"] = df_TAs["TAs"].astype(float)
    # df_TAs["TAs"] = df_TAs["TAs"].apply(lambda x: x if isinstance(x, float) else None)

    df = df.merge(df_TAs[["Utente", "Data Último TAs", "TAs"]], on="Utente", how="left")

    df_DM_desde = uoload_list[10]["df"]

    # st.write(df_DM_desde)

    df_DM_desde.rename(
        columns={
            "Data Último Registo": "Data Último DM desde",
            "Resultado Último Registo": "DM_desde",
        },
        inplace=True,
    )

    df_DM_desde["DM_desde"] = df_DM_desde["DM_desde"].astype(float)

    # df_DM_desde["Anos_diabetes"] =

    df = df.merge(
        df_DM_desde[["Utente", "Data Último DM desde", "DM_desde"]],
        on="Utente",
        how="left",
    )

    df["Idade_dm"] = df["Idade_hoje"] - (
        pd.to_datetime("today").year - df_DM_desde["DM_desde"]
    )

    # GFR

    df["GFR_CKI"] = df.apply(
        lambda x: gfr_cki(
            age=x["Idade_hoje"], creatinine=x["Creatinina"], sex=x["Sexo"]
        ),
        axis=1,
    )

    df["LDL_calculado"] = df.apply(
        lambda x: ldl_check_and_calc(
            colesterol_total=x["Colesterol Total"],
            hdl=x["HDL"],
            trigliceridos=x["Triglicéridos"],
            data_colesterol_total=x["Data Último Colesterol Total"],
            data_hdl=x["Data Último HDL"],
            data_trigliceridos=x["Data Último Triglicéridos"],
        ),
        axis=1,
    )

    df["LDL_calculado_data"] = df.apply(
        lambda x: x["Data Último Colesterol Total"] if x["LDL_calculado"] else None,
        axis=1,
    )

    df["Último LDL"] = df.apply(
        lambda x: x["LDL_calculado"]
        if x["LDL_calculado_data"] > x["Data Último LDL"]
        else x["LDL"],
        axis=1,
    )

    icpc_cadiovascular_disease = [
        "K74",  # Doença Cardíaca Isquémica sem Angina
        "K75",  # Enfarte Agudo do Miocárdio
        "K76",  # Doença Cardíaca Isquémica sem Angina
        # "K77",  # Insuficiência Cardíaca
        "K89",  # Isquémia Cerbral Transitória
        "K90",  # Acidente Vascular Cerebral
        "K91",  # Doença Vascular Cerebral
        "K92",  # Doença Vascular Periférica
    ]

    df["DCV establecida"] = df[icpc_cadiovascular_disease].apply(
        lambda row: "DCV" if any(row == 1.0) else None, axis=1
    )

    return df


def calculate_score2(df):
    df["SCORE2"] = df.apply(
        lambda x: score2_algorithm(
            sex=x["Sexo"],
            age=x["Idade_hoje"],
            has_diabetes=True if x["T90"] == 1 or x["T89"] == 1 else False,
            age_at_diagnosis=x["Idade_dm"],
            smoker=True if x["P17"] == 1 else False,
            systolic_blood_pressure=x["TAs"],  # mmHg
            total_cholesterol=x["Colesterol Total"],  # mmol/L
            hdl_cholesterol=x["HDL"],  # mmol/L
            hba1c=x["Hemoglobina A1c"],  # %
            gfr=x["GFR_CKI"],
            region_risk="Moderate",
            cvd=True if x["DCV establecida"] == "DCV" else False,
        ),
        axis=1,
    )

    df["SCORE2_tipo"] = df.apply(
        lambda x: score_type_algorithm(
            score=x["SCORE2"],
            age=x["Idade_hoje"],
            has_diabetes=True if x["T90"] == 1 or x["T89"] == 1 else False,
            cvd=True if x["DCV establecida"] == "DCV" else False,
        ),
        axis=1,
    )

    df["Risco_CV"] = df.apply(
        lambda x: score2_interpretation(
            cvd=x["DCV establecida"],
            score=x["SCORE2"],
            score_type=x["SCORE2_tipo"],
            age=x["Idade_hoje"],
        ),
        axis=1,
    )

    df["Alvo_LDL"] = df.apply(
        lambda x: alvo_ldl(
            risco_cv=x["Risco_CV"],
        ),
        axis=1,
    )

    df["LDL_no_alvo"] = df.apply(
        lambda x: score2_LDL_no_alvo(
            ldl=x["Último LDL"],
            cvd=x["DCV establecida"],
            risco_cv=x["Risco_CV"],
        ),
        axis=1,
    )

    return df


def extract_mcdt_biometria(metadata):
    mcdt_list = {
        "({Exame MCDT} = 650412:Colesterol da fração HDL, s)": "HDL",
        "({Exame MCDT} = 651029:Colesterol total, s/l)": "Colesterol total",
        "({Exame MCDT} = 650620:Triglicéridos, s/u/l)": "Triglicéridos",
        "({Exame MCDT} = 650542:Colesterol da fração LDL, s)": "LDL",
        "({Exame MCDT} = 650427:Creatinina, s/u)": "Creatinina",
        "({Exame MCDT} = 650531:Hemoglobina A1c (glicada))": "Hemoglobina A1c",
        "({Exame MCDT} = 651318:Albumina de baixa concentração, l/u/LCR)": "Albuminúria",
        "({Tipo Dado} = DM desde)": "DM desde",
        "({Tipo Dado} = TAs)": "TAs",
    }

    # if metadata["Query"][0] starts with "({Exame MCDT} = 650412:Colesterol da fração HDL, s) "

    for start, mcdt in mcdt_list.items():
        if metadata["Query"][0].startswith(start):
            return mcdt


if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

if "status_starting_info" not in st.session_state:
    st.session_state["status_starting_info"] = [
        {
            "report": "P01.01.L01",
            "file": "P01.01.L01 - Inscritos",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P04.01.L01",
            "file": "P04.01.L01 - Problemas",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - Colesterol total",
            "file": "P07.03.L01 - Colesterol total",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - HDL",
            "file": "P07.03.L01 - HDL",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - Triglicéridos",
            "file": "P07.03.L01 - Triglicéridos",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - LDL",
            "file": "P07.03.L01 - LDL",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - Creatinina",
            "file": "P07.03.L01 - Creatinina",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - Hemoglobina A1c",
            "file": "P07.03.L01 - Hemoglobina A1c",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P07.03.01.L01 - Albuminúria",
            "file": "P07.03.L01 - Albuminúria",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P10.01.L01 - TAs",
            "file": "P010.01.L01 - TAs",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
        {
            "report": "P10.01.L01 - DM desde",
            "file": "P010.01.L01 - DM desde",
            "status": not_uploaded,
            "message": not_uplaod_messege,
            "df": None,
        },
    ]


# def update_status(uploaded_files):
#     for each in st.session_state["status_starting_info"].iterrows():
#         print(each)
#         if each["df"]:
#             print("Uploaded")
#         #     each["status"] = uploaded
#         #     each["message"] = uploaded_messege
#         # else:
#         #     each["status"] = spining
#         #     each["message"] = spining_messege

# @st.dialog("Define data")
# def metadata_input():
#     st.write(df)


def etl_uploads():
    table_starting_keywords = {
        "P01.01.L01": "NOP",
        "P04.01.L01": "NOP",
        "P07.03.01.L01": "NOP",
        "P10.01.L01": "NOP",
    }

    for each in st.session_state["uploaded_files"]:
        df_xlsx = pd.read_excel(each)

        # get the reoprt name from the 1st columns text
        report_name = df_xlsx.columns[0].split(". ")[0]

        df, metadata = split_metadata_from_df(
            df=df_xlsx, df_start=table_starting_keywords[report_name]
        )

        metadata = process_metadata(metadata)

        # if metadata.empty:
        #     metadata_manual_input = metadata_input(df)

        if report_name == "P07.03.01.L01" or report_name == "P10.01.L01":
            mcdt = extract_mcdt_biometria(metadata)

            report_name = f"{report_name} - {mcdt}"

        # # update status based on identified report
        # if report_name in st.session_state["status_starting_info"]["report"]:
        #     st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "status"] = spining
        #     # st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "message"] = uploaded_messege
        #     # st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "df"] = df

        df = basic_mimuf_cleaning(df)

        df.rename(columns={"NaN1": "Nome"}, inplace=True)

        # # update status based on identified report
        # if report_name in st.session_state["status_starting_info"]["report"]:
        #     st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "status"] = uploaded
        #     # st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "message"] = uploaded_messege
        #     # st.session_state["status_starting_info"].loc[st.session_state["status_starting_info"]["report"] == report_name, "df"] = df

        # save df to respective report in st.session_state["uploaded_files"]

        for each in st.session_state["status_starting_info"]:
            if each["report"] == report_name:
                each["status"] = uploaded
                each["message"] = uploaded_messege
                each["df"] = df

    # update_status(st.session_state["uploaded_files"])


def main():
    st.title("SCORE 2")

    st.sidebar.divider()

    st.sidebar.header("Upload Files")
    st.session_state["uploaded_files"] = st.sidebar.file_uploader(
        "Upload multiple xlsx",
        type=["xlsx"],
        accept_multiple_files=True,
        on_change=update_status,
    )

    etl_uploads()

    upload_status = upload_status_script()

    if upload_status == "all files uploaded!":
        df = etl_transform(st.session_state["status_starting_info"])

        df = calculate_score2(df)

        st.write(df)

        st.download_button(
            label="Download em csv",
            data=df.to_csv(index=False),
            file_name="SCORE2.csv",
            mime="text/csv",
        )

        # st.download_button(
        #     label = "Download em Excel",
        #     data = df.to_excel("SCORE2.xlsx", index=False),
        #     file_name = "SCORE2.xlsx",
        #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )

    # for each in st.session_state["status_starting_info"]:
    #    st.write(each["df"])

    # st.write(st.session_state["uploaded_files"])

    st.sidebar.divider()
    st.sidebar.header("Status")
    for status_info in st.session_state["status_starting_info"]:
        st.sidebar.markdown(
            status_info["file"] + " " + status_info["status"],
            help=status_info["message"],
        )

    st.sidebar.divider()


if __name__ == "__main__":
    main()
