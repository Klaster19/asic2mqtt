import semantic_version


def parse_version_number(version):
    """
    Parse a version number of varying lengths into a SemVer instance.

    This function takes a variable length version number and does a
    reasonably good job of converting it into a valid instance of
    a SemVer object.
    """
    if not version:
        return semantic_version.Version('0.0.0')
    
    # Извлекаем числовые части из строки версии
    parts = version.split('.')
    numeric_parts = []
    
    for part in parts:
        # Извлекаем числовую часть из строки
        numeric_part = ''.join(filter(str.isdigit, part))
        if numeric_part:
            numeric_parts.append(numeric_part)
    
    # Если не удалось извлечь числовые части, используем 0.0.0
    if not numeric_parts:
        return semantic_version.Version('0.0.0')
    
    number_of_parts = len(numeric_parts)
    if number_of_parts == 3:
        v = '.'.join(numeric_parts)
    elif number_of_parts == 2:
        v = '{}.0'.format('.'.join(numeric_parts))
    elif number_of_parts > 3:
        v = '{}'.format('.'.join(numeric_parts[:3]))
    else:
        # Если только одна числовая часть, используем ее как major версию
        v = '{}.0.0'.format(numeric_parts[0])

    try:
        return semantic_version.Version(v)
    except ValueError:
        # Если не удалось создать версию, возвращаем 0.0.0
        return semantic_version.Version('0.0.0')
