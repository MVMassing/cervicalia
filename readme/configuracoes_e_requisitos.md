# ⚙️ Configurações e Requisitos

## Requisitos

Antes de rodar o projeto, certifique-se de instalar todas as dependências necessárias:

```bash
pip install -r requirements.txt

```

### Conteúdo do arquivo `requirements.txt`:

  

```text

kivy==2.3.0
kivymd==1.2.0
opencv-python==4.10.0.84
mediapipe==0.10.18
numpy==1.26.4
playsound==1.2.2
wheel==0.43.0
pandas==2.2.1
matplotlib==3.8.3
openpyxl==3.1.2

```

⚠️ **IMPORTANTE:**

-  **mediapipe**: Requer a instalação do  [ **Microsoft Visual C++ Redistributable for Visual Studio 2015-2022**](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-160).

## Execução
 
### **1.  Verifique se a câmera está conectada**.

### **2.  Execute o script `main.py`:**

```bash

python  main.py

```

### **2.1. Alternativamente, baixe o executável disponível na página de releases.**

### **3. O programa criará automaticamente um banco de dados SQLite na primeira execução.**
   - O banco será criado no mesmo diretório do executável
   - Nome do arquivo: `posture_data.db`

### **4.  Interaja com a aplicação:**

- Após a execução, o programa exibirá uma tela com as opções disponíveis.

- Se o usuário escolher a opção com visão lateral, será necessário instalar o aplicativo DroidCam no celular via [(Google Play)](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam&hl=pt_BR) ou [(App Store)](https://play.google.com/store/apps/details?id=com.dev47apps.droidcam&hl=pt_BR).

⚠️ **IMPORTANTE:**

- O endereço IP da câmera lateral deve seguir o formato:`http://192.168.X.XXX:4747/video` e o aplicativo Droidcam deverá estar aberto no momento da conexão, **caso contrário, a câmera lateral não será conectada**. Problemas de conexão podem ocorrer, recomenda-se reiniciar ambas aplicações ou tentar novamente nesses casos.

- Caso a postura esteja incorreta, o programa exibirá um alerta em vermelho na tela e emitirá um som após o usuário permanecer com a postura inadequada por 5 segundos. O sistema possui um intervalo de 10 segundos entre os alertas (configuração padrão).

- Relatórios podem ser consultados e exportados na tela de dados e estatísticas.