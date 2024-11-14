from django.contrib import admin

from mysite.base.models import Aluno, Pergunta, Resposta


def tornar_disponivel(modeladmin, request, queryset):
    queryset.update(disponivel=True)


tornar_disponivel.short_description = "Tornar Disponivel"


def tornar_indisponivel(modeladmin, request, queryset):
    queryset.update(disponivel=False)


tornar_indisponivel.short_description = "Tornar Indisponivel"


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'enunciado', 'disponivel')
    actions = [tornar_disponivel, tornar_indisponivel]


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'criacao')


@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ('criacao', 'pergunta', 'aluno', 'pontos')
