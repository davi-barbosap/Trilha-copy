# Trilha-copywritter

Estrutura e revisão de copy para anúncios. A ferramenta não escreve por você: ela junta o que o briefing sabe do cliente antes de você escrever, acompanha a peça até a aprovação e aponta o que vai ser reprovado, cortado ou soar falso. Quem escreve e decide é o assessor.

Serve para qualquer segmento. O exemplo (`clientes/_exemplo/`) é uma escola de inglês fictícia.

Formatos desta versão:
- anúncio do Meta: feed, Reels e Stories;
- anúncio responsivo de pesquisa do Google;
- roteiro de vídeo curto, em versão básica (cenas com tempo, fala, visual e texto na tela).

Onde a ferramenta entra:
- **Recebe** do [Trilha-briefing](https://github.com/davi-barbosap/Trilha-briefing) o `copy.yaml`: personas, voz, ofertas, provas utilizáveis, compliance e a grade de células. A copy não inventa nada sobre o cliente: o que não está no contrato não pode ser afirmado.
- **Entrega** o `anuncios.csv` e os roteiros das peças aprovadas. Cada linha leva o código da célula (`PT01`, `GB01`…), que é o mesmo `utm_content` que o [Trilha](https://github.com/davi-barbosap/Trilha) lê no raio-x e que a [Trilha-LP](https://github.com/davi-barbosap/Trilha-LP) põe na mensagem do WhatsApp.

## Como usar

```bash
pip install -e .

# no Trilha-briefing: python -m trilha_briefing exportar clientes/minha-cliente --para copy
python -m trilha_copy importar ../Trilha-briefing/dist/minha-cliente/copy.yaml   # → clientes/minha-cliente/copy.yaml

python -m trilha_copy pacote    clientes/minha-cliente PT01 --formato meta_feed   # os 6 Ps da célula, antes de escrever
python -m trilha_copy nova      clientes/minha-cliente PT01 --formato meta_feed   # cria pecas/PT01/pt01-meta-feed.yaml
python -m trilha_copy checklist clientes/minha-cliente/pecas/PT01/pt01-meta-feed.yaml   # o que falta para avançar
python -m trilha_copy avancar   clientes/minha-cliente/pecas/PT01/pt01-meta-feed.yaml   # próximo estado, se nada faltar
python -m trilha_copy revisar   clientes/minha-cliente                            # avisos por gravidade; sai com erro se algo bloqueia
python -m trilha_copy aprovar   clientes/minha-cliente/pecas/PT01/pt01-meta-feed.yaml --por "Seu nome" --teste-do-vendedor
python -m trilha_copy exportar  clientes/minha-cliente                            # dist/<id>/anuncios.csv e roteiros/

python -m trilha_copy ganchos                                                     # catálogo de 15 tipos de gancho
python -m trilha_copy referencias                                                 # banco de referências decupadas
```

## O caminho de uma peça

| Estado | Para sair dele |
|---|---|
| **fundação** | persona, micro-ação (o que esta peça provoca), macro-ação (o que o sistema precisa), a ideia grande em uma frase, e um briefing sem buraco crítico: persona com dores, promessa e ao menos uma prova |
| **rascunho** | 10 rascunhos de título ou gancho ou mais, emoção principal (novo, fácil, seguro ou grande), ângulo, tipo de gancho e o mínimo de textos que a plataforma pede |
| **refinado** | subtexto anotado (ao menos 3 trechos, cada um com o que deve fazer sentir ou pensar), a prova usada e nenhum aviso que bloqueie |
| **final** | só o comando `aprovar`, que exige o **teste do vendedor** ("um bom vendedor diria isso com o cliente na frente dele?") e que a peça tenha virado final em outro dia (`--mesmo-dia` para pular, de propósito) |
| **aprovado** | a aprovação guarda uma assinatura do texto. Mudou uma vírgula depois de aprovar, a peça não exporta até ser aprovada de novo |

`avancar` e `aprovar` trocam a linha `estado:` e acrescentam ao `historico:` sem reescrever o resto do arquivo: os comentários ficam.

## A revisão

- **Bloqueia:**
  - termo ou promessa proibidos no briefing;
  - texto acima do limite que a plataforma recusa;
  - menos textos do que a plataforma exige;
  - prazo ou vagas acabando sem urgência ou escassez reais no briefing;
  - prova que não está no contrato;
  - no Meta, afirmação sobre atributo pessoal de quem lê ("você está endividado?");
  - texto alterado depois da aprovação;
  - célula que não existe na grade.
- **Atenção:**
  - número que não vem de nenhuma prova, oferta ou promessa do briefing;
  - promessa de ganho com número;
  - concorrente citado pelo nome;
  - mais "nós/nosso" do que "você";
  - autoelogio ("somos líderes", "exija o original");
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

## Arquivos

```
clientes/<id>/
  copy.yaml                    contrato vindo do Trilha-briefing (não edite aqui; edite lá e importe de novo)
  pecas/<codigo>/<peca>.yaml   uma peça por arquivo, na pasta da célula da grade
referencias/<id>.yaml          peças boas de qualquer segmento, decupadas trecho a trecho
```

## O que a ferramenta não faz

- **Não gera texto.** Não há IA escrevendo: a ferramenta organiza, confere e registra.
- **Não sobe anúncio.** O CSV é para você copiar ou importar no gerenciador; não foi testado contra a importação em massa do Meta ou do Google.
- **Não substitui a política das plataformas.** As listas de termos sensíveis pegam os casos comuns, não todos. Os limites de caracteres mudam de tempos em tempos.
- **Não mede resultado.** Quem mede é o Trilha, pelo código da célula.

## Documentação

- [Método](docs/metodo.md): de onde vêm as regras, o que cada uma confere e onde fomos críticos com as fontes.
- [Contrato com o Trilha-briefing](docs/contrato.md): o que entra, o que sai e como mudar sem quebrar.
- [Mudanças](CHANGELOG.md).

## Testes

```bash
python -m unittest discover -s tests -v
PYTHONPATH=../Trilha-briefing python -m unittest tests.test_contrato -v   # contrato, com o briefing ao lado
```

## Dados de clientes

Peças e contratos de clientes reais têm estratégia e dados do cliente (LGPD). Por padrão, o `.gitignore` deixa `clientes/*` fora do Git e versiona só o exemplo. Se o repositório for privado e você quiser versionar os clientes aqui, apague as duas linhas no fim do `.gitignore`.
