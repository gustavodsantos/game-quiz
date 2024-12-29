DIFICULDADE_CHOICES = [
    ('facil', 'Fácil'),
    ('medio', 'Médio'),
    ('dificil', 'Difícil'),
    ('especialista', 'Especialista'),
]

NIVEL_DIFICULDADE = {key: idx + 1 for idx, (key, _) in enumerate(DIFICULDADE_CHOICES)}

PONTUACAO_MAXIMA = 100
PONTUACAO_MINIMA = 0
