# Configurações e Requisitos

## Requisitos

Antes de rodar o projeto, instale as dependências necessárias:

```bash

pip  install  -r  requirements.txt

```

### Conteúdo do arquivo `requirements.txt`:

  

```text

numpy==1.26.4

opencv-python==4.10.0.84

mediapipe==0.10.18

playsound==1.2.2

```

⚠️ **IMPORTANTE:**

-  **mediapipe**: Requer a instalação do  [ **Microsoft Visual C++ Redistributable for Visual Studio 2015-2022**](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-160).

-  **playsound**: Pode ser necessária a instalação do **wheel** para funcionar corretamente. Caso haja algum erro durante a instalação, execute o comando abaixo e tente novamente:

```bash

pip install wheel

```

## Execução

  

**1.  Verifique se a câmera está conectada**.

**2.  Execute o script `main.py`:**

```bash

python  main.py

```

**3.  Interaja com a aplicação:**

- O programa exibirá a captura de vídeo em tempo real. O usuário deve manter uma postura adequada durante a calibração inicial para garantir melhores resultados.

- Caso a postura esteja incorreta, o programa exibirá um alerta em vermelho na tela e emitirá um som após o usuário permanecer com a postura inadequada por 3 segundos. O sistema possui um intervalo de 10 segundos entre os alertas (configuração padrão).

- Para encerrar o programa, pressione `q` na janela de vídeo.