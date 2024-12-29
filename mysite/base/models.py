from django.core.exceptions import ValidationError
from django.db import models

from mysite.base.constants import DIFICULDADE_CHOICES


class Pergunta(models.Model):
    dificuldade = models.CharField(max_length=10, choices=DIFICULDADE_CHOICES, default='facil')
    enunciado = models.TextField()
    alternativa_correta = models.IntegerField(choices=[(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')])
    alternativas = models.JSONField()

    def clean(self):
        super().clean()
        # Garante que o campo "alternativas" seja uma lista com exatamente 4 itens
        if not isinstance(self.alternativas, list) or len(self.alternativas) != 4:
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

    def __str__(self):
        return self.email


class Resposta(models.Model):
    def __str__(self):
        return f"Resposta de {self.aluno} para '{self.pergunta}' - {self.pontos} pontos"

    criacao = models.DateTimeField(auto_now_add=True)
    pontos = models.IntegerField()
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'pergunta'],
                name='resposta_unica',
                violation_error_message='Cada aluno pode responder a cada pergunta apenas uma vez.',
            )
        ]
