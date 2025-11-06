#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки функциональности asic2mqtt.py без подключения к реальным устройствам
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_wm_functionality():
    """Тест функциональности asic2mqtt.py"""
    print("Тестирование функциональности asic2mqtt.py")
    print("=" * 40)
    
    # Имитируем зависимости
    with patch('subprocess.run') as mock_subprocess, \
         patch('paho.mqtt.client.Client') as mock_mqtt_client, \
         patch('whatsminer.WhatsminerAccessToken') as mock_whatsminer_token, \
         patch('whatsminer.WhatsminerAPI') as mock_whatsminer_api, \
         patch('antminer.base.BaseClient') as mock_antminer_client:
        
        # Настраиваем имитацию subprocess.run для проверки доступности хостов
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""
        
        # Настраиваем имитацию MQTT клиента
        mock_mqtt_instance = MagicMock()
        mock_mqtt_client.return_value = mock_mqtt_instance
        mock_mqtt_instance.connect.return_value = None
        
        # Настраиваем имитацию Whatsminer API
        mock_token_instance = MagicMock()
        mock_whatsminer_token.return_value = mock_token_instance
        
        mock_summary_data = {"SUMMARY": [{"Power": 100, "Hashrate": 50}]}
        mock_edevs_data = {"DEVS": [{"ID": 0, "Status": "Alive"}]}
        mock_whatsminer_api.get_read_only_info.side_effect = [
            mock_summary_data,  # для cmd="summary"
            mock_edevs_data     # для cmd="edevs"
        ]
        
        # Настраиваем имитацию Antminer API
        mock_antminer_instance = MagicMock()
        mock_antminer_client.return_value = mock_antminer_instance
        
        mock_stats_data = {"STATS": [{"ID": 0, "Temperature": 70}]}
        mock_devs_data = {"DEVS": [{"ASC": 0, "Status": "Alive"}]}
        mock_antminer_instance.stats.return_value = mock_stats_data
        mock_antminer_instance.devs.return_value = mock_devs_data
        
        try:
            # Импортируем и запускаем основную логику wm.py
            import asic2mqtt
            
            # Проверяем, что конфигурация загружена корректно
            print("✅ Импорт asic2mqtt.py выполнен успешно")
            
            # Проверяем функцию проверки доступности хоста
            result = asic2mqtt.is_host_available("192.168.3.34")
            print(f"✅ Функция is_host_available работает: {result}")
            
            # Проверяем функцию получения данных от Whatsminer
            summary, edevs = asic2mqtt.get_whatsminer_data("192.168.3.34", mock_token_instance)
            print(f"✅ Функция get_whatsminer_data работает")
            print(f"  - Summary data: {summary is not None}")
            print(f"  - Edevs data: {edevs is not None}")
            
            # Проверяем функцию получения данных от Antminer
            stats, devs = asic2mqtt.get_antminer_data("192.168.3.73", "root", "root")
            print(f"✅ Функция get_antminer_data работает")
            print(f"  - Stats data: {stats is not None}")
            print(f"  - Devs data: {devs is not None}")
            
            print("\n🎉 Все тесты пройдены успешно!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_wm_functionality()
    
    if success:
        print("\n✅ Тест функциональности asic2mqtt.py пройден успешно!")
        sys.exit(0)
    else:
        print("\n❌ Тест функциональности asic2mqtt.py не пройден!")
        sys.exit(1)