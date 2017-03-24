# Лукьянов Илья, ПМИ-151 #

## Анализ видеопоследовательностей для автоматического поиска и выделения рекламы ##

Собственно, название отлично отражает цель проекта: автоматическое выделение рекламы.

### Актуальность задачи ###

* Существуют различные решения для автоматического поиска и удаления рекламных вставок из видеопотока, у всех есть свои преимущества и недостатки.
* Хотелось бы реализовать работающую с хорошей точностью утилиту для поиска рекламы, желательно работающую в реалтайме или с небольшой буферизацией, сохраняющее очищенный видеопоток "на лету".

### Используемые технологии ###

* Python — язык, с которым я себя комфортно чувствую, к тому же являющийся более или менее стандартом (вместе с C++) в анализе видео и изображений.
* OpenCV — одна из лучших библиотек компьютерного зрения.
* ffmpeg — пожалуй, лучшая утилита для обработки видео.
* STIP — отличный алгоритм поиска точек интереса в пространстве-времени видео. 
* Optical Flow
* Различные библиотеки для анализа данных для Python.
* Другие алгоритмы для обработки видео (будут заполнены по мере использования в проекте)

### Архитектура ###

![graph.png](https://bitbucket.org/ilyaluk/detect_ads/raw/master/graph.png)

### Как запустить ###

* Требуется установленный OpenCV 2 (для работы STIP). Возможно, будет в репозитории, если не будет проблем с зависимостями.
* Требуется OpenCV 3 (любой подойдёт, главное чтоб были биндинги для Python)
* Требуется ffmpeg
* Бла-бла-бла

Когда более или менее закончу добавлять зависимости, разверну на чистой виртуалке с Ubuntu 16.04 и напишу подробную инструкцию для неё.

### Описание функциональности ###

