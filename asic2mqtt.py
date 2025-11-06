#!/usr/bin/python3

import json
import paho.mqtt.client as mqtt
import time
import subprocess
import socket
import argparse
import logging
import sys
import os
from whatsminer import WhatsminerAccessToken, WhatsminerAPI
from antminer.base import BaseClient

# Настройка логгирования
def setup_logging(config_logging, verbose_level=0):
    """Настройка логгирования в файл и консоль"""
    # Создаем логгер
    logger = logging.getLogger('asic2mqtt')
    
    # Определяем уровень логгирования для консоли
    # Если указан параметр -v, используем его, иначе по умолчанию только ошибки
    if verbose_level > 0:
        # Преобразуем уровень verbose в уровень логгирования
        if verbose_level == 1:
            log_level = logging.WARNING
        elif verbose_level == 2:
            log_level = logging.INFO
        else:  # verbose_level >= 3
            log_level = logging.DEBUG
    else:
        # По умолчанию выводим только ошибки, если уровень не задан в конфиге
        level_str = config_logging.get('level', 'ERROR').upper()
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        log_level = log_level_map.get(level_str, logging.ERROR)
    
    logger.setLevel(logging.DEBUG)  # Устанавливаем максимальный уровень для логгера
    
    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Хендлер для записи в файл
    log_file = config_logging.get('file', '/var/log/asic2mqtt.log')
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # В файл пишем все логи
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Предупреждение: Не удалось создать файл логов {log_file}: {e}")
        print("Логи будут записываться только в консоль")
    
    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)  # Уровень для консоли зависит от настроек
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Загрузка конфигурации
def load_config(logger):
    """Загрузка конфигурации из файла"""
    # Определяем путь к конфигурационному файлу
    # Если задана переменная окружения CONFIG_PATH, используем её
    # Иначе используем config_secrets.json в текущей директории
    config_path = os.environ.get('CONFIG_PATH', 'config_secrets.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.debug(f"Конфигурация загружена успешно из {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Файл {config_path} не найден. Пожалуйста, создайте его на основе config_example.json")
        exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка в формате {config_path}. Проверьте файл конфигурации: {e}")
        exit(1)

# Функция для проверки доступности хоста
def is_host_available(host, timeout=1, logger=None):
    """Проверка доступности хоста с помощью ping"""
    try:
        output = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        result = output.returncode == 0
        if logger:
            logger.debug(f"Пинг хоста {host}: {'успешно' if result else 'неудачно'}")
        return result
    except Exception as e:
        if logger:
            logger.debug(f"Ошибка при пинге хоста {host}: {e}")
        return False

# Функция для получения данных от Whatsminer асика
def get_whatsminer_data(ip, token, logger=None):
    """Получение данных от Whatsminer асика"""
    try:
        if logger:
            logger.debug(f"Запрос данных summary от Whatsminer {ip}")
        summary_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd="summary")
        
        if logger:
            logger.debug(f"Запрос данных edevs от Whatsminer {ip}")
        edevs_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd="edevs")
        
        return summary_json, edevs_json
    except Exception as e:
        if logger:
            logger.error(f"Ошибка при получении данных от Whatsminer {ip}: {e}")
        return None, None

# Функция для получения данных от Antminer асика
def get_antminer_data(ip, username=None, password=None, logger=None):
    """Получение данных от Antminer асика"""
    try:
        if logger:
            logger.debug(f"Подключение к Antminer {ip}")
        client = BaseClient(ip)
        
        # Получаем статистику
        if logger:
            logger.debug(f"Запрос статистики от Antminer {ip}")
        stats = client.stats()
        
        # Получаем информацию об устройствах
        if logger:
            logger.debug(f"Запрос информации об устройствах от Antminer {ip}")
        devs = client.devs()
        
        return stats, devs
    except Exception as e:
        if logger:
            logger.error(f"Ошибка при получении данных от Antminer {ip}: {e}")
        return None, None

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Сбор статистики с асиков и отправка в MQTT')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Уровень детализации логов (-v, -vv, -vvv)')
    
    args = parser.parse_args()
    
    # Загрузка конфигурации
    config = load_config(logging.getLogger('asic2mqtt'))
    
    # Получение конфигурации логгирования
    config_logging = config.get('logging', {})
    
    # Настройка логгирования
    logger = setup_logging(config_logging, args.verbose)
    logger.info("Запуск скрипта сбора статистики с асиков")
    
    # Получение конфигурации асиков
    asics = config.get('asics', {})
    mqtt_config = config.get('mqtt', {})
    
    # Конфигурация MQTT
    broker_address = mqtt_config.get('broker_address', 'localhost')
    broker_port = mqtt_config.get('broker_port', 1883)
    mqtt_user = mqtt_config.get('username', '')
    mqtt_password = mqtt_config.get('password', '')
    
    # Создание клиента MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if mqtt_user and mqtt_password:
        client.username_pw_set(mqtt_user, mqtt_password)
    
    # Подключение к MQTT Брокеру
    try:
        client.connect(broker_address, broker_port, 60)
        logger.info(f"Подключено к MQTT брокеру {broker_address}:{broker_port}")
    except Exception as e:
        logger.error(f"Ошибка подключения к MQTT брокеру: {e}")
        exit(1)
    
    # Цикл для публикации сообщений
    try:
        while True:
            # Обработка каждого асика из конфигурации
            for asic_name, asic_config in asics.items():
                ip = asic_config.get('ip')
                topic = asic_config.get('topic')
                username = asic_config.get('username')
                password = asic_config.get('password')
                
                if not ip or not topic:
                    logger.warning(f"Неполная конфигурация для асика {asic_name}")
                    continue
                
                # Проверка доступности асика
                if not is_host_available(ip, logger=logger):
                    logger.warning(f"Асик {asic_name} ({ip}) недоступен")
                    continue
                
                logger.info(f"Обработка асика {asic_name} ({ip})")
                
                # Определяем тип асика по имени или другим признакам
                if 'whatsminer' in asic_name.lower():
                    # Работа с Whatsminer асиком
                    try:
                        token = WhatsminerAccessToken(ip_address=ip)
                        summary_data, edevs_data = get_whatsminer_data(ip, token, logger)
                        
                        if summary_data:
                            message = json.dumps(summary_data)
                            client.publish(f"{topic}/summary", message)
                            logger.debug(f"Отправлены данные summary для {asic_name}")
                        
                        if edevs_data:
                            message = json.dumps(edevs_data)
                            client.publish(f"{topic}/edevs", message)
                            logger.debug(f"Отправлены данные edevs для {asic_name}")
                    except Exception as e:
                        logger.error(f"Ошибка при работе с Whatsminer {asic_name}: {e}")
                
                elif 'antminer' in asic_name.lower():
                    # Работа с Antminer асиком
                    try:
                        stats_data, devs_data = get_antminer_data(ip, username, password, logger)
                        
                        if stats_data:
                            message = json.dumps(stats_data)
                            client.publish(f"{topic}/stats", message)
                            logger.debug(f"Отправлены данные stats для {asic_name}")
                        
                        if devs_data:
                            message = json.dumps(devs_data)
                            client.publish(f"{topic}/devs", message)
                            logger.debug(f"Отправлены данные devs для {asic_name}")
                    except Exception as e:
                        logger.error(f"Ошибка при работе с Antminer {asic_name}: {e}")
                
                time.sleep(1)  # Небольшая пауза между запросами к разным асикам
            
            logger.info("Цикл завершен, ожидание 5 секунд...")
            time.sleep(5)  # Ожидание 5 секунд перед следующим циклом
            
    except KeyboardInterrupt:
        logger.info("Скрипт остановлен пользователем.")
    
    # Отключение от MQTT Брокера
    client.disconnect()
    logger.info("Отключено от MQTT брокера")

if __name__ == "__main__":
    main()
