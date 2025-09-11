# Влияние токенизации на оценку качества нейросетевого синтаксического анализа

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

3. визуализация результатов: [Russian_token_parser_statistics.ipynb](Russian_token_parser_statistics.ipynb);
4. вспомогательные файлы:
	- [data_classes.py](data_classes.py) - описание данных:
		- класс ConllEntry - информация о токене, 
		- класс Sentence - информация о предложении;
	- [functions.py](functions.py) - описание основных функций;
 	- [treebank_data_getting.py](treebank_data_getting.py) - чтение предложений с эталонной разметкой;
5. директории с данными:
	- [treebank_test_sets](treebank_test_sets) - тестовые выборки датасетов деревьев зависимостей;
	- [pickle_results](pickle_results) - результаты работы синтаксических анализаторов в формате pickle.
