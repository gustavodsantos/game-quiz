from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils.timezone import now

from mysite.base.constants import NIVEL_DIFICULDADE, PONTUACAO_MAXIMA, PONTUACAO_MINIMA
from mysite.base.forms import AlunoForm
from mysite.base.models import Aluno, Pergunta, Resposta


def home(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            aluno = Aluno.objects.get(email=email)
        except Aluno.DoesNotExist:
            # Caso o aluno não exista, criar um novo a partir do formulário
            form = AlunoForm(request.POST)
            if form.is_valid():
                aluno = form.save()
                request.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                return render(request, 'base/home.html', {'form': form})

        # Caso o aluno já exista, armazenar o ID na sessão e redirecionar
        request.session['aluno_id'] = aluno.id
        return redirect('/perguntas/1')

    # Retornar o formulário inicial ao carregar a página
    return render(request, 'base/home.html', {'form': AlunoForm()})


def perguntas(request, indice: int):
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        return redirect('/')

    # Recuperar as perguntas disponíveis
    perguntas_disponiveis = Pergunta.objects.filter(disponivel=True).order_by('id')
    try:
        pergunta = perguntas_disponiveis[indice - 1]
    except IndexError:
        return redirect('/classificacao')

    # Contexto inicial para a renderização
    context = {
        'indice_da_questao': indice,
        'pergunta': pergunta,
        'dificuldade_da_pergunta': pergunta.dificuldade,
    }

    if request.method == 'POST':
        resposta_indice = int(request.POST.get('resposta_indice', -1))  # Define -1 para casos de falha
        if resposta_indice == pergunta.alternativa_correta:
            # Calcula pontuação baseada no tempo da primeira resposta
            try:
                data_primeira_resposta = Resposta.objects.filter(pergunta=pergunta).earliest('criacao').criacao
                segundos_passados = max(int((now() - data_primeira_resposta).total_seconds()), 0)
                pontos_base = max(PONTUACAO_MAXIMA - segundos_passados, PONTUACAO_MINIMA)
            except Resposta.DoesNotExist:
                pontos_base = PONTUACAO_MAXIMA  # Primeira resposta recebe a pontuação máxima

            dificuldade = pergunta.dificuldade
            pontos = pontos_base * NIVEL_DIFICULDADE.get(dificuldade, 1)

            try:
                Resposta.objects.create(aluno_id=aluno_id, pergunta=pergunta, pontos=pontos)
            except IntegrityError:
                messages.error(request, 'Você já respondeu a esta pergunta! Por favor, continue.')
                return redirect(f'/perguntas/{indice}')

            return redirect(f'/perguntas/{indice + 1}')

        # Caso a resposta esteja errada
        return redirect(f'/perguntas/{indice + 1}')

    return render(request, 'base/perguntas.html', context)


def classificacao(request):
    aluno_id = request.session.get('aluno_id')
    if not aluno_id:
        return redirect('/')

    # Pontuação total do aluno atual
    pontos_dct = Resposta.objects.filter(aluno_id=aluno_id).aggregate(total_pontos=Sum('pontos'))
    pontos_do_aluno = pontos_dct.get('total_pontos') or 0

    # Cálculo da posição do aluno
    alunos_com_mais_pontos = (
        Resposta.objects.values('aluno')
        .annotate(total_pontos=Sum('pontos'))
        .filter(total_pontos__gt=pontos_do_aluno)
        .count()
    )

    # Recuperar os primeiros 10 alunos em ordem decrescente de pontos
    primeiros_alunos_do_ranking = (
        Resposta.objects.values('aluno_id', 'aluno__nome')
        .annotate(total_pontos=Sum('pontos'))
        .order_by('-total_pontos')[:10]
    )

    # Construir o contexto para o template do ranking
    context = {
        'pontos': pontos_do_aluno,
        'posicao': alunos_com_mais_pontos + 1,
        'primeiros_alunos_do_ranking': primeiros_alunos_do_ranking,
        'ranking_total': Resposta.objects.aggregate(total_pontos=Sum('pontos')).get('total_pontos', 0),
    }

    return render(request, 'base/classificacao.html', context)
