"""
Utilidades para evaluación de candidatos en procesos de selección
"""

# CONFIGURACIÓN DE CRITERIOS DE APTITUD
APTITUD_CONFIG = {
    "experiencia": {
        "senior": 5,      # 5+ años -> 3 puntos
        "mid": 2,         # 2-4 años -> 2 puntos  
        "junior": 1       # 1+ años -> 1 punto
    },
    "educacion": {
        "avanzada": ["PhD", "Master"],    # 2 puntos
        "basica": ["Bachelor"]            # 1 punto
    },
    "skills_tecnicos": [
        "python", "java", "c++", "javascript", "sql", "aws", "azure",
        "machine learning", "data analysis", "software development",
        "project management", "agile", "scrum", "git", "docker",
        "kubernetes", "terraform", "react", "angular", "nodejs"
    ],
    "idiomas_requeridos": {
        "english_levels": ["B2", "C1", "C2", "NATIVE"]
    },
    "puntuacion": {
        "apto_minimo": 7,           # Score >= 7 -> Apto (1)
        "revision_minimo": 4,       # Score 4-6 -> Revisión manual (-1)
        "no_apto_maximo": 3         # Score <= 3 -> No apto (0)
    }
}

def evaluar_aptitud_candidato(row, config=None):
    """
    Evalúa la aptitud de un candidato basado en criterios configurables
    
    Args:
        row: Fila del DataFrame con datos del candidato
        config: Configuración personalizada (opcional)
    
    Returns:
        int: 1 (apto), 0 (no apto), -1 (necesita revisión manual)
    """
    if config is None:
        config = APTITUD_CONFIG
    
    score = 0
    
    # 1. Experiencia (peso: hasta 3 puntos)
    years_exp = row.get('years_total_experience', 0) or 0
    if years_exp >= config["experiencia"]["senior"]:
        score += 3
    elif years_exp >= config["experiencia"]["mid"]:
        score += 2
    elif years_exp >= config["experiencia"]["junior"]:
        score += 1
    
    # 2. Nivel educativo (peso: hasta 2 puntos)
    education = row.get('education_level', '')
    if education in config["educacion"]["avanzada"]:
        score += 2
    elif education in config["educacion"]["basica"]:
        score += 1
    
    # 3. Skills técnicos (peso: hasta 3 puntos)
    skills = row.get('skills', []) or []
    if isinstance(skills, list):
        skills_text = ' '.join(skills).lower()
        matching_skills = sum(1 for skill in config["skills_tecnicos"] 
                            if skill.lower() in skills_text)
        
        if matching_skills >= 3:
            score += 3
        elif matching_skills >= 2:
            score += 2
        elif matching_skills >= 1:
            score += 1
    
    # 4. Certificaciones (peso: 1 punto)
    certifications = row.get('certifications', []) or []
    if isinstance(certifications, list) and len(certifications) > 0:
        score += 1
    
    # 5. Idiomas (peso: 1 punto)
    languages = row.get('languages', {}) or {}
    if isinstance(languages, dict):
        english_level = languages.get('English', '').upper()
        if english_level in config["idiomas_requeridos"]["english_levels"]:
            score += 1
    
    # Determinar aptitud basada en score
    if score >= config["puntuacion"]["apto_minimo"]:
        return 1    # Apto
    elif score >= config["puntuacion"]["revision_minimo"]:
        return -1   # Necesita revisión manual
    else:
        return 0    # No apto

def obtener_estadisticas_aptitud(df, col_apto='apto'):
    """
    Calcula estadísticas de aptitud del dataset
    
    Args:
        df: DataFrame con evaluaciones
        col_apto: Nombre de la columna de aptitud
    
    Returns:
        dict: Estadísticas de aptitud
    """
    if col_apto not in df.columns:
        return {"error": f"Columna '{col_apto}' no encontrada"}
    
    counts = df[col_apto].value_counts()
    total = len(df)
    
    stats = {
        "total_candidatos": total,
        "aptos": counts.get(1, 0),
        "no_aptos": counts.get(0, 0),
        "revision_manual": counts.get(-1, 0),
        "porcentaje_aptos": (counts.get(1, 0) / total * 100) if total > 0 else 0,
        "porcentaje_no_aptos": (counts.get(0, 0) / total * 100) if total > 0 else 0,
        "porcentaje_revision": (counts.get(-1, 0) / total * 100) if total > 0 else 0
    }
    
    return stats

def personalizar_criterios_ingeniero_software():
    """
    Configuración específica para puestos de Ingeniero de Software
    """
    config = APTITUD_CONFIG.copy()
    
    # Skills específicos para software
    config["skills_tecnicos"] = [
        "python", "java", "javascript", "react", "angular", "nodejs", "sql",
        "git", "docker", "kubernetes", "aws", "azure", "mongodb", "postgresql",
        "rest api", "microservices", "agile", "scrum", "ci/cd", "testing"
    ]
    
    # Criterios más estrictos
    config["puntuacion"]["apto_minimo"] = 8
    config["puntuacion"]["revision_minimo"] = 5
    
    return config

def personalizar_criterios_data_scientist():
    """
    Configuración específica para puestos de Data Scientist
    """
    config = APTITUD_CONFIG.copy()
    
    # Skills específicos para data science
    config["skills_tecnicos"] = [
        "python", "r", "sql", "machine learning", "deep learning", "tensorflow",
        "pytorch", "pandas", "numpy", "scikit-learn", "jupyter", "statistics",
        "data analysis", "data visualization", "aws", "azure", "spark", "hadoop"
    ]
    
    # Educación más importante para data science
    config["educacion"]["avanzada"] = ["PhD", "Master"]  # 2 puntos
    config["educacion"]["basica"] = ["Bachelor"]         # 1 punto
    
    return config

# Mapeo de puestos a configuraciones
CONFIGURACIONES_PUESTO = {
    "software_engineer": personalizar_criterios_ingeniero_software,
    "data_scientist": personalizar_criterios_data_scientist,
    "general": lambda: APTITUD_CONFIG
}

def evaluar_por_puesto(df, puesto="general"):
    """
    Evalúa candidatos usando criterios específicos del puesto
    
    Args:
        df: DataFrame con candidatos
        puesto: Tipo de puesto ("software_engineer", "data_scientist", "general")
    
    Returns:
        DataFrame: DataFrame con columna 'apto' añadida
    """
    if puesto in CONFIGURACIONES_PUESTO:
        config = CONFIGURACIONES_PUESTO[puesto]()
    else:
        config = APTITUD_CONFIG
    
    df_result = df.copy()
    df_result['apto'] = df_result.apply(
        lambda row: evaluar_aptitud_candidato(row, config), 
        axis=1
    )
    
    return df_result
