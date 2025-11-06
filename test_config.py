#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки конфигурации
"""

import json
import os

def test_config():
    """Тест конфигурационного файла"""
    print("Проверка конфигурационного файла...")
    
    # Проверяем наличие файла config_secrets.json
    if not os.path.exists('config_secrets.json'):
        print("❌ Файл config_secrets.json не найден")
        return False
    
    # Проверяем наличие файла config_example.json
    if not os.path.exists('config_example.json'):
        print("❌ Файл config_example.json не найден")
        return False
    
    # Проверяем формат config_secrets.json
    try:
        with open('config_secrets.json', 'r') as f:
            config = json.load(f)
        print("✅ Файл config_secrets.json загружен успешно")
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в формате config_secrets.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при загрузке config_secrets.json: {e}")
        return False
    
    # Проверяем структуру конфигурации
    asics = config.get('asics', {})
    mqtt_config = config.get('mqtt', {})
    
    if not asics:
        print("❌ В конфигурации отсутствует секция 'asics'")
        return False
    
    if not mqtt_config:
        print("❌ В конфигурации отсутствует секция 'mqtt'")
        return False
    
    print("✅ Структура конфигурации корректна")
    
    # Проверяем наличие необходимых асиков
    required_asics = ['whatsminer1', 'whatsminer2', 'antminer3']
    for asic_name in required_asics:
        if asic_name not in asics:
            print(f"❌ В конфигурации отсутствует асик {asic_name}")
            return False
        
        asic_config = asics[asic_name]
        if 'ip' not in asic_config or 'topic' not in asic_config:
            print(f"❌ Неполная конфигурация для асика {asic_name}")
            return False
    
    print("✅ Все необходимые асики присутствуют в конфигурации")
    
    # Проверяем конфигурацию MQTT
    required_mqtt_fields = ['broker_address', 'broker_port', 'username', 'password']
    for field in required_mqtt_fields:
        if field not in mqtt_config:
            print(f"❌ В конфигурации MQTT отсутствует поле {field}")
            return False
    
    print("✅ Конфигурация MQTT корректна")
    
    # Выводим информацию о настроенных асиках
    print("\nНастроенные асики:")
    for asic_name, asic_config in asics.items():
        ip = asic_config.get('ip', 'N/A')
        topic = asic_config.get('topic', 'N/A')
        username = asic_config.get('username', 'N/A')
        print(f"  {asic_name}:")
        print(f"    IP: {ip}")
        print(f"    Topic: {topic}")
        if username != 'N/A':
            print(f"    Username: {username}")
    
    print("\nКонфигурация MQTT:")
    print(f"  Broker: {mqtt_config.get('broker_address', 'N/A')}:{mqtt_config.get('broker_port', 'N/A')}")
    print(f"  Username: {mqtt_config.get('username', 'N/A')}")
    
    return True

if __name__ == "__main__":
    print("Тестирование конфигурации")
    print("=" * 30)
    
    success = test_config()
    
    if success:
        print("\n✅ Тест конфигурации пройден успешно!")
        exit(0)
    else:
        print("\n❌ Тест конфигурации не пройден!")
        exit(1)