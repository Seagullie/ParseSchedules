# ParseSchedules

Парсер розкладів для [переглядача розкладів під андроїд та веб.]()



Цей скрипт витягує таблиці зі розкладами із вордівських файлів.

Загальний хід: **.docx** --> **pandas таблиця** --> **.json зі розкладом**

`python parse_schedules.py -h`

```shell
usage: parse_schedules.py [-h] [-w WORD_SCHEDULES] [-g] [-n SCHEDULES_PER_FOLDER] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -w WORD_SCHEDULES, --word_schedules WORD_SCHEDULES
                        Path to .docx files with schedules
  -g, --group_into_folders
                        Chunk output into folders. Specify the number of schedules per folder with --schedules_per_folder (default is 20)
  -n SCHEDULES_PER_FOLDER, --schedules_per_folder SCHEDULES_PER_FOLDER
                        Number of schedules per folder. Only used if --group_into_folders is True
  -v, --verbose         Include more info in the output. Default is False
```

Примітка: `--group_into_folder` було зроблено для зручності, оскільки **Contentful** не дозволяє завантажувати більше 20-ти файлів за раз.

Приклад використання скрипта:

```
python parse_schedules.py -w ./word_schedules
```

`Parsing schedules... |███████████▌                    | 13/36`
