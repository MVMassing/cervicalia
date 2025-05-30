<p align="center">
  <img src="readme/img/logo.png" alt="Logo" width="300" height="300">
</p>

_Matheus Vinícius Pires Massing_

Este artigo apresenta a documentação do projeto **Cervicalia**, em conformidade com os requisitos da disciplina de Projeto de Desenvolvimento II, do curso de Análise e Desenvolvimento de Sistemas do Centro Universitário Senac-RS.

### 🚧 Projeto em desenvolvimento!
Para acompanhar o progresso das implementações descritas na documentação, [acesse a branch dev](https://github.com/MVMassing/cervicalia/tree/dev)

## Resumo do Projeto

A má postura adquirida durante longos períodos de home office ou estudo é uma das principais causas de dores crônicas no pescoço e nas costas. Essa condição compromete a saúde física e mental de milhões de trabalhadores e estudantes no mundo todo. O Cervicalia propõe uma solução tecnológica que utiliza visão computacional com múltiplas câmeras para detectar e alertar em tempo real sobre desvios posturais. Como consequência, a ferramenta promove maior consciência corporal, prevenção de lesões e aumento da produtividade, através de relatórios personalizados e notificações inteligentes.

## Definição do Problema

O crescimento do trabalho remoto e o aumento das horas de estudo em casa expuseram um problema silencioso, porém crescente: a má postura mantida por longos períodos sem correção imediata. Estudos indicam que 80% da população mundial relata dores posturais em algum momento da vida [(CNN Brasil)](https://www.cnnbrasil.com.br/saude/dores-nas-costas-atingem-80-da-populacao-mundial-veja-causas-e-como-evita-las/)
, o que resulta em redução de produtividade, aumento de afastamentos médicos, e custos com tratamentos fisioterapêuticos.

A maioria das soluções atuais de correção postural exige sensores físicos ou wearables, o que eleva o custo e dificulta a adoção em larga escala. Além disso, muitas ferramentas carecem de relatórios analíticos e não oferecem integração entre dispositivos móveis e desktops.

## Objetivos

### Objetivo Geral

Desenvolver uma aplicação multiplataforma capaz de detectar, alertar e documentar desvios de postura utilizando visão computacional e integração entre desktop e dispositivos móveis.

### Objetivos Específicos

* Implementar a detecção de postura com duas câmeras (webcam e celular). ✅

* Exibir alertas visuais e sonoros em tempo real em caso de má postura. ✅

* Gerar dashboards interativos com horários críticos e progresso postural. ⏳

* Permitir sincronização de dados entre app Android e aplicativo desktop. ⏳

## Stack Tecnológico

#### Backend / Desktop

| Função                 | Tecnologia            |
|------------------------|------------------------|
| Backend/Desktop        | Python                |
| Visão Computacional    | OpenCV + MediaPipe    |
| Interface Desktop      | Kivy + KivyMD         |
| API Local              | FastAPI               |
| Processamento de Dados | Pandas + Matplotlib   |

#### App Android

| Função                | Tecnologia              |
|------------------------|--------------------------|
| Framework             | Kivy + KivyMD            |
| Conexão da Câmera     | DroidCam (USB/Wi-Fi)     |

#### Banco de Dados & Sincronização

| Função               | Tecnologia |
|----------------------|------------|
| Banco Local (Desktop)| SQLite     |
| Banco na Nuvem       | Firebase   |

#### Infraestrutura & Deploy

| Componente             | Tecnologia |
|------------------------|------------|
| Deploy Frontend (Web)  | Vercel     |
| Deploy Backend (API)   | Render     |
| Versionamento          | Git + GitHub |


## Descrição da Solução

O Cervicalia é um sistema de correção postural que utiliza duas câmeras (webcam e celular) para monitorar a postura do usuário em tempo real. A aplicação desktop realiza a análise de imagem com MediaPipe e emite alertas sonoros e visuais sempre que a postura correta não é mantida por mais de alguns segundos.

A interface do sistema permitirá que o usuário visualize gráficos de progresso e exporte relatórios, com o aplicativo Android atuando como visualizador e configurador remoto.

A sincronização ocorrerá por meio de um banco local (SQLite) e uma base na nuvem (Firebase), garantindo funcionalidade offline e mobilidade entre dispositivos.

## Arquitetura

O Cervicalia segue um modelo híbrido, combinando elementos de MVC (Model-View-Controller) e Camadas Lógicas, adaptado para sistemas de visão computacional e sincronização multiplataforma.

### Fluxo de Funcionamento

**1. Captura da Imagem**
- **Webcam (frontal):** Monitora ombros e pescoço.
- **Celular (lateral via DroidCam):** Analisa curvatura cervical.

**2. Processamento em Tempo Real**
- **MediaPipe + OpenCV:** Detectam pontos-chave do corpo.
- **Algoritmo de Ângulos:** Calcula inclinação dos ombros e pescoço.

**3. Feedback e Alertas**
- **Sonoro, via playsound:** `alert.wav`.
- **Visual:** Via KivyMD indicando a qualidade da postura.

**4. Armazenamento Local**
- **SQLite:** Registra eventos de má postura.

**5. Sincronização (Futuro)**
- **Firebase:** Recebe dados do desktop para o app Android.

**6. Relatórios (em progresso)**
- **Pandas + Matplotlib:** Geram gráficos e exportam arquivos em CSV/PDF.

---

### Modelo de Arquitetura

* ![Arquitetura](readme/img/arquitetura.png)

---

## Visão Lógica

### Banco de Dados

Está sendo desenvolvida solução que registra os dados usando SQLite com uma estrutura semelhante a:

| id | timestamp           | angulo_ombro | angulo_pescoco | camera  |
|----|---------------------|--------------|----------------|----------------|
| 1  | 2025-05-13 10:45:00 | 65.2         | 42.8           | Lateral |
| 2  | 2025-05-13 10:47:00 | 68.2         | 43.6           | Frontal |

Tal solução visa criar um banco de dados para embasar os dashboards e estatísticas no app mobile.

### Estrutura da Tabela: `postura`

| Coluna          | Tipo SQLite          | Restrições / Validação                                        |
|-----------------|----------------------|--------------------------------------------------------------|
| `id`            | INTEGER              | PRIMARY KEY AUTOINCREMENT                                    |
| `timestamp`     | TEXT                 | NOT NULL (formato ISO 8601 recomendado)                      |
| `angulo_ombro`  | REAL                 | NOT NULL (valor numérico representando ângulo em graus)      |
| `angulo_pescoco`| REAL                 | NOT NULL (valor numérico representando ângulo em graus)      |
| `camera`        | TEXT                 | NOT NULL, **valores permitidos**: `'lateral'` ou `'frontal'` |

### Validação:
- `camera` possui **restrição CHECK** para aceitar apenas `'lateral'` ou `'frontal'`.
- `timestamp` deve ser armazenado preferencialmente no formato **ISO 8601** (`YYYY-MM-DD HH:MM:SS`).

### Demais Artefatos

![Canvas MVP](readme/img/canvas_mvp.png)
![É- Não É - Faz - Não Faz](readme/img/produto.png)
![Elevator Pitch](readme/img/elevator_pitch.png)

## Validação
⏳ 

### Estratégia
⏳

### Consolidação dos Dados Coletados
⏳

## Conclusões
⏳

## Limitações do Projeto e Perspectivas Futuras
⏳

## Referências Bibliográficas

- **ZHU, C.; SHAO, R.; ZHANG, X.; GAO, S.; LI, B.** Application of Virtual Reality Based on Computer Vision in Sports Posture Correction. *Wireless Communications and Mobile Computing*, 2022, p. 1-15. [https://doi.org/10.1155/2022/3719971](https://doi.org/10.1155/2022/3719971)

- **CAI, D.; LIN, S.** A Study on Posture Correction Based on Computer Vision. In: *Applied Mechanics and Materials*, v. 513-517, p. 3207-3211, 2014. [https://doi.org/10.4028/www.scientific.net/AMM.513-517.3207](https://doi.org/10.4028/www.scientific.net/AMM.513-517.3207)

- **SITAPARA, S.; D.P., A.; JAIN, M.; SINGH, S.; GUPTA, N.** Novel Approach for Real-Time Exercise Posture Correction Using Computer Vision and CNN. In: *2023 International Conference on Ambient Intelligence, Knowledge Informatics and Industrial Electronics (AIKIIE)*, 2023, p. 1-6. [https://doi.org/10.1109/AIKIIE60097.2023.10389979](https://doi.org/10.1109/AIKIIE60097.2023.10389979)

- **TAN, Z.; SEOW, B.** Development of a Posture Corrector Device with Data Analysis System. In: *Lecture Notes in Mechanical Engineering*, 2022. [https://doi.org/10.1007/978-981-16-8954-3_1](https://doi.org/10.1007/978-981-16-8954-3_1)

- **RAJU, J.; REDDY, Y.; PRADEEPREDDY, G.** Smart Posture Detection and Correction System Using Skeletal Points Extraction. In: *Learning and Analytics in Intelligent Systems*, 2019. [https://doi.org/10.1007/978-3-030-24322-7_23](https://doi.org/10.1007/978-3-030-24322-7_23)

## Demais Links

### [Configurações e Requisitos do MVP](readme/configuracoes_e_requisitos.md)

### [Desenvolvimento da Solução do MVP](readme/desenvolvimento_da_solucao.md)

### [POSTMORTEM](readme/postmortem.md)