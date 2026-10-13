# Método

A ferramenta junta três fontes, cada uma com um papel:

- **Claude Hopkins** (*Scientific Advertising* e *My Life in Advertising*) dá os princípios que não envelhecem. Anúncio é venda multiplicada; quem lê quer saber o que ganha; fato vence adjetivo; o título decide quem lê; só o teste decide o que funciona.
- **O curso de copy do KJ** dá o método de trabalho: entender o público, saber o que cada trecho precisa fazer a pessoa sentir, escrever em volume e passar por um checklist em cada fase.
- **A aula dos 6 Ps** dá o formato do material de partida. Com Pessoas, Posicionamento, Promessa, Prova, Prioridade e Processo preenchidos, "o anúncio quase se escreve sozinho".

O que dá para conferir virou regra. O que depende de julgamento virou pergunta obrigatória ou campo da peça. Quem escreve e decide continua sendo o assessor.

## 1. Antes de escrever: o pacote da célula (6 Ps)

`pacote <codigo>` monta, a partir do contrato, o que você precisa saber daquela célula da grade:

| P | Pergunta | De onde vem |
|---|---|---|
| **Pessoas** | Para quem é? | persona da célula: dores, desejos e medos (os mais mencionados na escuta primeiro), frases literais, crenças com a forma de derrubar, objeções, consciência e sofisticação; quem não atender |
| **Posicionamento** | Por que você e não outro? | posicionamento, unicidade, raridade, bastidores, diferenciais com a escada do "e daí?" |
| **Promessa** | O que a pessoa ganha? | promessa da célula (ajustada à persona), promessa da oferta, antes e depois |
| **Prova** | Por que confiar? | só provas utilizáveis; as do perfil da persona vêm primeiro |
| **Prioridade** | Por que agir agora? | urgência e escassez **reais** e dentro do prazo, custo de não agir, inversão de risco |
| **Processo** | Como funciona? | "todos acham X → está errado por Y → o certo é Z", alternativas e por que não resolvem, passos |

O P vazio aparece como **"Falta no briefing"**. Faltou algo, volte ao briefing: é melhor do que inventar na peça.

## 2. O caminho de uma peça

Os estados seguem o checklist do curso:

1. **Fundação.** A peça declara para quem é e duas ações. A **micro-ação** é o que esta peça precisa provocar (parar de rolar, clicar). A **macro-ação** é o que o sistema precisa (lead qualificado, agendamento). A micro não pode atrapalhar a macro: um gancho que dá clique de curioso sem perfil derruba o funil. A peça também declara a ideia grande em uma frase.
2. **Rascunho.** Volume sem julgamento: ao menos 10 títulos ou ganchos. Hopkins conta que trocar só o título mudava muito o retorno do mesmo anúncio. O número exato é dele e de outra época, mas a lição fica: escreva muitos e descarte a maioria. Aqui a peça também escolhe a emoção principal (novo, fácil, seguro ou grande), o ângulo e o tipo de gancho (`ganchos`).
3. **Refinado.** **Subtexto anotado:** cada trecho diz o que deveria fazer a pessoa sentir ou pensar. Isso deixa a revisão objetiva ("este trecho deveria passar segurança e não passa") em vez de uma questão de gosto. A peça também precisa da prova escolhida e de nenhum aviso que bloqueie.
4. **Final → aprovado.** Duas regras de juízo viram trava:
   - o **teste do vendedor** de Hopkins: um bom vendedor diria isso com o cliente na frente dele?
   - **dormir sobre a peça**: aprovar no mesmo dia em que ela ficou final pede `--mesmo-dia`, de propósito.

   A aprovação guarda uma assinatura do texto, e qualquer mudança depois exige aprovar de novo.

## 3. Regras da revisão e de onde vêm

As regras estão no **padrão de texto da Trilha** (`trilha_copy/regras/padrao.yaml`), o mesmo para anúncio, roteiro, página e briefing. [docs/padrao-de-texto.md](padrao-de-texto.md) tem:
- os 15 princípios e as 48 regras, por superfície e gravidade, cada uma com a fonte (Hopkins, KJ, 6 Ps, aula de landing page, CDC, CONAR, políticas das plataformas, decisões das ferramentas);
- as 21 divergências que havia entre as três ferramentas e o que o padrão adotou;
- o que ainda não está automatizado, em ordem de valor.

Além do texto, a revisão da peça confere o modelo de corpo do roteiro (seção 6). Esse é processo da copy, não regra de texto.

## 4. Medidas de texto

- **Legibilidade:** índice de Flesch adaptado ao português (Martins e outros, 1996):

  `248,835 − 1,015 × (palavras por frase) − 84,6 × (sílabas por palavra)`

  Acima de 75 é fácil; abaixo de 50, difícil. Só calcula com 30 palavras ou mais. O Hemingway, citado na aula, só funciona em inglês.
- **Sílabas:** contadas por grupos de vogais. Ditongos contam como uma sílaba; hiatos às vezes também ("reunião" conta 2). Serve para comparar textos entre si, não como nota absoluta.
- **Ritmo:** coeficiente de variação do tamanho das frases, com 4 frases ou mais. Abaixo de 0,25, as frases estão todas parecidas.

## 5. Onde fomos críticos com as fontes

- **Curiosidade solta traz clique de quem não compra.** O gancho precisa estar preso à dor ou ao desejo da persona. A ferramenta não consegue conferir isso sozinha. Por isso a peça declara micro e macro-ação, e o subtexto diz o que cada trecho deve fazer.
- **Ângulo positivo ou negativo é variável de teste, não regra.** As aulas divergem; quem decide é o resultado medido no Trilha-ads.
- **A "fórmula do gancho"** (benefício × relevância × credibilidade ÷ esforço) é útil para comparar variações, mas não é medida. Não virou nota automática.
- **Autoridade por associação** ("fulano recomenda") sem autorização sugere um endosso que não existe. Esbarra no CONAR e no direito de imagem. Aqui, prova só entra pelo contrato, com fonte.
- **Ganchos de identidade e promessa de renda** ("só para mulheres", "de barista a milionária") são pontos de reprovação no Meta. Anúncio de oportunidade de trabalho pode cair em categoria especial. Promessa de ganho precisa dizer que o resultado não é típico.
- **Transcrever ligações de vendas com IA** é a dica mais forte da aula 3 e também a mais sensível. São dados de clientes do seu cliente (LGPD): anonimize antes de colar em qualquer ferramenta. As frases chegam aqui sem nome, pelo briefing.
- **"Não troque o anúncio que funciona"** (Hopkins, Ogilvy). O cansaço de um anúncio se mede por frequência e CTR no Trilha-ads, não pelo cansaço de quem o vê todo dia.
- **Urgência falsa não é técnica, é publicidade enganosa (CDC).** Por isso bloqueia, e não só alerta.

## 6. Roteiro e briefing do criativo

**Modelos de corpo** (`trilha_copy/regras/roteiros.yaml`, editável). Cada cena declara a parte do modelo que cumpre, e a revisão avisa parte que falta, fora de ordem ou desconhecida.

| Modelo | Partes | Origem | Quando |
|---|---|---|---|
| educativo | gancho → o quê → por quê → como | aula de copy 3 | ensinar algo útil preso à dor; público que ainda não conhece a solução |
| história | gancho → situação → mas… → então… (repete) → resultado | aula de copy 3 ("but, therefore") | a mudança de alguém parecido com a persona; só com história autorizada |
| oferta direta | gancho → promessa → prova → processo → prioridade (opcional) | aula dos 6 Ps | público que já conhece o problema e compara soluções |

- **Chamada:** fica no fim, em qualquer modelo (`parte: cta`), e o texto dela vai no campo `cta` (quem, o quê, até quando, como).
- **Ponto crítico:** o modelo organiza, não garante. Um roteiro educativo que ensina algo sem ligação com a oferta atrai quem quer conteúdo grátis. Por isso o "como" pede a oferta fazendo pela pessoa, e a macro-ação continua na peça.

**Briefing do criativo.** Não fazemos o design: ele é da equipe de criação. A copy entrega o que a arte precisa comunicar, num arquivo por peça aprovada:
- para que serve e o que varia no teste;
- para quem, a ideia, as provas, o que não pode;
- o que mostrar, o texto na arte e as medidas.

O texto na arte passa pela mesma revisão do resto, porque é texto que o público lê. A arte entra na assinatura da aprovação: mudou a arte, aprove de novo.

## 7. O caminho de volta

O que o teste ensinou volta para quem escreve. Ninguém começa uma peça sem saber o que já se aprendeu com aquele público.
- **No pacote da célula:** "O que os testes já disseram" mostra as hipóteses decididas no briefing, com o aprendizado. Primeiro vêm as da célula, depois as das outras. Se há teste rodando na célula, o pacote avisa para não mudar a variável testada nas versões novas.
- **Na referência:** `vencedora` transforma a peça aprovada de uma hipótese validada em referência do cliente (`copy/<id>/referencias/`), decupada pelo próprio subtexto.
- **Ponto crítico:** um teste validado vale para aquele público, naquela época e com aquela oferta. A referência registra a fonte e a data para ninguém tratar o resultado como lei. Ângulo e gancho continuam sendo variáveis de teste.

## 8. O que ficou de fora nesta versão

- **Uma ideia grande por peça:** conferir que não há duas promessas exige ler o sentido. Ficou como campo (`ideia`), não como regra.
- **Nada inacreditável:** comparar a promessa com a sofisticação do público. O pacote mostra a sofisticação; a revisão não julga.
- **Lista de jargões por público:** depende do segmento. Hoje entra pelos termos proibidos do briefing.
- **Chamada única,** **superlativo sem prova** e **coerência anúncio → página:** estão entre as lacunas do padrão de texto, em ordem de valor.
