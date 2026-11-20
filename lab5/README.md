# Лабораторная работа №5 — MikroTik CHR как vCPE

## Параметры

| Параметр | Значение |
| --- | --- |
| ИСУ | 409303 |
| `STUDENT` | `panina` |
| `N` | `3` |
| ЦОД | `10.3.100.0/24`, шлюз SONiC `10.3.100.1` |
| DC ↔ HQ | `10.3.1.0/30`, SONiC `.1`, HQ `.2` |
| WAN HQ | `100.64.1.0/30`, ISP `.1`, HQ `.2` |
| WAN филиала | `100.64.2.0/30`, ISP `.1`, BR `.2` |
| Филиал | `10.3.200.0/24`, шлюз BR `10.3.200.1` |
| WireGuard | `10.3.254.0/30`, HQ `.1`, BR `.2` |
| WireGuard UDP | `13003` |
| AS SONiC / HQ | `65003` / `65103` |
| Management | `10.105.3.0/24` |

## Топология

```text
srv1 10.3.100.10 — dc1/SONiC — eBGP — hq/MikroTik — isp — br/MikroTik — pcb 10.3.200.10
                                  \________ WireGuard 10.3.254.0/30 ________/
```

`lab5.clab.yml` задаёт имена и management-адреса узлов явно. Образ SONiC собирается из официального `docker-sonic-vs` артефакта ветки `202511` с shims из материалов курса. Образ RouterOS `vrnetlab/mikrotik_routeros:7.23.8` собирается локально скриптом `images/build-mikrotik.sh` из CHR-диска, скачанного с MikroTik. В этой среде официальный контейнер `mikrotik/chr:7.23.8` не запускает даже `/bin/sh` (`exec format error`), поэтому используется вариант vrnetlab из задания.

## Запуск в WSL

```bash
cd /mnt/c/Users/79525/network_functions_virtualization/lab5
sh images/build-sonic-course.sh
sh images/build-mikrotik.sh
containerlab deploy -t lab5.clab.yml
sh scripts/dc1.sh
read -rsp 'RouterOS password: ' ROS_PASS; export ROS_PASS; echo
python3 scripts/configure-routeros.py
sh scripts/collect-evidence.sh
```

Если `containerlab inspect` показывает узлы как `exited`, выполните `containerlab redeploy -t lab5.clab.yml`, дождитесь `Startup complete` для `hq` и `br`, затем повторно запустите `sh scripts/dc1.sh` и `python3 scripts/configure-routeros.py`. Полный redeploy заново применяет адреса Linux-узлов из `exec` в topology и восстанавливает все data links. `containerlab deploy` после частичного ручного старта может пересоздать только часть узлов и не повторить команды инициализации Linux-контейнеров.

Если `lab-tools:1.0` ещё не собран, используйте Dockerfile из `../lab4/images/lab-tools`:

```bash
docker build -t lab-tools:1.0 ../lab4/images/lab-tools
```

Скрипт `configure-routeros.py` задаёт персональные имена, маршруты, eBGP, NAT, WireGuard и firewall. Пароль передаётся через окружение и не записывается в репозиторий. Он использует management-канал CHR внутри контейнера vrnetlab; SSH на `ether1` остаётся доступен через отдельный management-маршрут.

`collect-evidence.sh` проверяет связность и REST, воспроизводит заблокированную WAN-пробу с последующим удалением временного маршрута и сохраняет выводы в `evidence/`. Для финального краткого вывода используйте:

```bash
sh scripts/final-check.sh
```

Настройка SONiC и FRR также доступна отдельно:

```bash
sh scripts/dc1.sh
```

На HQ и BR публичные ключи получаются скриптом из RouterOS. Приватные ключи создаются и хранятся внутри CHR; файлы `/export terse` в `configs/` их не содержат.

## Проверенные результаты

Проверено на работающей топологии Containerlab в WSL:

| Проверка | Результат | Скриншот |
| --- | --- | --- |
| Containerlab | Все шесть узлов running; оба CHR healthy | [01-topology.png](evidence/screenshots/01-topology.png) |
| eBGP | Established между `10.3.1.1` / AS65003 и `10.3.1.2` / AS65103 | [04-hq-bgp-session.png](evidence/screenshots/04-hq-bgp-session.png) |
| BGP в SONiC | Установлены `0.0.0.0/0` и `10.3.200.0/24` через `10.3.1.2` | [05-frr-summary.png](evidence/screenshots/05-frr-summary.png), [06-frr-routes.png](evidence/screenshots/06-frr-routes.png) |
| NAT | HTTP 200; сервер ISP зарегистрировал источник `100.64.1.2` | [07-nat-isp-log.png](evidence/screenshots/07-nat-isp-log.png) |
| WireGuard | Свежий handshake на UDP/13003; PCB → SRV1: 3/3 ICMP | [09-wireguard-ping.png](evidence/screenshots/09-wireguard-ping.png) |
| Firewall | ISP → `10.3.100.10`: 0/2 ответов; `forward-default-deny`: 4 пакета / 336 байт накопительно | [08-firewall-deny.png](evidence/screenshots/08-firewall-deny.png) |
| REST | GET, PUT, PATCH и DELETE завершены; удаление вернуло HTTP 204 | [10-wg-capture-rest.png](evidence/screenshots/10-wg-capture-rest.png), [11-rest-put.png](evidence/screenshots/11-rest-put.png), [12-rest-patch-delete.png](evidence/screenshots/12-rest-patch-delete.png) |
| Версия и лицензия CHR | RouterOS 7.23.8, лицензия Free на HQ и BR | [02-br-license.png](evidence/screenshots/02-br-license.png), [03-hq-license.png](evidence/screenshots/03-hq-license.png) |
| Экспорты | `configs/hq.rsc`, `configs/br.rsc`, `configs/dc1-frr.conf`, `configs/dc1.sh` | — |

Основные выводы находятся в `evidence/final-output.txt`; подробные логи проверок и захват внешних UDP-заголовков — в `evidence/`.
Итоговый отчёт: [PDF](output/pdf/ЛР5_Панина_АС_409303.pdf) и [DOCX](output/docx/ЛР5_Панина_АС_409303.docx); исходный текст: `lab5_report.md`.
Скриншоты отчёта лежат в `evidence/screenshots/`; ссылки на конкретные файлы приведены в таблице результатов. Приложение Б PDF содержит текст сохранённого финального вывода, а не скриншот.

## Фильтр HQ

Правила идут сверху вниз; `established,related` пропускает ответы на разрешённые соединения.

| Цепочка | Правило | Назначение |
| --- | --- | --- |
| input | accept established,related | Ответы и связанные соединения к vCPE |
| input | drop invalid | Отброс некорректных состояний |
| input | accept ICMP | Диагностика маршрутизатора |
| input | accept `ether1` | Управление Containerlab |
| input | accept TCP/179 на `ether2` | eBGP от SONiC |
| input | accept UDP/13003 | WireGuard от филиала |
| input | drop `ether3` | Запрет прочего входящего трафика с WAN |
| input | drop all | Запрет остального трафика к самому HQ |
| forward | accept established,related | Ответный трафик разрешённых сессий |
| forward | drop invalid | Отброс некорректных состояний |
| forward | accept `ether2` → `ether3` | Интернет из ЦОД; source NAT на WAN |
| forward | accept `wg-br` → `ether2` | Филиал в ЦОД |
| forward | accept `ether2` → `wg-br` | ЦОД в филиал |
| forward | drop all | Остальной транзит запрещён |

Филиальный NAT выполняется на BR при выходе через `ether2`.

## REST

В лабораторном изолированном сегменте REST включается командой `/ip service set www disabled=no`. Запустите `scripts/rest-demo.sh` с `ROS_PASS=...`; пароль не хранится в Git.

## Вопросы для защиты

- CHR требует аппаратной виртуализации, поскольку RouterOS загружается как полноценная QEMU/KVM VM; SONiC здесь — контейнер на ядре Linux.
- Бесплатная CHR ограничивает исходящую скорость интерфейса до 1 Мбит/с, поэтому скорость туннеля не отражает производительность сервера.
- Management-маршрут ядра имеет меньшую административную дистанцию, чем BGP default, поэтому его удаляют, чтобы FRR установил полученный default в таблицу Linux.
- `default-originate=if-installed` рекламирует default только при наличии рабочего default-маршрута; `always` может объявить недействующий выход.
- Возвратные пакеты проходят по состоянию `established,related`; для новых соединений из WAN через HQ нет разрешающего forward-правила.
- Провайдер видит внешние IP/UDP-порт WireGuard и объём/время пакетов; внутренние адреса `10.3.x.x` находятся внутри зашифрованного туннеля.
- Экспорт не должен включать приватный ключ WireGuard. Секреты хранят вне Git в менеджере секретов либо в защищённом локальном хранилище.
