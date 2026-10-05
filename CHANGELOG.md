# Mudanças

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
