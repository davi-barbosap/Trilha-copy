# Contrato com o Trilha-briefing e o que sai daqui

Os repositórios não dependem um do outro em código. Eles combinam um arquivo.

## Entrada: `copy.yaml`

Gerado no Trilha-briefing com `python -m trilha_briefing exportar clientes/<id> --para copy` e trazido com `python -m trilha_copy importar <arquivo>`.

O campo `contrato` diz a versão. Esta ferramenta aceita as versões em `VERSOES_SUPORTADAS` (`trilha_copy/contrato.py`), hoje `{1}`, e recusa as outras com a mensagem "atualize o trilha-copy". Campos que ela ainda não conhece são ignorados. Assim o briefing pode acrescentar campos sem quebrar nada; mudar ou remover um campo exige uma versão nova.

| Bloco | Para que a copy usa |
|---|---|
| `cliente` | id da pasta, nome no pacote e nos roteiros |
| `voz` | tom, exemplos de "assim sim / assim não", termos proibidos, **intensidade** (limite de exagero) |
| `posicionamento`, `unicidade` | P de Posicionamento |
| `compliance` | termos e promessas proibidos (bloqueiam), avisos legais e o que não pode (no pacote) |
| `concorrentes` | só os nomes, para avisar quando a peça cita um |
| `personas` | P de Pessoas; frases literais conferidas na revisão; ids ligam peças e provas |
| `nao_atender` | no pacote, para a peça filtrar quem não é cliente |
| `ofertas` | Promessa, Prioridade e Processo; urgência e escassez reais liberam palavras de prazo; os números da oferta dão lastro |
| `provas` | só as utilizáveis. Cada uma com `id`; `personas` e `perfil` dizem para quem a prova convence |
| `historias` | só as autorizadas |
| `grade` | cada peça nasce de uma célula (`codigo`), com persona, oferta e a promessa da célula |
| `hipoteses` | a peça se liga a uma hipótese da célula |
| `metrica_principal`, `evento_otimizacao` | preenchem a macro-ação da peça nova |

O exemplo versionado (`clientes/_exemplo/copy.yaml`) é a exportação do exemplo do briefing. `tests/test_contrato.py` confere, com o briefing no `PYTHONPATH`, que a exportação carrega, que é igual ao exemplo daqui e que as peças do exemplo continuam sem bloqueio.

## Saída: `dist/<id>/`

Só saem peças **aprovadas** cujo texto não mudou depois da aprovação.

**`anuncios.csv`**, uma linha por texto:

| Coluna | Conteúdo |
|---|---|
| `codigo` | código da célula (`PT01`) |
| `utm_content` | o mesmo código: é o que o Trilha lê no raio-x e o que a Trilha-LP põe na mensagem do WhatsApp |
| `peca` | id da peça |
| `formato` | `meta_feed`, `meta_reels` ou `google_rsa` |
| `campo` | `texto_principal`, `titulo`, `descricao`, `botao` (Meta); `titulo`, `descricao`, `caminho` (Google) |
| `ordem` | posição do texto no campo, a partir de 1 |
| `texto`, `caracteres` | o texto e o tamanho dele |

**`roteiros/<peca>.md`**, um por roteiro aprovado: tabela de cenas (tempo, fala, visual, texto na tela), chamada e o código para a UTM.

## Mudou algo?

- **Campo novo no briefing:** nada a fazer aqui até a copy usar o campo. Quando usar, acrescente ao modelo em `contrato.py` com valor padrão.
- **Campo mudou de sentido ou saiu:** suba a versão do contrato nos dois repositórios, no mesmo dia, e atualize o exemplo daqui com a exportação nova.
- **Coluna nova no CSV:** acrescente no fim, para não quebrar planilhas que já leem as colunas pela posição.
