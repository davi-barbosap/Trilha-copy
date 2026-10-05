# Trilha-copy

Estrutura e revisão da copy dos anúncios, fiel ao briefing do cliente. A ferramenta **não escreve**. Ela:
- junta o que o briefing sabe do cliente antes de você escrever;
- acompanha cada peça até a aprovação;
- aponta o que vai ser reprovado, cortado ou soar falso.

Quem escreve e decide é o assessor. Serve para qualquer segmento; o exemplo (`clientes/_exemplo/`) é uma escola de inglês fictícia.

## Ecossistema Trilha

| Etapa | Repositório | Papel |
|---|---|---|
| 1. Diagnóstico e planejamento | [Trilha-briefing](https://github.com/davi-barbosap/Trilha-briefing) | entende o cliente e decide a estratégia; é a fonte de tudo o que as outras ferramentas usam |
| 2. Copy | **Trilha-copy (este)** | estrutura e revisa os textos dos anúncios, fiel ao briefing |
| 3. Página | [Trilha-LP](https://github.com/davi-barbosap/Trilha-LP) | landing page com o rastreamento que leva a origem do lead até o Kommo |
| 4. Execução e medição | [Trilha-ads](https://github.com/davi-barbosap/Trilha-ads) | coleta, confere e calcula: raio-x do funil, conversão real, freio, material das reuniões |
| Dados dos clientes | Trilha-clientes (privado) | os arquivos reais de cada cliente; esta ferramenta usa a pasta `copy/` |

O código da célula da grade (`PT01`, `GB01`…) amarra as etapas. Ele nasce na grade do briefing e cada peça daqui pertence a uma célula. Ele sai no `utm_content` do anúncio e é o mesmo que a página põe na mensagem do WhatsApp.

## O que faz

| Comando | O que faz |
|---|---|
| `importar <copy.yaml>` | Traz o contrato gerado pelo Trilha-briefing (só é preciso fora do Trilha-clientes, onde o briefing já grava direto). |
| `validar <pasta>` | Confere se o contrato e as peças estão no formato certo. Não julga o texto. |
| `pacote <pasta> <codigo>` | **Antes de escrever:** os 6 Ps da célula, o que falta no briefing, a voz e os limites. Os 6 Ps são Pessoas, Posicionamento, Promessa, Prova, Prioridade e Processo. |
| `nova <pasta> <codigo> --formato F` | Cria a peça a partir da célula, já com persona, oferta, macro-ação, hipótese e intensidade preenchidas. |
| `checklist <peca>` | Mostra o que falta para a peça sair do estado atual. |
| `avancar <peca>` | Passa a peça ao próximo estado, se nada faltar. |
| `revisar <peça ou pasta>` | Dá avisos em três gravidades e sai com erro se algo bloqueia. |
| `aprovar <peca> --por NOME --teste-do-vendedor` | Aprova a peça final (regras abaixo). |
| `exportar <pasta>` | Gera `anuncios.csv` (Meta e Google) e os roteiros em Markdown, só das peças aprovadas. |
| `ganchos` | Catálogo de 15 tipos de gancho, com exemplos de segmentos diferentes. |
| `referencias` | Banco de peças boas, decupadas trecho a trecho, com o porquê. |

Formatos:
- anúncio do Meta: feed, Reels e Stories;
- anúncio responsivo de pesquisa do Google;
- roteiro de vídeo curto, em versão básica (cenas com tempo, fala, visual e texto na tela).

## Como faz

**O caminho de uma peça:**

| Estado | Para sair dele |
|---|---|
| **fundação** | persona, micro-ação (o que esta peça provoca), macro-ação (o que o sistema precisa), a ideia grande em uma frase e um briefing sem buraco crítico: persona com dores, promessa e ao menos uma prova |
| **rascunho** | 10 rascunhos de título ou gancho ou mais, emoção principal (novo, fácil, seguro ou grande), ângulo, tipo de gancho e o mínimo de textos que a plataforma pede |
| **refinado** | subtexto anotado (ao menos 3 trechos, cada um com o que deve fazer sentir ou pensar), a prova usada e nenhum aviso que bloqueie |
| **final** | só o comando `aprovar`, que exige o **teste do vendedor** ("um bom vendedor diria isso com o cliente na frente dele?") e que a peça tenha virado final em outro dia (`--mesmo-dia` para pular, de propósito) |
| **aprovado** | a aprovação guarda uma assinatura do texto: mudou uma vírgula depois de aprovar, a peça não exporta até ser aprovada de novo |

`avancar` e `aprovar` trocam a linha `estado:` e acrescentam ao `historico:` sem reescrever o resto do arquivo: os comentários ficam.

**A revisão** confere a peça contra o contrato do cliente, o formato e os princípios de copy ([método](docs/metodo.md)):
- **Bloqueia:**
  - termo ou promessa proibidos no briefing;
  - texto acima do limite que a plataforma recusa;
  - menos textos do que a plataforma exige;
  - prazo ou vagas acabando sem urgência ou escassez reais no briefing;
  - prova que não está no contrato;
  - no Meta, afirmação sobre atributo pessoal de quem lê;
  - texto alterado depois da aprovação;
  - célula que não existe na grade.
- **Atenção:**
  - número que não vem de nenhuma prova, oferta ou promessa do briefing;
  - promessa de ganho com número;
  - concorrente citado pelo nome;
  - mais "nós/nosso" do que "você";
  - autoelogio;
  - intensidade acima da combinada com o cliente;
  - prova de outro perfil de persona;
  - leitura difícil;
  - gancho cortado pelo "ver mais";
  - fala que não cabe no tempo da cena;
  - vídeo que não prende nos 3 primeiros segundos.
- **Sugestão:**
  - frases todas do mesmo tamanho;
  - nenhuma palavra das frases literais da persona;
  - adjetivo sem fato;
  - chamada sem "quando";
  - menos de 10 títulos no Google;
  - título que não repete a busca;
  - vídeo sem texto na tela.

A revisão aponta e não reescreve. Os limites de cada formato estão em [`trilha_copy/formatos.py`](trilha_copy/formatos.py).

**Entradas:**
- `copy.yaml`, o contrato com o Trilha-briefing: personas, voz, ofertas, provas utilizáveis, compliance, grade e hipóteses;
- as peças, em `pecas/<codigo>/<peca>.yaml`.

**Saídas:** `dist/<id>/anuncios.csv`, com uma linha por texto, o código da célula e o `utm_content`, e `dist/<id>/roteiros/<peca>.md`. Detalhes em [contrato](docs/contrato.md).

## Arquivos

```
<id>/
  copy.yaml                    contrato vindo do Trilha-briefing (não edite aqui; edite lá e exporte de novo)
  pecas/<codigo>/<peca>.yaml   uma peça por arquivo, na pasta da célula da grade
referencias/<id>.yaml          peças boas de qualquer segmento, decupadas trecho a trecho
```

## O que não faz

- **Não gera texto.** Não há IA escrevendo: a ferramenta organiza, confere e registra.
- **Não faz o criativo visual.** O design é da equipe de criação. O roteiro só descreve o visual de cada cena.
- **Não sobe anúncio.** O CSV é para copiar ou importar no gerenciador; não foi testado na importação em massa do Meta ou do Google.
- **Não substitui a política das plataformas.** As listas de termos sensíveis pegam os casos comuns, não todos, e os limites de caracteres mudam de tempos em tempos.
- **Não mede resultado.** Quem mede é o Trilha-ads, pelo código da célula, e o agrupamento por código ainda está no roadmap de lá.

## Situação atual

Versão 0.1.1, sem cliente real ainda. Próximos passos:
- os roteiros completos, com os modelos de corpo educativo e de história;
- o briefing de criativo de cada peça para a equipe de criação: formatos, direção visual e identidade;
- as peças vencedoras voltando como referência.

## Como usar

```bash
pip install -e .

# Clientes reais ficam no Trilha-clientes (privado), pasta copy/
cd ../Trilha-clientes
python -m trilha_briefing exportar briefing/minha-cliente --para copy --saida copy   # copy/minha-cliente/copy.yaml

python -m trilha_copy validar   copy/minha-cliente
python -m trilha_copy pacote    copy/minha-cliente PT01 --formato meta_feed
python -m trilha_copy nova      copy/minha-cliente PT01 --formato meta_feed
python -m trilha_copy checklist copy/minha-cliente/pecas/PT01/pt01-meta-feed.yaml
python -m trilha_copy avancar   copy/minha-cliente/pecas/PT01/pt01-meta-feed.yaml
python -m trilha_copy revisar   copy/minha-cliente
python -m trilha_copy aprovar   copy/minha-cliente/pecas/PT01/pt01-meta-feed.yaml --por "Seu nome" --teste-do-vendedor
python -m trilha_copy exportar  copy/minha-cliente        # dist/minha-cliente/anuncios.csv (não versionar)

python -m trilha_copy ganchos
python -m trilha_copy referencias
```

Neste repositório, os comandos rodam também sobre o exemplo: `python -m trilha_copy revisar clientes/_exemplo`.

## Documentação

- [Método](docs/metodo.md): de onde vêm as regras, o que cada uma confere e onde fomos críticos com as fontes.
- [Contrato](docs/contrato.md): o que entra do Trilha-briefing, o que sai daqui e como mudar sem quebrar.
- [Mudanças](CHANGELOG.md).

## Testes

```bash
python -m unittest discover -s tests -v
```

O teste de contrato (`tests/test_contrato.py`) confere três coisas: que a exportação do Trilha-briefing carrega aqui, que ela é igual ao exemplo versionado e que as peças do exemplo continuam sem bloqueio. Ele roda quando o briefing está instalado; sem ele, é pulado. A CI clona o Trilha-briefing e roda o teste a cada push.

## Dados de clientes

Peças e contratos de clientes reais ficam no repositório privado Trilha-clientes. Aqui, o `.gitignore` deixa `clientes/*` fora do Git e versiona só o exemplo fictício.
