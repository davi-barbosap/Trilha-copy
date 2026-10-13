# Contrato com o Trilha-briefing e o que sai daqui

Os repositórios não dependem um do outro em código. Eles combinam um arquivo.

## Entrada: `copy.yaml`

Gerado no Trilha-briefing. Com os clientes no Trilha-clientes, a exportação grava direto na pasta desta ferramenta: `python -m trilha_briefing exportar briefing/<id> --para copy --saida copy` cria `copy/<id>/copy.yaml`. Fora dele, `python -m trilha_copy importar <arquivo>` copia o contrato para `clientes/<id>/`.

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
| `utm_content` | o mesmo código: vai no anúncio e é o que a Trilha-LP põe na mensagem do WhatsApp. O raio-x do Trilha-ads agrupa os resultados por ele (`por_criativo`) |
| `peca` | id da peça |
| `formato` | `meta_feed`, `meta_reels` ou `google_rsa` |
| `campo` | `texto_principal`, `titulo`, `descricao`, `botao` (Meta); `titulo`, `descricao`, `caminho` (Google) |
| `ordem` | posição do texto no campo, a partir de 1 |
| `texto`, `caracteres` | o texto e o tamanho dele |

**`subida.csv`**, uma linha por anúncio a criar na plataforma. Sai quando o contrato traz o plano de campanhas (`veiculacao`):

| Coluna | Conteúdo |
|---|---|
| `plataforma` | `meta` ou `google` |
| `campanha`, `conjunto` | os nomes do plano, já com as regras de nomes do cliente |
| `nome_anuncio` | o molde do plano (padrão `{codigo} \| v{versao}`) com o código e a `versao` da peça: `PT01 \| v2` |
| `parametros_url` | o molde de UTM do plano, com o código: vai no campo "parâmetros de URL" do anúncio |
| `codigo`, `peca`, `formato` | para achar os textos da peça no `anuncios.csv` |

A mesma peça aparece em uma linha por conjunto em que a célula está no plano, porque cada campanha tem o seu `utm_campaign`. Peça aprovada cuja célula não está em nenhum conjunto daquela plataforma fica fora e gera um aviso: o lugar dela se decide no plano do briefing, não na hora de subir. Roteiro de vídeo não entra: ele vira anúncio pela peça `meta_reels` que usa o vídeo.

`versao` (1, 2, 3…) numera as peças da mesma célula na mesma plataforma. O `nova` dá o próximo número sozinho, e o `validar` recusa duas peças com o mesmo, porque os anúncios teriam o mesmo nome.

**`criativos/<peca>.md`**, um por anúncio do Meta aprovado: o briefing do criativo para a equipe de criação. Traz:
- para que serve a peça e o que varia no teste;
- para quem, a ideia e as provas;
- o que não pode e o que é obrigatório;
- o que a arte mostra, o texto na arte e as medidas;
- a identidade da marca (`identidade_visual` do contrato);
- os textos que acompanham a arte.

**`roteiros/<peca>.md`**, um por roteiro aprovado, com o mesmo cabeçalho do briefing do criativo. Traz a tabela de cenas (tempo, parte do modelo, fala, visual, texto na tela), o que cada parte faz, a chamada e o código para a UTM.

## Mudou algo?

- **Campo novo no briefing:** nada a fazer aqui até a copy usar o campo. Quando usar, acrescente ao modelo em `contrato.py` com valor padrão.
- **Campo mudou de sentido ou saiu:** suba a versão do contrato nos dois repositórios, no mesmo dia, e atualize o exemplo daqui com a exportação nova.
- **Coluna nova no CSV:** acrescente no fim, para não quebrar planilhas que já leem as colunas pela posição.
