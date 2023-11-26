# Отчёт о выполнении задачи "Дрон-инспектор"

- [Отчёт о выполнении задачи "Дрон-инспектор"](#отчёт-о-выполнении-задачи-дрон-инспектор)
  - [Постановка задачи](#постановка-задачи)
  - [Известные ограничения и вводные условия](#известные-ограничения-и-вводные-условия)
    - [Цели и Предположения Безопасности (ЦПБ)](#цели-и-предположения-безопасности-цпб)
  - [Описание системы](#описание-системы)
    - [Компоненты](#компоненты)
    - [Алгоритм работы решения](#алгоритм-работы-решения)
    - [Описание Сценариев (последовательности выполнения операций), при которых ЦБ могут нарушаться](#описание-сценариев-последовательности-выполнения-операций-при-которых-цб-могут-нарушаться)
    - [Политики безопасности](#политики-безопасности)
  - [Запуск приложения и тестов](#запуск-приложения-и-тестов)
    - [Запуск приложения](#запуск-приложения)
    - [Запуск тестов](#запуск-тестов)
    - [Ожидаемый результат](#ожидаемый-результат)

## Постановка задачи

Компания создаёт дрон для мониторинга трубопроводов, тянущихся на сотни километров в том числе по горам, лесам и пустыням. Поэтому нужна функция автономного выполнения задачи. 
При этом даже в горах летает гражданская авиация (те же вертолёты экстренной медицинской помощи), очень бы не хотелось, чтобы, например, дрон компании врезался в вертолёт с пациентами. Поэтому тяжёлые автономные дроны должны летать в контролируемом воздушном пространстве, координацию полётов в котором осуществляет система организации воздушного движения (ОрВД).

В рамках хакатона участникам предлагается: 
- доработать предложенную архитектуру (см. далее) бортового обеспечения дронов-инспекторов с учётом целей безопасности
- декомпозировать систему и отделить критический для целей безопасности код
- в бортовом ПО нужно внедрить компонент "монитор безопасности" и реализовать контроль взаимодействия всех подсистем дрона
- доработать функциональный прототип 
- создать автоматизированные тесты, демонстрирующие работу механизмов защиты


## Известные ограничения и вводные условия
1. По условиям организаторов должна использоваться микросервисная архитектура и шина обмена сообщениями для реализации асинхронной работы сервисов.
2. Между собой сервисы ПЛК общаются через шину сообщений (message bus), а всё "снаружи" принимают в виде REST запросов.
3. Физическая надёжность аппаратуры (ПЛК и всего остального производства) и периметра не учитывается.
4. Графический интерфейс для взаимодействия с пользователем не требуется, достаточно примеров REST запросов.
5. Персонал, обслуживающий систему, благонадёжен.


### Цели и Предположения Безопасности (ЦПБ)

#### Цели безопасности:

1. Выполняются только аутентичные задания на мониторинг 
2. Выполняются только авторизованные системой ОрВД задания 
3. Все манёвры выполняются согласно ограничениям в полётном задании (высота, полётная зона/эшелон) 
4. Только авторизованные получатели имеют доступ к сохранённым данным фото-видео фиксации 
5. В случае критического отказа дрон снижается со скоростью не более 1 м/с 
6. Для запроса авторизации вылета к системе ОрВД используется только аутентичный идентификатор дрона 
7. Только авторизованные получатели имеют доступ к оперативной информации

#### Предположения безопасности:

1. Аутентичная система ОрВД благонадёжна
2. Аутентичная система планирования полётов благонадёжна
3. Аутентичные сотрудники благонадёжны и обладают необходимой квалификацией
4. Только авторизованные сотрудники управляют системами
5. Аутентичное полётное задание составлено так, что на всём маршруте дрон может совершить аварийную посадку без причинения неприемлемого ущерба заказчику и третьим лицам


### Описание системы

Изначально, в общем виде контекст работы выглядел следующим образом:

![Контекст](docs/images/drone-inspector_general.png)

В ходе решения она была детализирована до следующей:

![Решение](docs/images/drone-inspector_result.png)


### Компоненты
| Название | Назначение | Комментарий |
|----|----|----|
|*ATM (Air Traffic Manager, Система организации воздушного движения)* | Имитатор центральной (возможно, государственной) системы управления движением дронов в общем воздушном пространстве. Получает информацию о местоположении каждого дрона, подтверждает полетное задание. | - |
|*FPS (Flight Planning System, Система планирования полетов)* | Имитатор сервиса распределения задач по дронам. Позволяет согласовывать полетное задание с системой ATM, отправлять  дронов на задание, задавать режимы полёта. Получает данные телеметрии от дрона. | - |
|*decoder(шифратор)* | Расшифровывает входящие зашифрованные команды и передает в CCS(центральная система управления). | Повышающий доверие, т.к. используется шифрование. |
|*encoder(дешифратор)* | Зашифровывает данные приходящие из CSS(центральная система управления). | Доверенный.|
|*css(central control system, центральная система управления)* | Центральный блок управления. Выполняет функцию раздатчика комманд, при условии, что валидатор комманд разрешил их передать.  | Повышающий доверие, т.к. общается с валидатором комманд. |
|*fly_controller(полётный котроллер)* | Управляет приводами. | Недоверенный. |
|*drives(приводы)* | Включаются и выключаются по командам. | Недоверенный. |
|*monitoring* | Проводит самодиагностику и мониторинг состояния "хардверных" компонентов. | Недоверенный. |
|*battery_status* | Смотрит на заряд батареи и отдает значение в мониторинг | Недоверенный. |
|*navigation_handler(обработчик навигационных данных)* | Обрабатывает навигационные данные от ИНС и GPS и передает в шину данных. | Повышающий доверие, т.к. использует алгоритмы для улучшения данных на основе двух источников. |
|*INS(Инс)* | Имитатор системы ИНС. | Недоверенный. |
|*GPS* | Имитатор системы GPS. | Недоверенный. |
|*camera* | Камера для видео и фото фиксации. | Недоверенный. |
|*data_handler(обработчик данных)* | Обрабатывает фото и видео для последующей передачи. | Повышающий доверие, т.к. обрабатывает данные. |
|*data_storage(хранилище данных)* | Хранит данные. | Доверенный. |
|*command_validator(валидатор комманд и шина данных)* | Управляет данными. Выдает только после успешной проверки соседними компонентами(проверка на аутентичность и авторизованность, уточнение навигации и проверка валидности получателя), так же отправляет на проверку команды CSS. | Недоверенный. |
|*navigation_verification(валидация навигационных данных)* | Проверяет сходятся ли навигационные данные с заданным маршрутом. | Повышающий доверие, т.к. сравнивает данные маршрута и геолокацию. |
|*authentication_verification(проверка команд на аутентичность и авторизованность)* | Проверяет аутентичны ли команды с помощью какой нибудь подписи или ключа. | Повышающий доверие, т.к. проверяет данные. |
|*crit_handler(Обработчик критических ситуаций)* | При условии, что все проверки прошли успешно, отдает команду на CSS, в ином случае перехватывает управление полетным контроллером. | Доверенный. |

### Операции
| Назначение           | Источник             | Канал | Операция                  | Параметры |
|----------------------|----------------------|:-----:|---------------------------|---|
| **Cutoff**           | **IAM**              | MB    | `hard_stop`               | 🟢 |
| **Cutoff**           | **PLC control**      | MB    | `hard_stop`               | 🟢 |
| **Downloader**       | **Update manager**   | MB    | `request_download`        | `module_name`                   |

### Алгоритм работы решения

Диаграмма последовательности этого примера выглядит следующим образом:

![Диаграмма последовательности](./docs/images/drone-inspector_sd.png)

[ссылка на исходник диаграммы](https://www.plantuml.com/plantuml/uml/vLRTRkDK4BxtKnpjxJP8_CCA8HwaDzxMb4XPEuhTIdlNj9HsbHKHAoGG4Zz8mBNhnCHDM_SLvhmHtuoFVNoyDb759HUfL7k-RsQ--HadusGIg2VqHY_eWKgwfNlAyIieLxIXbDRuuL-zVE9v_d4IXSSldWSpR-hFal71UEg72T2_ms2kpu2yetG_1DEjWPs2Csieb1-hmt4yzPE3hzuY-GN6R-XxCJgAJjotxxwZu2NJIzhers9o48MXQ_C-RFxYwFKPg5AwrQ_XDzNB_L3FtGZrEJs8JOP8SniTioQpQ1A_Z5tk3y3zizWNj0BdDmqYz3kXVWBJNq5UmBYajLw8MHpCJg9OkQOViIchhhz3RFUemGtKsr9fSi0RZa-V2WNBFnrFeiGbUK-akQPIdoegb8YDvE5_0pAf7rFh2o6PpgA388x7uP7ByY5O_cH9R0FqeECaclb7WGlzM098eIpI1J2b5K2bw5tGLZgYKF8Ql7XOYZhtj3BAJBuy7FkTU3u5wKzM22wcGf8fu2aUv5G8-BcV9C7ifUSTpQBZgQ8VnGMgKzT8eMaM8YA0dcq-DVfSMkYPeWTR0IexVK-vnrQmvfvy-lIP4kShQIT4rkycZ990HIVm0j1UrQg3EDh2-xVwab96uu7ISvXUuwKtKWXXNVKqpByMFQ51KsoeB55dqZqv9mDvf1Wv-z4BHMiH44snWyxLOKLbPmFiAHw0fdwRUhIjkHbXBmWF5MlW8NqZ7UjijW7wcTqYblsmNvNzi2sdgYQ2jcnieuEHpKmScPAEHbAbb3O2kB8B3PQjGZMLjKEF0k_g1ubvDxVbL9-Di2GWWAoVhJxNhmGXMK5AcHcW8S32guU1GQQt0OGu_1xGUOUujcSZCtAbNfgO99DrU_UrqKxYbM8mk-J4CQpSHleAltFspHNr9b4qnQJBnbmtnHT7cS3fXglHE-cKkgxjCeFaFLqhHoHdZUNPgtf9UmtE8Uc4trxlUedXWkBwebByJg9UEqHcEoEKNYZb3bJAnFOMYHIolWiwuF1jwNCqr3alkQhIIB_BX-Hxcgg_YuQht1r27g9cLVzTEy9Js_FDkDaIcuPmtTZB8YMrUyse8Md2Hy6A33I9wR7VA9M31YtStg9y26YzEx78O3J74NcrhgDgdxSEWJbqPgmkXW-ZYznTMRtOCH-FBsvOhHQPIpD0LH57lGJoVE1EZoHVkaPUPypH7wiOcldCyExIB4eSb98DHvIPErCsEzPUtg5egNYSNFOizmlbNc7boUVOHjYaqQkz_b0TbNemrZnnTX3Qno3rEC8pYV7QNN_tLIv08oipCZU2rNEPeoqLzYW-PZfvvOEq54Llgf3bjRvg3UkTRFWvJ8f_7KpZ8PTJcjPRTNYe3WF_81cV-D3HajIVMZzqGn4U6yaU0giapxhUK27vcEDQF-ukgF_rML3_vIf8PvZQ_K65tOFsMxHLFTMcjHzMraO0tNRiZkLku-vos8MHBBmlyFVunUGV)


### Описание Сценариев (последовательности выполнения операций), при которых ЦБ могут нарушаться

 Название | Атакованный модуль | Нарушенная ЦБ | Комментарий |
|----|----|----| ----|
|*1. Взлом и подмена команд* | decoder/css/command_validator | - | Отказ в выполнении команд при проверке в authentication_verificator |
|*2. Взлом и передача ложных комманд на приводы* | fly_controller/drives | 3,5 | drives и fly_controller передают свои данные на monitoring, дальше по цепочке доходит до crit_handler, он сравнивает текущие данные с ожидаемыми и выключает подачу питания на приводы |
|*3. Взлом и подмена данных состояния "хардверных" компонентов* | monitoring/battery_status/drives/command_validator | 3,5 | crit_handler обработает данные и передаст нужные указания для остановки работы и аварийной посадки/ внезапно разрядится батарея/ внезапно выйдут из строя приводы|
|*4. Взлом и подмена навигационных данных* | navigation_verification/navigation_handler/INS+GPS/command_validator | 3,5 | - |
|*5. Взлом encoder* | encoder | - | потеря/порча данных(не противоречит ЦБ) |
|*6. Взлом и подмена фото/видео данных* | - | camera/data_handler/data_storage/command_validator | не противоречит ЦБ |

 Взломанный модуль | Нарушенная ЦБ | Комментарий |
|----|----| ----|
| encoder | - | - |
| decoder | - | - |  
| fly_controller | 3,5 | - |
| drives| 3,5 | - |
| monitoring | 3,5 | - |
| battery_status | 3,5 | - |
| navigation_handler | 3,5 | - |
| INS | 3,5 | - |
| GPS | 3,5 | - |
| css | - | - |
| command_validator | 3,5 | - |
| authentication_verification | - | - |
| navigation_verification | 3,5 | - |
| crit_handler | 3,5 | - |
| data_storage | - | - |
| data_handler | - | - |
| camera | - | - |

**Негативный сценарий 1 - DOS атака на communication_in:**

![Негативный сценарий 1](./docs/images/drone-inspector_negative_1.png)

[ссылка на исходник диаграммы](https://www.plantuml.com/plantuml/uml/vLRTRkDK4BxtKnpjxJP8_CCA8HwaDzxMb4XPEuhTIdlNj9HsbHKHAoGG4Zz8mBNhnCHDM_SLvhmHtuoFVNoyDb759HUfL7k-RsQ--HadusGIg2VqHY_eWKgwfNlAyIieLxIXbDRuuL-zVE9v_d4IXSSldWSpR-hFal71UEg72T2_ms2kpu2yetG_1DEjWPs2Csieb1-hmt4yzPE3hzuY-GN6R-XxCJgAJjotxxwZu2NJIzhers9o48MXQ_C-RFxYwFKPg5AwrQ_XDzNB_L3FtGZrEJs8JOP8SniTioQpQ1A_Z5tk3y3zizWNj0BdDmqYz3kXVWBJNq5UmBYajLw8MHpCJg9OkQOViIchhhz3RFUemGtKsr9fSi0RZa-V2WNBFnrFeiGbUK-akQPIdoegb8YDvE5_0pAf7rFh2o6PpgA388x7uP7ByY5O_cH9R0FqeECaclb7WGlzM098eIpI1J2b5K2bw5tGLZgYKF8Ql7XOYZhtj3BAJBuy7FkTU3u5wKzM22wcGf8fu2aUv5G8-BcV9C7ifUSTpQBZgQ8VnGMgKzT8eMaM8YA0dcq-DVfSMkYPeWTR0IexVK-vnrQmvfvy-lIP4kShQIT4rkycZ990HIVm0j1UrQg3EDh2-xVwab96uu7ISvXUuwKtKWXXNVKqpByMFQ51KsoeB55dqZqv9mDvf1Wv-z4BHMiH44snWyxLOKLbPmFiAHw0fdwRUhIjkHbXBmWF5MlW8NqZ7UjijW7wcTqYblsmNvNzi2sdgYQ2jcnieuEHpKmScPAEHbAbb3O2kB8B3PQjGZMLjKEF0k_g1ubvDxVbL9-Di2GWWAoVhJxNhmGXMK5AcHcW8S32guU1GQQt0OGu_1xGUOUujcSZCtAbNfgO99DrU_UrqKxYbM8mk-J4CQpSHleAltFspHNr9b4qnQJBnbmtnHT7cS3fXglHE-cKkgxjCeFaFLqhHoHdZUNPgtf9UmtE8Uc4trxlUedXWkBwebByJg9UEqHcEoEKNYZb3bJAnFOMYHIolWiwuF1jwNCqr3alkQhIIB_BX-Hxcgg_YuQht1r27g9cLVzTEy9Js_FDkDaIcuPmtTZB8YMrUyse8Md2Hy6A33I9wR7VA9M31YtStg9y26YzEx78O3J74NcrhgDgdxSEWJbqPgmkXW-ZYznTMRtOCH-FBsvOhHQPIpD0LH57lGJoVE1EZoHVkaPUPypH7wiOcldCyExIB4eSb98DHvIPErCsEzPUtg5egNYSNFOizmlbNc7boUVOHjYaqQkz_b0TbNemrZnnTX3Qno3rEC8pYV7QNN_tLIv08oipCZU2rNEPeoqLzYW-PZfvvOEq54Llgf3bjRvg3UkTRFWvJ8f_7KpZ8PTJcjPRTNYe3WF_81cV-D3HajIVMZzqGn4U6yaU0giapxhUK27vcEDQF-ukgF_rML3_vIf8PvZQ_K65tOFsMxHLFTMcjHzMraO0tNRiZkLku-vos8MHBBmlyFVunUGV)

**Негативный сценарий 2 - Подмена/Фальшивые входные данные:**

![Негативный сценарий 2](./docs/images/drone-inspector_negative_2.png)

[ссылка на исходник диаграммы](https://www.plantuml.com/plantuml/uml/vLP9RzjM4BxpLpoabmQsYkvBK1GvzaSOA1YPTOJAf21I1dBp4jSE5DHeKA15WIu5sfufMepenSfVcFUF-isGJu-F8QCAFVQW87wS-MRvPfc7SUAFayd-q4i6oJ1Gz-Y5dj8hMj8DtL6ENq6veWMbDCSFV-gBUvxdJv8edEm_2iQUtq-YiVhIxtyJZ9KVgyVb_zuQ1xlU2DY3_c3aXmcG_u3oaJu6wYsbEo6it5IGXx2NhU0PPNSGZ_oa_nW6N91V8Vo2VX2XlUZ0_VhUEmfMCdr12_rSKIPI_MZ_gq7e2hxl2XQqM8b6ayIL_G2oVtCgz35iftIZdyFHL5_iXFh83KcVq2kHoH1QRiC1S9YCes7y96v9p8Smy8ie5NG9u6zPJRqz26DuflP6yNt12Fr6j9z2xpUOAw2vfBcUYbWSZ0-YMBcY7xCeawg_XxTteFWA15pZHQ8Ikk6nFXG8PdSq64P98xllIjPcjDI7x9aGXdnm-e0czS7O-bHGHkEe7yJn8DnpOJu2ob-S9LjWBTengihV2rpLJyI1b6uvNYYcT0cbfL1GqBLKLQ7aCt3nk9JqtD5bbPhXrxi3l-7FPm3zkPu9heWPfL1FyP1J8SgF_2G9nayyRsySJKQAVX8Ju6h56EffAbc4ecSBMFM-g6fmQ-k14iHBAHkOiso3mskO_awVcQJSzqejrhVrioc6rNHn12K5mZbqdrOTY0ow2gOZkgrwbGI4kH_Vu1xDnSeTR43GPWKA80gsuRFQKZ9yvdZAk1xf9SrDCAtv-FVQvM2g_7mWaXLRA25to5bnwwPeI0UrQNIxjrwhdI0P55qiIVkXtC0qqco63S3rAUKGJhqmIW8L7I02HBjjXc0NDRPmKiu87XHWSvhXezU3jJAFY05kbArMTfSuWWQKs3APB3c7ZCwHFitPZfxMo5y3vsRhafQDvREjU5AkMdjXDeSLhpQ45uIxYhCWrMPP5p-aEgf4xeJjMTa9wmsjocb9ronilODGewnN1TFhbUpHGbJELnonhBBO7Ms-jdB4x_Necmu0jGNgRO9iHTM0Fk_nDfBMov6H4_sCJKkAX9Uv35rmggUU6RfGCZCKYiWqVuVgKGFOoBCGLvPGVM62a_QkhztryPrn1XKlQ5JYENudR9lBmnj64KzoHZAy2vLbkgl6cgzAJ3p8IbAlMB1rrJHdg5sd8BMbD-GIOlkvl3qpXuEtqdD06d7LJmvzWHO65VgqfE9Ml9wxGELz05TQLIbtL9a_aRUQ225hEn4x3BxEIOwIFU4jMvO0mdVn9FYMQcilhsxwcwtEhRgw5LwA8UbosrMsgIt5LQMuPknf8vI-jdObJDWeE2DTHL8Mt--KoaM5NBYrHNcNehNk-Y8TOwupn5KxprJzld81pALLzTjfzsNcQgvdLa_NzCV6vCgbKOqTjARfePB7NYk6l7VSYZq9cMO8xPWnsjqLmQf5CtmxC-FXgT2sxF6hBBHb_HYo1s2NmrHibZJdq6hFcBlsbKSPP1O2A1KlAqGQ0twO3fbpwzcEgE-Tr6CdZyNDcJi7xyfme8t0gjwv4brz90rrJONTmPkqAIy5WF9R0KXnMJxhyrhNtieEE898ySOEhIpaihbJCrwxksityFl9uC177Ys8EVf_RBeYEDQJRJXMfZnhMfErF8C-wDviGQZ_zNvG_saze38CTtzIOGUYEV8SzbJxmC4XPyL4frcHpURSIDuEYhLg4iv3_3FP7_u3)

**Еще много отдельных диаграмм**

### Политики безопасности 


```python {lineNo:true}

  if src == 'drone_battery_control' and dst == 'drone_diagnostic' \
        and operation == 'battery_status':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'stop':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'clear':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'watchdog':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_data_aggregation' \
        and operation == 'camera_on':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_data_aggregation' \
        and operation == 'camera_off':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'log':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_flight_controller' \
        and operation == 'move_to':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_diagnostic' \
        and operation == 'get_status':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'register':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'sign_out':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'send_position':
        authorized = True
    if src == 'drone_ccu' and dst == 'drone_communication_out' \
        and operation == 'data':
        authorized = True
    if src == 'drone_communication_in' and dst == 'drone_ccu' \
        and operation == 'in':
        authorized = True
    if src == 'drone_data_aggregation' and dst == 'drone_ccu' \
        and operation == 'data':
        authorized = True
    if src == 'drone_data_aggregation' and dst == 'drone_data_saver' \
        and operation == 'smth':
        authorized = True
    if src == 'drone_diagnostic' and dst == 'drone_ccu' \
        and operation == 'diagnostic_status':
        authorized = True
    if src == 'drone_diagnostic' and dst == 'drone_battery_control' \
        and operation == 'get_battery':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_gps' \
        and operation == 'get_coordinate':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_ins' \
        and operation == 'get_coordinate':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_ccu' \
        and operation == 'reached':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_battery_control' \
        and operation == 'change_battery':
        authorized = True
    if src == 'drone_flight_controller' and dst == 'drone_engines' \
        and operation == 'smth':
        authorized = True
    if src == 'drone_gps' and dst == 'drone_ccu' \
        and operation == 'gps_coordinate':
        authorized = True
    if src == 'drone_ins' and dst == 'drone_ccu' \
        and operation == 'ins_coordinate':
        authorized = True  

```

## Запуск приложения и тестов

### Запуск приложения

см. [инструкцию по запуску](README.md)

### Запуск тестов

_Предполагается, что в ходе подготовки рабочего места все системные пакеты были установлены, среда разработки настроена в соответсвии с руководством, на которое приведена ссылка выше._

Запуск примера: открыть окно терминала в Visual Studio code, в папке с исходным кодом выполнить 

**make run**
или **docker-compose up -d**

запуск тестов:
**make test**
или **pipenv run pytest**

### Ожидаемый результат

![Результат выполнения тестов](./docs/images/drone-inspector_tests.png)