DIFICULDADE_CHOICES = [
    ('facil', 'Fácil'),
    ('medio', 'Médio'),
    ('dificil', 'Difícil'),
]

NIVEL_DIFICULDADE = {key: idx + 1 for idx, (key, _) in enumerate(DIFICULDADE_CHOICES)}

PONTUACAO_MAXIMA = 1000
PONTUACAO_MINIMA = 10
