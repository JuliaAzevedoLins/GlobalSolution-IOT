from tkinter import *
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import requests
import os

from gesture_detector import detectar_gesto
from utils import get_latlon_from_endereco

# Variáveis globais para os campos do formulário
entry_nome = None
entry_email = None
entry_cep = None
entry_logradouro = None
entry_bairro = None
entry_cidade = None
entry_estado = None
entry_numero = None

# Janela principal (root)
root = None
logo_image = None

# --- Funções de Navegação e Lógica ---

def mostrar_tela(frame_para_mostrar):
    global root
    for frame in [tela_inicial, formulario_parte1, formulario_parte2]:
        frame.grid_forget()

    # Ajusta o tamanho da janela dinamicamente
    if frame_para_mostrar == tela_inicial:
        root.geometry("600x550")
    elif frame_para_mostrar == formulario_parte1:
        root.geometry("600x520")
    elif frame_para_mostrar == formulario_parte2:
        root.geometry("600x650")

    frame_para_mostrar.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

def buscar_endereco():
    cep = entry_cep.get().strip()
    if not cep:
        messagebox.showwarning("CEP Vazio", "Por favor, digite um CEP.")
        return

    cep_limpo = ''.join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        messagebox.showwarning("CEP Inválido", "O CEP deve conter 8 dígitos.")
        return

    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
        data = response.json()

        if "erro" in data:
            messagebox.showerror("CEP Não Encontrado", "CEP não encontrado ou inválido.")
            limpar_campos_endereco()
            return

        entry_logradouro.set(data.get('logradouro', ''))
        entry_bairro.set(data.get('bairro', ''))
        entry_cidade.set(data.get('localidade', ''))
        entry_estado.set(data.get('uf', ''))

        messagebox.showinfo("Endereço Encontrado", "Endereço preenchido com sucesso! Por favor, insira o número e confirme.")
        mostrar_tela(formulario_parte2)

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao ViaCEP: {e}")
        limpar_campos_endereco()
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao buscar o CEP: {e}")
        limpar_campos_endereco()

def limpar_campos_endereco():
    entry_logradouro.set("")
    entry_bairro.set("")
    entry_cidade.set("")
    entry_estado.set("")
    if entry_numero and entry_numero.winfo_exists():
        entry_numero.delete(0, END)

def iniciar_sistema_completo():
    nome = entry_nome.get().strip()
    cep = entry_cep.get().strip()
    email = entry_email.get().strip()
    logradouro = entry_logradouro.get().strip()
    numero = entry_numero.get().strip()
    bairro = entry_bairro.get().strip()
    cidade = entry_cidade.get().strip()
    estado = entry_estado.get().strip()

    if not all([nome, email, cep, logradouro, numero, bairro, cidade, estado]):
        messagebox.showwarning("Campos obrigatórios", "Por favor, preencha todos os campos do formulário, incluindo o número.")
        return

    endereco_completo = f"{logradouro}, {numero}, {bairro}, {cidade}, {estado}, Brasil"

    messagebox.showinfo("Sistema iniciado", f"Olá {nome}! Ativando detecção de gestos para {endereco_completo}...")
    root.destroy()
    detectar_gesto(nome, [email], cep, endereco_completo)

# --- Configuração da Janela Principal ---
root = ThemedTk(theme="forest-dark")
root.title("Alertaê - Sistema de Alerta por Gesto")
root.geometry("600x550")
root.resizable(True, True)

# Tentar definir um ícone para a janela (opcional)
icon_path_ico = "icon.ico"
icon_path_png = "icon.png"

if os.path.exists(icon_path_ico):
    root.iconbitmap(icon_path_ico)
elif os.path.exists(icon_path_png):
    try:
        photo = PhotoImage(file=icon_path_png)
        root.iconphoto(False, photo)
    except Exception as e:
        print(f"Não foi possível carregar o ícone PNG: {e}")

# --- Estilos Personalizados ---
style = ttk.Style()
style.configure('TLabel', font=('Roboto', 11))
style.configure('TEntry', font=('Roboto', 11), padding=(8, 8))
style.configure('TButton', font=('Roboto', 11, 'bold'), padding=(10, 5))
style.configure('Accent.TButton', font=('Roboto', 12, 'bold'), padding=(12, 7))

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# --- Tela Inicial ---
tela_inicial = ttk.Frame(root, style='Card.TFrame')

# Carregar e exibir o logo.png
logo_path = "logo.png"
if os.path.exists(logo_path):
    try:
        logo_image = PhotoImage(file=logo_path)
        logo_label = ttk.Label(tela_inicial, image=logo_image)
        logo_label.image = logo_image  # Mantém referência
        logo_label.pack(pady=(40, 10))
    except Exception as e:
        print(f"Erro ao carregar o logo: {e}")
        ttk.Label(tela_inicial, text="[LOGO AQUI]", font=('Roboto', 16, 'bold')).pack(pady=(40,10))
else:
    ttk.Label(tela_inicial, text="[LOGO AQUI]", font=('Roboto', 16, 'bold')).pack(pady=(40,10))

titulo = ttk.Label(tela_inicial, text="Bem-vindo ao Alertaê",
                   font=("Roboto", 24, "bold"), anchor="center")
titulo.pack(pady=(10, 20))

subtitulo = ttk.Label(tela_inicial, text="Seu sistema inteligente de detecção de gestos para emergências",
                      font=("Roboto", 13), anchor="center", wraplength=450)
subtitulo.pack(pady=15)

btn_iniciar = ttk.Button(tela_inicial, text="INICIAR SISTEMA",
                         command=lambda: mostrar_tela(formulario_parte1),
                         style="Accent.TButton")
btn_iniciar.pack(pady=40, ipadx=30, ipady=15)

tela_inicial.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

# --- Formulário Parte 1 (Dados Pessoais e CEP) ---
formulario_parte1 = ttk.Frame(root, padding=(40, 30), style='Card.TFrame')

msg_parte1 = ttk.Label(formulario_parte1, text="Parte 1/2: Dados Pessoais e CEP",
                       font=("Roboto", 14, "bold"))
msg_parte1.grid(row=0, column=0, columnspan=2, pady=(0, 25), sticky="w")

formulario_parte1.grid_columnconfigure(0, weight=0)
formulario_parte1.grid_columnconfigure(1, weight=1)

row_idx = 1
ttk.Label(formulario_parte1, text="Nome completo:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_nome = ttk.Entry(formulario_parte1)
entry_nome.grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte1, text="E-mail para notificações:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_email = ttk.Entry(formulario_parte1)
entry_email.grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte1, text="CEP:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_cep = ttk.Entry(formulario_parte1)
entry_cep.grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
btn_buscar_cep = ttk.Button(formulario_parte1, text="Buscar Endereço e Próximo",
                            command=buscar_endereco, style="Accent.TButton")
btn_buscar_cep.grid(row=row_idx, column=0, columnspan=2, pady=(30, 10), ipadx=20, ipady=10)

# --- Formulário Parte 2 (Endereço Completo e Número) ---
formulario_parte2 = ttk.Frame(root, padding=(40, 30), style='Card.TFrame')

msg_parte2 = ttk.Label(formulario_parte2, text="Parte 2/2: Confirme o Endereço e adicione o Número",
                       font=("Roboto", 14, "bold"))
msg_parte2.grid(row=0, column=0, columnspan=2, pady=(0, 25), sticky="w")

formulario_parte2.grid_columnconfigure(0, weight=0)
formulario_parte2.grid_columnconfigure(1, weight=1)

row_idx = 1
ttk.Label(formulario_parte2, text="Logradouro:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_logradouro = StringVar()
ttk.Entry(formulario_parte2, textvariable=entry_logradouro, state='readonly').grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte2, text="Bairro:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_bairro = StringVar()
ttk.Entry(formulario_parte2, textvariable=entry_bairro, state='readonly').grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte2, text="Cidade:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_cidade = StringVar()
ttk.Entry(formulario_parte2, textvariable=entry_cidade, state='readonly').grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte2, text="Estado (UF):").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_estado = StringVar()
ttk.Entry(formulario_parte2, textvariable=entry_estado, state='readonly').grid(row=row_idx, column=1, sticky="ew", pady=(10, 5))

row_idx += 1
ttk.Label(formulario_parte2, text="Número:").grid(row=row_idx, column=0, sticky="w", pady=(10, 0), padx=(0, 10))
entry_numero = ttk.Entry(formulario_parte2)
entry_numero.grid(row=row_idx, column=1, sticky="ew", pady=(10, 20))

button_frame = ttk.Frame(formulario_parte2)
button_frame.grid(row=row_idx + 1, column=0, columnspan=2, sticky="ew", pady=(20, 0))
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

btn_voltar_parte1 = ttk.Button(button_frame, text="← Voltar",
                               command=lambda: mostrar_tela(formulario_parte1))
btn_voltar_parte1.grid(row=0, column=0, sticky="w", padx=(0, 10), ipadx=10, ipady=5)

btn_iniciar_sistema = ttk.Button(button_frame, text="INICIAR SISTEMA",
                                 command=iniciar_sistema_completo,
                                 style="Accent.TButton")
btn_iniciar_sistema.grid(row=0, column=1, sticky="e", ipadx=20, ipady=10)

root.mainloop()