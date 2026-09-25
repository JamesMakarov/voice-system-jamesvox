# Internal filename: 'main.py'

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import os
import shutil
import threading
import pystray
from PIL import Image, ImageDraw
import socket
import sys
import csv
import ctypes
import time
import pygame
import random
import dados
import motor_voz
import manual
import motor_audio
try:
    myappid = 'thiago.jamesvox.escola.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass
ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
def garantir_instancia_unica():
    global _lock_socket
    _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        _lock_socket.bind(('127.0.0.1', 54321))
    except socket.error:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('Aviso de Execução', 'O JamesVox já está em execução!\n\nVerifique o ícone perto do relógio do Windows.')
        sys.exit()
class SistemaSinal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('JamesVox')
        self.geometry('1050x700')
        self.minsize(900, 650)
        caminho_icone = resource_path('icone.ico')
        if os.path.exists(caminho_icone):
            self.after(200, lambda: self.iconbitmap(caminho_icone))
        self.horarios = dados.carregar_horarios()
        self.motor = motor_audio.GerenciadorAudio(self.horarios, self.sincronizar_dados_seguro)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.criar_sidebar()
        self.criar_timeline()
        self.atualizar_lista_tela()
        self.protocol('WM_DELETE_WINDOW', self.ocultar_para_bandeja)
        self.timer_redimensionamento = None
        self.tela_em_movimento = False
        self.bind('<Configure>', self.ao_redimensionar_tela)
    def ao_redimensionar_tela(self, event):
        if event.widget == self:
            if self.timer_redimensionamento:
                self.after_cancel(self.timer_redimensionamento)
            if not self.tela_em_movimento:
                self.tela_em_movimento = True
                self.lista_timeline.pack_forget()
                self.lbl_redimensionando.pack(fill='both', expand=True)
            self.timer_redimensionamento = self.after(300, self.finalizar_redimensionamento)
    def finalizar_redimensionamento(self):
        self.timer_redimensionamento = None
        self.tela_em_movimento = False
        self.lbl_redimensionando.pack_forget()
        self.lista_timeline.pack(fill='both', expand=True)
    def sincronizar_dados_seguro(self):
        self.after(0, self._processar_sincronizacao)
    def _processar_sincronizacao(self):
        dados.salvar_horarios(self.horarios)
        self.atualizar_lista_tela()
    def criar_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=340, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.lbl_titulo_sidebar = ctk.CTkLabel(self.sidebar, text='Novo Evento', font=('Arial', 22, 'bold'))
        self.lbl_titulo_sidebar.grid(row=0, column=0, padx=20, pady=(20, 15), sticky='w')
        frame_horas = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        frame_horas.grid(row=1, column=0, padx=20, pady=5, sticky='ew')
        ctk.CTkLabel(frame_horas, text='Hora:').pack(side='left')
        self.entry_hora = ctk.CTkEntry(frame_horas, width=70, placeholder_text='09:00')
        self.entry_hora.pack(side='left', padx=5)
        ctk.CTkLabel(frame_horas, text='até').pack(side='left', padx=5)
        self.entry_hora_fim = ctk.CTkEntry(frame_horas, width=70, placeholder_text='09:35')
        self.entry_hora_fim.pack(side='left', padx=5)
        ctk.CTkLabel(self.sidebar, text='Idioma do Alerta:', font=('Arial', 12)).grid(row=2, column=0, padx=20, pady=(10, 0), sticky='w')
        self.combo_idioma = ctk.CTkComboBox(self.sidebar, values=['Português', 'Inglês', 'Bilíngue'])
        self.combo_idioma.set('Português')
        self.combo_idioma.grid(row=3, column=0, padx=20, pady=5, sticky='ew')
        self.frame_dias = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        self.frame_dias.grid(row=4, column=0, padx=10, pady=15, sticky='ew')
        self.frame_dias.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.vars_dias = {}
        self.btns_dias = {}
        dias_map = {'Seg': 'S', 'Ter': 'T', 'Qua': 'Q', 'Qui': 'Q', 'Sex': 'S', 'Sab': 'S', 'Dom': 'D'}
        def toggle_dia(dia):
            self.vars_dias[dia] = not self.vars_dias[dia]
            if self.vars_dias[dia]:
                self.btns_dias[dia].configure(fg_color='#3498DB', hover_color='#2980B9')
            else:
                self.btns_dias[dia].configure(fg_color='#4A4A4A', hover_color='#333333')
        for i, (dia, letra) in enumerate(dias_map.items()):
            self.vars_dias[dia] = True
            btn = ctk.CTkButton(
                self.frame_dias,
                text=letra,
                width=35,
                height=30,
                corner_radius=4,
                fg_color='#3498DB',
                hover_color='#2980B9',
                font=('Arial', 12, 'bold'),
                command=lambda d=dia: toggle_dia(d),
            )
            btn.grid(row=0, column=i, padx=2, pady=5)
            self.btns_dias[dia] = btn
        self.frame_freq = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        self.frame_freq.grid(row=5, column=0, padx=20, pady=10, sticky='ew')
        ctk.CTkLabel(self.frame_freq, text='Frequência:', width=80, anchor='w').pack(side='left')
        self.combo_freq = ctk.CTkComboBox(self.frame_freq, values=['Toda Semana', 'Semana 1', 'Semana 2'])
        self.combo_freq.set('Toda Semana')
        self.combo_freq.pack(side='right', expand=True, fill='x', padx=(5, 0))
        self.var_evento_unico = ctk.BooleanVar(value=False)
        self.check_unico = ctk.CTkCheckBox(self.sidebar, text='Tocar apenas uma vez', variable=self.var_evento_unico, text_color='#F39C12')
        self.check_unico.grid(row=6, column=0, padx=20, pady=(10, 5), sticky='w')
        self.var_imediato = ctk.BooleanVar(value=False)
        self.check_imediato = ctk.CTkCheckBox(self.sidebar, text='Tocar Imediatamente (Agora)', variable=self.var_imediato, text_color='#E74C3C', command=self.alternar_imediato)
        self.check_imediato.grid(row=7, column=0, padx=20, pady=5, sticky='w')
        self.frame_vol = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        self.frame_vol.grid(row=8, column=0, padx=20, pady=15, sticky='ew')
        self.lbl_vol = ctk.CTkLabel(self.frame_vol, text='Volume: 100%', width=90, anchor='w')
        self.lbl_vol.pack(side='left')
        def atualizar_lbl_vol(val):
            self.lbl_vol.configure(text=f'Volume: {int(val * 100)}%')
        self.slider_vol = ctk.CTkSlider(self.frame_vol, from_=0, to=1, command=atualizar_lbl_vol)
        self.slider_vol.set(1.0)
        self.slider_vol.pack(side='right', expand=True, fill='x', padx=(10, 0))
        self.var_usar_voz = ctk.BooleanVar(value=False)
        self.check_voz = ctk.CTkCheckBox(self.sidebar, text='Usar Voz Neural', variable=self.var_usar_voz, command=self.alternar_modo, font=('Arial', 14, 'bold'), text_color='#3498DB')
        self.check_voz.grid(row=9, column=0, padx=20, pady=(15, 5), sticky='w')
        self.frame_voz = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        opcoes_velocidade = ['Lentíssima (-40%)', 'Muito Lenta (-30%)', 'Lenta (-20%)', 'Levemente Lenta (-10%)', 'Normal (+0%)', 'Levemente Rápida (+10%)', 'Rápida (+20%)', 'Muito Rápida (+40%)']
        ctk.CTkLabel(self.frame_voz, text='Velocidade da Fala:', text_color='#AAAAAA', font=('Arial', 12)).pack(anchor='w', pady=(5, 0))
        self.combo_vel = ctk.CTkComboBox(self.frame_voz, values=opcoes_velocidade)
        self.combo_vel.set('Normal (+0%)')
        self.combo_vel.pack(fill='x', pady=(0, 15))
        ctk.CTkLabel(self.frame_voz, text='Mensagem (Português):', text_color='#AAAAAA', font=('Arial', 12)).pack(anchor='w')
        self.entry_texto = ctk.CTkTextbox(self.frame_voz, height=50, wrap='word')
        self.entry_texto.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(self.frame_voz, text='Mensagem (Inglês):', text_color='#AAAAAA', font=('Arial', 12)).pack(anchor='w')
        self.entry_texto_en = ctk.CTkTextbox(self.frame_voz, height=50, wrap='word')
        self.entry_texto_en.pack(fill='x', pady=(0, 10))
        self.btn_preview = ctk.CTkButton(self.frame_voz, text='🔊 Ouvir Mensagem Agora (Gasta Saldo)', fg_color='#8E44AD', hover_color='#732D91', height=35, command=self.ouvir_preview)
        self.btn_preview.pack(fill='x', pady=(5, 10))
        self.frame_arquivo = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        self.frame_arquivo.grid(row=10, column=0, padx=20, pady=10, sticky='ew')
        self.btn_audio = ctk.CTkButton(self.frame_arquivo, text='Escolher Toque (Arquivo)', fg_color='#4A4A4A', hover_color='#2D2D2D', command=self.escolher_audio)
        self.btn_audio.pack(fill='x', pady=5)
        self.btn_pasta = ctk.CTkButton(self.frame_arquivo, text='Escolher Playlist (Pasta)', fg_color='#A95C00', hover_color='#8A4A00', command=self.escolher_pasta)
        self.btn_pasta.pack(fill='x', pady=5)
        self.caminho_audio_temp = ctk.StringVar()
        self.label_audio_escolhido = ctk.CTkLabel(self.frame_arquivo, text='Nenhum arquivo...', text_color='gray', wraplength=260)
        self.label_audio_escolhido.pack(anchor='w', pady=5)
        self.btn_adicionar = ctk.CTkButton(self.sidebar, text='Adicionar ao Relógio', fg_color='green', hover_color='darkgreen', height=45, font=('Arial', 15, 'bold'), command=self.adicionar_horario)
        self.btn_adicionar.grid(row=11, column=0, padx=20, pady=(25, 25), sticky='ew')
        frame_rodape = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        frame_rodape.grid(row=12, column=0, padx=20, pady=(10, 20), sticky='ew')
        semana_atual = dados.obter_tipo_semana_atual()
        self.lbl_semana_atual = ctk.CTkLabel(frame_rodape, text=f'Calendário: {semana_atual}', font=('Arial', 12, 'bold'), text_color='#F1C40F')
        self.lbl_semana_atual.pack(pady=(0, 10))
        saldo_atual = motor_voz.obter_saldo()
        self.lbl_saldo = ctk.CTkLabel(frame_rodape, text=f'Créditos Premium: {saldo_atual} letras', font=('Arial', 12, 'bold'), text_color='#2ECC71')
        self.lbl_saldo.pack(pady=(0, 10))
        self.btn_config = ctk.CTkButton(frame_rodape, text='⚙️ Configurações do Sistema', fg_color='#2C3E50', hover_color='#1A252F', height=35, command=self.abrir_configuracoes)
        self.btn_config.pack(fill='x', pady=(0, 10))
        self.btn_emergencia = ctk.CTkButton(frame_rodape, text='🛑 PARAR ÁUDIO AGORA', fg_color='#C62828', hover_color='#8E0000', font=('Arial', 12, 'bold'), height=40, command=self.acionar_emergencia)
        self.btn_emergencia.pack(fill='x', pady=(0, 10))
        self.lbl_assinatura = ctk.CTkLabel(frame_rodape, text='Developed by Thiago Monteiro', font=('Arial', 10, 'italic'), text_color='#555555')
        self.lbl_assinatura.pack(pady=(5, 0))
    def ouvir_preview(self):
        texto_pt = self.entry_texto.get('0.0', 'end-1c').strip()
        texto_en = self.entry_texto_en.get('0.0', 'end-1c').strip()
        idioma = self.combo_idioma.get()
        if not texto_pt and (not texto_en):
            messagebox.showwarning('Aviso', 'Digite pelo menos uma mensagem para ouvir o preview.')
            return
        else:
            cfg = dados.carregar_config()
            n_voz_pt = cfg.get('voz_padrao', 'Alice (Educadora Cativante)')
            n_voz_en = cfg.get('voz_padrao_en', 'Adam (Masculino Firme)')
            cache_vozes = dados.carregar_vozes_cache()
            cod_voz_pt = cache_vozes.get(n_voz_pt, 'Xb7hH8MSUJpSbSDYk0k2')
            cod_voz_en = cache_vozes.get(n_voz_en, 'pNInz6obpgDQGcFmaJgB')
            nome_vel_selecionada = self.combo_vel.get()
            mapa_vel = {'Lentíssima (-40%)': '-40%', 'Muito Lenta (-30%)': '-30%', 'Lenta (-20%)': '-20%', 'Levemente Lenta (-10%)': '-10%', 'Normal (+0%)': '+0%', 'Levemente Rápida (+10%)': '+10%', 'Rápida (+20%)': '+20%', 'Muito Rápida (+40%)': '+40%'}
            codigo_vel = mapa_vel.get(nome_vel_selecionada, '+0%')
            self.btn_preview.configure(state='disabled', text='Gerando Preview...')
            def _thread_preview():
                try:
                    fatias_obj = []
                    if idioma == 'Bilíngue':
                        if texto_pt:
                            fatias_obj.append((cod_voz_pt, texto_pt, 'Português'))
                        if texto_en:
                            fatias_obj.append((cod_voz_en, texto_en, 'Inglês'))
                    else:
                        if idioma == 'Inglês':
                            fatias_obj.append((cod_voz_en, texto_en, 'Inglês'))
                        else:
                            fatias_obj.append((cod_voz_pt, texto_pt, 'Português'))
                    velocidade_real = codigo_vel.split(' ')[1].replace('(', '').replace(')', '') if ' ' in codigo_vel else codigo_vel
                    total = len(fatias_obj)
                    for idx, (c_voz, txt, lang_fatia) in enumerate(fatias_obj):
                        t_inicio = time.time()
                        path = motor_voz.criar_audio_voz('PREVIEW', c_voz, txt, velocidade_real, lang_fatia)
                        t_fim = time.time()
                        if path and os.path.exists(path):
                                som = pygame.mixer.Sound(path)
                                som.set_volume(self.slider_vol.get())
                                self.motor.canal_voz.play(som)
                                while self.motor.canal_voz.get_busy():
                                    time.sleep(0.1)
                                if idx < total - 1 and t_fim - t_inicio > 1.0:
                                        time.sleep(random.uniform(2.0, 4.5))
                    self.after(0, lambda: self.btn_preview.configure(state='normal', text='🔊 Ouvir Mensagem Agora'))
                    self.after(0, lambda: self.lbl_saldo.configure(text=f'Créditos Premium: {motor_voz.obter_saldo()} letras'))
                except Exception as e:
                    self.after(0, lambda err=e: messagebox.showerror('Erro de IA', f'{err}'))
                    self.after(0, lambda: self.btn_preview.configure(state='normal', text='🔊 Ouvir Mensagem Agora'))
            threading.Thread(target=_thread_preview, daemon=True).start()
    def testar_amostra_gratis(self, nome_voz):
        def _bg():
            caminho = motor_voz.baixar_amostra_voz(nome_voz)
            if caminho and os.path.exists(caminho):
                som = pygame.mixer.Sound(caminho)
                som.set_volume(1.0)
                self.motor.canal_voz.play(som)
                return
            else:
                self.after(0, lambda: messagebox.showinfo('Sem Amostra', f'A voz \'{nome_voz}\' não possui um áudio de demonstração gratuito na ElevenLabs.'))
        threading.Thread(target=_bg, daemon=True).start()
    def ouvir_item_timeline(self, item):
        audios = item.get('audio')
        if not audios:
            messagebox.showinfo('Aviso', 'Este evento ainda não gerou áudio ou está em processamento.')
            return
        else:
            if isinstance(audios, str) and os.path.isdir(audios):
                messagebox.showinfo('Playlist', 'Este evento é uma pasta de músicas de Recreio.\nAs músicas vão tocar sequencialmente na hora programada.')
                return
            else:
                def _thread_play():
                    lista_audios = audios if isinstance(audios, list) else [audios]
                    for idx, path in enumerate(lista_audios):
                        if os.path.exists(path):
                            som = pygame.mixer.Sound(path)
                            som.set_volume(item.get('volume', 1.0))
                            self.motor.canal_voz.play(som)
                            if self.motor.canal_voz.get_busy():
                                time.sleep(0.1)
                            if idx < len(lista_audios) - 1:
                                time.sleep(0.5)
                threading.Thread(target=_thread_play, daemon=True).start()
    def abrir_configuracoes(self):
        janela = ctk.CTkToplevel(self)
        janela.title('Configurações do Sistema')
        janela.geometry('450x700')
        janela.transient(self)
        janela.grab_set()
        ctk.CTkLabel(janela, text='Configurações Gerais', font=('Arial', 18, 'bold')).pack(pady=(20, 10))
        frame_voz = ctk.CTkFrame(janela, fg_color='transparent')
        frame_voz.pack(fill='x', padx=30, pady=5)
        cfg = dados.carregar_config()
        cache_vozes = dados.carregar_vozes_cache()
        opcoes_vozes = list(cache_vozes.keys())
        ctk.CTkLabel(frame_voz, text='Chave API ElevenLabs (Opcional):', font=('Arial', 12)).pack(anchor='w')
        entry_api_key = ctk.CTkEntry(frame_voz)
        entry_api_key.pack(fill='x', pady=(0, 15))
        entry_api_key.insert(0, cfg.get('api_key_elevenlabs', ''))
        ctk.CTkLabel(frame_voz, text='Voz Padrão (Português):', font=('Arial', 12)).pack(anchor='w')
        frame_combo_pt = ctk.CTkFrame(frame_voz, fg_color='transparent')
        frame_combo_pt.pack(fill='x', pady=(0, 15))
        combo_voz_pt = ctk.CTkComboBox(frame_combo_pt, values=opcoes_vozes)
        combo_voz_pt.set(cfg.get('voz_padrao', 'Alice (Educadora Cativante)'))
        combo_voz_pt.pack(side='left', fill='x', expand=True)
        btn_ouvir_pt = ctk.CTkButton(frame_combo_pt, text='▶️', width=35, fg_color='#1ABC9C', hover_color='#16A085', command=lambda: self.testar_amostra_gratis(combo_voz_pt.get()))
        btn_ouvir_pt.pack(side='right', padx=(5, 0))
        ctk.CTkLabel(frame_voz, text='Voz Padrão (Inglês):', font=('Arial', 12)).pack(anchor='w')
        frame_combo_en = ctk.CTkFrame(frame_voz, fg_color='transparent')
        frame_combo_en.pack(fill='x', pady=(0, 10))
        combo_voz_en = ctk.CTkComboBox(frame_combo_en, values=opcoes_vozes)
        combo_voz_en.set(cfg.get('voz_padrao_en', 'Adam (Masculino Firme)'))
        combo_voz_en.pack(side='left', fill='x', expand=True)
        btn_ouvir_en = ctk.CTkButton(frame_combo_en, text='▶️', width=35, fg_color='#1ABC9C', hover_color='#16A085', command=lambda: self.testar_amostra_gratis(combo_voz_en.get()))
        btn_ouvir_en.pack(side='right', padx=(5, 0))
        def salvar_configs_gerais():
            c = dados.carregar_config()
            c['api_key_elevenlabs'] = entry_api_key.get().strip()
            c['voz_padrao'] = combo_voz_pt.get()
            c['voz_padrao_en'] = combo_voz_en.get()
            dados.salvar_config(c)
            messagebox.showinfo('Sucesso', 'Configurações gerais salvas com sucesso!', parent=janela)
        def acionar_sincronizacao():
            c = dados.carregar_config()
            c['api_key_elevenlabs'] = entry_api_key.get().strip()
            dados.salvar_config(c)
            btn_sync.configure(state='disabled', text='Sincronizando com API...')
            def _thread_sync():
                try:
                    novas_vozes = motor_voz.sincronizar_vozes_elevenlabs()
                    lista_novas = list(novas_vozes.keys())
                    self.after(0, lambda: combo_voz_pt.configure(values=lista_novas))
                    self.after(0, lambda: combo_voz_en.configure(values=lista_novas))
                    self.after(0, lambda: btn_sync.configure(state='normal', text='🔄 Sincronizar Vozes da ElevenLabs'))
                    self.after(0, lambda: messagebox.showinfo('Sucesso', f'{len(lista_novas)} vozes sincronizadas e salvas com sucesso!', parent=janela))
                except Exception as e:
                    self.after(0, lambda err=e: messagebox.showerror('Erro de Sincronização', f'{err}', parent=janela))
                    self.after(0, lambda: btn_sync.configure(state='normal', text='🔄 Sincronizar Vozes da ElevenLabs'))
            threading.Thread(target=_thread_sync, daemon=True).start()
        btn_sync = ctk.CTkButton(frame_voz, text='🔄 Sincronizar Vozes da ElevenLabs', fg_color='#8E44AD', hover_color='#732D91', command=acionar_sincronizacao)
        btn_sync.pack(fill='x', pady=(5, 15))
        btn_salvar_gerais = ctk.CTkButton(frame_voz, text='Salvar Chave e Padrões', fg_color='#2980B9', hover_color='#1F618D', command=salvar_configs_gerais)
        btn_salvar_gerais.pack(fill='x', pady=(0, 5))
        ctk.CTkLabel(janela, text='✝️ Versículo Diário', font=('Arial', 18, 'bold')).pack(pady=(15, 5))
        frame_verso = ctk.CTkFrame(janela, fg_color='transparent')
        frame_verso.pack(fill='x', padx=30, pady=5)
        verso_existente = next((item for item in self.horarios if item.get('texto') == '[VERSICULO]'), None)
        var_verso_ativo = ctk.BooleanVar(value=bool(verso_existente))
        check_verso = ctk.CTkCheckBox(frame_verso, text='Ativar leitura automática de versículos', variable=var_verso_ativo)
        check_verso.pack(anchor='w', pady=5)
        frame_hora_verso = ctk.CTkFrame(frame_verso, fg_color='transparent')
        frame_hora_verso.pack(anchor='w', pady=5)
        ctk.CTkLabel(frame_hora_verso, text='Horário (HH:MM):').pack(side='left')
        entry_hora_verso = ctk.CTkEntry(frame_hora_verso, width=70)
        entry_hora_verso.pack(side='left', padx=10)
        entry_hora_verso.insert(0, verso_existente['hora'] if verso_existente else '12:00')
        ctk.CTkButton(frame_verso, text='🕊️ Editar Textos (Bloco de Notas)', fg_color='#2980B9', hover_color='#1F618D', command=self.abrir_txt_versiculos).pack(fill='x', pady=(10, 5))
        def salvar_config_verso():
            self.horarios = [h for h in self.horarios if h.get('texto') != '[VERSICULO]']
            if var_verso_ativo.get():
                hora_v = entry_hora_verso.get().strip()
                if len(hora_v) != 5 or ':' not in hora_v:
                    messagebox.showerror('Erro', 'Use o formato HH:MM para o horário do versículo.', parent=janela)
                    return
                else:
                    novo_verso = {'hora': hora_v, 'hora_fim': '', 'usar_voz': True, 'audio': '', 'texto': '[VERSICULO]', 'evento_unico': False, 'nome_voz': 'Adam (Masculino Firme)', 'nome_velocidade': 'Normal (+0%)', 'idioma': 'Português', 'dias_semana': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'], 'volume': 1.0, 'frequencia': 'Toda Semana', 'ativo': True}
                    self.horarios.append(novo_verso)
            self.horarios.sort(key=lambda k: k['hora'])
            dados.salvar_horarios(self.horarios)
            self.atualizar_lista_tela()
            messagebox.showinfo('Sucesso', 'Configuração do Versículo salva com sucesso!', parent=janela)
        ctk.CTkButton(frame_verso, text='Salvar Horário do Versículo', fg_color='#27AE60', hover_color='#1E8449', command=salvar_config_verso).pack(fill='x', pady=5)
        ctk.CTkLabel(janela, text='Utilitários', font=('Arial', 18, 'bold')).pack(pady=(15, 5))
        ctk.CTkButton(janela, text='🎂 Central de Aniversariantes', fg_color='#8E44AD', hover_color='#732D91', height=35, command=self.abrir_aniversarios).pack(fill='x', padx=30, pady=5)
        ctk.CTkButton(janela, text='🔔 Definir Som de Aviso Global', fg_color='#4A4A4A', hover_color='#333333', height=35, command=self.escolher_aviso_global).pack(fill='x', padx=30, pady=5)
        ctk.CTkButton(janela, text='🖨️ Exportar Mural (Excel)', fg_color='#27AE60', hover_color='#229954', height=35, command=self.exportar_mural).pack(fill='x', padx=30, pady=5)
    def abrir_txt_versiculos(self):
        caminho = motor_voz.garantir_arquivo_versiculos()
        try:
            os.startfile(caminho)
        except Exception as e:
            messagebox.showerror('Erro', f'Não foi possível abrir o arquivo de versículos: {e}')
    def exportar_mural(self):
        caminho = filedialog.asksaveasfilename(defaultextension='.csv', initialfile='Mural_Horarios.csv', title='Salvar Mural', filetypes=[('Arquivo CSV (Excel)', '*.csv')])
        if not caminho:
            return
        else:
            try:
                with open(caminho, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['Hora', 'SEMANA 1', '', '', '', '', '', '', '', 'SEMANA 2', '', '', '', '', '', ''])
                    dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
                    writer.writerow([''] + dias + [''] + dias)
                    horas_unicas = sorted(list(set([item['hora'] for item in self.horarios if not item.get('evento_unico')])))
                    for hora in horas_unicas:
                        linha = [hora]
                        for semana_alvo in ['Semana 1', 'Semana 2']:
                            for dia in dias:
                                eventos_celula = []
                                for item in self.horarios:
                                    if item['hora'] == hora and (not item.get('evento_unico')) and (dia in item.get('dias_semana', [])):
                                                freq = item.get('frequencia', 'Toda Semana')
                                                if freq == 'Toda Semana' or freq == semana_alvo:
                                                    if item.get('usar_voz'):
                                                        texto_resumo = item.get('texto', '')[:25] + '...' if len(item.get('texto', '')) > 25 else item.get('texto', '')
                                                        eventos_celula.append(f'Voz: {texto_resumo}')
                                                    else:
                                                        eventos_celula.append(os.path.basename(item.get('audio', '')))
                                linha.append(' | '.join(eventos_celula))
                            if semana_alvo == 'Semana 1':
                                linha.append('')
                        writer.writerow(linha)
                messagebox.showinfo('Sucesso', f'Mural exportado com sucesso!\n\nArquivo salvo em:\n{caminho}\n\nBasta abrir com o Excel.')
            except Exception as e:
                messagebox.showerror('Erro', f'Falha ao exportar mural: {e}')
    def criar_timeline(self):
        self.frame_direita = ctk.CTkFrame(self, fg_color='transparent')
        self.frame_direita.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
        ctk.CTkLabel(self.frame_direita, text='Linha do Tempo', font=('Arial', 26, 'bold')).pack(anchor='w', pady=(0, 15))
        self.lbl_redimensionando = ctk.CTkLabel(self.frame_direita, text='Ajustando layout...', font=('Arial', 18), text_color='gray')
        self.lista_timeline = ctk.CTkScrollableFrame(self.frame_direita, fg_color='transparent')
        self.lista_timeline.pack(fill='both', expand=True)
    def criar_icone_imagem(self):
        try:
            return Image.open(resource_path('icone.ico'))
        except Exception:
            image = Image.new('RGB', (64, 64), color=(31, 83, 141))
            draw = ImageDraw.Draw(image)
            draw.ellipse((16, 16, 48, 48), fill=(255, 255, 255))
            return image
    def ocultar_para_bandeja(self):
        self.withdraw()
        menu = pystray.Menu(pystray.MenuItem('Abrir Painel', self.mostrar_janela, default=True), pystray.MenuItem('Encerrar Sistema', self.fechar_de_vez))
        self.icone_tray = pystray.Icon('JamesVox', self.criar_icone_imagem(), 'JamesVox', menu)
        threading.Thread(target=self.icone_tray.run, daemon=True).start()
    def mostrar_janela(self, icon, item):
        icon.stop()
        self.after(0, self.deiconify)
    def fechar_de_vez(self, icon, item):
        icon.stop()
        self.after(0, self.quit)
    def acionar_emergencia(self):
        self.motor.parar_tudo_emergencia()
        messagebox.showwarning('Aviso de Emergência', 'TODOS os áudios foram interrompidos e a fila atual foi limpa.\n\nA agenda do sistema NÃO foi apagada. Os próximos eventos tocarão normalmente no horário programado.')
    def alternar_imediato(self):
        if self.var_imediato.get():
            self.entry_hora.configure(state='disabled')
            self.entry_hora_fim.configure(state='disabled')
            self.check_unico.configure(state='disabled')
            self.combo_freq.configure(state='disabled')
            for btn in self.btns_dias.values():
                btn.configure(state='disabled')
        else:
            self.entry_hora.configure(state='normal')
            self.check_unico.configure(state='normal')
            self.combo_freq.configure(state='normal')
            for btn in self.btns_dias.values():
                btn.configure(state='normal')
            self.alternar_modo()
    def alternar_modo(self):
        if self.var_usar_voz.get():
            self.frame_arquivo.grid_remove()
            self.frame_voz.grid(row=10, column=0, padx=20, pady=5, sticky='ew')
            self.entry_hora_fim.delete(0, 'end')
            self.entry_hora_fim.configure(state='disabled')
        else:
            self.frame_voz.grid_remove()
            self.frame_arquivo.grid(row=10, column=0, padx=20, pady=5, sticky='ew')
            if not self.var_imediato.get():
                self.entry_hora_fim.configure(state='normal')
    def escolher_audio(self):
        caminho = filedialog.askopenfilename(initialdir=os.getcwd(), title='Selecione a musica', filetypes=(('Audio', '*.mp3 *.wav'),))
        if caminho:
            self.caminho_audio_temp.set(caminho)
            self.label_audio_escolhido.configure(text=os.path.basename(caminho), text_color='white')
    def escolher_pasta(self):
        caminho = filedialog.askdirectory(initialdir=os.getcwd(), title='Selecione a pasta da Playlist')
        if caminho:
            self.caminho_audio_temp.set(caminho)
            self.label_audio_escolhido.configure(text=f'Playlist: {os.path.basename(caminho)}', text_color='yellow')
    def escolher_aviso_global(self):
        caminho = filedialog.askopenfilename(initialdir=os.getcwd(), title='Selecione o aviso', filetypes=(('Audio', '*.mp3 *.wav'),))
        if caminho:
            try:
                shutil.copy(caminho, os.path.join('audios', 'aviso.mp3'))
                messagebox.showinfo('Sucesso', 'Aviso atualizado com sucesso!')
            except Exception as e:
                messagebox.showerror('Erro', f'Erro: {e}')
    def abrir_ajuda(self):
        janela_ajuda = ctk.CTkToplevel(self)
        janela_ajuda.title('Manual do Usuario')
        janela_ajuda.geometry('600x400')
        janela_ajuda.transient(self)
        tabview = ctk.CTkTabview(janela_ajuda)
        tabview.pack(padx=20, pady=20, fill='both', expand=True)
        for titulo, texto in manual.CONTEUDO.items():
            tabview.add(titulo)
            caixa_texto = ctk.CTkTextbox(tabview.tab(titulo), wrap='word', font=('Arial', 14))
            caixa_texto.pack(fill='both', expand=True, padx=10, pady=10)
            caixa_texto.insert('0.0', texto)
            caixa_texto.configure(state='disabled')
    def abrir_aniversarios(self):
        import aniversarios
        aniversarios.JanelaAniversarios(self, self.motor)
    def abrir_janela_edicao(self, item_ref):
        if item_ref not in self.horarios:
            messagebox.showerror('Erro', 'Este evento já ocorreu ou foi apagado.')
            return
        else:
            janela = ctk.CTkToplevel(self)
            janela.title('Editar Evento')
            janela.geometry('420x750')
            janela.transient(self)
            janela.grab_set()
            ctk.CTkLabel(janela, text='Editar Evento Agendado', font=('Arial', 18, 'bold')).pack(pady=10)
            frame_h = ctk.CTkFrame(janela, fg_color='transparent')
            frame_h.pack(pady=5)
            ctk.CTkLabel(frame_h, text='Hora:').pack(side='left')
            entry_h = ctk.CTkEntry(frame_h, width=70)
            entry_h.pack(side='left', padx=5)
            entry_h.insert(0, item_ref['hora'])
            ctk.CTkLabel(frame_h, text='até').pack(side='left', padx=5)
            entry_hf = ctk.CTkEntry(frame_h, width=70)
            entry_hf.pack(side='left', padx=5)
            if item_ref.get('hora_fim'):
                entry_hf.insert(0, item_ref['hora_fim'])
            if item_ref.get('usar_voz'):
                ctk.CTkLabel(janela, text='Idioma do Alerta:', font=('Arial', 12)).pack(anchor='w', padx=30, pady=(10, 0))
                combo_idioma_ed = ctk.CTkComboBox(janela, values=['Português', 'Inglês', 'Bilíngue'])
                combo_idioma_ed.pack(fill='x', padx=30, pady=5)
                combo_idioma_ed.set(item_ref.get('idioma', 'Português'))
            else:
                combo_idioma_ed = None
            ctk.CTkLabel(janela, text='Dias da Semana:', font=('Arial', 12)).pack(anchor='w', padx=30, pady=(10, 0))
            frame_dias_modal = ctk.CTkFrame(janela, fg_color='transparent')
            frame_dias_modal.pack(fill='x', padx=15, pady=10)
            frame_dias_modal.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
            vars_dias_modal = {}
            btns_dias_modal = {}
            dias_map = {'Seg': 'S', 'Ter': 'T', 'Qua': 'Q', 'Qui': 'Q', 'Sex': 'S', 'Sab': 'S', 'Dom': 'D'}
            dias_salvos = item_ref.get('dias_semana', ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'])
            def toggle_dia_ed(dia):
                vars_dias_modal[dia] = not vars_dias_modal[dia]
                if vars_dias_modal[dia]:
                    btns_dias_modal[dia].configure(fg_color='#3498DB', hover_color='#2980B9')
                else:
                    btns_dias_modal[dia].configure(fg_color='#4A4A4A', hover_color='#333333')
            for i, (dia, letra) in enumerate(dias_map.items()):
                is_active = dia in dias_salvos
                vars_dias_modal[dia] = is_active
                color = '#3498DB' if is_active else '#4A4A4A'
                hover = '#2980B9' if is_active else '#333333'
                btn = ctk.CTkButton(
                    frame_dias_modal,
                    text=letra,
                    width=35,
                    height=30,
                    corner_radius=4,
                    fg_color=color,
                    hover_color=hover,
                    font=('Arial', 12, 'bold'),
                    command=lambda d=dia: toggle_dia_ed(d),
                )
                btn.grid(row=0, column=i, padx=2, pady=5)
                btns_dias_modal[dia] = btn
            ctk.CTkLabel(janela, text='Frequência:', font=('Arial', 12)).pack(anchor='w', padx=30, pady=(5, 0))
            combo_f_ed = ctk.CTkComboBox(janela, values=['Toda Semana', 'Semana 1', 'Semana 2'])
            combo_f_ed.pack(fill='x', padx=30, pady=5)
            combo_f_ed.set(item_ref.get('frequencia', 'Toda Semana'))
            vol_atual = item_ref.get('volume', 1.0)
            frame_vol_ed = ctk.CTkFrame(janela, fg_color='transparent')
            frame_vol_ed.pack(fill='x', padx=30, pady=10)
            lbl_vol_ed = ctk.CTkLabel(frame_vol_ed, text=f'Volume: {int(vol_atual * 100)}%', width=90, anchor='w')
            lbl_vol_ed.pack(side='left')
            def atualizar_lbl_ed(val):
                lbl_vol_ed.configure(text=f'Volume: {int(val * 100)}%')
            slider_vol_ed = ctk.CTkSlider(frame_vol_ed, from_=0, to=1, command=atualizar_lbl_ed)
            slider_vol_ed.set(vol_atual)
            slider_vol_ed.pack(side='right', expand=True, fill='x', padx=(10, 0))
            var_unico = ctk.BooleanVar(value=item_ref.get('evento_unico', False))
            ctk.CTkCheckBox(janela, text='Tocar apenas uma vez', variable=var_unico).pack(pady=10, anchor='w', padx=30)
            if item_ref.get('usar_voz'):
                opcoes_velocidade = ['Lentíssima (-40%)', 'Muito Lenta (-30%)', 'Lenta (-20%)', 'Levemente Lenta (-10%)', 'Normal (+0%)', 'Levemente Rápida (+10%)', 'Rápida (+20%)', 'Muito Rápida (+40%)']
                ctk.CTkLabel(janela, text='Velocidade da Fala:', font=('Arial', 12)).pack(anchor='w', padx=30)
                combo_vel_ed = ctk.CTkComboBox(janela, values=opcoes_velocidade)
                combo_vel_ed.pack(fill='x', padx=30, pady=(0, 10))
                combo_vel_ed.set(item_ref.get('nome_velocidade', 'Normal (+0%)'))
                cache_vozes = dados.carregar_vozes_cache()
                opcoes_vozes = list(cache_vozes.keys())
                ctk.CTkLabel(janela, text='Mensagem (Português):', font=('Arial', 12)).pack(anchor='w', padx=30)
                entry_t = ctk.CTkTextbox(janela, height=50, wrap='word')
                entry_t.pack(fill='x', padx=30, pady=(0, 5))
                ctk.CTkLabel(janela, text='Mensagem (Inglês):', font=('Arial', 12)).pack(anchor='w', padx=30)
                entry_t_en = ctk.CTkTextbox(janela, height=50, wrap='word')
                entry_t_en.pack(fill='x', padx=30, pady=(0, 10))
                texto_salvo = item_ref.get('texto', '')
                if ' | ' in texto_salvo:
                    t_pt, t_en = texto_salvo.split(' | ', 1)
                    entry_t.insert('0.0', t_pt)
                    entry_t_en.insert('0.0', t_en)
                else:
                    entry_t.insert('0.0', texto_salvo)
            else:
                ctk.CTkLabel(janela, text='Arquivo Agendado:', font=('Arial', 12)).pack(anchor='w', padx=30)
                ctk.CTkLabel(janela, text=f'{os.path.basename(item_ref.get('audio', ''))}', text_color='#3498DB', font=('Arial', 14, 'bold')).pack(pady=5)
            def salvar_modificacoes():
                if item_ref not in self.horarios:
                    messagebox.showwarning('Aviso', 'O evento original já tocou e foi removido.')
                    janela.destroy()
                    return
                else:
                    nova_hora = entry_h.get().strip()
                    nova_hora_fim = entry_hf.get().strip()
                    dias_selecionados = [d for d, v in vars_dias_modal.items() if v]
                    novo_volume = slider_vol_ed.get()
                    nova_freq = combo_f_ed.get()
                    novo_idioma = combo_idioma_ed.get() if combo_idioma_ed else 'Português'
                    status_ativo = item_ref.get('ativo', True)
                    if len(nova_hora) != 5 or ':' not in nova_hora:
                        messagebox.showerror('Erro', 'Use o formato HH:MM')
                        return
                    else:
                        if not dias_selecionados and (not var_unico.get()):
                            messagebox.showerror('Erro', 'Selecione pelo menos um dia da semana para eventos repetitivos.')
                            return
                        else:
                            if item_ref.get('usar_voz'):
                                t_pt = entry_t.get('0.0', 'end-1c').strip()
                                t_en = entry_t_en.get('0.0', 'end-1c').strip()
                                nome_vel = combo_vel_ed.get()
                                cfg = dados.carregar_config()
                                n_voz_pt = cfg.get('voz_padrao', 'Alice (Educadora Cativante)')
                                n_voz_en = cfg.get('voz_padrao_en', 'Adam (Masculino Firme)')
                                cache_vozes = dados.carregar_vozes_cache()
                                cod_voz_pt = cache_vozes.get(n_voz_pt, 'Xb7hH8MSUJpSbSDYk0k2')
                                cod_voz_en = cache_vozes.get(n_voz_en, 'pNInz6obpgDQGcFmaJgB')
                                mapa_vel = {'Lentíssima (-40%)': '-40%', 'Muito Lenta (-30%)': '-30%', 'Lenta (-20%)': '-20%', 'Levemente Lenta (-10%)': '-10%', 'Normal (+0%)': '+0%', 'Levemente Rápida (+10%)': '+10%', 'Rápida (+20%)': '+20%', 'Muito Rápida (+40%)': '+40%'}
                                codigo_vel = mapa_vel.get(nome_vel, '+0%')
                                texto_display = f'{t_pt} | {t_en}'.strip(' |') if novo_idioma == 'Bilíngue' else t_en if novo_idioma == 'Inglês' else t_pt
                                novo_horario = {'hora': nova_hora, 'hora_fim': nova_hora_fim, 'usar_voz': True, 'audio': [], 'texto': texto_display, 'evento_unico': var_unico.get(), 'nome_voz': n_voz_pt, 'nome_velocidade': nome_vel, 'idioma': novo_idioma, 'dias_semana': dias_selecionados, 'volume': novo_volume, 'frequencia': nova_freq, 'status': 'gerando', 'ativo': status_ativo}
                                old_audios = item_ref.get('audio')
                                if isinstance(old_audios, list):
                                    for a in old_audios:
                                        if a:
                                            self.motor.arquivos_lixo.append(a)
                                else:
                                    if old_audios:
                                        self.motor.arquivos_lixo.append(old_audios)
                                idx_real = self.horarios.index(item_ref)
                                self.horarios[idx_real] = novo_horario
                                janela.destroy()
                                dados.salvar_horarios(self.horarios)
                                self.atualizar_lista_tela()
                                fatias_obj = []
                                if novo_idioma == 'Bilíngue':
                                    fatias_obj.append((cod_voz_pt, t_pt, 'Português'))
                                    fatias_obj.append((cod_voz_en, t_en, 'Inglês'))
                                else:
                                    if novo_idioma == 'Inglês':
                                        fatias_obj.append((cod_voz_en, t_en, 'Inglês'))
                                    else:
                                        fatias_obj.append((cod_voz_pt, t_pt, 'Português'))
                                threading.Thread(target=self._gerar_audio_bg_async, args=(novo_horario, fatias_obj, codigo_vel, False), daemon=True).start()
                                return
                            else:
                                novo_horario = {'hora': nova_hora, 'hora_fim': nova_hora_fim, 'usar_voz': False, 'audio': item_ref['audio'], 'texto': '', 'evento_unico': var_unico.get(), 'nome_voz': '', 'nome_velocidade': '', 'idioma': 'Português', 'dias_semana': dias_selecionados, 'volume': novo_volume, 'frequencia': nova_freq, 'ativo': status_ativo}
                                if item_ref.get('usar_voz'):
                                    old_audios = item_ref.get('audio')
                                    if isinstance(old_audios, list):
                                        for a in old_audios:
                                            if a:
                                                self.motor.arquivos_lixo.append(a)
                                    else:
                                        if old_audios:
                                            self.motor.arquivos_lixo.append(old_audios)
                                idx_real = self.horarios.index(item_ref)
                                self.horarios[idx_real] = novo_horario
                                janela.destroy()
                                dados.salvar_horarios(self.horarios)
                                self.atualizar_lista_tela()
            btn_salvar = ctk.CTkButton(janela, text='Salvar Alterações', fg_color='#E67E22', hover_color='#D35400', command=salvar_modificacoes)
            btn_salvar.pack(pady=15, fill='x', padx=30)
    def adicionar_horario(self):
        imediato = self.var_imediato.get()
        hora = 'AGORA' if imediato else self.entry_hora.get().strip()
        hora_fim = '' if imediato else self.entry_hora_fim.get().strip()
        idioma_escolhido = self.combo_idioma.get()
        usar_voz = self.var_usar_voz.get()
        audio = self.caminho_audio_temp.get()
        texto_pt = self.entry_texto.get('0.0', 'end-1c').strip()
        texto_en = self.entry_texto_en.get('0.0', 'end-1c').strip()
        evento_unico = self.var_evento_unico.get()
        volume_escolhido = self.slider_vol.get()
        frequencia_escolhida = self.combo_freq.get()
        dias_selecionados = [dia for dia, val in self.vars_dias.items() if val]
        if not imediato:
            if len(hora) != 5 or ':' not in hora:
                messagebox.showerror('Erro', 'Use o formato HH:MM na Hora Inicial (Ex: 09:00)')
                return
            else:
                if hora_fim and (len(hora_fim) != 5 or ':' not in hora_fim):
                    messagebox.showerror('Erro', 'Use o formato HH:MM na Hora Final, ou deixe em branco.')
                    return
                else:
                    if not dias_selecionados and (not evento_unico):
                        messagebox.showerror('Erro', 'Selecione pelo menos um dia da semana para tocar!')
                        return
        if not usar_voz and (not audio):
            messagebox.showerror('Erro', 'Escolha um áudio/playlist ou marque \'Usar Voz Neural Premium\'!')
            return
        else:
            if usar_voz or (audio and (not os.path.isdir(audio))):
                hora_fim = ''
            if not imediato and (not usar_voz) and os.path.isdir(audio) and (not hora_fim):
                messagebox.showerror('Erro', 'Para Playlists (Recreio), é OBRIGATÓRIO preencher o campo \'até\'!')
                return
            else:
                cfg = dados.carregar_config()
                n_voz_pt = cfg.get('voz_padrao', 'Alice (Educadora Cativante)')
                n_voz_en = cfg.get('voz_padrao_en', 'Adam (Masculino Firme)')
                cache_vozes = dados.carregar_vozes_cache()
                cod_voz_pt = cache_vozes.get(n_voz_pt, 'Xb7hH8MSUJpSbSDYk0k2')
                cod_voz_en = cache_vozes.get(n_voz_en, 'pNInz6obpgDQGcFmaJgB')
                nome_vel_selecionada = self.combo_vel.get()
                mapa_vel = {'Lentíssima (-40%)': '-40%', 'Muito Lenta (-30%)': '-30%', 'Lenta (-20%)': '-20%', 'Levemente Lenta (-10%)': '-10%', 'Normal (+0%)': '+0%', 'Levemente Rápida (+10%)': '+10%', 'Rápida (+20%)': '+20%', 'Muito Rápida (+40%)': '+40%'}
                codigo_vel = mapa_vel.get(nome_vel_selecionada, '+0%')
                texto_display = f'{texto_pt} | {texto_en}'.strip(' |') if idioma_escolhido == 'Bilíngue' else texto_en if idioma_escolhido == 'Inglês' else texto_pt
                novo_horario = {
                    'hora': hora,
                    'hora_fim': hora_fim,
                    'usar_voz': usar_voz,
                    'audio': audio if not usar_voz else [],
                    'texto': texto_display,
                    'evento_unico': evento_unico,
                    'nome_voz': n_voz_pt if usar_voz else '',
                    'nome_velocidade': nome_vel_selecionada if usar_voz else '',
                    'idioma': idioma_escolhido,
                    'dias_semana': dias_selecionados,
                    'volume': volume_escolhido,
                    'frequencia': frequencia_escolhida,
                    'ativo': True,
                }
                if usar_voz:
                    novo_horario['status'] = 'gerando'
                self.var_imediato.set(False)
                self.alternar_imediato()
                self.entry_hora.delete(0, 'end')
                self.entry_hora_fim.configure(state='normal')
                self.entry_hora_fim.delete(0, 'end')
                if usar_voz:
                    self.entry_hora_fim.configure(state='disabled')
                self.entry_texto.delete('0.0', 'end')
                self.entry_texto_en.delete('0.0', 'end')
                self.caminho_audio_temp.set('')
                self.combo_idioma.set('Português')
                self.var_usar_voz.set(False)
                self.var_evento_unico.set(False)
                self.slider_vol.set(1.0)
                self.lbl_vol.configure(text='Volume: 100%')
                self.combo_freq.set('Toda Semana')
                self.combo_vel.set('Normal (+0%)')
                for dia in self.vars_dias:
                    self.vars_dias[dia] = True
                    self.btns_dias[dia].configure(fg_color='#3498DB', hover_color='#2980B9')
                self.alternar_modo()
                if not imediato:
                    self.horarios.append(novo_horario)
                    self.horarios.sort(key=lambda k: k['hora'])
                    dados.salvar_horarios(self.horarios)
                    self.atualizar_lista_tela()
                if usar_voz:
                    fatias_obj = []
                    if idioma_escolhido == 'Bilíngue':
                        fatias_obj.append((cod_voz_pt, texto_pt, 'Português'))
                        fatias_obj.append((cod_voz_en, texto_en, 'Inglês'))
                    else:
                        if idioma_escolhido == 'Inglês':
                            fatias_obj.append((cod_voz_en, texto_en, 'Inglês'))
                        else:
                            fatias_obj.append((cod_voz_pt, texto_pt, 'Português'))
                    threading.Thread(target=self._gerar_audio_bg_async, args=(novo_horario, fatias_obj, codigo_vel, imediato), daemon=True).start()
                else:
                    if imediato:
                        self.motor.tocar_imediato(novo_horario)
    def _gerar_audio_bg_async(self, novo_horario, fatias_obj, velocidade_real, imediato):
        try:
            caminhos_finais = []
            total = len(fatias_obj)
            for idx, (c_voz, txt, lang_fatia) in enumerate(fatias_obj):
                t_inicio = time.time()
                path = motor_voz.criar_audio_voz(novo_horario['hora'], c_voz, txt, velocidade_real, lang_fatia)
                t_fim = time.time()
                if path:
                    caminhos_finais.append(path)
                if idx < total - 1 and t_fim - t_inicio > 1.0:
                        tempo_pausa = random.uniform(8.5, 15.2)
                        time.sleep(tempo_pausa)
            novo_horario['audio'] = caminhos_finais
            if 'status' in novo_horario:
                del novo_horario['status']
            if imediato:
                self.motor.tocar_imediato(novo_horario)
                if isinstance(caminhos_finais, list):
                    for a in caminhos_finais:
                        self.motor.arquivos_lixo.append(a)
                else:
                    self.motor.arquivos_lixo.append(caminhos_finais)
            else:
                self.after(0, self.sincronizar_dados_seguro)
            self.after(0, lambda: self.lbl_saldo.configure(text=f'Créditos Premium: {motor_voz.obter_saldo()} letras'))
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror('Erro na Geração de Voz', f'{err}'))
            novo_horario['status'] = 'erro'
            self.after(0, self.sincronizar_dados_seguro)
    def alternar_status_horario(self, index):
        atual = self.horarios[index].get('ativo', True)
        self.horarios[index]['ativo'] = not atual
        dados.salvar_horarios(self.horarios)
        self.atualizar_lista_tela()
    def remover_horario(self, index):
        item_removido = self.horarios.pop(index)
        dados.salvar_horarios(self.horarios)
        self.atualizar_lista_tela()
        if item_removido.get('usar_voz'):
            audio_val = item_removido.get('audio')
            if isinstance(audio_val, list):
                for a in audio_val:
                    if a:
                        self.motor.arquivos_lixo.append(a)
            else:
                if audio_val:
                    self.motor.arquivos_lixo.append(audio_val)
    def atualizar_lista_tela(self):
        for widget in self.lista_timeline.winfo_children():
            widget.destroy()
        for idx, item in enumerate(self.horarios):
            idioma = item.get('idioma', 'Português')
            ativo = item.get('ativo', True)
            if idioma == 'Bilíngue':
                cor_lang = '#9B59B6'
                txt_lang = '[BILÍNGUE]'
            else:
                if idioma == 'Inglês':
                    cor_lang = '#E67E22'
                    txt_lang = '[INGLÊS]'
                else:
                    cor_lang = '#3498DB'
                    txt_lang = ''
            status = item.get('status')
            if status == 'gerando':
                cor_fundo = '#D35400'
                icone = '⏳ PROCESSANDO VOZ...'
                desc = 'Aguarde, a IA está gerando o áudio no servidor...'
            else:
                if status == 'erro':
                    cor_fundo = '#C0392B'
                    icone = '❌ ERRO NA GERAÇÃO'
                    desc = 'Falha ao baixar áudio. Verifique sua chave API, créditos ou conexão e edite.'
                else:
                    if item.get('usar_voz'):
                        if item.get('texto') == '[VERSICULO]':
                            cor_fundo = '#1C2833'
                            icone = 'VOZ MICROSOFT (Religioso)'
                            desc = '✝️ Mensagem Bíblica Diária (Sorteio Automático)'
                        else:
                            cor_fundo = '#2D2440'
                            vel_str = item.get('nome_velocidade', 'Normal (+0%)').split(' ')[0]
                            icone = f'VOZ PREMIUM ({vel_str})'
                            txt = item.get('texto')
                            if txt:
                                desc = f'\"{txt[:65]}... (Continua)\"' if len(txt) > 65 else f'\"{txt}\"'
                            else:
                                desc = 'Aviso Automático de Hora'
                    else:
                        if isinstance(item.get('audio'), str) and os.path.isdir(item.get('audio', '')):
                            cor_fundo = '#243B2A'
                            icone = 'PLAYLIST'
                            desc = os.path.basename(item['audio'])
                        else:
                            cor_fundo = '#222222'
                            icone = 'TOQUE ÚNICO'
                            audio_val = item.get('audio', '')
                            desc = os.path.basename(audio_val[0] if isinstance(audio_val, list) else audio_val)
            if not ativo:
                cor_fundo = '#1E1E1E'
                cor_texto_principal = '#777777'
                cor_repeticao = '#555555'
                cor_lang = '#555555'
                icone = '[DESATIVADO] ' + icone
            else:
                cor_texto_principal = '#FFFFFF'
                if item.get('evento_unico'):
                    cor_repeticao = '#F39C12'
                else:
                    if len(item.get('dias_semana', ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'])) == 7:
                        cor_repeticao = '#3498DB'
                    else:
                        cor_repeticao = '#2ECC71'
            texto_hora = f'{item['hora']} até {item['hora_fim']}' if item.get('hora_fim') else item['hora']
            dias_agendados = item.get('dias_semana', ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'])
            vol_show = f'{int(item.get('volume', 1.0) * 100)}%'
            freq_show = item.get('frequencia', 'Toda Semana')
            if item.get('evento_unico'):
                txt_repeticao = 'Evento Único'
            else:
                if len(dias_agendados) == 7:
                    txt_repeticao = f'Todos os Dias ({freq_show})'
                else:
                    txt_repeticao = f'Dias: {', '.join(dias_agendados)} ({freq_show})'
            card = ctk.CTkFrame(self.lista_timeline, fg_color=cor_fundo, corner_radius=10)
            card.pack(fill='x', pady=6, padx=5, ipady=5)
            ctk.CTkLabel(card, text=texto_hora, font=('Arial', 22, 'bold'), text_color=cor_texto_principal, width=160, anchor='w').pack(side='left', padx=15)
            frame_botoes = ctk.CTkFrame(card, fg_color='transparent')
            frame_botoes.pack(side='right', padx=15)
            btn_toggle = ctk.CTkSwitch(frame_botoes, text='', width=40, command=lambda i=idx: self.alternar_status_horario(i))
            if ativo:
                btn_toggle.select()
            else:
                btn_toggle.deselect()
            btn_toggle.pack(side='left', padx=10)
            btn_ouvir = ctk.CTkButton(frame_botoes, text='🔊 Ouvir', width=70, height=35, fg_color='#8E44AD' if ativo else '#444444', hover_color='#732D91', font=('Arial', 13, 'bold'), command=lambda ref=item: self.ouvir_item_timeline(ref))
            btn_ouvir.pack(side='left', padx=5)
            btn_editar = ctk.CTkButton(frame_botoes, text='Editar', width=70, height=35, fg_color='#D68910' if ativo else '#444444', hover_color='#B9770E', font=('Arial', 13, 'bold'), command=lambda ref=item: self.abrir_janela_edicao(ref))
            btn_editar.pack(side='left', padx=5)
            btn_remover = ctk.CTkButton(frame_botoes, text='Remover', width=70, height=35, fg_color='#C62828' if ativo else '#444444', hover_color='#8E0000', font=('Arial', 13, 'bold'), command=lambda i=idx: self.remover_horario(i))
            btn_remover.pack(side='left', padx=5)
            info_frame = ctk.CTkFrame(card, fg_color='transparent')
            info_frame.pack(side='left', fill='both', expand=True, padx=10)
            tag_text = f'{txt_lang}   ' if txt_lang else ''
            ctk.CTkLabel(info_frame, text=f'{tag_text}{txt_repeticao}   |   {icone}   |   Vol: {vol_show}', font=('Arial', 11, 'bold'), text_color=cor_lang if txt_lang else cor_repeticao, anchor='w').pack(fill='x')
            lbl_desc = ctk.CTkLabel(info_frame, text=desc, font=('Arial', 16), text_color=cor_texto_principal, anchor='w')
            lbl_desc.pack(fill='x', pady=(2, 0))
if __name__ == '__main__':
    garantir_instancia_unica()
    if not os.path.exists('audios'):
        os.makedirs('audios')
    app = SistemaSinal()
    app.mainloop()
