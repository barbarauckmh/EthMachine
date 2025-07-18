﻿
# ⚔️ EthMachine

## Общая информация

Данный софт позволит вам сделать активность в сети ETH. Большинство настроек подготовлены к работе, остальные простые и понятные. 
> Путь осилит идущий, а софт осилит любой деген🕵️

**Подробная [статья](https://teletype.in/@realaskaer/attackmachine) по работе с этим подобным зверем**

## 🧩Модули

    1.  OKX                 (Депозит / Вывод / Сбор средств с субАккаунтов)                                       
    2.  BingX               (Депозит / Вывод / Сбор средств с субАккаунтов)                                       
    3.  Binance             (Депозит / Вывод / Сбор средств с субАккаунтов)                                       
    4.  Bitget              (Депозит / Вывод / Сбор средств с субАккаунтов)                                       
    5.  Across              (Bridge по любым направлениям / для любых монет)
    6.  Bungee              (Bridge по любым направлениям / для любых монет)
    7.  Nitro               (Bridge по любым направлениям / для любых монет)
    8.  Owlto               (Bridge по любым направлениям / для любых монет)
    9.  Orbiter             (Bridge по любым направлениям / для любых монет)    
    10. Relay               (Bridge по любым направлениям / для любых монет)   
    11. Rhino               (Bridge по любым направлениям / для любых монет)   
    12. Native bridge       (офф. мост Bridge / Withdraw)
    13. Uniswap             (Свапы между стейблами и ETH)
    14. iZumi               (Свапы между стейблами и ETH)   
    15. ODOS                (Свапы между стейблами и ETH)
    16. 1inch               (Свапы между стейблами и ETH)
    17. Mint.fun            (Минт любой NFT по контракту)
    18. Bungee              (Refuel в/из любой сети)
    19. ETH Sender          (Отправка пыли в ETH на свой / рандомный адрес)
    20. Wrap/Unwrap ETH     (Делает врапы / анврапы ETH через офф. контракт WETH в сети)
    21. Balancer            (Уравнивает баланс токена на аккаунтах)
    22. Random Approve      (Делает случайный апрув на контракт DEX)

## ♾️Основные функции

1.  **🚀Запуск прогона всех аккаунтов по подготовленным классическим маршрутам**

    После генерации маршрута (следующая функция), софт запустит выполнение маршрутов для всех аккаунтов. Все варианты работы смотрите в разделе **Настройка софта**  

2.  **📄Генерация классических роутов для каждого аккаунта**

    Классический генератор, работает по дедовской методике. Вам нужно указать списки модулей в настройке `CLASSIC_ROUTES_MODULES_USING` и при запуске этой функции софт соберет вам маршрут по этой настройке. Поддерживается 
    `None` как один из модулей в списке, при его попадании в маршрут, софт пропустит этот список.

3. **💾Создание файла зависимостей ваших и OKX кошельков**

    Создает файл JSON, где привязываются ваши адреса к кошелькам OKX. Сделал для вашей безопасности. Софт сопоставляет
    к каждой строке в `CEX address` эту же строку в `Private Key` и если вы ошиблись, то всегда можно проверить это в 
    файле `cex_withdraw_list.json`, во избежания пересечений кошельков.

4. **✅Проверка всех прокси на работоспособность**

    Быстрая проверка прокси(реально быстрая, как с цепи срывается)

5. **📊Получение статистики для каждого аккаунта**

    Практически моментальное получение всей статистики по аккаунтам, даже если их больше 100 штук(не забудьте про прокси). Сделаны все необходимые
    поля.


## 📄Ввод своих данных

### Все нужные данные необходимо указать в таблицу `accounts_data` в папке `/data`. Для каждого проекта необходим свой отдельный в лист. 
   1. **Name** - имена ваших аккаунтов, каждое название должно быть уникальным
   2. **Private Key** - приватные ключи от кошельков
   3. **Proxy** - прокси для каждого аккаунта. Если их будет меньше, софт будет брать их по кругу. Если прокси мобильные, то можно указать просто одну проксю.
   4. **CEX address** - адреса пополнения CEX. Для каждого кошелька необходимо указать адрес, иначе вывод не сработает.

Вы можете установить пароль на вашу таблицу и включить настройку `EXCEL_PASSWORD = True`. При активации пароля, софт будет требовать его ввести для дальнейшей работы. Полезно при работе на сервере.

## ⚙️Настройка софта

>Крайне рекомендую ознакомиться с этой **[статьей](https://teletype.in/@realaskaer/attackmachine)**, с ее помощью вы сможете настроить любую деталь в софте.

Все настройки вынесены в файл `settings.py`. Заходим в него и видим подробное описание каждого раздела.
Самые важные настройки продублирую здесь. 

1. Раздел `API KEYS`. Получите все API ключи. В разделе есть ссылки на сайты, где это нужно сделать
2. Раздел `GENERAL SETTINGS`. Внимательно прочитайте все описания и проставьте необходимые значения
3. Далее сверху вниз настройте все модули. К каждому модулю есть описание

## 🛠️Установка и запуск проекта

> Устанавливая проект, вы принимаете риски использования софта для добывания денег(потерять жопу, деньги, девственность).

Как только вы скачаете проект, **убедитесь**, что у вас Python 3.10.11

Установка проекта

```bash
  git clone https://github.com/realaskaer/EthMachine.git
```

Для установки необходимых библиотек, пропишите в консоль

```bash
  pip install -r requirements.txt
```

Запуск проекта

```bash
  cd ethmachine
  python main.py
```

## 🔗 Ссылки на установку Python и PyCharm

 - [Установка PyCharm](https://www.jetbrains.com/pycharm/download/?section=windows)
 - [Установка Python](https://www.python.org/downloads/windows/) (Вам нужна версия 3.10.11)

## 🧾FAQ

#### Есть ли дрейнер в софте?

> Нет, но перед запуском любого софта, необходимо его проверять 

#### Что делать, если ничего работает?

> Сначала, прочитать README, если не получилось с первого раза, попытаться еще раз.
