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
| `nova <pasta> <codigo> --formato F [--modelo M]` | Cria a peça a partir da célula, já com persona, oferta, macro-ação, hipótese, intensidade e a próxima `versao`. Para roteiro, `--modelo` cria as cenas do modelo de corpo com tempos sugeridos. |
| `checklist <peca>` | Mostra o que falta para a peça sair do estado atual. |
| `avancar <peca>` | Passa a peça ao próximo estado, se nada faltar. |
| `revisar <peça ou pasta>` | Dá avisos em três gravidades, pelo padrão de texto da Trilha, e sai com erro se algo bloqueia. |
| `revisar-pagina <pagina.yaml>` | O texto de uma página da Trilha-LP pelo mesmo padrão. |
| `padrao` | Os princípios e as regras do padrão de texto, por superfície e gravidade. |
| `aprovar <peca> --por NOME --teste-do-vendedor` | Aprova a peça final (regras abaixo). |
| `exportar <pasta>` | Gera, só das peças aprovadas: `anuncios.csv` (os textos de Meta e Google), `subida.csv` (um anúncio por linha, com campanha, conjunto, nome do anúncio e parâmetros de URL vindos do plano de campanhas do briefing), o **briefing do criativo** de cada anúncio do Meta e os roteiros, para a equipe de criação. |
| `ganchos` | Catálogo de 15 tipos de gancho, com exemplos de segmentos diferentes. |
| `roteiros` | Modelos de corpo para roteiro: educativo (o quê → por quê → como), história (mas… então…) e oferta direta (os 6 Ps). Ficam em `trilha_copy/regras/roteiros.yaml`, editáveis. |
| `referencias [pasta]` | Banco de peças boas, decupadas trecho a trecho, com o porquê. O geral fica em `referencias/`; o de cada cliente, em `copy/<id>/referencias/`. |
| `vencedora <peca> --hipotese H` | **O caminho de volta.** A peça aprovada que venceu um teste vira referência do cliente. A decupagem vem do subtexto da peça; o porquê, do aprendizado registrado no briefing (`decidir`). Só aceita hipótese validada que testou a célula da peça. |

Formatos:
- anúncio do Meta: feed, Reels e Stories;
- anúncio responsivo de pesquisa do Google;
- roteiro de vídeo curto: cenas com tempo, parte do modelo de corpo, fala, visual e texto na tela.

## Como faz

**O caminho de uma peça:**

| Estado | Para sair dele |
|---|---|
| **fundação** | persona, micro-ação (o que esta peça provoca), macro-ação (o que o sistema precisa), a ideia grande em uma frase e um briefing sem buraco crítico: persona com dores, promessa e ao menos uma prova |
| **rascunho** | 10 rascunhos de título ou gancho ou mais, emoção principal (novo, fácil, seguro ou grande), ângulo, tipo de gancho e o mínimo de textos que a plataforma pede; roteiro com modelo de corpo |
| **refinado** | subtexto anotado (ao menos 3 trechos, cada um com o que deve fazer sentir ou pensar), a prova usada, o briefing do criativo nos anúncios do Meta (`meta.arte.mostrar`) e nenhum aviso que bloqueie |
| **final** | só o comando `aprovar`, que exige o **teste do vendedor** ("um bom vendedor diria isso com o cliente na frente dele?") e que a peça tenha virado final em outro dia (`--mesmo-dia` para pular, de propósito) |
| **aprovado** | a aprovação guarda uma assinatura do texto: mudou uma vírgula depois de aprovar, a peça não exporta até ser aprovada de novo |

`avancar` e `aprovar` trocam a linha `estado:` e acrescentam ao `historico:` sem reescrever o resto do arquivo: os comentários ficam.

**A revisão** segue o **padrão de texto da Trilha** ([`trilha_copy/regras/padrao.yaml`](trilha_copy/regras/padrao.yaml), explicado em [docs/padrao-de-texto.md](docs/padrao-de-texto.md)). É um arquivo só, com princípios, vocabulários, parâmetros e 48 regras, cada uma com gravidade, mensagem e fonte. O mesmo padrão vale para anúncio, roteiro e página; o briefing e a LP conferem as cópias deles contra ele na CI.
- **Bloqueia:**
  - termo ou promessa proibidos (do cliente ou do segmento);
  - garantia de resultado que não depende só da empresa;
  - prazo ou vagas acabando sem urgência real (com motivo) ou escassez real (com evidência) no briefing;
  - prova que não está no contrato;
  - preço num canal em que o cliente não mostra preço;
  - no Meta, afirmação sobre atributo pessoal de quem lê;
  - limite de caracteres ou de quantidade que a plataforma recusa;
  - texto alterado depois da aprovação;
  - célula que não existe na grade.
- **Atenção:**
  - número sem lastro no briefing;
  - promessa de ganho com número e sem ressalva;
  - público restringido no texto;
  - concorrente pelo nome;
  - mais "nós" do que "você";
  - autoelogio;
  - peça sem nenhum dado concreto;
  - intensidade acima da combinada;
  - prova de outra persona;
  - preço fora da forma combinada ("a partir de", parcela);
  - registro profissional ausente;
  - antes e depois em saúde;
  - leitura difícil;
  - texto cortado na tela;
  - no roteiro: gancho depois de 3 s, fala que não cabe, roteiro fora do modelo de corpo.
- **Sugestão:**
  - adjetivo sem fato;
  - frases do mesmo tamanho;
  - nenhuma palavra das frases literais da persona;
  - chamada sem "quando";
  - poucos títulos no Google;
  - título que não repete a busca;
  - vídeo sem texto na tela;
  - roteiro sem modelo.

Os termos casam como palavra inteira (com `radical*` e `re:` quando a lista quer variações): "corra" não pega mais "ocorra". Para mudar uma gravidade ou desligar uma regra, edite o YAML.

**`revisar-pagina <pagina.yaml>`** revisa o texto de uma página da Trilha-LP com o mesmo padrão. Lê o contrato do cliente em `copy/<id>/` do Trilha-clientes (ou `--contrato`) e confere, além das regras de texto:
- título de bloco genérico;
- botão genérico;
- objeção sem resposta;
- título do topo e descrição de SEO longos;
- registro no rodapé.

A estrutura da página continua com `python -m trilha_lp validar`.

A revisão aponta e não reescreve. Os limites de cada formato estão em [`trilha_copy/formatos.py`](trilha_copy/formatos.py).

**Entradas:**
- `copy.yaml`, o contrato com o Trilha-briefing: personas, voz, ofertas, provas utilizáveis, compliance, grade, hipóteses e onde cada célula vira anúncio (`veiculacao`, do plano de campanhas);
- as peças, em `pecas/<codigo>/<peca>.yaml`.

**Saídas:** `dist/<id>/anuncios.csv`, com uma linha por texto, o código da célula e o `utm_content`; `dist/<id>/subida.csv`, com uma linha por anúncio (campanha, conjunto, nome e parâmetros de URL); `dist/<id>/criativos/<peca>.md`, o briefing do criativo de cada anúncio do Meta; e `dist/<id>/roteiros/<peca>.md`. Detalhes em [contrato](docs/contrato.md).

**O briefing do criativo** é o que a equipe de criação recebe. Não é design: diz o que a arte precisa comunicar.
- **Para que serve a peça:** a micro e a macro-ação, e o que varia no teste, para não mudar outra coisa.
- **Para quem:** a persona e as frases dela.
- **A ideia, o tom, as provas** que podem aparecer.
- **O que não pode e o que é obrigatório:** compliance, palavras proibidas inclusive na arte, avisos legais.
- **A arte:** o que precisa mostrar, o texto na arte (já revisado), o que evitar e as referências.
- **A identidade da marca e as medidas** do formato.
- **O texto que acompanha a arte.**

## Arquivos

```
<id>/
  copy.yaml                    contrato vindo do Trilha-briefing (não edite aqui; edite lá e exporte de novo)
  pecas/<codigo>/<peca>.yaml   uma peça por arquivo, na pasta da célula da grade
referencias/<id>.yaml          peças boas de qualquer segmento, decupadas trecho a trecho
```

## O que não faz

- **Não gera texto.** Não há IA escrevendo: a ferramenta organiza, confere e registra.
- **Não faz o criativo visual.** O design é da equipe de criação. O briefing do criativo e o roteiro dizem o que comunicar, não como desenhar.
- **Não sobe anúncio.** O CSV é para copiar ou importar no gerenciador; não foi testado na importação em massa do Meta ou do Google.
- **Não substitui a política das plataformas.** As listas de termos sensíveis pegam os casos comuns, não todos, e os limites de caracteres mudam de tempos em tempos.
- **Não mede resultado.** Quem mede é o Trilha-ads: o raio-x agrupa leads, qualificados e vendas pelo código da célula.

## Situação atual

Versão 0.3.0, sem cliente real ainda. Próximos passos:
- o que o padrão de texto ainda não automatiza ([lista em ordem de valor](docs/padrao-de-texto.md#o-que-ainda-não-está-automatizado)): coerência anúncio → página, superlativo sem prova, chamada única;

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
python -m trilha_copy revisar-pagina lp/minha-cliente/X-meta/pagina.yaml   # contrato achado em copy/minha-cliente/
python -m trilha_copy aprovar   copy/minha-cliente/pecas/PT01/pt01-meta-feed.yaml --por "Seu nome" --teste-do-vendedor
python -m trilha_copy exportar  copy/minha-cliente        # dist/minha-cliente/anuncios.csv e subida.csv (não versionar)

python -m trilha_copy ganchos
python -m trilha_copy roteiros
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
