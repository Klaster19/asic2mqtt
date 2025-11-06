#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для подключения к Antminer API
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
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
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
    
    print("Тестирование подключения к Antminer API")
    print("=" * 40)
    
    success = test_connection(miner_host)
    
    if success:
        print("\nТест подключения прошел успешно!")
        sys.exit(0)
    else:
        print("\nТест подключения не удался!")
        sys.exit(1)