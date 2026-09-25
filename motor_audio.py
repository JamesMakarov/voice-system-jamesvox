import pygame
import threading
import time
from datetime import datetime
import os
import random
import logging
import dados
import motor_voz
logging.basicConfig(filename='jamesvox.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
class GerenciadorAudio:
    def __init__(self, ref_horarios, callback_atualizar):
        self.horarios = ref_horarios
        self.callback_atualizar = callback_atualizar
        logging.info(f'Sistema iniciado. {len(self.horarios)} horários carregados no cache.')
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        self.canal_sino = pygame.mixer.Channel(1)
        self.canal_voz = pygame.mixer.Channel(2)
        self.ultimo_minuto_tocado = ''
        self.fila_reproducao = []
        self.playlist_ativa = None
        self.hora_fim_playlist = ''
        self.volume_playlist_atual = 1.0
        self.historico_playlists = dados.carregar_historico_playlists()
        self.data_historico = datetime.now().strftime('%Y-%m-%d')
        self.ultimo_foi_voz = False
        self.arquivos_lixo = []
        self.config = dados.carregar_config()
        self.parabens_tocado_hoje = False
        self.audio_parabens_hoje = None
        self.preparar_aniversarios_do_dia()
        threading.Thread(target=self.loop_do_relogio, daemon=True).start()
    def preparar_aniversarios_do_dia(self):
        if getattr(self, 'audio_parabens_hoje', None):
            audios = self.audio_parabens_hoje if isinstance(self.audio_parabens_hoje, list) else [self.audio_parabens_hoje]
            for a in audios:
                if a not in self.arquivos_lixo:
                    self.arquivos_lixo.append(a)
        self.config = dados.carregar_config()
        self.parabens_tocado_hoje = False
        self.audio_parabens_hoje = None
        hora_parabens = self.config.get('hora_parabens', '').strip()
        if not hora_parabens:
            return
        else:
            alunos = dados.carregar_aniversarios()
            if not alunos:
                logging.warning('Hora de parabéns configurada, mas banco de aniversariantes está vazio.')
                return
            else:
                hoje = datetime.now().strftime('%d/%m')
                aniversariantes = [a['nome'] for a in alunos if a['data_nasc'].startswith(hoje)]
                if aniversariantes:
                    logging.info(f'Preparando parabéns automático para {len(aniversariantes)} pessoas.')
                    modo = self.config.get('idioma_aniversario', 'Português')
                    voz_pt = self.config.get('voz_parabens_pt', 'pt-BR-FranciscaNeural')
                    voz_en = self.config.get('voz_parabens_en', 'en-US-AriaNeural')
                    if len(aniversariantes) > 1:
                        nomes_str = ', '.join(aniversariantes[:(-1)]) + ' e ' + aniversariantes[(-1)]
                        in_pt = self.config.get('texto_inicio_plu', 'Atenção! Feliz aniversário para')
                        fim_pt = self.config.get('texto_fim_plu', 'Parabéns a todos!')
                        in_en = self.config.get('texto_inicio_en_plu', 'Attention! Happy birthday to')
                        fim_en = self.config.get('texto_fim_en_plu', 'Congratulations to all!')
                    else:
                        nomes_str = aniversariantes[0]
                        in_pt = self.config.get('texto_inicio_sing', 'Atenção! Feliz aniversário para')
                        fim_pt = self.config.get('texto_fim_sing', 'Parabéns!')
                        in_en = self.config.get('texto_inicio_en_sing', 'Attention! Happy birthday to')
                        fim_en = self.config.get('texto_fim_en_sing', 'Congratulations!')
                    fatias = []
                    if modo == 'Bilíngue':
                        if in_pt:
                            fatias.append((in_pt, voz_pt))
                        if in_en:
                            fatias.append((in_en, voz_en))
                        if nomes_str:
                            fatias.append((nomes_str, voz_pt))
                        if fim_pt:
                            fatias.append((fim_pt, voz_pt))
                        if fim_en:
                            fatias.append((fim_en, voz_en))
                    else:
                        if modo == 'Inglês':
                            if in_en:
                                fatias.append((in_en, voz_en))
                            if nomes_str:
                                fatias.append((nomes_str, voz_pt))
                            if fim_en:
                                fatias.append((fim_en, voz_en))
                        else:
                            if in_pt:
                                fatias.append((in_pt, voz_pt))
                            if nomes_str:
                                fatias.append((nomes_str, voz_pt))
                            if fim_pt:
                                fatias.append((fim_pt, voz_pt))
                    caminhos_gerados = []
                    for texto_fatia, voz_fatia in fatias:
                        try:
                            caminho = motor_voz.criar_audio_voz('PARABENS', voz_fatia, texto_fatia)
                            if caminho:
                                caminhos_gerados.append(caminho)
                        except Exception as e:
                            logging.error(f'Falha ao gerar fatia do parabéns: {e}')
                    if caminhos_gerados:
                        self.audio_parabens_hoje = caminhos_gerados
    def limpar_lixo(self):
        if not self.canal_voz.get_busy() and not self.canal_sino.get_busy() and not self.fila_reproducao:
            arquivos_protegidos = set()

            for item in self.horarios:
                if item.get('usar_voz') and item.get('audio'):
                    if isinstance(item['audio'], list):
                        for a in item['audio']:
                            arquivos_protegidos.add(a)
                    else:
                        arquivos_protegidos.add(item['audio'])

            if getattr(self, 'audio_parabens_hoje', None):
                if isinstance(self.audio_parabens_hoje, list):
                    for a in self.audio_parabens_hoje:
                        arquivos_protegidos.add(a)
                else:
                    arquivos_protegidos.add(self.audio_parabens_hoje)

            for arq in self.arquivos_lixo[:]:
                if arq in arquivos_protegidos:
                    self.arquivos_lixo.remove(arq)
                    continue

                try:
                    if os.path.exists(arq):
                        os.remove(arq)
                    self.arquivos_lixo.remove(arq)
                except Exception as e:
                    logging.warning(f'Não foi possível remover lixo {arq}: {e}')
    def parar_tudo_emergencia(self):
        logging.warning('PARADA DE EMERGÊNCIA acionada pelo usuário.')
        self.fila_reproducao.clear()
        pygame.mixer.music.stop()
        self.canal_sino.stop()
        self.canal_voz.stop()
        self.playlist_ativa = None
        self.hora_fim_playlist = ''
        self.ultimo_foi_voz = False
        pygame.mixer.music.set_volume(1.0)
    def tocar_imediato(self, item):
        logging.info('Tocando evento imediato acionado manualmente.')
        self.fila_reproducao.append(item)
    def tocar_proxima_da_playlist(self, pasta):
        musicas = [f for f in os.listdir(pasta) if f.endswith(('.mp3', '.wav', '.ogg'))]
        if not musicas:
            logging.error(f'Playlist vazia ou sem arquivos de áudio válidos: {pasta}')
            return
        else:
            if pasta not in self.historico_playlists:
                self.historico_playlists[pasta] = []
            nao_tocadas = [m for m in musicas if m not in self.historico_playlists[pasta]]
            if not nao_tocadas:
                self.historico_playlists[pasta] = []
                nao_tocadas = musicas
            escolhida = random.choice(nao_tocadas)
            self.historico_playlists[pasta].append(escolhida)
            dados.salvar_historico_playlists(self.historico_playlists)
            logging.info(f'Tocando playlist: {escolhida}')
            pygame.mixer.music.load(os.path.join(pasta, escolhida))
            pygame.mixer.music.set_volume(self.volume_playlist_atual)
            pygame.mixer.music.play()
    def fade_ducking(self):
        if pygame.mixer.music.get_busy():
            vol = pygame.mixer.music.get_volume()
            alvo = self.volume_playlist_atual * 0.2

            while round(vol, 2) > alvo:
                vol -= 0.01
                pygame.mixer.music.set_volume(vol)
                time.sleep(0.01)

            pygame.mixer.music.set_volume(alvo)
    def fade_restore(self):
        if pygame.mixer.music.get_busy() and pygame.mixer.music.get_volume() < self.volume_playlist_atual:
            vol = pygame.mixer.music.get_volume()

            while round(vol, 2) < self.volume_playlist_atual:
                vol += 0.01
                pygame.mixer.music.set_volume(vol)
                time.sleep(0.01)

            pygame.mixer.music.set_volume(self.volume_playlist_atual)
    def loop_do_relogio(self):
        while True:
            agora = datetime.now().strftime('%H:%M')
            data_hoje = datetime.now().strftime('%Y-%m-%d')

            dias_da_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
            dia_semana_hoje = dias_da_semana[datetime.now().weekday()]

            if data_hoje != self.data_historico:
                self.data_historico = data_hoje
                self.preparar_aniversarios_do_dia()

            hora_parabens = self.config.get('hora_parabens', '').strip()
            if hora_parabens and agora == hora_parabens and not self.parabens_tocado_hoje:
                self.parabens_tocado_hoje = True

                if self.audio_parabens_hoje:
                    audios_para_tocar = self.audio_parabens_hoje if isinstance(self.audio_parabens_hoje, list) else [self.audio_parabens_hoje]

                    if all(os.path.exists(a) for a in audios_para_tocar):
                        logging.info('Disparando aniversariantes do dia.')

                        item_niver = {
                            'hora': agora,
                            'hora_fim': '',
                            'usar_voz': True,
                            'audio': self.audio_parabens_hoje,
                            'texto': 'Aniversariantes do Dia',
                            'evento_unico': True,
                            'volume': 1.0,
                        }

                        self.tocar_imediato(item_niver)

                        for a in audios_para_tocar:
                            self.arquivos_lixo.append(a)
                    else:
                        logging.error('Arquivos de parabéns não encontrados no momento do disparo.')
                        self.preparar_aniversarios_do_dia()
                        self.parabens_tocado_hoje = True

            if self.playlist_ativa and self.hora_fim_playlist == agora:
                logging.info(f'Encerrando playlist ativa. Horário atingido: {agora}')
                pygame.mixer.music.stop()
                self.playlist_ativa = None
                self.hora_fim_playlist = ''

            if agora != self.ultimo_minuto_tocado:
                self.ultimo_minuto_tocado = agora
                eventos_agora = []

                tipo_semana_atual = dados.obter_tipo_semana_atual()

                for item in list(self.horarios):
                    if not item.get('ativo', True):
                        continue

                    if item['hora'] != agora:
                        continue

                    if item.get('evento_unico'):
                        eventos_agora.append(item)
                    else:
                        dias_configurados = item.get('dias_semana', ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'])
                        frequencia_configurada = item.get('frequencia', 'Toda Semana')

                        if dia_semana_hoje not in dias_configurados:
                            continue

                        if frequencia_configurada != 'Toda Semana' and frequencia_configurada != tipo_semana_atual:
                            continue

                        eventos_agora.append(item)

                for item in eventos_agora:
                    val_audio = item.get('audio', '')

                    if isinstance(val_audio, str) and os.path.isdir(val_audio):
                        logging.info(f'Iniciando Playlist programada: {val_audio}')
                        self.playlist_ativa = val_audio
                        self.hora_fim_playlist = item.get('hora_fim', '')
                        self.volume_playlist_atual = item.get('volume', 1.0)
                        self.tocar_proxima_da_playlist(self.playlist_ativa)
                    else:
                        logging.info(f"Disparando evento programado: {item.get('texto', 'Toque Simples')} ({agora})")
                        self.fila_reproducao.append(item)

                if eventos_agora:
                    houve_remocao = False

                    for item in eventos_agora:
                        if not item.get('evento_unico'):
                            continue

                        if item not in self.horarios:
                            continue

                        self.horarios.remove(item)
                        houve_remocao = True

                        if item.get('usar_voz'):
                            audios = item['audio'] if isinstance(item['audio'], list) else [item['audio']]
                            for a in audios:
                                self.arquivos_lixo.append(a)

                    if houve_remocao:
                        self.callback_atualizar()

            if not self.canal_voz.get_busy() and not self.canal_sino.get_busy():
                if self.fila_reproducao:
                    item_atual = self.fila_reproducao.pop(0)

                    if isinstance(item_atual.get('audio'), list):
                        lista_audios = item_atual['audio']

                        for idx, path in enumerate(reversed(lista_audios)):
                            fatia = item_atual.copy()
                            fatia['audio'] = path

                            if idx < len(lista_audios) - 1:
                                fatia['fatia_secundaria'] = True

                            self.fila_reproducao.insert(0, fatia)

                        continue

                    self.fade_ducking()

                    try:
                        vol_item = item_atual.get('volume', 1.0)

                        if item_atual.get('usar_voz'):
                            if not self.ultimo_foi_voz and not item_atual.get('fatia_secundaria'):
                                caminho_aviso = os.path.join('audios', 'aviso.mp3')

                                if os.path.exists(caminho_aviso):
                                    som_aviso = pygame.mixer.Sound(caminho_aviso)
                                    som_aviso.set_volume(vol_item)
                                    duracao = som_aviso.get_length()
                                    self.canal_sino.play(som_aviso)
                                    time.sleep(min(1.5, duracao))

                            som_voz = pygame.mixer.Sound(item_atual['audio'])
                            som_voz.set_volume(vol_item)
                            self.canal_voz.play(som_voz)
                            self.ultimo_foi_voz = True
                        else:
                            som_toque = pygame.mixer.Sound(item_atual['audio'])
                            som_toque.set_volume(vol_item)
                            self.canal_voz.play(som_toque)
                            self.ultimo_foi_voz = False

                    except Exception as e:
                        logging.error(f'Erro Crítico de reprodução (Pygame): {e}')
                        self.ultimo_foi_voz = False
                else:
                    self.fade_restore()
                    self.ultimo_foi_voz = False

            if self.playlist_ativa and not pygame.mixer.music.get_busy():
                self.tocar_proxima_da_playlist(self.playlist_ativa)

            self.limpar_lixo()
            time.sleep(0.1)
