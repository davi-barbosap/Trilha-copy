# Padrão de texto da Trilha

Um arquivo só, [`trilha_copy/regras/padrao.yaml`](../trilha_copy/regras/padrao.yaml), vale para todo texto que o público lê: anúncio, roteiro, página e as afirmações do briefing que viram copy. Antes ele estava espalhado em três ferramentas, com listas e gravidades diferentes.

- **O Trilha-copy** revisa anúncio e roteiro (`revisar`) e o texto da página (`revisar-pagina`) com este arquivo. `python -m trilha_copy padrao` lista as regras por superfície.
- **O Trilha-briefing e a Trilha-LP** guardam uma cópia só dos vocabulários que usam, e a CI deles confere a cópia contra este arquivo. Mudou aqui? Atualize a cópia lá, ou a CI deles avisa.
- **Para mudar uma regra,** mude o YAML: a gravidade (`bloqueia`, `atencao`, `sugestao` ou `desligada`), a mensagem, os vocabulários ou os parâmetros. Cada regra diz de onde veio (`fonte`).
- **A estrutura da página** (blocos, ordem, rastreamento) continua com a Trilha-LP. A economia, a verba e as campanhas continuam com o briefing. Não são texto público.

## Princípios

- **Anúncio é venda multiplicada: fale do que a pessoa ganha, não de quem a empresa é.** O teste é o do vendedor: um bom vendedor diria isso com o cliente na frente dele? Autoelogio, pedido egoísta ("exija", "evite imitações") e título que apresenta a empresa afastam quem lê.
- **Concretude obrigatória: número, nome próprio ou detalhe no lugar do adjetivo.** "Barbear em 78 segundos" e não "barbear rápido"; "a 500 m do Shopping Pátio" e não "perto de tudo". Se você só pudesse apontar, para o que apontaria?
- **Tudo o que a peça afirma vem do briefing: número, prova, promessa, urgência.** Faltou algo, volta ao briefing; não se inventa na peça. Prova só entra com fonte (número) ou autorização (depoimento), e convence mais quando se parece com quem lê.
- **Promessa com resultado observável, prazo e para quem vale, do tamanho em que esse público acredita.** Promessa que dá para cobrar diferencia; promessa grande demais vira "bom demais para ser verdade". Nunca garantir o que não depende só da empresa (valorização, aprovação, renda, cura).
- **Urgência e escassez só quando são reais, específicas e com motivo.** Prazo inventado é publicidade enganosa e queima a confiança. Sem urgência real, use o custo de não agir.
- **O que o cliente, a lei e a plataforma proíbem não vai ao ar; regra de segmento entra por condição.** Termos e promessas proibidos, atributos pessoais, registro profissional, regra de preço por canal. A ferramenta serve para qualquer segmento: a regra do imobiliário ou da saúde só vale quando o cliente declara o segmento, e mora em dados (playbook, briefing), nunca no código.
- **Escreva para uma pessoa, com as palavras que ela usa, sobre o desejo e a situação dela.** Frases literais da escuta voltam para o anúncio. Falar da situação ("organize as contas do mês") e nunca afirmar quem a pessoa é ("você está endividado?").
- **Uma ideia por peça, uma chamada, um objetivo por página.** Ideias demais diluem a mensagem; dois objetivos criam dúvida. A chamada diz quem, o quê, até quando e como.
- **Claro, curto e com ritmo: frases simples, palavras comuns, tamanhos variados.** Quem lê está ocupado e distraído. Leitura difícil e frases todas iguais fazem a pessoa desistir no meio.
- **O título escolhe quem lê e carrega a promessa principal; título de bloco diz o benefício.** Muita gente só lê os títulos. Trocar só o título muda muito o retorno do mesmo anúncio: escreva muitos, descarte a maioria.
- **A voz é a combinada com o cliente: intensidade, termos, exemplos de assim sim e assim não, pessoa gramatical.** O termostato de 1 (sóbrio) a 5 (euforia de lançamento) limita exclamação, CAIXA ALTA e palavra de euforia. A assinatura (marca, pessoa, marca e pessoa) define se o texto diz "nós" ou "eu".
- **A régua é a venda, não o clique: a peça provoca a micro-ação sem sabotar a macro.** Gancho que dá clique de curioso sem perfil derruba o funil. Curiosidade presa à dor ou ao desejo da persona; a peça também filtra quem não é cliente.
- **Anúncio, página e WhatsApp dizem a mesma coisa, ligados pelo código da célula.** A primeira dobra da página continua a promessa do anúncio que trouxe a pessoa; o código da célula vai no utm_content e na mensagem do WhatsApp.
- **Não somos genéricos: cada peça trata uma objeção real, com a resposta que o time usa ao vivo.** No imobiliário, os três eixos (preço, produto, localização) são obrigatórios na régua. Produto difícil de vender no presencial pede contorno de objeção já no criativo.
- **A revisão aponta, o assessor decide e o teste diz o que funciona.** O que dá para conferir virou regra; o que depende de julgamento virou pergunta ou campo da peça (teste do vendedor, dormir sobre a peça). Ângulo positivo ou negativo é variável de teste, não regra; anúncio que funciona não se troca por cansaço de quem o vê todo dia.

## Como um termo casa com o texto

Texto e vocabulário são comparados sem acento e em minúsculas.

| Notação | Casa com | Exemplo |
|---|---|---|
| `termo` | o termo inteiro | "corra" casa com "Corra!", não com "ocorra"; "so ate" casa com "Só até sexta", não com "isso até" |
| `radical*` | o começo de uma palavra | "garantid*" pega garantido e garantida, não garantia |
| `re:expressão` | expressão regular, com borda no começo e sem emendar em letra no fim | `re:r\$ ?\d` casa com "R$ 450" |

Antes, o briefing, a página e parte da copy procuravam o termo dentro das palavras. Por isso "corra" pegava "ocorra" e "gravida" pegava "gravidade".

## Regras por superfície

| Regra | O que exige | Anúncio | Roteiro | Página | Briefing |
|---|---|---|---|---|---|
| `termo_ou_promessa_proibida` | Nenhum texto público usa termo ou promessa que a marca, o compliance do cliente ou o padrão do segmento proíbem. | bloqueia | bloqueia | bloqueia | bloqueia |
| `garantia_de_resultado` | Não garantir resultado que não depende só da empresa: valorização, aprovação de crédito, renda, cura, fluência, vendas. | bloqueia | bloqueia | bloqueia | bloqueia |
| `atributo_pessoal` | Não afirmar nada sobre quem lê: saúde, finanças, idade, religião, orientação, origem. | bloqueia | atenção | atenção |  |
| `exclusao_de_publico` | Não restringir nem excluir público por gênero, idade, estado civil ou família no texto. | atenção | atenção | atenção |  |
| `promessa_de_ganho` | Promessa de ganho com número diz de quem é o resultado e que ele não é o típico. | atenção | atenção | atenção | atenção |
| `concorrente_citado` | Citar concorrente pelo nome só com o cliente sabendo: publicidade comparativa tem regras. | atenção | atenção | atenção |  |
| `urgencia_ou_escassez_sem_lastro` | Prazo ou vagas acabando só aparecem quando são reais, com motivo, e estão registrados no briefing. | bloqueia | bloqueia | bloqueia | bloqueia |
| `urgencia_vencida` | Urgência com data passada é atualizada antes de ir para qualquer peça. |  |  |  | atenção |
| `numero_sem_lastro` | Todo número que afirma algo vem de uma prova, da oferta ou da promessa aprovada no briefing. | atenção | atenção | atenção |  |
| `prova_nao_utilizavel` | Só entra em anúncio e página a prova com fonte (número, autoridade, mídia, certificação) ou com autorização (depoimento, case). | bloqueia | bloqueia | bloqueia | atenção |
| `prova_de_outra_persona` | A prova usada se parece com quem lê. | atenção | atenção | atenção | sugestão |
| `validada_sem_evidencia` | Afirmação marcada como validada tem evidência registrada. |  |  |  | atenção |
| `afirmacao_sem_fonte` | Toda afirmação do briefing diz quem falou: empresa, consumidor, mercado, dados ou assessor. |  |  |  | sugestão |
| `promessa_incobravel` | A promessa da oferta tem resultado observável com número, prazo e condição (para quem vale). |  |  |  | atenção |
| `objecao_sem_resposta` | Toda objeção que aparece tem a resposta que o time usa ao vivo. |  |  | atenção | atenção |
| `fala_de_si` | A peça fala mais de quem lê do que da empresa. | atenção | atenção | atenção |  |
| `frase_egoista` | Sem autoelogio nem pedido egoísta. | atenção | atenção | atenção | atenção |
| `vago_sem_fato` | Adjetivo ou prova vaga vem acompanhado de um fato no mesmo campo. | sugestão | sugestão | sugestão | sugestão |
| `peca_sem_concretude` | A peça tem ao menos um dado concreto: número, nome próprio ou prova. | atenção | atenção | atenção |  |
| `intensidade_acima_da_combinada` | O tom não passa da intensidade combinada com o cliente (termostato de 1 a 5). | atenção | atenção | atenção |  |
| `sem_palavras_da_persona` | A peça usa ao menos uma palavra das frases literais da persona. | sugestão | sugestão | sugestão |  |
| `diferencial_sem_e_dai` | Diferencial da oferta principal sobe a escada do "e daí?" até o resultado. |  |  |  | sugestão |
| `leitura_dificil` | O texto corrido é fácil de ler. | atenção | atenção | atenção |  |
| `ritmo_monotono` | As frases variam de tamanho. | sugestão | sugestão | sugestão |  |
| `limite_rigido_da_plataforma` | Nenhum texto passa do limite de caracteres que a plataforma recusa. | bloqueia |  |  |  |
| `quantidade_de_textos` | Cada campo tem a quantidade de textos que a plataforma aceita. | bloqueia |  |  |  |
| `texto_longo_para_a_tela` | O texto cabe na tela antes do corte: o gancho e o título aparecem inteiros. | atenção |  | atenção |  |
| `titulos_google_repetidos` | Os títulos do anúncio responsivo não se repetem. | atenção |  |  |  |
| `poucos_titulos_google` | O anúncio responsivo tem títulos suficientes para o Google combinar. | sugestão |  |  |  |
| `titulo_sem_palavra_chave` | Algum título repete uma palavra-chave do grupo. | sugestão |  |  |  |
| `meta_sem_botao` | O anúncio do Meta tem o botão que leva à micro-ação. | atenção |  |  |  |
| `chamada_sem_quando` | A chamada diz quem, o quê, até quando e como. | sugestão | sugestão |  |  |
| `roteiro_tempo_ilegivel` | Toda cena tem o tempo no formato início-fim, em segundos. |  | atenção |  |  |
| `gancho_depois_de_3s` | O gancho resolve nos primeiros 3 segundos. |  | atenção |  |  |
| `duracao_nao_bate` | A soma das cenas bate com a duração declarada. |  | atenção |  |  |
| `fala_nao_cabe_na_cena` | A fala cabe no tempo da cena. |  | atenção |  |  |
| `roteiro_sem_chamada` | O roteiro diz o que fazer depois de assistir. |  | atenção |  |  |
| `roteiro_sem_texto_na_tela` | O roteiro funciona sem som. |  | sugestão |  |  |
| `titulo_de_bloco_generico` | O título de cada bloco diz o benefício, porque muita gente só lê os títulos. |  |  | atenção |  |
| `cta_generico` | O botão diz o que a pessoa recebe ao clicar. |  |  | sugestão |  |
| `preco_proibido_no_canal` | Preço só aparece no canal em que a regra comercial do cliente permite. | bloqueia | bloqueia | bloqueia |  |
| `preco_sem_forma_combinada` | Quando o preço pode aparecer, ele aparece na forma combinada: "a partir de" ou em parcela. | atenção | atenção | atenção |  |
| `registro_profissional_ausente` (só imobiliario, saude, educacao_fisica, juridico) | Onde a profissão exige, o registro profissional aparece em toda publicidade. | atenção | atenção | bloqueia |  |
| `antes_e_depois_em_saude` (só saude) | Antes e depois e prazo de resultado em saúde só com a regra do conselho do cliente conferida. | atenção | atenção | atenção |  |
| `aprovacao_invalidada` | Texto aprovado não muda sem nova aprovação. | bloqueia | bloqueia | bloqueia |  |
| `celula_inexistente` | Toda peça pertence a uma célula da grade do briefing. | bloqueia | bloqueia |  |  |
| `peca_diferente_da_celula` | Persona e oferta da peça são as da célula. | atenção | atenção |  |  |
| `hipotese_inexistente` | A hipótese da peça existe no briefing. | atenção | atenção |  |  |

No anúncio do Meta, `atributo_pessoal` bloqueia. No Google, no roteiro e na página, ele é atenção. `registro_profissional_ausente` é atenção no anúncio e no roteiro, porque o registro pode estar na arte (`arte.registro_na_arte`), e bloqueia na página, onde ele vai no rodapé.

As regras do briefing (`validada_sem_evidencia`, `afirmacao_sem_fonte`, `promessa_incobravel`, `diferencial_sem_e_dai`, `urgencia_vencida`) continuam aplicadas pelo Trilha-briefing. Elas estão aqui para que as três ferramentas falem a mesma língua.

## Divergências resolvidas

Onde as três ferramentas discordavam e o que o padrão adotou:

| Tema | Como era | O padrão adota | Por quê |
|---|---|---|---|
| gravidades na LP | {'copy': 'três gravidades; revisar sai com erro se algo bloqueia', 'briefing': 'três gravidades; bloqueio impede a aprovação', 'lp': 'sem gravidade: tudo sai como "Atenção:" e validar sempre termina com sucesso, até com termo proibido'} | as três gravidades em toda superfície; termo proibido, garantia e preço proibido bloqueiam também na página | é a mesma frase na mesma marca; não pode bloquear no anúncio e passar na página que ele abre |
| como os termos casam com o texto | {'copy': 'proibidos por termo inteiro (texto.py::contem_termo); exagero, urgência e atributos por substring no texto todo', 'briefing': 'substring (_norm(termo) in _norm(texto))', 'lp': 'substring (_sem_acento(termo) in normal)'} | termo inteiro sempre; variação só com radical explícito (*) ou regex (re:) | substring gera falso positivo que ensina o assessor a ignorar o aviso: "corra" em "ocorra", "so ate" em "isso até", "depress" em "depressa", "gravida" em "gravidade", um proibido "caro" em "carona". Com radical explícito, quem escreve a lista decide o alcance. |
| termo que está nas duas listas (voz e promessas) | {'copy': 'tira o repetido e avisa uma vez', 'briefing': 'tira o repetido e avisa uma vez', 'lp': 'avisa duas vezes, uma como termo e outra como promessa'} | uma lista só, sem repetidos, um aviso por campo e termo | aviso repetido vira ruído |
| lista e alcance do adjetivo vago | {'copy': 'melhor(es), qualidade, excelência, excelente, incrível, líder, único no mercado, top; em todo campo sem dígito; sugestão', 'briefing': 'a mesma lista sem "top"; só nos diferenciais; sugestão', 'lp': 'não confere'} | uma lista (união, mais as frases vagas do imobiliário e a prova vaga); toda superfície; sugestão; nome próprio também conta como fato | o mesmo diferencial vago passa por três ferramentas; a lista tem que ser uma só |
| o que é urgência válida | {'copy': 'real e (sem data ou data ≥ hoje); o modelo do contrato ignora urgencia.evidencia; texto com prazo sem isso bloqueia', 'briefing': 'real e (evidência ou motivo), senão bloqueia; data vencida é atenção', 'lp': 'não confere'} | real e (motivo ou evidência) e não vencida; no briefing a data vencida segue como atenção, no texto ela deixa de valer como lastro | o copy aceita hoje uma urgência que o briefing bloqueia (real, sem motivo nem evidência). O dado já chega no copy.yaml; falta o modelo do copy ler. A Aula 2 pede o motivo ("combine with a reason why"). |
| concretude | {'nucleo': 'Trilha/docs/arquitetura/nucleo.md §1.6: copy sem número, fato ou nome próprio é barrada', 'agencia': 'skill fluxos-imobiliarios: adjetivo solto sem dado é proibido', 'copy': 'adjetivo sem fato é sugestão', 'briefing': 'promessa sem número é atenção; diferencial vago é sugestão'} | peça inteira sem número, nome próprio nem prova vira atenção (nova); adjetivo solto num campo segue sugestão | bloqueia fica para risco jurídico, recusa da plataforma ou afirmação falsa; falta de concretude custa caro, mas não é ilegal, e o detector não distingue fato sem dígito ("aulas aos sábados") de vagueza. Proposta: o núcleo troca "barrada" por "apontada na revisão e conferida na aprovação". |
| preço | {'lp': 'só no imobiliário, qualquer R$ seguido de dígito em qualquer campo sem "a partir de" (pega número de prova e parcela)', 'briefing': 'guarda a regra por canal (anuncio, whatsapp, landing → nunca, a_partir_de, parcela, valor_cheio), valida e exporta para o Trilha-ads, mas não para o copy nem para a página', 'copy': 'não confere', 'playbook_imobiliario': 'anuncio: parcela; whatsapp: nunca; landing: a_partir_de', 'agencia': 'WhatsApp nunca dá o valor fechado; o único número permitido é "a partir de", amarrado ao convite de visita'} | regra da marca por canal, com o padrão do playbook quando a marca não definiu; preço só conta com contexto de preço | a regra da LP aplicada ao anúncio imobiliário contradiz o próprio playbook (no anúncio o padrão é parcela). A regra já existe como dado no briefing; falta levar ao copy.yaml. |
| garantia de resultado | {'lp': 'só imobiliário, só "valorização garantida" ou "garantia de valorização" com as palavras coladas', 'copy': '"garantid*" só conta como marca de exagero no termostato', 'briefing': 'só pela lista de promessas proibidas do cliente', 'agencia': 'o exemplo de referência de objecoes_e_apelos.md e anatomia_nutricao.md diz "Comprar na planta agora é garantir um patrimônio com enorme potencial de valorização" e "oportunidade única", e o exemplo da LP proíbe "oportunidade única"'} | regra geral garantia_de_resultado com janela de 4 palavras; listas padrão do imobiliário e da saúde | garantir o que não depende da empresa é o caso clássico de publicidade enganosa em qualquer segmento. O exemplo da agência passaria hoje e deve ser reescrito na skill: "lotes prontos na mesma área custam de 20% a 30% a mais" (fato com fonte) fica; "garantir um patrimônio" e "oportunidade única" saem. |
| registro profissional | {'lp': 'erro de esquema no imobiliário sem marca.registro_profissional (a página nem é construída)', 'copy': 'compliance.registros_profissionais chega no contrato e não é usado', 'briefing': 'só exporta'} | regra de segmento: bloqueia na página, atenção no anúncio (o registro pode estar na arte) | a exigência vale para toda publicidade da profissão, não só para a página, e não só para o imobiliário |
| atributo pessoal fora do anúncio | {'copy': 'bloqueia no Meta, atenção no Google e no roteiro', 'lp': 'não confere', 'curso': 'curso-marketing.txt sugere na página de vendas "você vai continuar gordo" para trazer o medo'} | página também é conferida, com atenção | o Meta revisa o destino do anúncio; e a frase do curso é exatamente o que a política reprova |
| limites de título e corte | {'copy': 'Meta título 40 e descrição 30 recomendados (atenção); gancho de 125; Google 30, 90, 15 rígidos (bloqueia)', 'lp': 'topo.titulo 90, sem gravidade'} | uma regra de corte com limite por campo (atenção) e outra de limite rígido (bloqueia) | é o mesmo problema (o texto some antes do botão); muda só o número |
| lastro de números e provas na página | {'copy': 'todo número precisa estar no briefing; prova citada por id', 'lp': 'topo.provas e prova_social são texto livre; o rascunho vem das provas utilizáveis, mas o assessor edita sem conferência', 'briefing': 'o export para a LP usa só provas utilizáveis'} | número e prova da página conferidos contra o copy.yaml do cliente, como no anúncio | a página é onde mais aparecem números e depoimentos, e hoje é onde nada confere |
| gravidade de prova sem fonte ou autorização | {'briefing': 'atenção', 'copy': 'bloqueia quando a peça cita prova que não está no contrato'} | mantém por superfície: atenção no briefing (ainda é dado), bloqueia na peça (já é uso público) | as duas estão certas; o padrão só deixa explícito que é a mesma regra |
| de onde vêm as listas da página | {'lp': 'termos e promessas proibidos copiados para o pagina.yaml no export; se o briefing muda, a página não sabe', 'copy': 'lê do copy.yaml, que se exporta de novo quando o briefing muda'} | a revisão da página lê as listas do copy.yaml do cliente | uma fonte só; a cópia na página pode envelhecer sem aviso |
| exagero e urgência sobrepostos | {'copy': '"corra", "última chance" e "urgente" contam como exagero; "corra" e "última chance" também como urgência; "segredo" é exagero e também tipo de gancho do catálogo'} | mantém a sobreposição, agora documentada; "urgente" entra na urgência | são perguntas diferentes: o termostato mede o tom; a urgência pede lastro |
| promessa de ganho | {'copy': 'atenção sempre que há ganho e número na frase, mesmo com ressalva; "ganhe 30 minutos" também dispara', 'fontes': 'curso-marketing.txt conta que "100.000 em 7 dias" tomava bloqueio no Meta e no Google; aula-landing-page.txt usa a progressão de renda como argumento de franquia'} | atenção, com exceção quando há ressalva e com "ganh*" só em dinheiro ou %; quando vem junto de garantia, bloqueia pela regra de garantia | a ressalva é exatamente o que a mensagem pede; avisar mesmo com ela gera ruído |
| chamada sem quando e urgência real | {'copy': 'sugere "hoje, até tal dia, esta semana" em toda chamada'} | a mensagem lembra que prazo só entra se for real e que "agora" basta | sem isso, a sugestão empurra para a urgência inventada que outra regra bloqueia |
| CTA padrão do export | {'briefing': 'exportar.py::pagina_lp usa "Quero saber mais" quando a oferta não tem cta', 'lp': 'docs/estrutura.md pede botão com o que a pessoa recebe'} | "quero saber mais" entra em cta_generico; o export marca PENDENTE quando a oferta não tem cta | o rascunho nasce com o botão que a própria estrutura condena |
| escassez nas fontes | {'curso': 'curso-marketing.txt: na página de vendas "tem que ter alguma escassez de alguma forma"', 'aula2': 'Aula 2: "It must be real… don\'t do fake scarcity"', 'copy_briefing': 'só real, com evidência'} | só real; sem escassez real, use o custo de não agir (aula-copy-3.txt, a preferida do autor) | escassez falsa é publicidade enganosa (CDC); a decisão das ferramentas já é essa |
| tom das mensagens | {'copy': 'dizem o problema e o porquê ("o Meta reprova; fale do desejo…")', 'briefing': 'algumas secas ("marcada como validada sem evidência", "objeção sem resposta")', 'lp': 'a maioria explica ("no celular passa de 3 linhas e empurra o botão")'} | toda mensagem tem onde, o quê, por quê e o que fazer, em uma ou duas frases | o assessor decide; ele precisa do motivo para decidir |
| alcance do título genérico | {'lp': 'confere só prova_social, beneficios e como_funciona; o título padrão das objeções é "Perguntas frequentes"'} | confere também objeções e fechamento; "perguntas frequentes" segue aceito | o fechamento é a segunda primeira dobra (aula-landing-page.txt); FAQ simples é o único caso em que a aula aceita título funcional |

## O que ainda não está automatizado

Em ordem de valor. "Checklist humano" é o que depende de julgamento: fica como campo da peça ou pergunta da revisão do assessor.

| # | Regra | Automatizável | Situação |
|---|---|---|---|
| 1 | Exclusão de público e categoria especial (habitação, emprego, crédito) | sim | adotada como exclusao_de_publico (proposta) |
| 2 | Garantia de resultado em qualquer segmento | sim | adotada como garantia_de_resultado (generalizada) |
| 3 | Preço conforme a regra comercial do canal, em anúncio e página | sim | adotada como preco_proibido_no_canal e preco_sem_forma_combinada; depende de o copy.yaml trazer regras_comerciais.preco |
| 4 | Registro profissional e avisos legais obrigatórios nos anúncios (CRECI, registro da incorporação, conselho de saúde, "resultados variam", "imagens ilustrativas") | parcial | registro adotado como registro_profissional_ausente; aviso legal fica a fazer: cada aviso ganha um gatilho (ex.: "resultados variam" quando há promessa de resultado; "imagens ilustrativas" quando a peça usa render; registro da incorporação quando oferta.estagio é lançamento) e o que a imagem mostra segue no checklist humano |
| 5 | Coerência anúncio → página (a primeira dobra continua a promessa do anúncio) | parcial | a fazer: a página declara as células que recebe (pagina.celulas) e a revisão compara as palavras de conteúdo de topo.titulo com a promessa da célula e com os títulos aprovados dessas células (sugestão); o julgamento final é humano |
| 6 | Superlativo absoluto sem prova (o maior, o único, nº 1, o mais barato) | sim | a fazer: vocabulário superlativo e atenção quando a peça não cita prova com fonte |
| 7 | Peça inteira sem dado concreto | sim | adotada como peca_sem_concretude (proposta) |
| 8 | Promessa maior do que o público acredita | parcial | checklist humano com a sofisticação da persona no pacote; parte automática possível: número da promessa maior que o maior número das provas da mesma dimensão vira atenção |
| 9 | Objeções cobrindo os eixos do segmento (imobiliário: preço, produto, localização) | parcial | a fazer: objeções da página levam o eixo (o briefing já tem ObjecaoOferta.eixo) e a revisão avisa eixo do playbook sem objeção |
| 10 | Uma chamada por peça, um objetivo por página | parcial | a fazer: avisar peça com dois verbos de ação diferentes na chamada (agende e ligue; baixe e compre); o resto é humano |
| 11 | Finalidade moradia ou investimento muda a comunicação (imobiliário) | parcial | a fazer: persona ou célula declara a finalidade; peça para moradia com promessa_de_ganho vira atenção |
| 12 | Escassez inespecífica ("vagas limitadas" sem número e sem motivo, mesmo com lastro) | sim | a fazer: sugestão quando há lastro, mas o texto não traz número nem motivo |
| 13 | Título e descrição de SEO da página | sim | adotada: `revisar-pagina` já lê `titulo_seo` e `descricao_seo` (limite de 155 na descrição) |
| 14 | Termos obrigatórios da voz | sim | a fazer, depois de combinar o sentido: por peça ou por conjunto de peças da célula |
| 15 | Exemplos de "assim não" do cliente | parcial | a fazer: sugestão quando uma frase da peça repete boa parte das palavras de um assim_nao; o pacote já mostra os exemplos |
| 16 | Jargão e palavra técnica para o público errado | parcial | a fazer: lista de jargão por segmento no playbook, avisada quando a persona tem sofisticação baixa |
| 17 | Título de benefício com benefício e característica; passo do "como funciona" com o ganho no título | parcial | checklist humano; parte automática: título de passo que é só um verbo genérico ("Cadastro", "Etapa 1") |
| 18 | Mensagens de WhatsApp e salesbot sob o mesmo padrão | parcial | fora do escopo desta versão; candidata a quinta superfície (mensagem) usando os mesmos vocabulários |
| 19 | Uma ideia grande por peça | nao | checklist humano; a peça declara a ideia em uma frase (campo ideia) |
| 20 | Gancho preso à dor ou ao desejo da persona, e não curiosidade solta | nao | checklist humano; a peça declara micro e macro-ação e o subtexto |
| 21 | Contorno de objeção já no criativo quando a aderência digital é baixa | parcial | a fazer: com aderencia_digital baixa, o subtexto da peça precisa ter um trecho com função de objeção |

## Cuidados

- **Saúde:** as listas de saúde (`promessa_proibida_saude`, `antes_e_depois`) não vêm de nenhuma aula nem de nenhuma ferramenta da Trilha. Confira com as regras do conselho de cada cliente antes de confiar nelas. A regra de antes e depois é atenção, não bloqueio, e mostra as regras legais registradas no briefing.
- **Atributo pessoal:** as categorias de `atributo_pessoal` acrescentadas (idade, raça, religião, saúde, finanças) vêm da política de atributos pessoais do Meta, como está citada no método, e não de uma aula.
- **Exemplo de agência:** o exemplo de referência do `briefing-trilha` (fluxos imobiliários) usa "garantir um patrimônio… valorização" e "oportunidade única". Pelo padrão, esse texto bloqueia, e vale reescrever o exemplo lá.
