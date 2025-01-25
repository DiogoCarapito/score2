from pandas import isna


def gfr_cki(age=30, creatinine=0.9, sex="Mulher"):
    if isna(creatinine) or creatinine == 0:
        return None

    # 142 × (Scr/A)B × 0.9938age × (1.012 if Mulher)

    coeficients = {
        "Mulher": {
            "Scr ≤0.7": {"A": 0.7, "B": -0.241},
            "Scr >0.7": {"A": 0.7, "B": -1.2},
        },
        "Homem": {
            "Scr ≤0.9": {"A": 0.9, "B": -0.302},
            "Scr >0.9": {"A": 0.9, "B": -1.2},
        },
    }

    # Default assignment for src
    src = None

    if sex == "Mulher":
        if creatinine <= 0.7:
            src = "Scr ≤0.7"
        else:
            src = "Scr >0.7"
    elif sex == "Homem":
        if creatinine <= 0.9:
            src = "Scr ≤0.9"
        else:
            src = "Scr >0.9"
    else:
        raise ValueError("Invalid sex value. Must be 'Mulher' or 'Homem'.")

    gfr = (
        142
        * (creatinine / coeficients[sex][src]["A"]) ** coeficients[sex][src]["B"]
        * 0.9938**age
        * (1.012 if sex == "Mulher" else 1)
    )

    gfr = round(gfr, 1)

    return gfr


if __name__ == "__main__":
    gfr_cki()
