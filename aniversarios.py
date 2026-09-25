import customtkinter as ctk
from tkinter import messagebox

import dados


class JanelaAniversarios(ctk.CTkToplevel):
    """Editor simples do banco de aniversariantes usado pelo JamesVox.

    Este módulo foi reimplementado durante a recuperação do projeto porque o
    fonte original de aniversarios.py não estava entre os arquivos recuperados.
    """

    def __init__(self, master, motor=None):
        super().__init__(master)
        self.motor = motor
        self.title("Central de Aniversariantes")
        self.geometry("620x560")
        self.minsize(560, 500)
        self.transient(master)
        self.grab_set()

        self.alunos = dados.carregar_aniversarios()

        ctk.CTkLabel(
            self,
            text="Central de Aniversariantes",
            font=("Arial", 22, "bold"),
        ).pack(pady=(20, 10))

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(form, text="Nome").grid(
            row=0, column=0, padx=10, pady=(10, 3), sticky="w"
        )
        self.entry_nome = ctk.CTkEntry(form, placeholder_text="Nome do aluno")
        self.entry_nome.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="ew"
        )

        ctk.CTkLabel(form, text="Nascimento (DD/MM/AAAA)").grid(
            row=0, column=1, padx=10, pady=(10, 3), sticky="w"
        )
        self.entry_data = ctk.CTkEntry(form, placeholder_text="24/11/2002")
        self.entry_data.grid(
            row=1, column=1, padx=10, pady=(0, 10), sticky="ew"
        )

        form.grid_columnconfigure(0, weight=2)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            form,
            text="Adicionar",
            command=self.adicionar,
            fg_color="#27AE60",
            hover_color="#1E8449",
        ).grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.lista = ctk.CTkScrollableFrame(self)
        self.lista.pack(fill="both", expand=True, padx=20, pady=10)

        self.atualizar_lista()

    def adicionar(self):
        nome = self.entry_nome.get().strip()
        data = self.entry_data.get().strip()

        if not nome:
            messagebox.showerror("Erro", "Informe o nome.", parent=self)
            return

        partes = data.split("/")
        if len(partes) not in (2, 3):
            messagebox.showerror(
                "Erro",
                "Use DD/MM ou DD/MM/AAAA.",
                parent=self,
            )
            return

        try:
            dia = int(partes[0])
            mes = int(partes[1])
            if not 1 <= dia <= 31 or not 1 <= mes <= 12:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Data inválida.", parent=self)
            return

        self.alunos.append({"nome": nome, "data_nasc": data})
        self.alunos.sort(key=lambda item: (item.get("data_nasc", "")[3:5], item.get("data_nasc", "")[:2], item.get("nome", "")))
        self.salvar()

        self.entry_nome.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.atualizar_lista()

    def remover(self, indice):
        del self.alunos[indice]
        self.salvar()
        self.atualizar_lista()

    def salvar(self):
        dados.salvar_aniversarios(self.alunos)

        if self.motor is not None:
            try:
                self.motor.preparar_aniversarios_do_dia()
            except Exception:
                pass

    def atualizar_lista(self):
        for widget in self.lista.winfo_children():
            widget.destroy()

        if not self.alunos:
            ctk.CTkLabel(
                self.lista,
                text="Nenhum aniversariante cadastrado.",
                text_color="gray",
            ).pack(pady=20)
            return

        for indice, aluno in enumerate(self.alunos):
            linha = ctk.CTkFrame(self.lista)
            linha.pack(fill="x", padx=5, pady=4)

            ctk.CTkLabel(
                linha,
                text=aluno.get("nome", ""),
                anchor="w",
                font=("Arial", 14, "bold"),
            ).pack(side="left", padx=10, pady=8, fill="x", expand=True)

            ctk.CTkLabel(
                linha,
                text=aluno.get("data_nasc", ""),
                width=110,
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                linha,
                text="Remover",
                width=80,
                fg_color="#C62828",
                hover_color="#8E0000",
                command=lambda i=indice: self.remover(i),
            ).pack(side="right", padx=8, pady=6)
