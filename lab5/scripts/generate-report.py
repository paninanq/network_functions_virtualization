#!/usr/bin/env python3
"""Build the Russian lab report PDF from the verified lab artifacts."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    Image as ReportImage,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


LAB = Path(__file__).resolve().parents[1]
OUT = LAB / "output" / "pdf" / "ЛР5_Панина_409303.pdf"
FONTS = Path(r"C:\Windows\Fonts")

pdfmetrics.registerFont(TTFont("ArialLab", str(FONTS / "arial.ttf")))
pdfmetrics.registerFont(TTFont("ArialLab-Bold", str(FONTS / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("ConsolasLab", str(FONTS / "consola.ttf")))
pdfmetrics.registerFont(TTFont("ConsolasLab-Bold", str(FONTS / "consolab.ttf")))

NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#087F76")
PALE = colors.HexColor("#EAF1F5")
PALE_TEAL = colors.HexColor("#E6F4F1")
INK = colors.HexColor("#24313C")
MUTED = colors.HexColor("#5F6F7B")
LINE = colors.HexColor("#D6E0E7")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="LabTitle", fontName="ArialLab-Bold", fontSize=23, leading=29,
    textColor=NAVY, alignment=TA_CENTER, spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="LabSubtitle", fontName="ArialLab", fontSize=13, leading=18,
    textColor=TEAL, alignment=TA_CENTER, spaceAfter=13,
))
styles.add(ParagraphStyle(
    name="SectionLab", fontName="ArialLab-Bold", fontSize=16, leading=20,
    textColor=NAVY, spaceBefore=2, spaceAfter=9, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="SubLab", fontName="ArialLab-Bold", fontSize=11, leading=14,
    textColor=TEAL, spaceBefore=8, spaceAfter=5, keepWithNext=True,
))
styles.add(ParagraphStyle(
    name="BodyLab", fontName="ArialLab", fontSize=9.2, leading=13,
    textColor=INK, spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="SmallLab", fontName="ArialLab", fontSize=7.7, leading=10,
    textColor=MUTED, spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="CellLab", fontName="ArialLab", fontSize=8, leading=10.2,
    textColor=INK,
))
styles.add(ParagraphStyle(
    name="CellHeadLab", fontName="ArialLab-Bold", fontSize=8, leading=10.2,
    textColor=WHITE,
))
styles.add(ParagraphStyle(
    name="CodeLab", fontName="ConsolasLab", fontSize=6.2, leading=7.5,
    textColor=INK, leftIndent=0, rightIndent=0, spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="CalloutLab", fontName="ArialLab-Bold", fontSize=9.3, leading=13,
    textColor=TEAL, backColor=PALE_TEAL, borderColor=TEAL,
    borderWidth=0.6, borderPadding=8, spaceBefore=5, spaceAfter=8,
))


def read(rel: str) -> str:
    return (LAB / rel).read_text(encoding="utf-8", errors="replace").strip()


def p(text: str, style: str = "BodyLab") -> Paragraph:
    return Paragraph(text, styles[style])


def code(text: str, max_len: int = 108) -> Preformatted:
    return Preformatted(text.rstrip(), styles["CodeLab"], maxLineLength=max_len)


def make_table(rows, widths, header=True, font_size=8, repeat_rows=1):
    table = Table(rows, colWidths=widths, repeatRows=repeat_rows if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [WHITE, PALE]),
    ]
    if header:
        commands.extend([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ])
    table.setStyle(TableStyle(commands))
    return table


class TopologyDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 511
        self.height = 151

    def draw(self):
        c = self.canv
        nodes = [
            ("srv1", "10.3.100.10", "#3B6D8C"),
            ("dc1 / SONiC", "10.3.100.1", "#087F76"),
            ("hq / CHR", "10.3.1.2", "#17324D"),
            ("ISP", "198.51.100.1", "#687A89"),
            ("br / CHR", "10.3.200.1", "#17324D"),
            ("pcb", "10.3.200.10", "#3B6D8C"),
        ]
        box_w, box_h, gap, y0 = 67, 36, 21, 77
        xs = [2 + i * (box_w + gap) for i in range(6)]
        link_labels = [
            ("srv1 LAN", "10.3.100.0/24"), ("eBGP", "10.3.1.0/30"),
            ("HQ WAN", "100.64.1.0/30"), ("BR WAN", "100.64.2.0/30"),
            ("Branch LAN", "10.3.200.0/24"),
        ]
        c.setStrokeColor(MUTED)
        c.setLineWidth(1.1)
        for i in range(5):
            x1, x2 = xs[i] + box_w, xs[i + 1]
            c.line(x1, y0 + box_h / 2, x2, y0 + box_h / 2)
            center = (x1 + x2) / 2
            label_y = 119 if i % 2 == 0 else 133
            c.setFillColor(TEAL if i == 1 else MUTED)
            c.setFont("ArialLab-Bold", 5.6)
            c.drawCentredString(center, label_y + 8, link_labels[i][0])
            c.setFont("ConsolasLab", 5.5)
            c.drawCentredString(center, label_y, link_labels[i][1])
        for x, (name, address, color_hex) in zip(xs, nodes):
            c.setFillColor(colors.HexColor(color_hex))
            c.roundRect(x, y0, box_w, box_h, 5, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("ArialLab-Bold", 7.4)
            c.drawCentredString(x + box_w / 2, y0 + 21, name)
            c.setFont("ConsolasLab", 6.2)
            c.drawCentredString(x + box_w / 2, y0 + 8, address)
        hq_center = xs[2] + box_w / 2
        br_center = xs[4] + box_w / 2
        c.saveState()
        c.setStrokeColor(TEAL)
        c.setDash(3, 2)
        c.setLineWidth(1.3)
        c.line(hq_center, y0, hq_center, 28)
        c.line(hq_center, 28, br_center, 28)
        c.line(br_center, 28, br_center, y0)
        c.restoreState()
        c.setFillColor(TEAL)
        c.setFont("ArialLab-Bold", 7.1)
        c.drawCentredString((hq_center + br_center) / 2, 12, "WireGuard 10.3.254.0/30 / UDP 13003")


def page_chrome(canvas, doc):
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(42, A4[1] - 31, A4[0] - 42, A4[1] - 31)
        canvas.setFont("ArialLab-Bold", 7.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(42, A4[1] - 24, "ЛР5 | MikroTik CHR как vCPE")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(42, 29, A4[0] - 42, 29)
    canvas.setFillColor(MUTED)
    canvas.setFont("ArialLab", 7.2)
    canvas.drawString(42, 17, "STUDENT=panina | ИСУ 409303 | WSL / Containerlab")
    canvas.drawRightString(A4[0] - 42, 17, f"Стр. {page}")
    canvas.restoreState()


def build_story():
    story = []

    # Cover and topology.
    story += [Spacer(1, 22 * mm), p("ЛАБОРАТОРНАЯ РАБОТА №5", "LabTitle")]
    story += [p("Мультивендорная корпоративная сеть", "LabSubtitle")]
    story += [p("MikroTik CHR как виртуальный пограничный маршрутизатор vCPE", "LabSubtitle")]
    student_rows = [
        [p("Параметр", "CellHeadLab"), p("Значение", "CellHeadLab")],
        [p("Фамилия / STUDENT", "CellLab"), p("panina", "CellLab")],
        [p("Номер ИСУ", "CellLab"), p("409303", "CellLab")],
        [p("Персональный номер N", "CellLab"), p("3", "CellLab")],
        [p("Имя / инициалы", "CellLab"), p("не указаны в исходных данных", "CellLab")],
        [p("Дата выполнения", "CellLab"), p("19-20 ноября 2026, MSK", "CellLab")],
    ]
    story += [make_table(student_rows, [175, 325]), Spacer(1, 12)]
    story += [p("Схема стенда", "SubLab"), TopologyDiagram(), Spacer(1, 10)]
    result_rows = [
        [p("eBGP", "CellHeadLab"), p("WireGuard", "CellHeadLab"), p("NAT / firewall", "CellHeadLab")],
        [p("Established; в SONiC получены default и маршрут филиала", "CellLab"),
         p("Handshake активен; PCB -> SRV1: 3/3", "CellLab"),
         p("HTTP 200; внешний WAN probe отброшен", "CellLab")],
    ]
    story += [make_table(result_rows, [170, 165, 165]), Spacer(1, 8)]
    story += [p("Итог: все шесть узлов Containerlab запущены; оба CHR healthy. Подробные журналы и конфигурации приложены к каталогу lab5.", "CalloutLab")]
    story += [PageBreak()]

    # Address plan and platform.
    story += [p("1. Параметры и адресный план", "SectionLab")]
    address_rows = [[p("Сегмент / параметр", "CellHeadLab"), p("Адреса и назначение", "CellHeadLab")]]
    address_rows += [
        [p("ЦОД", "CellLab"), p("10.3.100.0/24; шлюз dc1 10.3.100.1; сервер srv1 10.3.100.10", "CellLab")],
        [p("dc1-HQ", "CellLab"), p("10.3.1.0/30; dc1 10.3.1.1 / AS65003; HQ 10.3.1.2 / AS65103", "CellLab")],
        [p("WAN головного офиса", "CellLab"), p("100.64.1.0/30; ISP 100.64.1.1; HQ 100.64.1.2", "CellLab")],
        [p("WAN филиала", "CellLab"), p("100.64.2.0/30; ISP 100.64.2.1; BR 100.64.2.2", "CellLab")],
        [p("Филиал", "CellLab"), p("10.3.200.0/24; BR 10.3.200.1; pcb 10.3.200.10", "CellLab")],
        [p("WireGuard", "CellLab"), p("10.3.254.0/30; HQ .1; BR .2; UDP/13003", "CellLab")],
        [p("Management", "CellLab"), p("10.105.3.0/24; management IP узлов назначены в topology", "CellLab")],
    ]
    story += [make_table(address_rows, [145, 365])]
    story += [p("Среда и виртуализация", "SubLab")]
    story += [p("WSL Ubuntu 24.04, Containerlab 0.83.0, Docker 29.1.3. SONiC работает как Linux-контейнер с FRR. CHR загружается как отдельная RouterOS VM в QEMU/KVM, поэтому нужен доступный /dev/kvm. Для заданного kind mikrotik_ros локально собран vrnetlab-образ из официального CHR-диска 7.23.8.")]
    story += [p("Оба CHR: RouterOS 7.23.8 long-term, архитектура x86_64, 1 vCPU, 256 MiB RAM, лицензия Free. Бесплатная CHR ограничивает исходящую скорость каждого интерфейса до 1 Mbit/s; пропускная способность не использовалась как оценка реального оборудования.")]
    story += [p("Задание 1.2", "SubLab")]
    story += [p("CHR требует аппаратную виртуализацию, так как RouterOS запускается как полноценная QEMU/KVM-машина. SONiC в этом стенде использует контейнерное ядро хоста и потому не запускает отдельный гостевой kernel. Лимит Free CHR в 1 Mbit/s на egress-интерфейс исказил бы скоростные измерения.")]
    story += [p("Контейнерный kind и модель запуска описаны в <link href='https://containerlab.dev/manual/kinds/vr-ros/' color='#087F76'>документации Containerlab</link>; ограничения CHR - в <link href='https://help.mikrotik.com/docs/spaces/ROS/pages/18350234/Cloud+Hosted+Router+CHR' color='#087F76'>документации MikroTik</link>.", "SmallLab")]
    story += [PageBreak()]

    # BGP proof.
    story += [p("2. Межвендорный eBGP", "SectionLab")]
    story += [p("RouterOS HQ настроен в AS65103, SONiC/FRR - в AS65003. Соседство установлено между 10.3.1.2 и 10.3.1.1. На dc1 удалён management default через eth0; FRR установил полученный BGP default в FIB.")]
    story += [p("FRR show bgp summary", "SubLab"), code(read("evidence/dc1-bgp-summary.txt"), 105)]
    story += [p("Установленные BGP-маршруты на SONiC", "SubLab"), code(read("evidence/dc1-bgp-routes.txt"), 110)]
    hq_final = read("evidence/hq-final.txt")
    bgp_line = next((line for line in hq_final.splitlines() if 'name="to-dc-1"' in line), "BGP session established")
    handshake = next((line.strip() for line in hq_final.splitlines() if "last-handshake=" in line), "last-handshake present")
    story += [p("RouterOS session: " + escape(bgp_line.strip()), "SmallLab")]
    story += [p("Задание 3.1", "SubLab")]
    story += [p("Management default имеет приоритет над внешним BGP default: маршрут K из ядра предпочитается B-маршруту. После удаления default через eth0 маршрут 0.0.0.0/0 от HQ выбран и установлен; в FRR он помечен B>*.")]
    story += [p("Задание 3.4", "SubLab")]
    story += [p("output.default-originate=if-installed анонсирует default только при наличии установленного маршрута выхода. Вариант always мог бы объявлять default при сломанном или отсутствующем upstream.")]
    story += [p("Настройка BGP соответствует синтаксису RouterOS 7: <link href='https://help.mikrotik.com/docs/spaces/ROS/pages/328220/BGP' color='#087F76'>MikroTik BGP</link>.", "SmallLab")]
    story += [PageBreak()]

    # NAT and firewall.
    story += [p("3. NAT и межсетевой экран HQ", "SectionLab")]
    story += [p("Для выхода из ЦОД включён masquerade на WAN ether3. Сервер ISP ответил HTTP 200, а его журнал зарегистрировал источник 100.64.1.2 - WAN-адрес HQ.")]
    story += [code(read("evidence/nat-http.txt") + "\n" + read("evidence/nat-isp-log.txt").splitlines()[-1], 105)]
    story += [p("Порядок firewall-правил", "SubLab")]
    firewall_rows = [[p("Цепь", "CellHeadLab"), p("Правило", "CellHeadLab"), p("Назначение", "CellHeadLab")]]
    firewall = [
        ("input", "accept established,related", "Ответы к самому HQ"),
        ("input", "drop invalid", "Отброс некорректных состояний"),
        ("input", "accept ICMP", "Диагностика HQ"),
        ("input", "accept ether1", "Управление Containerlab"),
        ("input", "accept ether2 TCP/179", "eBGP от dc1"),
        ("input", "accept UDP/13003", "WireGuard"),
        ("input", "drop ether3; drop all", "Запрет новых неразрешённых запросов к HQ"),
        ("forward", "accept established,related", "Ответы разрешённых транзитных сессий"),
        ("forward", "drop invalid", "Отброс некорректных состояний"),
        ("forward", "accept ether2 -> ether3", "ЦОД -> Интернет; вместе с NAT"),
        ("forward", "accept wg-br -> ether2", "Филиал -> ЦОД"),
        ("forward", "accept ether2 -> wg-br", "ЦОД -> филиал"),
        ("forward", "drop all", "Default deny для остального транзита"),
    ]
    for chain, rule, purpose in firewall:
        firewall_rows.append([p(chain, "CellLab"), p(rule, "CellLab"), p(purpose, "CellLab")])
    story += [make_table(firewall_rows, [60, 190, 260])]
    story += [p("Проверка WAN-атаки", "SubLab"), code(read("evidence/wan-attack.txt"), 110)]
    counter_lines = [line for line in hq_final.splitlines() if "forward-default-deny" in line or "forward  drop" in line]
    if counter_lines:
        story += [p("Счётчик final deny после двух проб: " + escape(" | ".join(counter_lines[-2:])), "SmallLab")]
    story += [p("Задание 4.3", "SubLab")]
    story += [p("Ответы на исходящий из ЦОД HTTP проходят как established,related. Новая сессия, начатая с WAN к внутреннему адресу, не подходит под разрешение ether2 -> ether3 и попадает в forward-default-deny.")]
    story += [PageBreak()]

    # WireGuard and REST.
    story += [p("4. Филиал, WireGuard и REST API", "SectionLab")]
    story += [p("Оба peer используют UDP/13003 и persistent-keepalive=25s. Туннельные сети: HQ 10.3.254.1/30, BR 10.3.254.2/30. HQ анонсирует 10.3.200.0/24 через BGP только при наличии статического маршрута через wg-br.")]
    story += [p("Handshake: " + escape(handshake) + ". Переданный трафик подтверждён RX/TX счётчиками peer и ping 10.3.200.10 -> 10.3.100.10 без потерь.")]
    story += [p("Внешние UDP-заголовки на провайдере", "SubLab"), code(read("evidence/isp-wg-capture.txt"), 110)]
    story += [p("Задание 5.4", "SubLab")]
    story += [p("Провайдер видит только WAN endpoints 100.64.1.2:13003 и 100.64.2.2:13003, направления пакетов, время и объём. В захвате нет адресов 10.3.x.x: они находятся внутри зашифрованных WireGuard-пакетов.")]
    story += [p("REST CRUD", "SubLab")]
    story += [p("GET прочитал identity, адреса и BGP session. PUT создал временную запись address-list, PATCH изменил комментарий, DELETE удалил запись с HTTP 204. Сервис www включён только в изолированной лабораторной management-сети; HTTP не предназначен для production.")]
    story += [code("GET /rest/system/identity -> hq-panina\nPUT /rest/ip/firewall/address-list -> created\nPATCH /rest/ip/firewall/address-list/{id} -> patched\nDELETE /rest/ip/firewall/address-list/{id} -> HTTP 204", 105)]
    story += [p("Задание 6.3", "SubLab")]
    story += [p("/export terse без show-sensitive не включает приватные ключи WireGuard. Экспорты HQ и BR сохранены в configs/; поиск по private-key/password не нашёл секретов. Секреты следует хранить вне Git в менеджере секретов или защищённом локальном хранилище.")]
    story += [p("Использованы официальные документы: <link href='https://help.mikrotik.com/docs/spaces/ROS/pages/69664792/WireGuard' color='#087F76'>WireGuard</link>, <link href='https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API' color='#087F76'>REST API</link>.", "SmallLab")]
    story += [PageBreak()]

    # Theory and artifact location.
    story += [p("5. Ответы для защиты", "SectionLab")]
    answers = [
        ("1.2 - виртуализация и лицензия", "CHR выполняется как полноценная QEMU/KVM VM и требует аппаратной виртуализации. SONiC здесь работает контейнером. Free CHR ограничивает egress каждого интерфейса до 1 Mbit/s, поэтому результаты throughput были бы ограничены лицензией."),
        ("3.1 - management default", "Маршрут K, полученный ядром через management, предпочтительнее BGP default. После удаления default через eth0 внешний BGP маршрут стал выбранным в FRR и Linux FIB."),
        ("3.4 - if-installed", "HQ рекламирует default только при наличии установленного upstream default. Это предотвращает анонс недействующего выхода."),
        ("4.3 - обратный трафик", "Connection tracking пропускает ответы как established,related; firewall не открывает новые WAN -> LAN сессии."),
        ("5.4 - что видит ISP", "Внешние IP endpoints и UDP/13003, длительность и объём обмена. Внутренние IP-пакеты скрыты шифрованием WireGuard."),
        ("6.3 - приватный ключ", "Обычный экспорт скрывает приватный ключ. Не включать show-sensitive в репозиторий; хранить секреты отдельно с контролем доступа и резервным копированием."),
    ]
    for title, answer in answers:
        story += [p(title, "SubLab"), p(answer)]
    story += [p("Репозиторий и статус", "SubLab")]
    story += [p("Настроенный origin: <link href='https://github.com/paninanq/network_functions_virtualization' color='#087F76'>github.com/paninanq/network_functions_virtualization</link>. Файлы lab5 собраны локально в текущем checkout и не отправлялись на remote.")]
    story += [p("Проверочные логи находятся в lab5/evidence/, экспортированные конфигурации - в lab5/configs/. Финальный краткий вывод сохранён в evidence/final-output.txt; он содержит фактический текст команд из WSL.", "CalloutLab")]
    story += [p("Основные источники", "SubLab")]
    sources = [
        "Containerlab kind vr-ros: https://containerlab.dev/manual/kinds/vr-ros/",
        "MikroTik CHR: https://help.mikrotik.com/docs/spaces/ROS/pages/18350234/Cloud+Hosted+Router+CHR",
        "MikroTik BGP: https://help.mikrotik.com/docs/spaces/ROS/pages/328220/BGP",
        "MikroTik WireGuard: https://help.mikrotik.com/docs/spaces/ROS/pages/69664792/WireGuard",
        "MikroTik REST API: https://help.mikrotik.com/docs/spaces/ROS/pages/47579162/REST+API",
        "Anuket RM, chapters 2 and 7: https://cntt.readthedocs.io/projects/rm/en/latest/chapters/",
    ]
    story += [code("\n".join(sources), 112)]
    story += [PageBreak()]

    # Exact final-check log as a textual appendix.
    story += [p("Приложение A. Финальный вывод WSL", "SectionLab")]
    story += [p("Лог получен непосредственно из WSL командами final-check.sh. Он содержит идентичность, состояние BGP/WireGuard, маршруты FRR, ping и HTTP-код ответа.")]
    story += [code(read("evidence/final-output.txt"), 108), PageBreak()]

    # User-provided terminal screenshots, grouped two per page.
    screenshot_items = [
        ("01-topology.png", "1. Containerlab: все шесть узлов running; оба CHR healthy."),
        ("02-br-license.png", "2. br-panina: версия RouterOS, ресурсы CHR и лицензия Free."),
        ("03-hq-license.png", "3. hq-panina: версия RouterOS, ресурсы CHR и лицензия Free."),
        ("04-hq-bgp-session.png", "4. BGP-сессия HQ: Established, сосед 10.3.1.1 / AS65003."),
        ("05-frr-summary.png", "5. FRR show bgp summary: сосед 10.3.1.2 / AS65103."),
        ("06-frr-routes.png", "6. FRR show ip route bgp: default и 10.3.200.0/24 через 10.3.1.2."),
        ("07-nat-isp-log.png", "7. NAT: HTTP 200; ISP видит исходный адрес HQ 100.64.1.2."),
        ("08-firewall-deny.png", "8. WAN probe теряется; на снимке показано начало статистики firewall. Полные счётчики находятся в evidence/hq-final.txt."),
        ("09-wireguard-ping.png", "9. Статистика peer WireGuard HQ и BR и ответы ping из филиала в ЦОД."),
        ("10-wg-capture-rest.png", "10. Захват внешнего UDP/13003 на ISP и REST GET."),
        ("11-rest-put.png", "11. REST PUT создал временную запись address-list; далее выполнен PATCH."),
        ("12-rest-patch-delete.png", "12. REST PATCH изменил запись, DELETE завершился HTTP 204."),
    ]
    story += [p("Приложение B. Скриншоты защиты", "SectionLab")]
    story += [p("Снимки экрана предоставлены пользователем и показывают команды и фактический вывод терминала WSL. Они сгруппированы по этапам лабораторной.")]
    screenshot_width = A4[0] - 84
    for index in range(0, len(screenshot_items), 2):
        if index:
            story.append(PageBreak())
        for filename, caption in screenshot_items[index:index + 2]:
            image_path = LAB / "evidence" / "screenshots" / filename
            screenshot = ReportImage(str(image_path))
            scale = min(screenshot_width / screenshot.imageWidth, 270 / screenshot.imageHeight)
            screenshot.drawWidth = screenshot.imageWidth * scale
            screenshot.drawHeight = screenshot.imageHeight * scale
            story += [screenshot, p(caption, "SmallLab"), Spacer(1, 5)]
    story += [PageBreak()]

    # Config exports.
    for title, rel in [
        ("Приложение C. RouterOS HQ - configs/hq.rsc", "configs/hq.rsc"),
        ("Приложение D. RouterOS BR - configs/br.rsc", "configs/br.rsc"),
        ("Приложение E. FRR - configs/dc1-frr.conf", "configs/dc1-frr.conf"),
        ("Приложение F. Повторное применение FRR - configs/dc1.sh", "configs/dc1.sh"),
    ]:
        story += [p(title, "SectionLab")]
        story += [p("Полный текст экспортированного файла. В RouterOS-экспорте приватные ключи отсутствуют.", "SmallLab")]
        story += [code(read(rel), 108), PageBreak()]

    return story


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4, rightMargin=42, leftMargin=42,
        topMargin=43, bottomMargin=39,
        title="Лабораторная работа 5 - MikroTik CHR как vCPE",
        author="STUDENT panina, ИСУ 409303",
        subject="Мультивендорная сеть SONiC, RouterOS, BGP, WireGuard, REST",
    )
    doc.build(build_story(), onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(OUT)


if __name__ == "__main__":
    main()
