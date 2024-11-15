from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils.timezone import now

from mysite.base.forms import AlunoForm
from mysite.base.models import Aluno, Pergunta, Resposta


def home(request):
    if request.method == 'POST':
        # Usuário já existe
        email = request.POST['email']
        try:
            aluno = Aluno.objects.get(email=email)
        except Aluno.DoesNotExist:
            # Usuário não existe
            form = AlunoForm(request.POST)
            if form.is_valid():
                aluno = form.save()
                request.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                contexto = {'form': form}
                return render(request, 'base/home.html', contexto)
        else:
            request.session['aluno_id'] = aluno.id
            return redirect('/perguntas/1')
    return render(request, 'base/home.html')


PONTUACAO_MAXIMA = 1000


def perguntas(request, indice: int):
    try:
        aluno_id = request.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        try:
            pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
        except IndexError:
            return redirect('/classificacao')
        else:
            contexto = {'indice_da_questao': indice, 'pergunta': pergunta}
            if request.method == 'POST':
                resposta_indice = int(request.POST['resposta_indice'])
                if resposta_indice == pergunta.alternativa_correta:
                    # Armazenar dados da resposta
                    try:
                        data_da_primeira_resposta = (
                            Resposta.objects.filter(pergunta=pergunta).order_by('criacao')[0].criacao
                        )
                    except IndexError:
                        pontos = PONTUACAO_MAXIMA
                    else:
                        diferenca = now() - data_da_primeira_resposta
                        diferenca_em_segundos = int(diferenca.total_seconds())
                        pontos = max(PONTUACAO_MAXIMA - diferenca_em_segundos, 10)

                    try:
                        Resposta.objects.create(aluno_id=aluno_id, pergunta=pergunta, pontos=pontos)
                    except IntegrityError:
                        messages.error(request, 'Resposta já existe para este aluno e pergunta.')
                        return redirect(f'/perguntas/{indice}')

                    return redirect(f'/perguntas/{indice + 1}')

                # Caso a resposta esteja incorreta
                contexto['resposta_correta'] = resposta_indice
            return render(request, 'base/perguntas.html', contexto)


def classificacao(request):
    if 'aluno_id' not in request.session:
        return redirect('/')
    aluno_id = request.session['aluno_id']
    pontos_dct = Resposta.objects.filter(aluno_id=aluno_id).aggregate(Sum('pontos'))
    pontos_do_aluno = pontos_dct['pontos__sum']
    if pontos_do_aluno is None:
        pontos_do_aluno = 0
    alunos_com_mais_pontos = (
        Resposta.objects.values('aluno').annotate(Sum('pontos')).filter(pontos__sum__gt=pontos_do_aluno).count()
    )
    primeiros_alunos_do_ranking = list(
        Resposta.objects.values('aluno', 'aluno__nome').annotate(Sum('pontos')).order_by('-pontos__sum')[:5]
    )
    contexto = {
        'pontos': pontos_do_aluno,
        'posicao': alunos_com_mais_pontos + 1,
        'primeiros_alunos_do_ranking': primeiros_alunos_do_ranking,
    }
    return render(request, 'base/classificacao.html', contexto)
