import os

import argparse


import logging
import warnings
from pandas.errors import SettingWithCopyWarning

from ParseSchedules.core import extract_all_schedules

# Disable pandas' SettingWithCopyWarning and FutureWarning
warnings.filterwarnings("ignore", category=SettingWithCopyWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
# warnings.resetwarnings()

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

path_to_doc_schedules: str = args["word_schedules"]

group_into_folders: bool = args["group_into_folders"]
group_size: int = args["schedules_per_folder"]
            

if __name__ == "__main__":
    
    doc_schedules = os.listdir(path_to_doc_schedules)

    # filter out non-word documents
    doc_schedules = [doc for doc in doc_schedules if doc.endswith(".docx")]

    # filter out opened word documents
    doc_schedules = [doc for doc in doc_schedules if not doc.startswith("~$")]
    
    # create full paths
    doc_schedules = [os.path.join(path_to_doc_schedules, doc) for doc in doc_schedules]
    
    extract_all_schedules(
        doc_schedules,
        group_into_folders,
        group_size
    )
    
    
warnings.resetwarnings()
