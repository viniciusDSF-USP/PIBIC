from manim import *
import numpy as np

# Sinais usados nas três cenas (N = 4, M = 3  ->  N + M - 1 = 6)
F = [1, 2, 3, 1]
G = [1, 2, 1]

CELL = 0.8      # lado de cada caixinha
STEP = 0.9      # distância entre colunas
C_F, C_G, C_Y = BLUE, GREEN, YELLOW


# Funções numéricas (os valores mostrados nas animações vêm daqui)
def pad(v, L):
    return list(v) + [0] * (L - len(v))

def conv_linear(f, g):
    return [int(x) for x in np.convolve(f, g)]

def conv_circular(f, g, L):
    f, g = pad(f, L), pad(g, L)
    return [sum(f[m] * g[(n - m) % L] for m in range(L)) for n in range(L)]


# Auxiliares de desenho
def cell(value, color=WHITE, fill=0.25):
    sq = Square(CELL, stroke_color=color, stroke_width=3,
                fill_color=color, fill_opacity=fill)
    txt = MathTex(str(value)).scale(0.8).move_to(sq)
    return VGroup(sq, txt)

def make_row(values, color, first_col, y, x_of, zero_color=GREY):
    """Linha de caixinhas; o elemento i fica na coluna first_col + i."""
    row = VGroup()
    for i, v in enumerate(values):
        c = zero_color if (v == 0 and zero_color is not None) else color
        row.add(cell(v, c).move_to([x_of(first_col + i), y, 0]))
    return row

def index_labels(cols, y, x_of, color=GREY_B):
    return VGroup(*[
        MathTex(str(c)).scale(0.5).set_color(color).move_to([x_of(c), y, 0])
        for c in cols
    ])

def row_label(tex, y, x=-5.4, color=WHITE):
    return MathTex(tex).scale(0.8).set_color(color).move_to([x, y, 0])


# 1) Convolução linear: (f*g)[n] = sum_m f[m] g[n-m]
class ConvolucaoLinear(Scene):
    def construct(self):
        N, M = len(F), len(G)
        K = N + M - 1
        x_of = lambda c: (c - (N - 1) / 2) * STEP
        y_f, y_g, y_out = 0.7, -0.6, -2.0
        y_sum = -3.4

        titulo = Text("Convolução linear", font_size=36).to_edge(UP)
        formula = MathTex(r"(f*g)[n]=\sum_{m}f[m]\,g[n-m]").next_to(titulo, DOWN, buff=0.25)
        self.play(Write(titulo), Write(formula))

        # f fixo (colunas 0..N-1)
        f_row = make_row(F, C_F, 0, y_f, x_of, zero_color=None)
        f_idx = index_labels(range(N), y_f + 0.65, x_of)
        self.play(FadeIn(f_row), FadeIn(f_idx), FadeIn(row_label("f[m]", y_f, color=C_F)))

        # g espelhado: a caixinha em m = n - j guarda g[j]  ->  valores em ordem inversa
        g_flip = make_row(G[::-1], C_G, -(M - 1), y_g, x_of, zero_color=None)
        g_lab = row_label("g[n-m]", y_g, color=C_G)
        self.play(FadeIn(g_flip), FadeIn(g_lab))

        self.play(FadeIn(row_label("y[n]", y_out, color=C_Y)),
                  FadeIn(index_labels(range(K), y_out - 0.65, x_of)))

        soma = None
        for n in range(K):
            if n > 0:
                self.play(g_flip.animate.shift(RIGHT * STEP), run_time=0.6)

            ms = [m for m in range(N) if 0 <= n - m < M]       # onde há sobreposição
            valor = sum(F[m] * G[n - m] for m in ms)
            termos = "+".join(f"{F[m]}\\cdot{G[n - m]}" for m in ms)
            nova_soma = MathTex(f"y[{n}]={termos}={valor}").move_to([0, y_sum, 0])
            destaques = VGroup(*[SurroundingRectangle(f_row[m], color=C_Y, buff=0.05) for m in ms])

            anim_soma = FadeIn(nova_soma) if soma is None else ReplacementTransform(soma, nova_soma)
            self.play(Create(destaques), anim_soma, run_time=0.6)
            saida = cell(valor, C_Y).move_to([x_of(n), y_out, 0])
            self.play(FadeIn(saida, shift=DOWN * 0.3), run_time=0.5)
            self.play(FadeOut(destaques), run_time=0.25)
            soma = nova_soma

        self.play(FadeOut(soma))
        fim = MathTex(rf"\text{{comprimento}}=N+M-1={N}+{M}-1={K}").move_to([0, y_sum, 0])
        self.play(Write(fim))
        self.wait(2)


# 2) Convolução circular: (f ⊛ g)[n] = sum_m f[m] g[(n-m) mod N]
class ConvolucaoCircular(Scene):
    def construct(self):
        N = len(F)
        Gp = pad(G, N)                          # g completado com zero até comprimento N
        x_of = lambda c: (c - (N - 1) / 2) * STEP
        y_f, y_g, y_out = 1.2, -0.1, -1.7

        titulo = Text("Convolução circular", font_size=20).to_edge(UP)
        formula = MathTex(r"(f\circledast g)[n]=\sum_{m=0}^{N-1}f[m]\,g[(n-m)\bmod N]").scale(0.6).next_to(titulo, DOWN, buff=0.25)
        self.play(Write(titulo), Write(formula))

        f_row = make_row(F, C_F, 0, y_f, x_of, zero_color=None)
        self.play(FadeIn(f_row), FadeIn(index_labels(range(N), y_f + 0.65, x_of)),
                  FadeIn(row_label("f[m]", y_f, color=C_F)))
        self.play(FadeIn(row_label("g[(n-m)\\bmod N]", y_g, x=-5.0, color=C_G)),
                  FadeIn(row_label("y[n]", y_out, color=C_Y)),
                  FadeIn(index_labels(range(N), y_out - 0.65, x_of)))

        legenda = Text("laranja: n−m < 0, o índice dá a volta (mod N)", font_size=22,
                       color=ORANGE).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(legenda))

        g_row, idx_row, soma = None, None, None
        for n in range(N):
            idx = [(n - m) % N for m in range(N)]
            vals = [Gp[i] for i in idx]
            nova_g = VGroup(*[
                cell(vals[m], ORANGE if n - m < 0 else C_G).move_to([x_of(m), y_g, 0])
                for m in range(N)
            ])
            novo_idx = VGroup(*[
                MathTex(str(idx[m])).scale(0.5)
                .set_color(ORANGE if n - m < 0 else GREY_B)
                .move_to([x_of(m), y_g - 0.65, 0])
                for m in range(N)
            ])
            valor = sum(F[m] * vals[m] for m in range(N))
            termos = "+".join(f"{F[m]}\\cdot{vals[m]}" for m in range(N))
            nova_soma = MathTex(f"y[{n}]={termos}={valor}").move_to([0, -3.0, 0])

            if g_row is None:
                self.play(FadeIn(nova_g), FadeIn(novo_idx), FadeIn(nova_soma))
            else:
                self.play(ReplacementTransform(g_row, nova_g),
                          ReplacementTransform(idx_row, novo_idx),
                          ReplacementTransform(soma, nova_soma), run_time=0.8)
            g_row, idx_row, soma = nova_g, novo_idx, nova_soma

            self.play(FadeIn(cell(valor, C_Y).move_to([x_of(n), y_out, 0]), shift=DOWN * 0.3),
                      run_time=0.5)
            self.wait(0.4)

        self.play(FadeOut(soma), FadeOut(legenda))
        fim = Text("saída com o mesmo comprimento N das entradas", font_size=26).move_to([0, -3.0, 0])
        self.play(Write(fim))
        self.wait(2)


# 3) Zero padding: a circular de L >= N+M-1 pontos coincide com a linear
class ZeroPadding(Scene):
    def construct(self):
        N, M = len(F), len(G)
        K = N + M - 1
        x_of = lambda c: (c - (K - 1) / 2) * STEP

        titulo = Text("Zero padding: linear via circular", font_size=36).to_edge(UP)
        self.play(Write(titulo))

        # convolução linear (referência)
        lin = conv_linear(F, G)
        y_lin = 1.7
        lin_row = make_row(lin, C_Y, 0, y_lin, x_of, zero_color=None)
        lin_lab = Text("linear", font_size=26, color=C_Y).move_to([-5.4, y_lin, 0])
        self.play(FadeIn(lin_row), FadeIn(lin_lab),
                  FadeIn(index_labels(range(K), y_lin + 0.65, x_of)))

        # circular com L = N < N+M-1: aliasing
        L1 = N
        circ1 = conv_circular(F, G, L1)
        y_c1 = 0.3
        c1_row = make_row(circ1, RED, 0, y_c1, x_of, zero_color=None)
        c1_lab = Text(f"circular, L={L1}", font_size=26, color=RED).move_to([-5.2, y_c1, 0])
        setas = VGroup(*[
            Arrow(lin_row[n].get_bottom(), c1_row[n - L1].get_top(), buff=0.1,
                  color=RED, stroke_width=3, max_tip_length_to_length_ratio=0.12)
            for n in range(L1, K)
        ])
        self.play(FadeIn(c1_lab), FadeIn(c1_row))
        self.play(*[GrowArrow(a) for a in setas])
        explic = MathTex(
            "".join(rf"y[{n - L1}]\!:\ {lin[n - L1]}+{lin[n]}={circ1[n - L1]}\qquad " for n in range(L1, K))
        ).scale(0.8).move_to([0, -0.9, 0])
        aviso = Text(f"L = {L1} < N+M−1 = {K}: a cauda volta e soma no início (aliasing)",
                     font_size=24, color=RED).move_to([0, -1.6, 0])
        self.play(Write(explic), FadeIn(aviso))
        self.wait(1.5)

        # zero padding até L = N+M-1
        self.play(FadeOut(setas), FadeOut(c1_row), FadeOut(c1_lab), FadeOut(explic), FadeOut(aviso))
        L2 = K
        circ2 = conv_circular(F, G, L2)
        y_fp, y_gp, y_c2 = 0.5, -0.65, -1.9
        fp = make_row(pad(F, L2), C_F, 0, y_fp, x_of)
        gp = make_row(pad(G, L2), C_G, 0, y_gp, x_of)
        self.play(FadeIn(fp), FadeIn(gp),
                  FadeIn(Text(f"f com zeros (L={L2})", font_size=22, color=C_F).move_to([-5.2, y_fp, 0])),
                  FadeIn(Text(f"g com zeros (L={L2})", font_size=22, color=C_G).move_to([-5.2, y_gp, 0])))

        c2_row = make_row(circ2, GREEN, 0, y_c2, x_of, zero_color=None)
        c2_lab = Text(f"circular, L={L2}", font_size=26, color=GREEN).move_to([-5.2, y_c2, 0])
        self.play(FadeIn(c2_lab), FadeIn(c2_row))

        igual = VGroup(SurroundingRectangle(lin_row, color=GREEN, buff=0.1),
                       SurroundingRectangle(c2_row, color=GREEN, buff=0.1))
        ok = Text(f"L = N+M−1 = {K}: circular = linear", font_size=26, color=GREEN).move_to([0, -2.9, 0])
        self.play(Create(igual), Write(ok))

        formula = MathTex(
            r"f*g=\mathrm{IFFT}\big(\mathrm{FFT}_L(f)\cdot\mathrm{FFT}_L(g)\big),\quad L\ge N+M-1"
        ).scale(0.85).move_to([0, -3.5, 0])
        self.play(Write(formula))
        self.wait(2)