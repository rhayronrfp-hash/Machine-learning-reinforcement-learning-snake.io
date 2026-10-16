# Machine-learning-reinforcement-learning-snake.io

🇺🇸 [English](#english) | 🇧🇷 [Português](#português)

---

<a name="english"></a>
## 🇺🇸 English

My first project with an area of machine learning.

It's a Snake.io game using machine learning models (perhaps this is not the most appropriate way to say it, but it is the one I like to use).

Fully developed on a phone. The width and height of the screen will have to be modified in `funções.py`.

*(I don't have a PC.)*

I hope you like it.

### What this is

There are several snakes in the game at once, all controlled by the same neural network (just one, shared by all of them), which keeps learning while the game runs. The game itself (drawing on screen, moving the snakes, checking who hit who) is in Python with `pygame`. The neural network and the training part are in C++ with the Eigen library, running separately and talking to Python through `stdin`/`stdout`.

### Files

| File | What it does |
|------|--------------|
| `MAIN.py` | The game loop: draws the screen, reads mouse/keyboard input, calls the AI every frame, gives rewards, and handles deaths and respawning. |
| `funções.py` | Creates and moves snakes, handles danger sensors, finds food and other snakes, and manages statistics counters. |
| `ML.py` | A small class that stores the snake's ID and the connection to `Calculo_da_rede`. There is no neural network logic here. |
| `colisoes_wrapper.py` | Opens the `./calculo` program and sends messages to it (everything is text, one line per message). |
| `calculo_ML.cpp` | Contains the actual neural network (training, memory, etc.), as well as collision calculations between snakes. This file must be compiled before playing. |
| `melhor_ia.txt` | Stores the trained network weights. It is generated automatically by the game. |
| `melhor_avaliacao.txt` | Stores the highest score achieved so far, to determine when a new `melhor_ia.txt` should be saved. |

### How to run

```bash
g++ -std=c++17 -O3 calculo_ML.cpp -o calculo
python3 MAIN.py
```

The Eigen path is hardcoded in `calculo_ML.cpp`:

```cpp
#include "/storage/emulated/0/eigen-3.4.0/Eigen/Dense"
```

This was made on a phone, using Termux. Change that `#include` to wherever you have Eigen installed.

### Training from scratch, without the already-trained AI

The repo might come with an already-trained `melhor_ia.txt`. If you want the AI to start from nothing (random weights, acting mostly by chance at first), just delete that file before running:

```bash
rm melhor_ia.txt
python3 MAIN.py
```

Without this file, the game can't load anything and creates fresh weights on its own, starting with epsilon at 1.0 (meaning it decides almost everything randomly at first). That's it: without `melhor_ia.txt`, training starts from scratch.

If you just want it to explore more again without losing what it already learned, use the **Epsilon** button in the game and set a manual value instead of deleting the file.

### Changing the sensors

Everything the network "sees" is put together in `funções.py`, inside the `observar()` function — it returns a list of 15 numbers (the state). The danger sensors (front, right, left) are calculated right above it, in the `perigos()` function.

- `alcance`: how far the sensor can see, in pixels. Currently 900.
- `largura_area`: the width of each sensor. Currently 260.
- `margem_pescoco`: how many pixels of its own neck the sensor ignores, so it doesn't keep detecting its own body as a danger all the time. Currently 60.

You can change these numbers as you like — this only changes the size of the area the sensors can see, without changing anything else.

But if you want to add or remove a sensor (changing how many numbers `observar()` returns), that changes the network's input size, and you need to change it in a few more places:

1. The `return [...]` of `observar()`, in `funções.py`.
2. `MatrixXd(24, 15)` (there's one in `inicializar()` and one in `carregar()`) in `calculo_ML.cpp` — swap the 15 for the new number.
3. The `for (int i = 0; i < 15; i++)` loop that reads the state, in two spots inside `main()` in `calculo_ML.cpp` (`tipo == 7` and `tipo == 6`).
4. Delete the old `melhor_ia.txt` — it was saved for the old input size and won't work with the new network.

### A few RL things used here

- **Double DQN:** one network chooses the action, another network (an older copy) evaluates whether that choice was good. This prevents the AI from overestimating its own value.
- **Target network:** this is the older copy of the weights, which only updates from time to time (every `contadormax` training steps), to make training more stable.
- **Replay buffer:** the game stores the latest experiences (what happened, which action was taken, what the reward was) and, when training, picks a random batch of these experiences instead of training only on the latest event.
- **Epsilon-greedy:** from time to time (with probability `epsilon`), the snake takes a random action instead of obeying the network, just to keep exploring the game. This `epsilon` gradually decreases and is saved along with the weights.
- **Proximity reward:** in addition to earning points for eating and losing points for dying, the snake also gets a little reward just for getting closer to food or another snake, to help it learn faster.
- **Evaluation mode:** the **Avaliação** button turns off randomness and training, just to see how the AI is really playing, without interference.

### One note

I didn't use any ready-made RL framework (no Gym, Stable-Baselines, PyTorch) — the network, the training, everything was written from scratch in C++ with Eigen. It's a learning project, so the focus was understanding what was going on, not doing it the most "proper" way possible.

---

<a name="português"></a>
## 🇧🇷 Português

Meu primeiro projeto com uma área de aprendizado de máquina.

É um jogo Snake.io que está usando modelos de aprendizado de máquina (talvez essa não seja a maneira mais apropriada de dizer isso, mas é a que eu gosto de usar).

Totalmente desenvolvido em um celular. A largura e a altura da tela terão que ser modificadas em `funções.py`.

*(Eu não tenho um PC.)*

Espero que gostem.

### O que é isso

Tem várias cobras no jogo ao mesmo tempo, e todas são controladas pela mesma rede neural (uma só, compartilhada entre todas), que vai aprendendo enquanto o jogo roda. A parte do jogo em si (desenhar na tela, mexer as cobras, ver quem bateu em quem) é em Python com `pygame`. A parte da rede neural e do treino é em C++ com a biblioteca Eigen, rodando separada e conversando com o Python por `stdin`/`stdout`.

### Arquivos

| Arquivo | O que faz |
|---------|-----------|
| `MAIN.py` | O loop do jogo: desenha a tela, lê o mouse/teclado, chama a IA a cada frame, dá as recompensas e cuida das mortes e dos respawns. |
| `funções.py` | Cria e move as cobras, cuida dos sensores de perigo, encontra a comida e outras cobras e gerencia os contadores de estatísticas. |
| `ML.py` | Uma classe pequena que guarda o ID da cobra e a conexão com `Calculo_da_rede`. Não há lógica da rede neural aqui. |
| `colisoes_wrapper.py` | Abre o programa `./calculo` e envia mensagens para ele (tudo é texto, uma linha por mensagem). |
| `calculo_ML.cpp` | Contém a rede neural propriamente dita (treinamento, memória etc.), além dos cálculos de colisão entre as cobras. Esse arquivo precisa ser compilado antes de jogar. |
| `melhor_ia.txt` | Armazena os pesos treinados da rede. É gerado automaticamente pelo jogo. |
| `melhor_avaliacao.txt` | Guarda a maior pontuação alcançada até agora, para determinar quando vale a pena salvar um novo `melhor_ia.txt`. |

### Como rodar

```bash
g++ -std=c++17 -O3 calculo_ML.cpp -o calculo
python3 MAIN.py
```

O caminho do Eigen tá fixo no `calculo_ML.cpp`:

```cpp
#include "/storage/emulated/0/eigen-3.4.0/Eigen/Dense"
```

Isso aqui foi feito no celular, usando Termux. Troque esse `#include` pelo caminho de onde você tiver o Eigen instalado.

### Pra treinar do zero, sem usar a IA já treinada

Pode ser que o repositório venha com um `melhor_ia.txt` já treinado. Se você quiser que a IA comece do nada (pesos aleatórios, agindo quase tudo por sorte no começo), é só apagar esse arquivo antes de rodar:

```bash
rm melhor_ia.txt
python3 MAIN.py
```

Sem esse arquivo, o jogo não consegue carregar nada e cria pesos novos sozinho, começando com epsilon em 1.0 (ou seja, no início ela decide quase tudo na sorte). É basicamente isso: sem o `melhor_ia.txt`, o treino começa do zero.

Se você só quer que ela volte a explorar mais, sem perder o que já aprendeu, usa o botão **Epsilon** dentro do jogo e põe um valor manual, em vez de apagar o arquivo.

### Mexendo nos sensores

Tudo que a rede "vê" é montado no `funções.py`, dentro da função `observar()` — ela devolve uma lista de 15 números (o estado). Os sensores de perigo (frente, direita, esquerda) são calculados logo acima, na função `perigos()`.

- `alcance`: até onde o sensor enxerga, em pixels. Hoje está 900.
- `largura_area`: a largura de cada sensor. Hoje está 260.
- `margem_pescoco`: quantos pixels do próprio pescoço o sensor ignora, pra não ficar detectando o próprio corpo como perigo o tempo todo. Hoje está 60.

Dá pra mudar esses números à vontade — isso só muda o tamanho da área que os sensores enxergam, sem mexer em mais nada.

Mas se você quiser adicionar ou tirar um sensor (mudar quantos números `observar()` devolve), aí muda o tamanho da entrada da rede, e você precisa mudar em mais lugares:

1. O `return [...]` do `observar()`, em `funções.py`.
2. O `MatrixXd(24, 15)` (tem um em `inicializar()` e outro em `carregar()`) no `calculo_ML.cpp` — troca o 15 pelo novo número.
3. O `for (int i = 0; i < 15; i++)` que lê o estado, em dois lugares do `main()` no `calculo_ML.cpp` (`tipo == 7` e `tipo == 6`).
4. Apaga o `melhor_ia.txt` antigo — ele foi salvo pro tamanho de entrada antigo e não serve mais pra rede nova.

### Umas coisas de reinforcement learning que tem aqui

- **Double DQN:** uma rede escolhe a ação, outra rede (uma cópia mais antiga) avalia se essa escolha foi boa. Isso evita que a IA fique superestimando o próprio valor.
- **Target network:** é essa cópia mais antiga dos pesos, que só atualiza de tempos em tempos (a cada `contadormax` passos de treino), pra deixar o treino mais estável.
- **Replay buffer:** o jogo guarda as últimas experiências (o que aconteceu, que ação foi tomada, qual foi a recompensa) e, na hora de treinar, pega um punhado aleatório dessas experiências em vez de treinar só com a última coisa que aconteceu.
- **Epsilon-greedy:** de vez em quando (com chance `epsilon`), a cobra faz uma ação aleatória em vez de obedecer a rede, só pra continuar explorando o jogo. Esse `epsilon` vai diminuindo aos poucos e fica salvo junto com os pesos.
- **Recompensa por aproximação:** além de ganhar pontos por comer e perder por morrer, a cobra também ganha um pouco de recompensa só por chegar mais perto da comida ou de outra cobra, pra ajudar ela a aprender mais rápido.
- **Modo avaliação:** o botão **Avaliação** desliga a aleatoriedade e o treino, só pra ver como a IA realmente está jogando, sem interferência.

### Uma observação

Não usei nenhum framework pronto de RL (nada de Gym, Stable-Baselines, PyTorch) — a rede, o treino e tudo mais foi escrito do zero em C++ com Eigen. É um projeto de aprendizado, então o foco foi entender o que tava acontecendo, não fazer do jeito mais "certinho" possível.
