# Задание
Необходимо создать программу, которая сравнивает два текста программ на Python и выдает оценку их похожести.

*Оригинальный текст задания находится в файле [task.md](task.md).*


# Реализация
```
$ python3 compare.py -h
usage: compare.py [-h] input_file output_file

Tool for calculating similarity between files. Used to detect plagiarism, especially in Python code.

positional arguments:
  input_file   path to the input file
  output_file  path to the output file

options:
  -h, --help   show this help message and exit
```

## Структура входного файла
Входной файл должен содержать строки с **парами** файлов для сравнения. В случае, если указано неверное число файлов или один из файлов не найден, в `output_file` записывается коэффициент `-1`.
```
example_files/files/differencing.py example_files/plagiat1/differencing.py
example_files/files/auto.py example_files/plagiat1/auto.py
example_files/files/basic.py example_files/plagiat1/basic.py
```

## Структура выходного файла
В выходном файле содержатся значения [0.0, 1.0], обозначающие коэффициент заимствования между парами файлов из `input_file`. Сохраняется исходный порядок следования пар.
```
0.552
1.0
0.985
```


# Замечания
1. В решении не используется библиотека `numpy`, так как, по всей видимости, выделение памяти для массивов занимает в ней слишком много времени. Было предпринято несколько попыток по оптимизации *самой очевидной* версии алгоритма поиска расстояния Левенштейна, но все они не увенчались успехом. 
2. Класс `Spinner` было бы логичнее оформить в виде отдельного модуля, однако я решил записать всё решение в одном файле для удобства проверяющих.
