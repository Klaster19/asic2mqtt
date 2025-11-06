#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Расширенный тестовый скрипт для подключения к Antminer API
"""

import sys
import traceback
from antminer.base import BaseClient

def test_connection(host):
    """Тест подключения к асику"""
    print(f"Попытка подключения к асику по адресу: {host}")
    
    try:
        # Создаем клиент
        client = BaseClient(host)
        
        # Получаем информацию о версии
        print("Запрос информации о версии...")
        version_info = client.version()
        print(f"Информация о версии: {version_info}")
        
        # Получаем статистику
        print("Запрос статистики...")
        try:
            stats = client.stats()
            print(f"Статистика получена успешно")
            print(f"Ключи статистики: {list(stats.keys()) if isinstance(stats, dict) else 'Не словарь'}")
            
            # Выводим немного подробной информации из статистики
            if 'STATS' in stats and len(stats['STATS']) > 0:
                stat_info = stats['STATS'][0]
                print(f"ID устройства: {stat_info.get('ID', 'N/A')}")
                print(f"Температура чипов: {stat_info.get('Temperature', 'N/A')}")
                print(f"Частота: {stat_info.get('Frequency', 'N/A')}")
                print(f"Скорость хэширования: {stat_info.get('MHS 5s', 'N/A')}")
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            print("Продолжаем выполнение...")
        
        # Получаем информацию об устройствах
        print("Запрос информации об устройствах...")
        try:
            devs = client.devs()
            print(f"Информация об устройствах получена успешно")
            print(f"Ключи информации об устройствах: {list(devs.keys()) if isinstance(devs, dict) else 'Не словарь'}")
        except Exception as e:
            print(f"Ошибка при получении информации об устройствах: {e}")
            print("Продолжаем выполнение...")
        
        # Получаем информацию о пулах
        print("Запрос информации о пулах...")
        try:
            pools = client.pools()
            print(f"Информация о пулах получена успешно")
            print(f"Ключи информации о пулах: {list(pools.keys()) if isinstance(pools, dict) else 'Не словарь'}")
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
    
    print("Расширенное тестирование подключения к Antminer API")
    print("=" * 50)
    
    success = test_connection(miner_host)
    
    if success:
        print("\nТест подключения прошел успешно!")
        sys.exit(0)
    else:
        print("\nТест подключения не удался!")
        sys.exit(1)