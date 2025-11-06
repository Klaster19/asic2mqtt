#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Подробный тестовый скрипт для подключения к Antminer API
"""

import sys
import traceback
import json
from antminer.base import BaseClient

def print_dict_structure(data, indent=0):
    """Вывод структуры словаря"""
    if isinstance(data, dict):
        for key, value in data.items():
            print("  " * indent + f"{key}: {type(value).__name__}")
            if isinstance(value, dict):
                print_dict_structure(value, indent + 1)
            elif isinstance(value, list):
                print("  " * (indent + 1) + f"List of {len(value)} items")
                if len(value) > 0 and isinstance(value[0], dict):
                    print("  " * (indent + 1) + "First item structure:")
                    print_dict_structure(value[0], indent + 2)
    elif isinstance(data, list):
        print("  " * indent + f"List of {len(data)} items")
        if len(data) > 0:
            print("  " * indent + f"First item type: {type(data[0]).__name__}")

def test_connection(host):
    """Тест подключения к асику"""
    print(f"Попытка подключения к асику по адресу: {host}")
    
    try:
        # Создаем клиент
        client = BaseClient(host)
        
        # Получаем информацию о версии
        print("\n1. Запрос информации о версии...")
        version_info = client.version()
        print(f"Информация о версии: {version_info}")
        
        # Получаем статистику
        print("\n2. Запрос статистики...")
        try:
            stats = client.stats()
            print(f"Статистика получена успешно")
            print("Структура статистики:")
            print_dict_structure(stats)
            
            # Выводим содержимое STATS подробнее
            if 'STATS' in stats and len(stats['STATS']) > 0:
                print("\nСодержимое первого элемента STATS:")
                first_stat = stats['STATS'][0]
                for key, value in first_stat.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            print("Продолжаем выполнение...")
        
        # Получаем информацию об устройствах
        print("\n3. Запрос информации об устройствах...")
        try:
            devs = client.devs()
            print(f"Информация об устройствах получена успешно")
            print("Структура информации об устройствах:")
            print_dict_structure(devs)
            
            # Выводим содержимое DEVS подробнее
            if 'DEVS' in devs and len(devs['DEVS']) > 0:
                print("\nСодержимое первого элемента DEVS:")
                first_dev = devs['DEVS'][0]
                for key, value in first_dev.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Ошибка при получении информации об устройствах: {e}")
            print("Продолжаем выполнение...")
        
        # Получаем информацию о пулах
        print("\n4. Запрос информации о пулах...")
        try:
            pools = client.pools()
            print(f"Информация о пулах получена успешно")
            print("Структура информации о пулах:")
            print_dict_structure(pools)
            
            # Выводим содержимое POOLS подробнее
            if 'POOLS' in pools and len(pools['POOLS']) > 0:
                print("\nСодержимое первого элемента POOLS:")
                first_pool = pools['POOLS'][0]
                for key, value in first_pool.items():
                    print(f"  {key}: {value}")
        except Exception as e:
            print(f"Ошибка при получении информации о пулах: {e}")
            print("Продолжаем выполнение...")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при подключении к асику: {e}")
        print("Трассировка:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Адрес асика для тестирования
    miner_host = "192.168.3.73"
    
    print("Подробное тестирование подключения к Antminer API")
    print("=" * 50)
    
    success = test_connection(miner_host)
    
    if success:
        print("\nТест подключения прошел успешно!")
        sys.exit(0)
    else:
        print("\nТест подключения не удался!")
        sys.exit(1)