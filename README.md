# JamesVox

Sistema desktop para automação de sinais, avisos por voz e reprodução de áudio em ambientes escolares.

O JamesVox foi desenvolvido em Python com uma interface gráfica baseada em CustomTkinter. A aplicação permite programar horários, tocar sinais e playlists, gerar avisos falados e manter uma rotina automática de reprodução ao longo do dia.

> **Estado do projeto:** versão recuperada e reconstruída a partir de uma distribuição executável do próprio sistema após a perda do código-fonte original. A maior parte das funcionalidades foi restaurada, mas alguns comportamentos ainda estão em revisão.

---

## Principais funcionalidades

- Agendamento de sinais por horário
- Seleção dos dias da semana em que cada evento deve ocorrer
- Alternância entre **Semana 1** e **Semana 2**
- Eventos de execução única
- Reprodução imediata de eventos
- Reprodução de arquivos `.mp3`, `.wav` e `.ogg`
- Reprodução contínua de playlists por intervalo de horário
- Histórico de músicas para reduzir repetições
- Controle individual de volume
- Sistema de *ducking* para reduzir a música durante avisos falados
- Avisos por voz com **Edge TTS**
- Integração opcional com **ElevenLabs**
- Velocidade configurável de fala
- Avisos em português e inglês
- Modo bilíngue
- Cadastro e anúncio automático de aniversariantes
- Mensagem/versículo diário
- Minimização para a bandeja do Windows
- Bloqueio de múltiplas instâncias do programa
- Persistência local através de arquivos JSON
- Registro de eventos em `jamesvox.log`

---

## Interface

A aplicação foi pensada para permanecer aberta durante o funcionamento da escola.

Na tela principal é possível configurar:

- horário inicial;
- horário final;
- dias da semana;
- frequência;
- volume;
- uso ou não de voz;
- idioma;
- voz utilizada;
- velocidade da fala;
- texto personalizado;
- arquivo de áudio ou pasta de playlist.

Os eventos configurados são exibidos em uma timeline e podem ser ativados, editados ou removidos.

---

## Tecnologias utilizadas

| Tecnologia | Uso |
|---|---|
| Python | Linguagem principal |
| Tkinter | Base da interface desktop |
| CustomTkinter | Componentes visuais da interface |
| Pygame | Reprodução e controle de áudio |
| Edge TTS | Síntese de voz neural |
| ElevenLabs API | Vozes adicionais opcionais |
| Pillow | Manipulação de imagens |
| Pystray | Ícone na bandeja do Windows |
| Requests | Comunicação HTTP |
| JSON | Persistência local dos dados |

---

## Estrutura do projeto

```text
JamesVox/
├── main.py
├── dados.py
├── motor_audio.py
├── motor_voz.py
├── aniversarios.py
├── manual.py
├── requirements.txt
├── README.md
├── .gitignore
└── audios/
```

### `main.py`

Contém a interface principal do programa e a maior parte da interação com o usuário.

### `motor_audio.py`

Responsável pelo relógio interno, filas de reprodução, sinais, playlists, canais de áudio, controle de volume e execução automática dos eventos.

### `motor_voz.py`

Responsável pela geração de áudio por voz, integração com Edge TTS e ElevenLabs, cache de vozes, amostras e conversão de horários para texto.

### `dados.py`

Centraliza a leitura e gravação dos arquivos JSON utilizados pela aplicação.

### `aniversarios.py`

Interface para gerenciamento da lista de aniversariantes.

### `manual.py`

Conteúdo da ajuda integrada ao programa.

---

## Executando pelo código-fonte

### Requisitos

- Windows
- Python 3.13 recomendado
- conexão com a internet para recursos de TTS online

Clone o repositório e entre na pasta:

```bash
git clone <URL-DO-SEU-REPOSITORIO>
cd JamesVox
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente no Windows:

```bat
.venv\Scripts\activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

Não é necessário gerar um `.exe` para utilizar o sistema.

---

## Arquivos gerados durante a execução

O JamesVox cria alguns arquivos locais conforme é utilizado:

```text
horarios.json
aniversarios.json
config.json
historico_playlists.json
vozes_cache.json
previews_cache.json
creditos_ia.json
versiculos.txt
jamesvox.log
```

Também podem ser criados áudios temporários dentro de:

```text
audios/
```

Esses arquivos representam dados locais da instalação e, por padrão, não são versionados pelo Git.

---

## Voz neural

O JamesVox possui duas formas principais de geração de voz.

### Edge TTS

É utilizado para vozes neurais disponíveis através do serviço da Microsoft.

Exemplos:

```text
pt-BR-FranciscaNeural
pt-BR-AntonioNeural
en-US-AriaNeural
```

### ElevenLabs

A integração com ElevenLabs é opcional.

Quando configurada, a aplicação pode:

- sincronizar vozes disponíveis;
- armazenar IDs de voz localmente;
- consultar saldo de caracteres;
- baixar amostras;
- gerar arquivos de áudio através da API.

A chave da API não deve ser adicionada ao repositório.

---

## Modo bilíngue

Existe suporte para avisos combinando português e inglês.

Nesta versão recuperada, o modo bilíngue **ainda está em revisão**. Em alguns casos, um trecho em inglês pode acabar sendo enviado para uma voz configurada para português, produzindo pronúncia com sotaque inadequado.

Esse comportamento está entre os pontos que ainda precisam ser corrigidos na reconstrução do projeto.

---

## Aniversariantes

O sistema pode verificar diariamente os aniversariantes cadastrados e preparar automaticamente os áudios do dia.

É possível configurar:

- horário do anúncio;
- idioma;
- voz em português;
- voz em inglês;
- texto para um aniversariante;
- texto para múltiplos aniversariantes.

Os dados são armazenados localmente em:

```text
aniversarios.json
```

---

## Semana 1 e Semana 2

O JamesVox permite alternar eventos quinzenais usando os modos:

```text
Toda Semana
Semana 1
Semana 2
```

A semana atual é calculada automaticamente a partir de uma data de referência e pode ser invertida pelas configurações.

---

## Recuperação do código-fonte

O código-fonte original deste projeto foi perdido, mas uma versão compilada com PyInstaller ainda estava disponível.

A recuperação envolveu:

1. extração dos arquivos internos do executável;
2. recuperação dos módulos `.pyc`;
3. decompilação do bytecode Python;
4. análise manual das funções que não foram reconstruídas corretamente;
5. comparação com o bytecode original;
6. reconstrução das partes corrompidas;
7. reorganização do projeto para voltar a ser executável diretamente pelo Python.

Por esse motivo, esta versão pode não ser textualmente idêntica ao código-fonte original, embora preserve grande parte de sua estrutura e comportamento.

---

## Estado atual

### Recuperado

- interface principal;
- persistência de dados;
- motor de áudio;
- playlists;
- eventos agendados;
- reprodução imediata;
- Edge TTS;
- integração ElevenLabs;
- controle de saldo;
- cache de vozes;
- aniversariantes;
- manual interno;
- lógica de Semana 1 / Semana 2.

### Em revisão

- comportamento do modo bilíngue;
- alguns detalhes visuais reconstruídos a partir do bytecode;
- testes completos de todas as combinações de eventos;
- equivalência integral com o código-fonte perdido.

---

## Motivação

O JamesVox nasceu como uma ferramenta prática para automatizar sinais e avisos de uma instituição de ensino, substituindo tarefas que precisavam ser executadas manualmente ao longo do dia.

Além do uso real da aplicação, o projeto envolve conceitos de:

- interfaces desktop;
- programação concorrente;
- manipulação de áudio;
- filas de execução;
- persistência de dados;
- integração com APIs;
- síntese de voz;
- gerenciamento de estado;
- automação baseada em horário.

---

## Aviso

Este repositório contém uma reconstrução de um projeto originalmente desenvolvido pelo autor.

Credenciais, chaves de API, arquivos de configuração pessoais e dados utilizados em produção não devem ser adicionados ao Git.

---

## Autor

**Thiago Monteiro**

Projeto desenvolvido originalmente para automação de sinais e avisos escolares.
