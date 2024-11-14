from django.forms import ModelForm

from mysite.base.models import Aluno


class AlunoForm(ModelForm):
    class Meta:
        model = Aluno
        fields = ['email', 'nome']
