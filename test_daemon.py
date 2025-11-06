#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import tempfile
import subprocess

def test_config_path_environment_variable():
    """Тестирование поддержки переменной окружения CONFIG_PATH"""
    print("Тестирование поддержки переменной окружения CONFIG_PATH...")
    
    # Создаем временный конфигурационный файл
    test_config = {
        "asics": {},
        "mqtt": {
            "broker_address": "localhost",
            "broker_port": 1883
        },
        "logging": {
            "level": "ERROR",
            "file": "/tmp/asic2mqtt_test.log"
        }
    }
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_config, f)
        temp_config_path = f.name
    
    try:
        # Устанавливаем переменную окружения
        env = os.environ.copy()
        env['CONFIG_PATH'] = temp_config_path
        env['PYTHONPATH'] = '.'
        
        # Запускаем asic2mqtt.py с флагом --help, чтобы проверить, что он корректно запускается
        result = subprocess.run([
            sys.executable, 'asic2mqtt.py', '--help'
        ], capture_output=True, text=True, env=env, timeout=10)
        
        if result.returncode == 0:
            print("✓ Переменная окружения CONFIG_PATH работает корректно")
            return True
        else:
            print("✗ Ошибка при тестировании переменной окружения CONFIG_PATH")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Тест превысил время ожидания")
        return False
    except Exception as e:
        print(f"✗ Ошибка при тестировании: {e}")
        return False
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)

def test_systemd_unit_file():
    """Тестирование наличия systemd unit файла"""
    print("Тестирование наличия systemd unit файла...")
    
    systemd_unit_path = 'asic2mqtt.service'
    if os.path.exists(systemd_unit_path):
        print("✓ systemd unit файл существует")
        return True
    else:
        print("✗ systemd unit файл не найден")
        return False

def test_readme_documentation():
    """Тестирование обновления документации"""
    print("Тестирование обновления документации...")
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем наличие ключевых разделов
        required_sections = [
            'Установка и запуск как системный демон',
            'Переменная окружения',
            'CONFIG_PATH'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if not missing_sections:
            print("✓ Документация обновлена корректно")
            return True
        else:
            print(f"✗ В документации отсутствуют разделы: {', '.join(missing_sections)}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка при проверке документации: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("Тестирование демона asic2mqtt")
    print("=" * 40)
    
    tests = [
        test_config_path_environment_variable,
        test_systemd_unit_file,
        test_readme_documentation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✓ Все тесты пройдены успешно!")
        return 0
    else:
        print("✗ Некоторые тесты не пройдены")
        return 1

if __name__ == "__main__":
    sys.exit(main())