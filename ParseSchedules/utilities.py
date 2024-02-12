import re
from pandas import DataFrame, Series
from fuzzywuzzy import process

from ParseSchedules.models import DaySchedule


qualifications = [
    r"доц\.",
    r"ст\.викл\.",
    r"проф\.",
    r"ст\. в\.",
    r"викл\.",
    r"ст\.пр\.",
    r"пр\.",
    r"ст\. ас\.",
    r"ас\.",
]

days_ukr = ["Понеділок", "Вівторок", "Середа", "Четвер", "П’ятниця"]
days_eng_lower = ["monday", "tuesday", "wednesday", "thursday", "friday"]


def remove_duplicates(df: DataFrame):
    """
    Removes duplicate rows from a DataFrame based on a combination of columns (row signature).

    Args:
        df (DataFrame): The DataFrame to remove duplicates from.

    Returns:
        DataFrame: The DataFrame with duplicate rows removed.
    """
    duplicate_signature = df["index"].astype(str) + df["name"] + df["room"]
    df.loc[:, "duplicate_signature"] = duplicate_signature

    duplicates = df.duplicated(subset="duplicate_signature", keep="first")

    # remove biweekly label from kept instance of duplicate
    df.loc[duplicates, "label"] = None

    # drop duplicates but keep first instance of each duplicate
    df = df.drop_duplicates(subset=["duplicate_signature"], keep="last")
    # drop duplicate_signature column
    df = df.drop(["duplicate_signature"], axis=1)

    return df


def strip_each_text_cell(df: DataFrame):
    """
    Removes whitespaces, trailing commas, underscores, and collapses double whitespaces in each text cell of a DataFrame.

    Parameters:
    df (DataFrame): The DataFrame containing text cells to be processed.

    Returns:
    DataFrame: The DataFrame with processed text cells.
    """
    # remove whitespaces and trailing commas in each text cell
    # select all string columns and apply the strip() function thrice to remove whitespaces and trailing commas and underscores, and whitespaces again ,
    string_cols_df = df.select_dtypes(include=["object"])
    string_cols = string_cols_df.columns
    df[string_cols] = string_cols_df.apply(
        lambda x: x.str.strip().str.strip("_,").str.strip()
    )

    # collapse all double whitespaces into single whitespaces
    df[string_cols] = df[string_cols].apply(lambda x: x.str.replace(r"\s+", " "))

    # remove spaces before commas and dots
    df[string_cols] = df[string_cols].apply(
        lambda x: x.str.replace(r"\s+([,.])", r"\1")
    )

    return df


def label_upper_and_lower_duplicates(df: DataFrame):
    """
    Labels the first set of duplicate rows with 'first' and the second set with 'second' based on the 'index' column.

    Args:
        df (DataFrame): The input DataFrame.

    Returns:
        DataFrame: The DataFrame with the 'label' column added.
    """
    # Identify rows with duplicate values in the 'index' column. keep = false for all duplicates
    duplicates = df.duplicated(subset=["index"], keep=False)

    # Label the first set of duplicate rows with 'first' and the second set with 'second'
    num_duplicates = sum(duplicates)
    if num_duplicates % 2 == 0:
        labels = [1, 2] * (num_duplicates // 2)
    else:
        labels = [1, 2] * (num_duplicates // 2) + [1]
    df.loc[duplicates, "label"] = labels

    return df


def extract_group_names(df: DataFrame):
    """
    Extracts group names from the DataFrame columns.

    Args:
        df (DataFrame): The input DataFrame.

    Returns:
        list[str]: A list of column names that match the group name pattern.
    """

    # it's a group if it follows this pattern: 1-2 letters, then dash, then 1-2 numbers
    pattern = r"(\w{1,2}-\d{1,2})"

    cols: list[str] = df.columns

    filtered_cols = [col for col in cols if re.search(pattern, col)]

    return filtered_cols


def is_group_name(name: str):
    # it's a group if it follows this pattern: 1-2 letters, then dash, then 1-2 numbers
    pattern = r"(\w{1,2}-\d{1,2})"

    is_match = re.search(pattern, name) is not None

    return is_match


def correct_group_name(name: str):
    # example of a name that has to be corrected: ТП-5м.1
    # it should be corrected to ТП-5м_2

    # we have to search for dot, followed by digit
    # and we gotta replace it with dash, followed by the same digits, but incremented by one

    # pattern to search for
    pattern = r"\.(\d)"

    # function to increment the digit found in the pattern
    def increment_digit(match):
        return "_" + str(int(match.group(1)) + 1)

    # use re.sub to replace the pattern with the incremented digit
    output_str = re.sub(pattern, increment_digit, name)

    return output_str


def correct_group_names(df: DataFrame):
    cols = df.columns

    corrected_col_names = map(
        lambda c: correct_group_name(c) if is_group_name(c) else c, list(cols)
    )
    corrected_col_names = list(corrected_col_names)

    df.columns = corrected_col_names

    return df


def construct_empty_schedule() -> DaySchedule:
    json_ = {}
    for day in days_eng_lower:
        json_[day] = {"classes": []}
    return json_

def correct_spelling(word, correct_words):
    
    is_misspelled = word not in correct_words
    
    if not is_misspelled:
        return word
    
    # Find the closest match to word in correct_words
    closest_match = process.extractOne(word, correct_words)
    
    # If the match is close enough, return it. Otherwise, return the original word.
    if closest_match[1] > 80:  # You can adjust this threshold as needed
        return closest_match[0]
    else:
        return word

# merges classes with same signature which is (index, name, week). The group fields are combined into final merge
def merge_classes(classes: "list[Series]"):
    """
    Merge classes with the same signature and append the group names to each merged class.

    Args:
        classes (list[Series]): A list of classes to be merged.

    Returns:
        list[Series]: A list of merged classes.
    """
    merged_classes: dict[tuple[int, str, int], Series] = {}

    for cls in classes:
        signature: tuple[int, str, int] = (
            cls["index"],
            cls["name"],
            cls.get("week", 1),
        )
        if signature not in merged_classes:
            merged_classes[signature] = cls
        else:
            # Merge the "group" field by appending the group name
            merged_classes[signature]["group"] += f"|{cls['group']}"

    # Convert the merged_classes dictionary back to a list of classes
    merged_classes_list = list(merged_classes.values())

    return merged_classes_list
