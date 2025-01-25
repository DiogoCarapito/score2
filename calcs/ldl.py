from pandas import isna, notna


def ldl_check_and_calc(
    colesterol_total,
    hdl,
    trigliceridos,
    data_colesterol_total,
    data_hdl,
    data_trigliceridos,
):
    ldl = None

    if isna(colesterol_total) or isna(hdl) or isna(trigliceridos):
        return None

    if trigliceridos >= 400:
        return None

    elif (
        data_colesterol_total == data_hdl
        and data_colesterol_total == data_trigliceridos
        and notna(data_colesterol_total)
    ):
        ldl = colesterol_total - hdl - trigliceridos / 5
        if ldl > 20:
            ldl = round(ldl, 0)
        else:
            return None
    else:
        return None

    return ldl
