# О проекте

Данный микросервис решает следующую задачу: собирать и хранить данные о "свечках" [1] по ценным бумагам, обращающимся на Московской бирже, а также предоставлять доступ другим сервисам системы к этим данным.

[1] https://ru.wikipedia.org/wiki/%D0%AF%D0%BF%D0%BE%D0%BD%D1%81%D0%BA%D0%B8%D0%B5_%D1%81%D0%B2%D0%B5%D1%87%D0%B8

Основной функционал:

- добавление ценных бумаг в базу с помощью команды CLI `create-security`;
- загрузка данных с API Московской биржи в виде фоновой задачи `update_candles` на движке TaskIQ;
- предоставление доступа к данным для потребителей через REST API.

# Архитектура приложения

Архитектурная схема компонентов:

<img src="https://storage.yandexcloud.net/armsmaster/candlestick-service-architecture.drawio.png">

А формате pdf: https://storage.yandexcloud.net/armsmaster/candlestick-service-architecture.drawio.pdf

# Workdir

`.`

# Test

`pytest app`

or

`pytest app -vvs` (debug)
