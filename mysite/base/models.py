from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from mysite.base.constants import DIFICULDADE_CHOICES


class Pergunta(models.Model):
    dificuldade = models.CharField(max_length=12, choices=DIFICULDADE_CHOICES, default='facil')
    enunciado = models.TextField()
    alternativa_correta = models.IntegerField(choices=[(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')])
    alternativas = models.JSONField(default=list)  # Define um valor padrão como uma lista vazia

    def clean(self):
        super().clean()
        # Validações para o campo "alternativas"
        if not self.alternativas:
            raise ValidationError('O campo "alternativas" não pode estar vazio.')
        if not isinstance(self.alternativas, list):
            raise ValidationError('O campo "alternativas" deve ser uma lista.')
        if len(self.alternativas) != 4:
            raise ValidationError('O campo "alternativas" deve conter exatamente 4 itens.')

    disponivel = models.BooleanField(default=False)

    def conferir_resposta(self, resposta_indice: int):
        resposta_indice = int(resposta_indice)
        return resposta_indice == self.alternativa_correta

    def __str__(self):
        return self.enunciado


class Aluno(models.Model):
    total_pontos = models.IntegerField(default=0)
    nome = models.CharField(max_length=64)
    email = models.EmailField(unique=True)
    criacao = models.DateTimeField(auto_now_add=True)
    pontuacao_maxima = models.IntegerField(default=0)

    def atualizar_pontuacao_maxima(self):
        pontos = Resposta.objects.filter(aluno=self).aggregate(total=Sum('pontos')).get('total') or 0
        if pontos > self.pontuacao_maxima:
            self.pontuacao_maxima = pontos
            self.save()

    def __str__(self):
        return self.email


class Partida(models.Model):
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE)
    data_inicio = models.DateTimeField(auto_now_add=True)
    finalizada = models.BooleanField(default=False)

    def __str__(self):
        return f'Partida de {self.aluno.nome} iniciada em {self.data_inicio}'


class Resposta(models.Model):
    criacao = models.DateTimeField(auto_now_add=True)
    pontos = models.IntegerField()
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, null=True, blank=True)

    @classmethod
    def registrar_resposta(cls, aluno, pergunta, partida, resposta_selecionada):
        # Garante que não existirá duplicidade consultando a base de dados
        resposta_existente = cls.objects.filter(aluno=aluno, pergunta=pergunta, partida=partida).first()

        if resposta_existente:
            # Retorna a resposta existente e seus pontos
            return resposta_existente, resposta_existente.pontos

        # Calcula a pontuação com base na resposta correta
        pontos = 10 if pergunta.conferir_resposta(resposta_selecionada) else 0

        # Cria uma nova resposta apenas se não existir
        instance = cls.objects.create(aluno=aluno, pergunta=pergunta, partida=partida, pontos=pontos)
        return instance, pontos

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'pergunta'],  # Garante apenas 1 resposta por aluno e pergunta
                name='resposta_unica',
            ),
        ]

    def __str__(self):
        return f'Resposta de {self.aluno} na Partida {self.partida} - {self.pontos} pontos'
