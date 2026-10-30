_This project has been created as part of the 42 curriculum by [iscarval](https://github.com/Isabelle-AL) and [ferde-so](https://github.com/ferdesmello)._

# A-Maze-ing
Create your own maze generator and display its result!

## Description 
clearly presents the project, including its goal and a
brief overview.

## Instructions 
any relevant information about compilation,
installation, and/or execution.

### Virtual environment

Create one following:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

```bash
deactivate
```

### Running

```bash
python3 a_maze_ing.py config.txt
```

## Resources 

classic references related to the topic (documentation, articles, tutorials, etc.), as well as a description of how AI was used — specifying for which tasks and which parts of the project.

## Additional sections

* The complete structure and format of your config file.
* The maze generation algorithm you chose.
* Why you chose this algorithm.
* What part of your code is reusable, and how.
* Your team and project management with:
* The roles of each team member.
* Your anticipated planning and how it evolved until the end
* What worked well and what could be improved
* Have you used any specific tools? Which ones?

## Advanced features 
(multiple algorithms, display options...)



| Código Binário <br> (C-D-B-E) | Paredes Ativas | Símbolo / Desenho | Como fica na Tabela |
| :---: | :--- | :---: | :---: |
| **0000** | Nenhuma parede (Vazio) | ` ` |   |
| **1000** | Apenas o **Topo** | `‾` | ‾ |
| **0100** | Apenas a **Direita** | ` │` |  │ |
| **0010** | Apenas o **Fundo** | `_` | _ |
| **0001** | Apenas a **Esquerda** | `│ ` | │  |
| **1100** | Topo e Direita (**Canto Sup. Dir.**) | `┐` | ┐ |
| **0110** | Direita e Fundo (**Canto Inf. Dir.**) | `┘` | ┘ |
| **0011** | Fundo e Esquerda (**Canto Inf. Esq.**) | `└` | └ |
| **1001** | Topo e Esquerda (**Canto Sup. Esq.**) | `┌` | ┌ |
| **1010** | Topo e Fundo (**Paralelas Horizontais**) | `_` e `‾` | ⬟ |
| **0101** | Direita e Esquerda (**Paralelas Verticais**) | `│ │` | │ │ |
| **1110** | Topo, Direita e Fundo (**Sem Esquerda**) | `⊐` | ⊐ |
| **0111** | Direita, Fundo e Esquerda (**Sem Topo**) | `⊔` | ⊔ |
| **1011** | Topo, Fundo e Esquerda (**Sem Direita**) | `⊏` | ⊏ |
| **1101** | Topo, Direita e Esquerda (**Sem Fundo**) | `⊓` | ⊓ |
| **1111** | **Todas as 4 paredes** (Quadrado Cheio) | `▢` | ▢ |

