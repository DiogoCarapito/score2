import pandas as pd
import os
import unicodedata
import re

# # Setup logging
# import logging
# from logging_config import setup_logging

# setup_logging()


def one_item_list_input_management(file_names, process, metadata_columns):
    # processes a single file while the input is a list of files (to be univerisal compatible with the multiples files case)
    # this function is used when the input is expected to be a single file in a 1 element list

    # logging.info(f"one_item_list_input_management {file_names}")

    # check if only one file was passed
    if len(file_names) == 1:
        # process the file
        df, metadata, new_name = process(file_names[0], metadata_columns)

        return df, metadata, new_name

    if not file_names:  # if empty list
        raise ValueError("No file was passed to the function")

    else:  # if more than one file was passed
        # raise an error if more than one file was passed
        raise ValueError("Only one file should be passed to the function")


def concat_list_input_management(file_names, process, metadata_columns):
    # processes a list of files from an input of a list of files, but accepts only 1 file as input

    # logging.info("concat_list_input_management")

    # temporary use of metadata_columns
    # print("metadata_columns", metadata_columns)

    # check if only one file was passed
    if not file_names:  # if empty list
        raise ValueError("No file was passed to the function")

    elif len(file_names) == 1:
        # process the file
        df, metadata, new_name = process(file_names[0], metadata_columns)

        return df, metadata, new_name

    # check if more than one file was passe
    else:
        df_list = []
        metadata_df = pd.DataFrame()

        # create a loop to process each file individually and then concatenate the dataframes and metadata in the end
        for each in file_names:
            # process the file
            df, metadata, new_name = process(each, metadata_columns)

            # add a new column with the metadata that is different for each file (most of the times is date)
            # df["metadata"] = metadata

            # save the dataframe and metadata in a list
            df_list.append(df)
            metadata_df = pd.concat([metadata_df, metadata], ignore_index=True)

            # show if there are NA
            # print(df.isna().sum())

        # concatenate the dataframes
        final_df = pd.concat(df_list, ignore_index=True)

        # reset the index
        final_df.reset_index(drop=True, inplace=True)

        # remove duplicates
        final_df.drop_duplicates(inplace=True)

        return final_df, metadata_df, new_name


def normalize_file_name(file_name):
    return unicodedata.normalize("NFKD", file_name)


def multiple_source_pattern_management(file_folder, file_pattern, file_extension):
    # logging.info(f"multiple_source_pattern_management for {file_pattern}")

    try:
        # Get all files in the directory
        files = os.listdir(file_folder)

        # Normalize the file names in the directory
        normalized_files = [normalize_file_name(file) for file in files]

        # Normalize the file name pattern
        file_name_pattern = normalize_file_name(file_pattern)

        # Compile the regex pattern
        pattern = re.compile(f"{file_name_pattern}.*{re.escape(file_extension)}")

        # Filter files that match the regex pattern
        matching_files = [
            os.path.join(file_folder, original)
            for original, normalized in zip(files, normalized_files)
            if pattern.match(normalized)
        ]

        # logging.info(f"Matching files: {matching_files}")
        return matching_files

    except Exception as e:
        raise ValueError from e


def get_multiple_files_names(file_names):
    # Get the directory and base name of the first file
    # logging.info(f"get_multiple_files_names {file_names}")

    directory = os.path.dirname(file_names[0])
    base_name = os.path.basename(file_names[0])

    # Split the base name into the base name and extension
    file_name_pattern, file_extension = os.path.splitext(base_name)

    # Normalize the file name pattern
    file_name_pattern = normalize_file_name(file_name_pattern)

    # Escape special characters in the file name pattern for regex
    file_name_pattern = re.escape(file_name_pattern)

    # Get all files in the directory
    files = os.listdir(directory)

    # Normalize the file names in the directory
    normalized_files = [normalize_file_name(file) for file in files]

    # Compile the regex pattern
    pattern = re.compile(f"{file_name_pattern}.*{re.escape(file_extension)}")

    # Filter files that match the regex pattern
    matching_files = [
        os.path.join(directory, original)
        for original, normalized in zip(files, normalized_files)
        if pattern.match(normalized)
    ]

    return matching_files


def convert_file_name(file_path):
    # remove directories
    # remove spaces in csv file name to use as new name
    # logging.info("convert_file_name")

    file_name = (
        file_path.split("/")[-1]
        .replace("-", "_")
        .replace(" _", "_")
        .replace("_ ", "_")
        .replace(" ", "_")
    )

    # remove the extension
    file_name = file_name.split(".")[0]

    return file_name


def re_metadata(metadata, re_pattern):
    # Regex pattern to find the first occurrence of any number of characters after ":" and before ") E"
    # Search for the pattern in the text
    match = re.search(re_pattern, metadata)
    return match.group(1)


def process_metadata(metadata):  # , file_name):
    def get_index_of_element_after_paginas(lst, text):
        for index, element in enumerate(lst):
            if text in element:
                return index + 1
        return -1  # Return -1 if the text is not found

    new_metadata = {}

    # i want to check the first letter in the first metadata element to see if its a P or another letter
    # if metadata[0][0] == "P":  # MIMUF
    if metadata[0][0] == "F" or metadata[0][0] == "P":  # MIMUF
        # logging.debug("MIMUF")
        # process metada from the list that is created when the metadata is split from the dataframe into a dictionary, that later will be a line in a dataframe with the metadata from all processed files
        # new_metadata["Report"], new_metadata["Report name"] = metadata[0].split(". ")

        try:
            new_metadata["Query"] = metadata[1]
        except IndexError:
            new_metadata["Query"] = "Not found"

        # find the line that contains the "Páginas:" and get the index to know where to start extracting diferent structure metadata
        index = get_index_of_element_after_paginas(metadata, "Páginas:")

        if index == -1:
            pass
        else:
            # split the metadata in key value pairs
            for each in metadata[index:]:
                key, value = each.split(": ")
                new_metadata[key] = value

            if (
                "Médico de Registo" in new_metadata
                and new_metadata["Médico de Registo"] != "Total"
            ):
                # process the "Médico de Registo" and into correct render of name and "OM de Registo"
                (
                    new_metadata["Médico de Registo"],
                    new_metadata["OM de Registo"],
                ) = new_metadata["Médico de Registo"].split(":M ")
                new_metadata["Médico de Registo"] = capitalize_name(
                    new_metadata["Médico de Registo"]
                )
                new_metadata["OM de Registo"] = int(new_metadata["OM de Registo"])

        # # save as a txt file, each item the list in a new line
        # with open("data/metadata/"+file_name+"_metadata.txt", "w") as f:
        #     for item in metadata:
        #         f.write("%s\n" % item)

    else:
        df_metadata = None

    # else:  # assimng BI-CSP
    #     logging.debug("BICSP")

    #     metadata = metadata[0].split("\n")

    #     new_metadata["Report"] = "BI-CSP"
    #     new_metadata["Report name"] = "BI-CSP"
    #     new_metadata["Query"] = metadata[2]
    #     new_metadata["Ano-Mês"] = metadata[1].split(" is ")[1]

    # transform the dictionary into a dataframe
    df_metadata = pd.DataFrame(new_metadata, index=[0])

    return df_metadata


def xsls_initial_opening(xlsx_file):  # , df_start="NOP"):
    # # logging.info(f"xsls_initial_opening {file_name}")

    # new_name = convert_file_name(file_name)

    # read the xlsx file
    df = pd.read_excel(xlsx_file)

    # remove the column names
    # xlsx = remove_column_names(xlsx)

    # split the metadata from the dataframe
    # df, metadata = split_metadata_from_df(df=xlsx, df_start=df_start)

    # process metadata
    # metadata = process_metadata(metadata)

    # make sure if the last row is named " " it is renamed to "NaN0" to avoid problems with the column names
    # df.rename(columns={" ": "NaN0"}, inplace=True)

    # return df, metadata, new_name

    return df


def remove_column_names(df):
    # logging.info("remove_column_names")

    # copy the header info to the first row
    df.loc[-1] = df.columns
    df.index = df.index + 1
    df = df.sort_index()
    # remove the column names
    df.columns = range(df.shape[1])

    return df


# def split_metadata_from_df(df, df_start):

#     ## logging.info("split_metadata_from_df")

#     # look for the row that contains the string df_start. thats the column's header for the df. what's before is the metadata

#     i = None  # Initialize i

#     for idx, row in df.iterrows():
#         if idx == 20:
#             raise ValueError(
#                 f"'{df_start}' not found in DataFrame. Mayve the keyword is wrong?"
#             )
#         elif df_start in row.values:
#             i = idx
#             break

#     if i is not None:
#         metadata = df.iloc[:i, 0].dropna().tolist()
#         df = df.iloc[i:]
#     else:
#         raise ValueError(f"'{df_start}' not found in DataFrame")

#     # drop index
#     df = df.reset_index(drop=True)

#     # Check if there are NaN values in the first row
#     if df.iloc[0].isnull().values.any():
#         # Iterate over the columns of the first row
#         nan_counter = 1
#         for col in df.columns:
#             if pd.isnull(df.iloc[0][col]):
#                 df.iloc[0, col] = f"NaN{nan_counter}"
#                 nan_counter += 1

#     # print(df.iloc[0])

#     # make dataframe's first row the header
#     df = pd.DataFrame(df.values[1:], columns=df.iloc[0])

#     return df, metadata


def split_metadata_from_df(df, df_start):
    # # logging.info("split_metadata_from_df")

    # look for the row that contains the string df_start. thats the column's header for the df. what's before is the metadata

    i = None  # Initialize i

    for idx, row in df.iterrows():
        if idx == 20:
            raise ValueError(
                f"'{df_start}' not found in DataFrame. Maybe the keyword is wrong?"
            )
        elif df_start in row.values:
            i = idx
            break

    if i is not None:
        metadata = df.iloc[:i, 0].dropna().tolist()
        df = df.iloc[i:]
    else:
        raise ValueError(f"'{df_start}' not found in DataFrame")

    # drop index
    df = df.reset_index(drop=True)

    # Check if there are NaN values in the first row
    if df.iloc[0].isnull().values.any():
        # Iterate over the columns of the first row
        nan_counter = 1
        for col in range(len(df.columns)):
            if pd.isnull(df.iloc[0, col]):
                df.iloc[0, col] = f"NaN{nan_counter}"
                nan_counter += 1

    # print(df.iloc[0])

    # make dataframe's first row the header
    df = pd.DataFrame(df.values[1:], columns=df.iloc[0])

    return df, metadata


# def remove_anos_idade(df, column_idade):

#     # logging.info("remove_anos_idade")

#     # remove 'anos' and 'idade' from the column
#     df.loc[:, column_idade] = (
#         df.loc[:, column_idade]
#         .str.replace(" Anos", "")
#         .str.replace(" Ano", "")
#         .str.strip()
#     )

#     # transform column to int
#     df.loc[:, column_idade] = pd.to_numeric(df.loc[:, column_idade], errors="coerce")

#     return df


def remove_anos_idade(df, column_idade):
    # logging.info("remove_anos_idade")

    # Ensure the column is of type string
    df.loc[:, column_idade] = df.loc[:, column_idade].astype(str)

    # Remove 'anos' and 'idade' from the column
    df.loc[:, column_idade] = (
        df.loc[:, column_idade]
        .str.replace(" Anos", "")
        .str.replace(" Ano", "")
        .str.strip()
    )

    # Transform column to int
    df.loc[:, column_idade] = pd.to_numeric(df.loc[:, column_idade], errors="coerce")

    return df


def capitalize_name(name):
    if ":" in name:
        name = name.split(":")[0]

    # Define a custom function to capitalize names based on length
    name = name.strip()
    words = name.split()
    capitalized_words = [
        word.capitalize() if len(word) > 2 else word.lower() for word in words
    ]
    return " ".join(capitalized_words)


def medico_familia_clean(df, column_mf):
    # logging.info("medico_familia_clean")

    # Apply the custom function to the specified column using .loc
    df.loc[:, column_mf] = df.loc[:, column_mf].apply(capitalize_name)

    return df


def basic_mimuf_cleaning(df):
    # logging.info("basic_mimuf_cleaning")

    # basic cleaning for mimuf files
    # checks if a certain column exists and processit acordingly for systematic known issues in mimuf files

    # check if the there is a row with "Total" in the first column's values and remove it
    if "Total" in df.iloc[:, 0].values:
        df = df[df.iloc[:, 0] != "Total"]

    if "Médico Familia" in df.columns:
        df = medico_familia_clean(df=df, column_mf="Médico Familia")

    if "Médico" in df.columns:
        df = medico_familia_clean(df=df, column_mf="Médico")

    if "Idade" in df.columns:
        df = remove_anos_idade(df=df, column_idade="Idade")

    if "Freguesia Habitação" in df.columns:
        df = df.drop(columns="Freguesia Habitação")

    # loop to remove columns that are not useful after checking if they exist
    columns_to_remove = ["NaN0", "Morada", "Código Postal", "Telefone"]

    for column in columns_to_remove:
        if column in df.columns:
            df.drop(columns=column, inplace=True)

    return df


def read_csv_to_dict(file_path):
    df = pd.read_csv(file_path)
    return dict(zip(df["antigo"], df["novo"]))


############################################


# def convert_mimuf_csv(file_path):
#     # logging.info("Processing")  # , new_name)

#     # open the file and read the lines using UTF-16 encoding
#     with open(file_path, "r", encoding="UTF-16") as f:
#         temp_file = f.readlines()

#         # find the line number where the table starts (the table starts after 2 consecutive \n characters)
#         start_line = 0
#         for i, line in enumerate(temp_file):

#             # if line ends with 'E ({Tipo Risco} (ID) = -24)\n', break to adress the probelm of havinf files that only as 1 \n, like 'P05_01_L02_ Risco de Diabetes _ Nível de Risco por Utente.csv'
#             if "E ({Tipo Risco} (ID) = -24)\n" in line:
#                 start_line = i + 2
#                 break
#             elif line == "\n" and temp_file[i + 1] == "\n":
#                 start_line = i + 2
#                 break

#         # get the text before the table (metadata) and the table itself
#         metadata = temp_file[: start_line - 2]

#         df = temp_file[start_line:]

#         # remove all " from the text
#         # df = [x.replace('"', "") for x in df]

#         # create a pandas dataframe from the table that has "" in each cell and is separated by ",". the first row is the header
#         df = pd.DataFrame(
#             [
#                 x.strip().split('","') for x in df[0:]
#             ]  # , columns=df[0].replace('"', "").split(",")
#         )

#         # if a column has only None values, remove it
#         # df = df.dropna(axis=1, how="all")

#         # print(df[10].drop_duplicates())

#         # print(df)

#         return {"metadata": metadata, "df": df}


def faixa_etaria_5(df):
    df["Faixa_etária_5"] = pd.cut(
        df["Idade"],
        bins=[
            0,
            1,
            4,
            9,
            14,
            19,
            24,
            29,
            34,
            39,
            44,
            49,
            54,
            59,
            64,
            69,
            74,
            79,
            84,
            89,
            94,
            99,
            200,
        ],
        labels=[
            "<1",
            "1-4",
            "5-9",
            "10-14",
            "15-19",
            "20-24",
            "25-29",
            "30-34",
            "35-39",
            "40-44",
            "45-49",
            "50-54",
            "55-59",
            "60-64",
            "65-69",
            "70-74",
            "75-79",
            "80-84",
            "85-89",
            "90-94",
            "95-99",
            ">100",
        ],
    )

    print(df["Faixa_etária_5"].value_counts())
    return df


def faixa_etaria_10(df):
    df["Faixa_etária_10"] = pd.cut(
        df["Idade"],
        bins=[0, 1, 9, 19, 29, 39, 49, 59, 69, 79, 89, 99, 200],
        labels=[
            "<1",
            "1-9",
            "10-19",
            "20-29",
            "30-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80-89",
            "90-99",
            ">100",
        ],
    )
    return df


def faixa_etaria_si(df):
    df["Faixa_etária_si"] = pd.cut(
        df["Idade"],
        bins=[0, 1, 2, 4, 9, 14, 18, 200],
        labels=["<1", "1-2", "3-4", "5-9", "10-14", "15-18", ">18"],
    )
    return df
