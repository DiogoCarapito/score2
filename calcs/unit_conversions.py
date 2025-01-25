def colesterol_mgdl_to_mmol(cholesterol):
    return round(cholesterol / 38.66976, 3)


def triglicerids_mgdl_to_mmol(triglicerids):
    return round(triglicerids / 88.57396, 3)


def hba1c_to_mmol_mol(hba1c):
    # The relationship between A1C and eAG is described by the formula 28.7 X A1C – 46.7 = eAG.
    # https://professional.diabetes.org/glucose_calc
    return round((10.93 * hba1c) - 23.5, 1)
