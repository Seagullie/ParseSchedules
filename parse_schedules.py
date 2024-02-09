import os
import pandas as pd
import json
from models import Lesson, WeeklySchedule
from pydocx import PyDocX
import argparse
from progress.bar import IncrementalBar


import logging
import warnings
from pandas.errors import SettingWithCopyWarning

# Disable pandas' SettingWithCopyWarning and FutureWarning
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
# warnings.resetwarnings()

from utilities import (
    remove_duplicates,
    strip_each_text_cell,
    label_upper_and_lower_duplicates,
    qualifications,
)
from utilities import (
    days_ukr,
    days_eng_lower,
    extract_group_names,
    correct_group_names,
)


# construct the argument parser and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument(
    "-w",
    "--word_schedules",
    default="./word_schedules",
    help="Path to .docx files with schedules",
)

ap.add_argument(
    "-g",
    "--group_into_folders",
    action="store_true",
    help="Chunk output into folders. Specify the number of schedules per folder with --schedules_per_folder (default is 20)",
)

ap.add_argument(
    "-n",
    "--schedules_per_folder",
    type=int,
    default=20,
    help="Number of schedules per folder. Only used if --group_into_folders is True",
)

ap.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Include more info in the output. Default is False",
)

args = vars(ap.parse_args())

# Configure the logging module

logging_level = logging.NOTSET if args["verbose"] else logging.ERROR
logging.basicConfig(level=logging_level)


def extract_single_schedule(df: pd.DataFrame, target_group: str):
    """
    Extracts a single schedule from a DataFrame based on the target group.
    Saves it to a separate file, the name of which is target_group.json

    Args:
        df (pandas.DataFrame): The DataFrame containing the schedule data.
        target_group (str): The target group to filter the schedule for.

    Returns:
        None
    """

    # filter groups to target group
    df = df.loc[:, ["День", "Пара", target_group]]

    # assumption: room number is always in the beginning of class description. May end with a slash and a number
    re_for_room_number = r"\b(\w\. ?\d{1,5}\w{0,5}(/\d)*)\b"
    # TODO: unhardcode
    df["Аудиторія"] = (
        df[target_group]
        .str.extractall(re_for_room_number)
        .groupby(level=0)[0]
        .apply(lambda x: "|".join(x))
    )  # extract
    df[target_group] = df[target_group].str.replace(re_for_room_number, "")  # remove

    # extract teacher qualifications into own column
    teacherQualRE = "(" + "|".join(qualifications) + ")"
    # The groupby() method is then used to group the matches by their original index (i.e., the index of the row in the original DataFrame),
    # and the apply() method is used to concatenate the grouped matches into a single string using the join() method.
    df["qualification"] = (
        df[target_group]
        .str.extractall(teacherQualRE)
        .groupby(level=0)[0]
        .apply(lambda x: "|".join(x))
    )

    # extract teacher name into own column. Use qualification column as a separator
    # teacher namee is their qualification in lower case, followed by a dot, followed by their name, first letter capitalized.
    # then, optionally, a space and single uppercase letter (for name)

    # warning: [А-Я] doesn't include some of ukrainian letters
    teacherRe = rf"{teacherQualRE} ([А-ЩЬЮЯҐЄІЇ][а-щьюяґєії]+( [А-ЩЬЮЯҐЄІЇ]\.)*)"
    # df['teacher'] = df[target_group].str.split(teacherQualRE).str[2]
    df["teacher"] = (
        df[target_group]
        .str.extractall(teacherRe)
        .groupby(level=0)[1]
        .apply(lambda x: "|".join(x))
    )

    # clean up class description column:
    # subtract qualification, then teacher name from the class description column
    df[target_group] = df[target_group].str.replace(teacherQualRE, "")
    df[target_group] = df[target_group].str.replace(
        "|".join(df["teacher"].dropna()), ""
    )

    # rename columns
    replacement_table = {"Аудиторія": "room", "Пара": "index"}
    replacement_table[target_group] = "name"
    df.rename(columns=replacement_table, inplace=True)

    df = strip_each_text_cell(df)

    # --- process the table [end] ---
    # chunk into df by each day

    dfs_per_day = [df[df["День"] == day] for day in days_ukr]

    def df_to_json():
        """
        Converts a DataFrame to a JSON object. Saves the JSON object to a file.
        """
        json_: WeeklySchedule = {}
        for day, day_df in zip(days_eng_lower, dfs_per_day):
            if day_df.empty:
                json_[day] = []
                continue

            label_upper_and_lower_duplicates(day_df)

            # TODO: unhardcode
            # drop rows if they don't have any data in name column
            day_df.dropna(subset=[df.columns[2]], inplace=True)

            # drop duplicates
            day_df = remove_duplicates(day_df)

            # TODO: unhardcode
            # drop rows if they don't have any meaningful data in class name column
            day_df = day_df[day_df["name"].str.startswith("---") != True]

            day_df = day_df.drop(["День"], axis=1)
            # TODO: Annotate
            classes: list[Lesson] = [
                Lesson(**lesson_dict)
                for lesson_dict in json.loads(
                    day_df.to_json(orient="records", force_ascii=False)
                )
            ]
            for class_ in classes:
                if not class_.label is None:
                    class_.isBiweekly = True
                    class_.week = int(class_.label)

            json_[day] = {"classes": classes}

        # write json to file
        dfs_per_day_json_string = json.dumps(
            json_, indent=4, default=lambda obj: obj.__dict__, ensure_ascii=False
        )
        with open(
            f"output_json/{target_group}.json",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(dfs_per_day_json_string)

    df_to_json()
    logging.info(df)


def preprocess_table(df: pd.DataFrame):
    # --- process the table ---

    # Drop empty columns
    df = df.dropna(axis=1, how="all")

    # correct group names
    df = correct_group_names(df)

    # rename first two columns
    df.columns = ["День", "Пара"] + df.columns[2::].tolist()

    # fill in NaN values in days with the values from the cells above them
    df["День"] = df["День"].fillna(method="ffill")

    # remove spaces and reverse the word if it ends with uppercase letter
    df["День"] = df["День"].map(lambda day: day.replace(" ", ""))
    df["День"] = df["День"].map(lambda day: day[::-1] if day[-1].isupper() else day)

    return df


path_to_doc_schedules: str = args["word_schedules"]

group_into_folders: bool = args["group_into_folders"]
group_size: int = args["schedules_per_folder"]

def extract_all_schedules(
    path_to_doc_schedules: str,
    group_into_folders: bool,
    group_size: int):

    doc_schedules = os.listdir(path_to_doc_schedules)

    # filter out non-word documents
    doc_schedules = [doc for doc in doc_schedules if doc.endswith(".docx")]

    # filter out opened word documents
    doc_schedules = [doc for doc in doc_schedules if not doc.startswith("~$")]
    
    # create full paths
    doc_schedules = [os.path.join(path_to_doc_schedules, doc) for doc in doc_schedules]

    bar = IncrementalBar("Parsing schedules...", max=len(doc_schedules))

    for doc_schedule in doc_schedules:
        # inputs:
        # path_to_html = "document_pydoc_x_ВП-5.html"
        # path_to_html = os.path.join(path_to_doc_schedules, doc_schedule)
        path_to_html = doc_schedule

        # Pass in a path
        html = PyDocX.to_html(path_to_html)

        df = pd.read_html(html, header=0)[0]
        df = preprocess_table(df)

        group_names = extract_group_names(df)

        for group in group_names:
            extract_single_schedule(df, group)

        bar.next()

    if group_into_folders:
        # group all the schedules into folders. Each folder should have group_size schedules
        # (except for the last folder, which may have less than group_size schedules)

        # get all the schedules
        schedules = os.listdir("output_json")

        # create folders
        for i in range(0, len(schedules), group_size):
            # overwrite existing folders
            os.mkdir(f"output_json/group{i//group_size}")

        # move schedules into folders
        for i, schedule in enumerate(schedules):
            os.rename(
                f"output_json/{schedule}", f"output_json/group{i//group_size}/{schedule}"
            )
            
    warnings.resetwarnings()


if __name__ == "__main__":
    extract_all_schedules(
        path_to_doc_schedules,
        group_into_folders,
        group_size
    )