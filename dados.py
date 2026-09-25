import json
import os
from datetime import datetime


def carregar_horarios():
    if os.path.exists("horarios.json"):
        with open("horarios.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_horarios(horarios):
    with open("horarios.json", "w", encoding="utf-8") as f:
        json.dump(horarios, f, indent=4, ensure_ascii=False)


def carregar_aniversarios():
    if os.path.exists("aniversarios.json"):
        with open("aniversarios.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def salvar_aniversarios(alunos):
    with open("aniversarios.json", "w", encoding="utf-8") as f:
        json.dump(alunos, f, indent=4, ensure_ascii=False)


def carregar_config():
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "hora_parabens": "",
        "voz_parabens": "pt-BR-FranciscaNeural",
        "texto_inicio_sing": "Atenção! Hoje é um dia muito especial! Queremos desejar um feliz aniversário para",
        "texto_fim_sing": "O Centro Educacional deseja muita paz, saúde e felicidades!",
        "texto_inicio_plu": "Atenção! Hoje é um dia de muita festa! Queremos desejar um feliz aniversário para os aniversariantes de hoje:",
        "texto_fim_plu": "O Centro Educacional deseja a todos vocês muita paz, saúde e felicidades!",
        "inverter_quinzena": False,
    }


def salvar_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def carregar_historico_playlists():
    if os.path.exists("historico_playlists.json"):
        with open("historico_playlists.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_historico_playlists(historico):
    with open("historico_playlists.json", "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)


def carregar_vozes_cache():
    if os.path.exists("vozes_cache.json"):
        with open("vozes_cache.json", "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "Alice (Educadora Cativante)": "Xb7hH8MSUJpSbSDYk0k2",
        "Bella (Profissional e Clara)": "hpp4J3VqNfWAUOO0d1Us",
        "Adam (Masculino Firme)": "pNInz6obpgDQGcFmaJgB",
    }


def salvar_vozes_cache(vozes):
    with open("vozes_cache.json", "w", encoding="utf-8") as f:
        json.dump(vozes, f, indent=4, ensure_ascii=False)


def carregar_previews_cache():
    if os.path.exists("previews_cache.json"):
        with open("previews_cache.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_previews_cache(previews):
    with open("previews_cache.json", "w", encoding="utf-8") as f:
        json.dump(previews, f, indent=4, ensure_ascii=False)


def obter_tipo_semana_atual():
    config = carregar_config()
    epoch = datetime(2024, 1, 1).date()
    hoje = datetime.now().date()
    semanas_passadas = (hoje - epoch).days // 7
    inverter = config.get("inverter_quinzena", False)
    is_par = semanas_passadas % 2 == 0

    if inverter:
        is_par = not is_par

    return "Semana 1" if is_par else "Semana 2"
