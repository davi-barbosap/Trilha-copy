"""Catálogo de tipos de gancho. Serve para variar o gancho de propósito, um tipo por variação.

Todo gancho abre uma lacuna entre o que a pessoa sabe e o que ela quer. Em anúncio, a lacuna precisa
estar presa ao desejo ou à dor da persona; curiosidade solta traz clique de quem não compra.
Os exemplos são de segmentos diferentes de propósito: o tipo vale para qualquer um.
"""

from __future__ import annotations

GANCHOS: dict[str, tuple[str, str]] = {
    "identidade": ("Chama quem você quer pelo nome do grupo",
                   "Dono de oficina com agenda vazia na segunda-feira: isto é para você."),
    "resultado_sem_como": ("Mostra o resultado e esconde o caminho",
                           "Em 4 meses ela apresentou o fechamento do trimestre em inglês, sem ler."),
    "pergunta": ("Pergunta que a pessoa quer ver respondida",
                 "Por que o seu orçamento é aprovado e o cliente some antes de fechar?"),
    "contradicao": ("Afirma o contrário do esperado",
                    "Mais treino não está te deixando mais forte. Mais descanso, sim."),
    "laco_aberto": ("Começa uma história e não termina",
                    "Na terceira vez que o cliente pediu desconto, o Paulo fez uma pergunta diferente."),
    "segredo": ("Promete algo que poucos sabem (use com cuidado; exige entrega)",
                "O que as clínicas com agenda cheia fazem na véspera de cada consulta."),
    "numero_especifico": ("Número exato no lugar do adjetivo",
                          "Barbear em 78 segundos."),
    "erro_comum": ("Aponta um erro que a pessoa provavelmente comete",
                   "Se você responde o orçamento por e-mail, está perdendo para quem liga."),
    "espelho": ("Descreve a situação da pessoa melhor do que ela descreveria",
                "Você entende a reunião inteira, prepara a frase, o assunto muda e a frase fica guardada."),
    "comparacao_incompleta": ("Analogia que pede explicação",
                              "É como um GPS, só que para o caixa da sua loja."),
    "bastidores": ("Conta o cuidado que ninguém conta (Schlitz)",
                   "Cada lote de pão é provado às 5h por quem assou. O que não passa, não vai para a vitrine."),
    "promessa": ("A promessa principal, direta",
                 "Mil músicas no seu bolso."),
    "custo_de_nao_agir": ("Mostra o que se perde ficando como está",
                          "Cada mês com a planilha errada custa a margem de um cliente inteiro."),
    "prova_social": ("Abre pela prova, com número ou nome",
                     "Nota 4,9 com 87 avaliações: o que os alunos dizem depois do primeiro mês."),
    "novidade": ("Algo que mudou e cria uma oportunidade",
                 "A nova regra da Receita mudou o prazo do seu MEI. Veja o que fazer até sexta."),
}
