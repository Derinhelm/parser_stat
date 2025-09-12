# Влияние токенизации на оценку качества нейросетевого синтаксического анализа
[Синтаксические анализаторы с эталонными токенизаторами](README.md#синтаксические-анализаторы-с-эталонными-токенизаторами)

[Структура проекта](README.md#структура-проекта)

[Вычисление метрик](README.md#вычисление-метрик)

## Синтаксические анализаторы с эталонными токенизаторами
### Реализация
Синтаксические анализаторы с эталонными токенизаторами реализованы в файле [parser_running.py](parser_running.py). Реализации представлены в виде классов: SpacyTokenParser, NatashaTokenParser, DeepPavlovTokenParser, StanzaTokenParser, UDPipeSpacyTokenParser.


### Запуск
Пример запуска синтаксического анализатора с эталонной токенизацией:
```
python3 parser_running.py treebank_test_sets/treebank_data.pickle udpipe_t
```
Пример запуска синтаксического анализатора со встроенной токенизацией:
```
python3 parser_running.py treebank_test_sets/treebank_data.pickle udpipe
```

## Структура проекта
1. Основной файл [parser_running.py](parser_running.py) - реализация синтаксических анализаторов с эталонной токенизацией, запуск синтаксического анализа;
2. файлы с историей запуска синтаксических анализаторов:
	- [parser_running.ipynb](parser_running.ipynb) - анализаторы со встроенными токенизаторами,
	- [parser_tokenization_running.ipynb](parser_tokenization_running.ipynb) - анализаторы с эталонными токенизаторами;

3. вычисление метрик и визуализация результатов: [Russian_token_parser_statistics.ipynb](Russian_token_parser_statistics.ipynb);
4. вспомогательные файлы:
	- [data_classes.py](data_classes.py) - описание данных:
		- класс ConllEntry - информация о токене, 
		- класс Sentence - информация о предложении;
	- [functions.py](functions.py) - описание основных функций;
 	- [treebank_data_getting.py](treebank_data_getting.py) - чтение предложений с эталонной разметкой;
5. директории с данными:
	- [treebank_test_sets](treebank_test_sets) - тестовые выборки датасетов деревьев зависимостей;
	- [pickle_results](pickle_results) - результаты работы синтаксических анализаторов в формате pickle.
	
## Вычисление метрик
Вычисление метрик UAS и LAS происходит в файле [Russian_token_parser_statistics.ipynb](Russian_token_parser_statistics.ipynb).

Для вычисления метрик предварительно происходит выравнивание эталонного дерева зависимостей и дерева зависимостей, построенного синтаксическим анализатором. На этом этапе выявляются токены, присутствующие в обоих деревьях зависимостей. Токены считаются одинаковыми, если совпадают индексы их начала и конца в предложении.

Далее происходит вычисление метрик UAS и LAS на основе выровненных наборов токенов. Для обеих метрик вычисляются точность, полнота и F-мера. Вычисление происходит по формулам, приведенным ниже. В формулах используются следующие обозначения:
- $G$ - набор эталонных токенов предложения (gold token set),
- $P$ - набор токенов, созданный анализатором (parser token set),
- $gt$ - токен из эталонного набора,
- $pt$ - токен из набора токенов, созданного анализатором,
- $\textbf{p}(t)$ - функция, возвращающая индексы начала и конца родительского токена для токена $t$,
- $\textbf{d}(t)$ - функция, возвращающая тип связи, которым токен $t$ связан с родительским токеном.

Метрика UAS:

$$precisionUAS = \frac{\parallel gt | gt=pt, gt \in G, pt \in P, \textbf{p}(gt)=\textbf{p}(pt)
	\parallel}{\parallel pt|pt \in P \parallel}$$

$$recallUAS = \frac{\parallel gt | gt=pt, gt \in G, pt \in P, \textbf{p}(gt)=\textbf{p}(pt)
	\parallel}{\parallel gt|gt \in G \parallel}$$

$$fUAS=\frac{2 * precisionUAS * recallUAS}{precisionUAS + recallUAS}$$

Метрика LAS:

$$precisionLAS = {\frac{\parallel gt | gt=pt, gt \in G, pt \in P, \textbf{p}(gt)=\textbf{p}(pt), \textbf{d}(gt)=\textbf{d}(pt) \parallel}{\parallel pt|pt \in P \parallel}}$$

$$recallLAS = \frac{\parallel gt | gt=pt, gt \in G, pt \in P, \textbf{p}(gt)=\textbf{p}(pt), \textbf{d}(gt)=\textbf{d}(pt) \parallel}{\parallel gt|gt \in G \parallel}$$

$$fLAS=\frac{2 * precisionLAS * recallLAS}{precisionLAS + recallLAS}$$
	
