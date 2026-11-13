## Установка GNS3 и базовая настройка

## Установка и настройка GNS3

Установка среды выполнена успешно.
![app](pic/image8.jpg)

GNS3 GUI работает в Windows и подключается к GNS3 VM в VirtualBox. Для настройки GNS3 VM был использован .ova file (Import Appliance)

![GNS VM](pic/image1.png)
![GNS VM](pic/image2.png)

Успешно создала проект:
Создание нового проекта представлено на рисунке 3:

![new project](pic/image3.png)

 В составе GNS3 VM обнаружен QEMU версии 8.2.2, аппаратное ускорение KVM доступно. Компонент Dynamips установлен в составе GNS3 и успешно проходит проверку настроек.

![dynamips](pic/image4.png)

Параметры QEMU Template SONiC представлены на рисунке 5:

![sonic](pic/image5.png)

## Тестовый проект


В качестве тестового проекта были настроены 2 VPCS и Ethernet switch между ними:
![test_project](pic/image6.png)


Дали IP 

PC1: `ip 10.10.0.1`
PC2: `ip 10.10.0.1`

и проверяем сеть:
![check](pic/image7.png)

Сеть работает.

Сохраняемся `save`.