# Mudanças

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
