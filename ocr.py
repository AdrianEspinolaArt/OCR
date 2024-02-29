import pytesseract
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import tempfile
import re

# Função para carregar a imagem selecionada
def carregar_imagem():
    # Abrir uma caixa de diálogo para selecionar a imagem
    global imagem_path
    imagem_path = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=[("Imagens", "*.jpg *.png")])

    # Verificar se o usuário selecionou uma imagem
    if imagem_path:
        # Carregar a imagem usando PIL (Pillow)
        imagem_pillow = Image.open(imagem_path)

        # Redimensionar a imagem para caber na interface gráfica
        imagem_pillow = imagem_pillow.resize((600, 400), Image.BICUBIC)

        # Converter a imagem para o formato suportado pelo tkinter
        imagem_tk = ImageTk.PhotoImage(imagem_pillow)

        # Exibir a imagem na interface gráfica
        imagem_label.config(image=imagem_tk)
        imagem_label.image = imagem_tk

# Função para realizar OCR no arquivo original selecionado
        
def detectar_bordas(imagem):
    # Converter a imagem para tons de cinza
    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    # Aplicar o detector de bordas Canny
    bordas = cv2.Canny(imagem_cinza, 100, 200)
    # Verificar se há bordas detectadas
    if cv2.countNonZero(bordas) == 0:
        return False  # Nenhuma borda detectada
    else:
        return True  # Bordas detectadas
    
def verificar_ocr_previo(imagem):
    caminho_tesseract = r"C:\Users\adrian.espinola\AppData\Local\Programs\Tesseract-OCR"
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract + r'\tesseract.exe'
    # Realizar uma verificação preliminar de OCR na imagem
    texto = pytesseract.image_to_string(imagem, lang="por")
    # Verificar se o texto extraído é vazio
    if not texto:
        return False  # Nenhum texto extraído
    else:
        return True  # Texto extraído    

def verificar_ruido(imagem):
    # Aplicar filtro de redução de ruído Gaussiano
    imagem_filtrada = cv2.GaussianBlur(imagem, (5, 5), 0)
    # Calcular a diferença absoluta entre a imagem original e a filtrada
    diferenca = cv2.absdiff(imagem, imagem_filtrada)
    # Converter a imagem de diferença para tons de cinza
    diferenca_cinza = cv2.cvtColor(diferenca, cv2.COLOR_BGR2GRAY)
    # Calcular a média da diferença absoluta
    media_diferenca = cv2.mean(diferenca_cinza)[0]
    # Se a média for alta, pode indicar presença de ruído
    if media_diferenca > 10:
        return False  # Presença de ruído
    else:
        return True  # Sem ruído significativo 
    
def verificar_resolucao(imagem):
    altura, largura = imagem.shape[:2]
    # Definir uma resolução mínima desejada
    resolucao_minima = 1000 # Exemplo de resolução mínima
    # Verificar se a resolução atende ao mínimo desejado
    if altura < resolucao_minima or largura < resolucao_minima:
        return False  # Resolução muito baixa
    else:
        return True  # Resolução adequada       



def realizar_ocr():
    global imagem_path
    # Verificar se um arquivo de imagem foi selecionado
    if imagem_path:
        # Carregar a imagem
        imagem = cv2.imread(imagem_path)
        
        # Verificar a qualidade da imagem
        if not detectar_bordas(imagem):
            tk.messagebox.showwarning("Aviso", "Por favor, verifique as bordas da imagem do documento.")
            return
        elif not verificar_ocr_previo(imagem):
            tk.messagebox.showwarning("Aviso", "Não foi possível extrair texto da imagem do documento.")
            return
        elif not verificar_ruido(imagem):
            tk.messagebox.showwarning("Aviso", "Por favor, verifique o ruído na imagem do documento.")
            return
        elif not verificar_resolucao(imagem):
            tk.messagebox.showwarning("Aviso", "Por favor, verifique a resolução da imagem do documento.")
            return

        # Configurar o caminho do Tesseract
        caminho_tesseract = r"C:\Users\adrian.espinola\AppData\Local\Programs\Tesseract-OCR"
        pytesseract.pytesseract.tesseract_cmd = caminho_tesseract + r'\tesseract.exe'

        # Realizar OCR no arquivo selecionado
        texto = pytesseract.image_to_string(imagem_path, lang="por")
        
        # Exibir o texto extraído na interface gráfica
        resultado_texto.config(state="normal")
        resultado_texto.delete("1.0", tk.END)
        resultado_texto.insert(tk.END, texto)
        resultado_texto.config(state="disabled")
    else:
        # Exibir mensagem de aviso se nenhum arquivo foi selecionado
        tk.messagebox.showwarning("Aviso", "Por favor, selecione um arquivo de imagem primeiro.")


# Criar a janela principal
root = tk.Tk()
root.title("OCR App")
root.geometry("800x600")

# Criar um frame para a imagem
imagem_frame = tk.Frame(root)
imagem_frame.pack()

# Criar um label para exibir a imagem
imagem_label = tk.Label(imagem_frame)
imagem_label.pack()

# Criar um botão para selecionar arquivo
selecionar_button = tk.Button(root, text="Selecionar Arquivo", command=carregar_imagem)
selecionar_button.pack(side="left", padx=10)

# Criar um botão para realizar o OCR
ocr_button = tk.Button(root, text="Realizar OCR", command=realizar_ocr)
ocr_button.pack(side="left")

# Criar um widget para exibir o resultado do OCR
resultado_texto = tk.Text(root, height=10, width=50, state="disabled")
resultado_texto.pack()

# Iniciar o loop principal
root.mainloop()
