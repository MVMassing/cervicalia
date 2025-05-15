# Desenvolvimento da Solução

## Funções


-   **`calcular_angulo(ponto1, ponto2, ponto3)`**: recebe três pontos no plano 2D e calcula o ângulo utilizado para verificar a inclinação dos ombros e do pescoço.
-   **`desenhar_angulo(frame, ponto1, ponto2, ponto3, angulo, cor)`**: Desenha o ângulo na tela.
-   **`feedback_postura(angulo_ombro, limite_ombro_min, limite_ombro_max, angulo_pescoco, limite_pescoco_min, limite_pescoco_max)`**: Fornece o feedback sobre a postura, exibindo seu status e dados, disparando o alerta sonoro, se necessário.

  ### Como Funciona

**1.  Processamento de Posições e Cálculo de Ângulos**: 
-   O código usa `resultados.pose_landmarks` para acessar os pontos-chave do corpo detectados pelo MediaPipe.
    
-   Extração dos pontos de interesse:
    
    -   **Ombro esquerdo** e **ombro direito**: Usados para calcular a posição do tronco.
    -   **Orelha esquerda** e **orelha direita**: Usados para calcular a posição do pescoço.
-   Cálculo dos ângulos:
    
    -   **`angulo_ombro`**: O ângulo entre os ombros é calculado entre os pontos do ombro esquerdo, ombro direito e um ponto fixo no eixo X (representado por `(ombro_direito[0], 0)`).
    -   **`angulo_pescoco`**: O ângulo entre a orelha esquerda, o ombro esquerdo e um ponto fixo no eixo X (representado por `(ombro_esquerdo[0], 0)`).

**2.  Processo de Calibração**: Durante os primeiros 30 quadros, o código coleta os ângulos dos ombros e pescoço em cada quadro e os armazena nas listas **`calibracao_angulo_ombro`** e **`calibracao_angulo_pescoco`**.

**3.  Detecção de Postura**: Após a calibração, os ângulos de ombro e pescoço são monitorados em tempo real. Se os ângulos saírem dos limites definidos durante a calibração, o sistema considera que a postura está ruim. A variável `margem` pode ser ajustada conforme necessário pelo usuário, representando a tolerância em graus.

**4.  Alerta Sonoro**: Se o usuário permanecer com a postura ruim por um tempo mínimo (definido pela variável `tempo_minimo_postura_ruim`), o sistema dispara um alerta sonoro. O intervalo entre os alertas também pode ser configurado por meio da variável `tempo_minimo_postura_ruim`, também medida em segundos.