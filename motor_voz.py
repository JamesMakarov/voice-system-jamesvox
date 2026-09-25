import os
import hashlib
import requests
import json
import asyncio
import edge_tts
import random
import logging
from datetime import datetime

import dados


ARQUIVO_CREDITOS = "creditos_ia.json"


def garantir_arquivo_versiculos():
    caminho = "versiculos.txt"

    if not os.path.exists(caminho):
        versos_padrao = [
            "O Senhor é o meu pastor; nada me faltará. Salmos 23, versículo 1.",
            "Lâmpada para os meus pés é tua palavra, e luz para o meu caminho. Salmos 119, versículo 105.",
            "Ainda que eu ande pelo vale da sombra da morte, não temerei mal algum, porque tu estás comigo. Salmos 23, versículo 4.",
            "Eu sou o caminho, a verdade e a vida. Ninguém vem ao Pai, a não ser por mim. João 14, versículo 6.",
            "Deixo-lhes a paz; a minha paz lhes dou. Não se perturbem os seus corações. João 14, versículo 27.",
            "Porque onde estiver o vosso tesouro, aí estará também o vosso coração. Mateus 6, versículo 21.",
            "Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei. Mateus 11, versículo 28.",
            "Peçam, e lhes será dado; busquem, e encontrarão; batam, e a porta lhes será aberta. Mateus 7, versículo 7.",
            "Tudo posso naquele que me fortalece. Filipenses 4, versículo 13.",
            "Sabemos que Deus age em todas as coisas para o bem daqueles que o amam. Romanos 8, versículo 28.",
        ]

        with open(caminho, "w", encoding="utf-8") as f:
            for v in versos_padrao:
                f.write(v + "\n")

    return caminho


def salvar_saldo(novo_saldo):
    with open(ARQUIVO_CREDITOS, "w", encoding="utf-8") as f:
        json.dump({"saldo": novo_saldo}, f)


def obter_saldo():
    cfg = dados.carregar_config()
    api_key = cfg.get("api_key_elevenlabs", "").strip()

    saldo_cache = 10000

    if os.path.exists(ARQUIVO_CREDITOS):
        try:
            with open(ARQUIVO_CREDITOS, "r", encoding="utf-8") as f:
                dados_creditos = json.load(f)
                saldo_cache = dados_creditos.get("saldo", 10000)
        except:
            pass

    if api_key:
        url = "https://api.elevenlabs.io/v1/user/subscription"
        headers = {"xi-api-key": api_key}

        try:
            response = requests.get(url, headers=headers, timeout=3)

            if response.status_code == 200:
                info = response.json()
                gastos = info.get("character_count", 0)
                limite = info.get("character_limit", 10000)
                saldo_real = limite - gastos

                salvar_saldo(saldo_real)
                return saldo_real
            else:
                logging.warning(
                    f"Falha ao checar saldo da API: {response.status_code}"
                )

        except Exception as e:
            logging.warning(f"Erro de rede ao checar saldo da API: {e}")
            return saldo_cache

        return saldo_cache

    return saldo_cache


def sincronizar_vozes_elevenlabs():
    cfg = dados.carregar_config()
    api_key = cfg.get("api_key_elevenlabs", "").strip()

    if not api_key:
        logging.error("Sincronização falhou: Chave API ausente.")
        raise Exception(
            "Você precisa configurar uma Chave API da ElevenLabs nas configurações antes de sincronizar as vozes."
        )

    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}

    logging.info("Iniciando requisição de sincronização com a API da ElevenLabs...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        vozes_json = response.json().get("voices", [])
        novo_cache = {}
        novo_previews = {}

        for v in vozes_json:
            novo_cache[v["name"]] = v["voice_id"]

            if v.get("preview_url"):
                novo_previews[v["name"]] = v["preview_url"]

        if novo_cache:
            dados.salvar_vozes_cache(novo_cache)

        if novo_previews:
            dados.salvar_previews_cache(novo_previews)

        logging.info(
            f"Sincronização concluída. {len(novo_cache)} vozes salvas no cache."
        )
        return novo_cache

    try:
        erro_json = response.json()
        msg_erro = erro_json.get("detail", {}).get("message", response.text)
    except:
        msg_erro = response.text

    logging.error(
        f"Sincronização da API falhou (HTTP {response.status_code}): {msg_erro}"
    )
    raise Exception(
        f"A ElevenLabs recusou a sincronização!\n\n"
        f"Código: {response.status_code}\n"
        f"Detalhe: {msg_erro}"
    )


def baixar_amostra_voz(nome_voz):
    previews = dados.carregar_previews_cache()
    url = previews.get(nome_voz)

    if not url:
        logging.warning(
            f"URL de preview não encontrada para a voz: {nome_voz}"
        )
        return

    hash_txt = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    caminho_amostra = os.path.join("audios", f"amostra_{hash_txt}.mp3")

    if not os.path.exists(caminho_amostra):
        logging.info(f"Baixando amostra de voz para {nome_voz}...")

        try:
            r = requests.get(url)

            if r.status_code == 200:
                with open(caminho_amostra, "wb") as f:
                    f.write(r.content)
            else:
                logging.error(
                    f"Falha ao baixar amostra HTTP {r.status_code}."
                )
                return

        except Exception as e:
            logging.error(f"Erro de rede ao baixar amostra: {e}")
            return

    return caminho_amostra


def tempo_por_extenso(hora_str):
    h = int(hora_str.split(":")[0])
    m = int(hora_str.split(":")[1])

    numeros = {
        0: "zero",
        1: "um",
        2: "dois",
        3: "três",
        4: "quatro",
        5: "cinco",
        6: "seis",
        7: "sete",
        8: "oito",
        9: "nove",
        10: "dez",
        11: "onze",
        12: "doze",
        13: "treze",
        14: "catorze",
        15: "quinze",
        16: "dezesseis",
        17: "dezessete",
        18: "dezoito",
        19: "dezenove",
        20: "vinte",
        30: "trinta",
        40: "quarenta",
        50: "cinquenta",
    }

    def num_extenso(n, feminino=False):
        if n == 1 and feminino:
            return "uma"

        if n == 2 and feminino:
            return "duas"

        if n <= 20 or n in [30, 40, 50]:
            return numeros.get(n)

        dezena = n // 10 * 10
        unidade = n % 10

        unidade_str = (
            "uma"
            if unidade == 1 and feminino
            else "duas"
            if unidade == 2 and feminino
            else numeros[unidade]
        )

        return f"{numeros[dezena]} e {unidade_str}"

    texto_hora = num_extenso(h, feminino=True)
    texto_minuto = num_extenso(m, feminino=False)

    if h == 1:
        str_h = "uma hora"
    elif h == 0:
        str_h = "meia-noite"
    elif h == 12:
        str_h = "meio-dia"
    else:
        str_h = f"{texto_hora} horas"

    if m == 0:
        frase = f"{str_h} em ponto."
    else:
        frase = f"{str_h} e {texto_minuto} minutos."

    return frase.capitalize()


def tempo_por_extenso_en(hora_str):
    h = int(hora_str.split(":")[0])
    m = int(hora_str.split(":")[1])

    h_en = h if h <= 12 else h - 12

    if h_en == 0:
        h_en = 12

    period = "A.M." if h < 12 else "P.M."

    numeros_en = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
        11: "eleven",
        12: "twelve",
        13: "thirteen",
        14: "fourteen",
        15: "fifteen",
        16: "sixteen",
        17: "seventeen",
        18: "eighteen",
        19: "nineteen",
        20: "twenty",
        30: "thirty",
        40: "forty",
        50: "fifty",
    }

    def min_extenso(n):
        if n <= 20 or n in [30, 40, 50]:
            return numeros_en.get(n)

        dezena = n // 10 * 10
        unidade = n % 10
        return f"{numeros_en[dezena]} {numeros_en[unidade]}"

    str_h = numeros_en[h_en]

    if m == 0:
        return f"It is {str_h} {period}."

    if m < 10:
        str_m = f"oh {numeros_en[m]}"
    else:
        str_m = min_extenso(m)

    return f"It is {str_h} {str_m} {period}."


def criar_audio_edge_gratuito(
    hora,
    texto_personalizado="",
    codigo_voz="pt-BR-FranciscaNeural",
    velocidade="+0%",
    idioma="Português",
):
    hoje = datetime.now().strftime("%Y-%m-%d")

    if texto_personalizado.strip() == "[VERSICULO]":
        caminho_arquivo = garantir_arquivo_versiculos()

        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            lista_versos = [
                linha.strip()
                for linha in f.readlines()
                if linha.strip()
            ]

        if not lista_versos:
            lista_versos = [
                "O Senhor é o meu pastor; nada me faltará. Salmos 23, versículo 1."
            ]

        random.seed(hoje)
        verso_do_dia = random.choice(lista_versos)

        texto_voz = f"Mensagem para reflexão: {verso_do_dia}"
        codigo_voz = "pt-BR-AntonioNeural"
        hash_str = (
            f"versiculo_{hoje}_{codigo_voz}_{velocidade}_edge"
        )

    else:
        if texto_personalizado.strip():
            texto_voz = texto_personalizado
        elif idioma == "Bilíngue":
            texto_voz = (
                f"{tempo_por_extenso_en(hora)} "
                f"{tempo_por_extenso(hora)}"
            )
        elif idioma == "Inglês":
            texto_voz = tempo_por_extenso_en(hora)
        else:
            texto_voz = tempo_por_extenso(hora)

        hash_str = f"{texto_voz}_{codigo_voz}_{velocidade}_edge"

    hash_txt = hashlib.md5(
        hash_str.encode("utf-8")
    ).hexdigest()[:8]

    nome_arquivo = f"voz_gratis_{hash_txt}.mp3"
    caminho_voz = os.path.join("audios", nome_arquivo)

    if not os.path.exists(caminho_voz):
        logging.info(
            f"Gerando áudio via Edge TTS (Gratuito): {hash_txt}"
        )

        try:
            async def _gerar():
                communicate = edge_tts.Communicate(
                    texto_voz,
                    codigo_voz,
                    rate=velocidade,
                )
                await communicate.save(caminho_voz)

            asyncio.run(_gerar())

        except Exception as e:
            logging.error(
                f"Falha na geração via Edge TTS: {e}"
            )
            raise Exception(
                f"Falha no motor de voz offline do Windows: {e}"
            )

    return caminho_voz


def criar_audio_voz(
    hora,
    codigo_voz,
    texto_personalizado="",
    velocidade="+0%",
    idioma="Português",
):
    cfg = dados.carregar_config()
    api_key_elevenlabs = cfg.get(
        "api_key_elevenlabs",
        "",
    ).strip()

    if texto_personalizado.strip() == "[VERSICULO]":
        texto_base = "[VERSICULO]"

    elif texto_personalizado.strip() == "":
        if idioma == "Bilíngue":
            texto_base = (
                f"{tempo_por_extenso_en(hora)} "
                f"{tempo_por_extenso(hora)}"
            )
        elif idioma == "Inglês":
            texto_base = tempo_por_extenso_en(hora)
        else:
            texto_base = tempo_por_extenso(hora)

    else:
        texto_base = texto_personalizado

    if (
        texto_base == "[VERSICULO]"
        or (codigo_voz and "Neural" in codigo_voz)
    ):
        return criar_audio_edge_gratuito(
            hora,
            texto_base,
            codigo_voz,
            velocidade,
            idioma,
        )

    texto_voz = texto_base
    vozes_dinamicas = dados.carregar_vozes_cache()

    if codigo_voz in vozes_dinamicas.values():
        voice_id = codigo_voz
    else:
        voice_id = vozes_dinamicas.get(
            codigo_voz,
            "Xb7hH8MSUJpSbSDYk0k2",
        )

    hash_str = (
        f"{texto_voz}_{voice_id}_{velocidade}_elevenlabs"
    )
    hash_txt = hashlib.md5(
        hash_str.encode("utf-8")
    ).hexdigest()[:8]

    nome_arquivo = f"voz_{hash_txt}.mp3"
    caminho_voz = os.path.join("audios", nome_arquivo)

    if not os.path.exists(caminho_voz):
        if not api_key_elevenlabs:
            logging.info(
                "Geração redirecionada para Edge TTS: "
                "Chave API ElevenLabs ausente."
            )
            return criar_audio_edge_gratuito(
                hora,
                texto_voz,
                "pt-BR-FranciscaNeural",
                velocidade,
                idioma,
            )

        saldo_atual = obter_saldo()
        custo_caracteres = len(texto_voz)

        if custo_caracteres > saldo_atual:
            logging.error(
                "Geração bloqueada por falta de saldo: "
                f"{saldo_atual} disponíveis, "
                f"{custo_caracteres} necessários."
            )
            raise Exception(
                "Saldo insuficiente na ElevenLabs!\n\n"
                f"Você tem apenas {saldo_atual} caracteres disponíveis, "
                f"mas esta mensagem precisa de {custo_caracteres}."
            )

        url = (
            "https://api.elevenlabs.io/v1/text-to-speech/"
            f"{voice_id}"
        )

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key_elevenlabs,
        }

        mapa_speed_eleven = {
            "-40%": 0.6,
            "-30%": 0.7,
            "-20%": 0.8,
            "-10%": 0.9,
            "+0%": 1.0,
            "+10%": 1.1,
            "+20%": 1.2,
            "+40%": 1.4,
        }

        vel_float = mapa_speed_eleven.get(
            velocidade,
            1.0,
        )

        data = {
            "text": texto_voz,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "speed": vel_float,
            },
        }

        logging.info(
            "Enviando requisição de TTS para ElevenLabs "
            f"({custo_caracteres} caracteres, voz: {voice_id})..."
        )

        response = requests.post(
            url,
            json=data,
            headers=headers,
        )

        if response.status_code == 200:
            with open(caminho_voz, "wb") as f:
                f.write(response.content)

            salvar_saldo(
                saldo_atual - custo_caracteres
            )

            logging.info(
                "Áudio ElevenLabs gerado e salvo com sucesso: "
                f"{nome_arquivo}"
            )
            return caminho_voz

        try:
            erro_json = response.json()
            msg_erro = erro_json.get(
                "detail",
                {},
            ).get(
                "message",
                response.text,
            )
        except:
            msg_erro = response.text

        logging.error(
            f"Erro na ElevenLabs "
            f"(HTTP {response.status_code}): {msg_erro}"
        )

        raise Exception(
            "A ElevenLabs bloqueou a geração!\n\n"
            f"Código: {response.status_code}\n"
            f"Detalhe: {msg_erro}"
        )

    return caminho_voz
