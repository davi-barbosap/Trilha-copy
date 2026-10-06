# Mudanças

## 0.2.0 — padrão de texto da Trilha (out/2026)

### Novo
- **`trilha_copy/regras/padrao.yaml`:** o padrão de texto num arquivo só.
  - **Conteúdo:** 15 princípios, 25 vocabulários, parâmetros e 48 regras, cada uma com gravidade, mensagem, fonte e exemplos.
  - **Alcance:** vale para anúncio, roteiro, página e briefing. Antes, as regras estavam espalhadas em três ferramentas, com listas e gravidades diferentes.
  - **Edição:** gravidade (inclusive `desligada`), mensagem, vocabulários e parâmetros são editáveis, e a gravidade pode mudar por contexto (`gravidade_por_contexto`).
  - **Documentação:** [docs/padrao-de-texto.md](docs/padrao-de-texto.md).
- **`revisar-pagina <pagina.yaml>`:** o texto de uma página da Trilha-LP pelo mesmo padrão, com o contrato do cliente.
- **`padrao`:** lista os princípios e as regras por superfície.
- **Regras novas:**
  - garantia de resultado, em qualquer segmento (bloqueia);
  - exclusão de público no texto;
  - peça sem nenhum dado concreto;
  - preço conforme a regra comercial do canal, que bloqueia quando o cliente não mostra preço;
  - registro profissional ausente (`arte.registro_na_arte` quando ele está na imagem);
  - antes e depois em saúde;
  - na página: título de bloco genérico, botão genérico, objeção sem resposta, título do topo e descrição de SEO longos.

### Mudou
- **Termos casam como palavra inteira** (`radical*` e `re:` quando a lista quer variações). "corra" não pega mais "ocorra", nem "gravida" pega "gravidade".
- **Urgência válida agora exige motivo** (real, com motivo e no prazo). Escassez continua exigindo evidência.
- **Promessa de ganho:** com ressalva ("resultados variam" ou um aviso legal do cliente), não avisa. "Ganhe 2 aulas" não conta como promessa de renda.
- **Mensagens:** as mensagens da revisão vêm do padrão. Algumas mudaram de texto.
- **Contrato:** lê `cliente.playbook` (liga as regras de segmento) e `preco` (regra comercial por canal), vindos do briefing. Sem eles, o segmento é deduzido dos registros profissionais (CRO → saúde) e o preço fica livre.

## 0.1.4 — roteiros com modelo de corpo e briefing do criativo (out/2026)

- **Modelos de corpo para roteiro** em `trilha_copy/regras/roteiros.yaml` (editável):
  - educativo: o quê → por quê → como;
  - história: mas… então…;
  - oferta direta: os 6 Ps.

  Cada cena declara a `parte` que cumpre. A revisão avisa parte que falta, fora de ordem ou que o modelo não tem. `nova --modelo` cria as cenas com tempos sugeridos, e `roteiros` lista os modelos. Para sair de rascunho, o roteiro precisa de um modelo.
- **Briefing do criativo** (`dist/<id>/criativos/<peca>.md`) para a equipe de criação. Não é design: diz o que a arte precisa comunicar.
  - **O que traz:** para que serve, o que varia no teste, para quem, a ideia, as provas, o que não pode, o que mostrar, o texto na arte, a identidade da marca e as medidas.
  - **Bloco novo:** o anúncio do Meta ganha `meta.arte` (tipo, mostrar, texto na arte, evitar, referências).
  - **Fluxo:** para ir a final, o anúncio precisa de `arte.mostrar`.
- **Texto na arte** passa pela revisão e entra na assinatura da aprovação. Os campos novos vazios não mudam a assinatura, então peças aprovadas antes continuam aprovadas.
- **O roteiro exportado** ganha o mesmo cabeçalho e a parte de cada cena.
- **Contrato:** lê `identidade_visual` (cores, tipografia, logo, estilo de imagem) vinda do briefing.
- **Exemplo:** o PT02 segue o modelo educativo, e o PT01 traz o briefing da arte (aprovação assinada de novo).

## 0.1.3 — lista de subida a partir do plano de campanhas (out/2026)

- **`subida.csv`:** um anúncio por linha, com a campanha, o conjunto, o nome do anúncio e os parâmetros de URL. Os nomes e a UTM vêm do plano de campanhas do briefing (`veiculacao` no contrato); a copy só põe o código e a versão da peça. Antes, quem subia montava o nome e a UTM à mão.
- **`versao` na peça:** numera as peças da mesma célula na mesma plataforma e entra no nome do anúncio. O `nova` dá o próximo número sozinho (rodar duas vezes na mesma célula cria a versão 2, em vez de recusar), e o `validar` recusa duas peças com a mesma versão.
- **Aviso:** peça aprovada cuja célula não está em nenhum conjunto da plataforma no plano fica fora da subida, com aviso. Contrato sem plano gera só os textos, também com aviso.
- **Teste de contrato:** tolera o bloco `veiculacao` no exemplo enquanto o Trilha-briefing instalado não o exporta (até o merge da 0.4.1 de lá).

## 0.1.2 — o raio-x já lê o código (out/2026)

- **Documentação:** o Trilha-ads 0.8.0 agrupa o raio-x pelo código da célula no `utm_content` (`por_criativo`). README, contrato e exportação deixam de dizer que isso está no roadmap.

## 0.1.1 — organização do ecossistema (out/2026)

- **Nome:** Trilha-copy (antes Trilha-copywritter).
- **`validar <pasta>`:** confere se o contrato e as peças estão no formato certo, sem julgar o texto. É o que o Trilha-clientes usa para conferir os clientes.
- **Correção:** a documentação dizia que o Trilha-ads já lê o `utm_content` no raio-x. Ele ainda não agrupa por esse código; está no roadmap de lá.
- **Clientes reais** ficam no Trilha-clientes, pasta `copy/`. O briefing exporta direto para lá.
- **CI:** clona o Trilha-briefing e roda o teste de contrato de verdade, em vez de pulá-lo.
- **README:** cada comando com o que faz, entradas e saídas, o que não faz e a situação atual.

## 0.1.0 — primeira versão (out/2026)

Estrutura e revisão de copy a partir do contrato com o Trilha-briefing. Não gera texto.

### Novo
- **Contrato:** lê o `copy.yaml` do Trilha-briefing (versão 1), ignora campos novos e recusa versões que não conhece.
- **Pacote da célula:** os 6 Ps (Pessoas, Posicionamento, Promessa, Prova, Prioridade, Processo), com o que falta no briefing.
- **Peças:** anúncio do Meta (feed, Reels e Stories), anúncio responsivo de pesquisa do Google e roteiro de vídeo curto, em versão básica.
- **Estados:** fundação → rascunho → refinado → final → aprovado, com checklist em cada passagem. A aprovação tem duas travas: o teste do vendedor e não aprovar no mesmo dia em que a peça ficou final. A assinatura do texto derruba a aprovação se ele mudar.
- **Revisão** em três gravidades:
  - compliance: termos e promessas proibidos, atributos pessoais, promessa de ganho, concorrente;
  - lastro: números, provas, urgência;
  - princípios de Hopkins: fala de si, autoelogio, adjetivo sem fato, intensidade;
  - leitura: legibilidade em português, ritmo, palavras da persona;
  - limites de cada formato;
  - integridade.
- **Exportação:** `anuncios.csv` com o código da célula como `utm_content`, e roteiros em Markdown.
- **Catálogo de 15 tipos de gancho** e **banco de referências decupadas**, com 4 exemplos clássicos de segmentos diferentes.
- **Testes:** 60 testes, sendo 4 do contrato, que rodam com o Trilha-briefing ao lado. CI com testes, revisão e exportação do exemplo.
