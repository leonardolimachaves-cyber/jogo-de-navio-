import pygame
import math
import random
import sys

# Inicialização do Pygame e Mixer de Som
pygame.init()
pygame.mixer.init()

# Configurações da Tela
LARGURA, ALTURA = 900, 650
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Batalha Naval Retrô - Desafio Python")
CLOCK = pygame.time.Clock()
FPS = 60

# Fontes Retrô
FONTE_HUD = pygame.font.SysFont("consolas", 20, bold=True)
FONTE_TITULO = pygame.font.SysFont("consolas", 42, bold=True)
FONTE_SUB = pygame.font.SysFont("consolas", 24, bold=True)

# Carregamento de Imagens e Sons
IMG_PLAYER = pygame.image.load("assets/images/player_ship.png").convert_alpha()
IMG_ENEMY = pygame.image.load("assets/images/enemy_ship.png").convert_alpha()
IMG_BOSS = pygame.image.load("assets/images/boss_ship.png").convert_alpha()
IMG_OCEAN = pygame.image.load("assets/images/ocean_tile.png").convert()

SOM_TIRO = pygame.mixer.Sound("assets/sounds/shoot.wav")
SOM_EXPLOSAO = pygame.mixer.Sound("assets/sounds/explosion.wav")
SOM_TIRO.set_volume(0.4)
SOM_EXPLOSAO.set_volume(0.5)


class Particula:
    """Partículas pixeladas para explosões e espuma do mar."""
    def __init__(self, x, y, cor, tamanho, vel_x, vel_y, duracao):
        self.x = x
        self.y = y
        self.cor = cor
        self.tamanho = tamanho
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.duracao = duracao

    def atualizar(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.duracao -= 1

    def desenhar(self, superficie):
        if self.duracao > 0:
            pygame.draw.rect(superficie, self.cor, (int(self.x), int(self.y), self.tamanho, self.tamanho))


class Projetil:
    """Tiros de canhão disparados pelo jogador ou inimigos."""
    def __init__(self, x, y, angulo, velocidade, dono):
        self.x = x
        self.y = y
        self.angulo = angulo
        self.velocidade = velocidade
        self.dono = dono  # 'player' ou 'enemy'
        self.raio = 5 if dono == 'player' else 6
        self.ativo = True

    def atualizar(self):
        rad = math.radians(self.angulo)
        self.x += math.sin(rad) * self.velocidade
        self.y -= math.cos(rad) * self.velocidade

        if self.x < 0 or self.x > LARGURA or self.y < 0 or self.y > ALTURA:
            self.ativo = False

    def desenhar(self, superficie):
        cor = (255, 240, 100) if self.dono == 'player' else (255, 80, 60)
        pygame.draw.rect(superficie, cor, (int(self.x - self.raio), int(self.y - self.raio), self.raio * 2, self.raio * 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)


class Jogador:
    """Navio Destróier controlado pelo jogador com física naval."""
    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA - 100
        self.angulo = 0
        self.velocidade = 0
        self.vel_max = 4.2
        self.hp = 100
        self.hp_max = 100
        self.cooldown = 0
        self.cooldown_max = 22  # Tempo de recarga do canhão

    def atualizar(self, teclas, particulas):
        # Aceleração e Ré
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.velocidade = min(self.vel_max, self.velocidade + 0.12)
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.velocidade = max(-self.vel_max * 0.5, self.velocidade - 0.12)
        else:
            self.velocidade *= 0.96  # Atrito da água

        # Leme (só vira bem se estiver em movimento)
        fator_giro = 2.4 if abs(self.velocidade) > 0.3 else 0.8
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.angulo -= fator_giro
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.angulo += fator_giro

        # Movimento
        rad = math.radians(self.angulo)
        self.x += math.sin(rad) * self.velocidade
        self.y -= math.cos(rad) * self.velocidade

        # Limites da tela
        self.x = max(30, min(LARGURA - 30, self.x))
        self.y = max(30, min(ALTURA - 30, self.y))

        # Rastro de espuma na água
        if abs(self.velocidade) > 0.8 and random.random() < 0.5:
            particulas.append(Particula(
                self.x - math.sin(rad) * 22 + random.randint(-4, 4),
                self.y + math.cos(rad) * 22 + random.randint(-4, 4),
                (200, 230, 255), 4, 0, 0, 18
            ))

        if self.cooldown > 0:
            self.cooldown -= 1

    def atirar(self, projeteis):
        if self.cooldown == 0:
            rad = math.radians(self.angulo)
            ponta_x = self.x + math.sin(rad) * 28
            ponta_y = self.y - math.cos(rad) * 28
            projeteis.append(Projetil(ponta_x, ponta_y, self.angulo, 9.5, 'player'))
            SOM_TIRO.play()
            self.cooldown = self.cooldown_max

    def desenhar(self, superficie):
        img_rot = pygame.transform.rotate(IMG_PLAYER, -self.angulo)
        rect = img_rot.get_rect(center=(int(self.x), int(self.y)))
        superficie.blit(img_rot, rect)

    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 20, 40, 40)


class Inimigo:
    """Fragatas inimigas e o Chefão Encouraçado."""
    def __init__(self, x, y, eh_boss=False, nivel=1):
        self.x = x
        self.y = y
        self.eh_boss = eh_boss
        self.angulo = 180
        self.velocidade = 1.1 if eh_boss else (1.5 + nivel * 0.3)
        self.hp = 350 if eh_boss else (30 + nivel * 10)
        self.hp_max = self.hp
        self.cooldown = random.randint(40, 100)

    def atualizar(self, jogador, projeteis):
        # Calcula ângulo em direção ao jogador
        dx = jogador.x - self.x
        dy = jogador.y - self.y
        angulo_alvo = math.degrees(math.atan2(dx, -dy))
        
        # Gira suavemente em direção ao jogador
        diff = (angulo_alvo - self.angulo + 180) % 360 - 180
        self.angulo += max(-1.5, min(1.5, diff))

        # Avança mantendo distância de combate
        distancia = math.hypot(dx, dy)
        dist_ideal = 220 if self.eh_boss else 180
        rad = math.radians(self.angulo)

        if distancia > dist_ideal:
            self.x += math.sin(rad) * self.velocidade
            self.y -= math.cos(rad) * self.velocidade

        # Disparo
        self.cooldown -= 1
        if self.cooldown <= 0:
            if self.eh_boss:
                # Chefão atira rajada tripla em leque!
                for desvio in [-18, 0, 18]:
                    projeteis.append(Projetil(self.x, self.y, self.angulo + desvio, 6.5, 'enemy'))
                self.cooldown = 75
            else:
                projeteis.append(Projetil(self.x, self.y, self.angulo, 6.0, 'enemy'))
                self.cooldown = random.randint(90, 140)
            SOM_TIRO.play()

    def desenhar(self, superficie):
        img_base = IMG_BOSS if self.eh_boss else IMG_ENEMY
        img_rot = pygame.transform.rotate(img_base, -self.angulo)
        rect = img_rot.get_rect(center=(int(self.x), int(self.y)))
        superficie.blit(img_rot, rect)

        # Barra de vida individual para inimigos comuns
        if not self.eh_boss:
            largura_barra = 36
            hp_atual = int((self.hp / self.hp_max) * largura_barra)
            pygame.draw.rect(superficie, (150, 0, 0), (self.x - 18, self.y - 32, largura_barra, 5))
            pygame.draw.rect(superficie, (0, 220, 80), (self.x - 18, self.y - 32, hp_atual, 5))

    def get_rect(self):
        tam = 48 if self.eh_boss else 22
        return pygame.Rect(self.x - tam, self.y - tam, tam * 2, tam * 2)


def criar_explosao(x, y, particulas, quantidade=18):
    SOM_EXPLOSAO.play()
    cores = [(255, 220, 50), (255, 120, 20), (220, 40, 40), (90, 90, 90)]
    for _ in range(quantidade):
        particulas.append(Particula(
            x, y,
            random.choice(cores),
            random.choice([4, 6, 8]),
            random.uniform(-3.5, 3.5),
            random.uniform(-3.5, 3.5),
            random.randint(18, 35)
        ))


def gerar_fase(fase):
    inimigos = []
    if fase == 1:
        for i in range(3):
            inimigos.append(Inimigo(200 + i * 250, 90, eh_boss=False, nivel=1))
    elif fase == 2:
        for i in range(5):
            inimigos.append(Inimigo(120 + i * 160, 80, eh_boss=False, nivel=2))
    elif fase == 3:
        # Fase Final: Chefão + 2 Escoltas
        inimigos.append(Inimigo(LARGURA // 2, 110, eh_boss=True, nivel=3))
        inimigos.append(Inimigo(180, 90, eh_boss=False, nivel=2))
        inimigos.append(Inimigo(LARGURA - 180, 90, eh_boss=False, nivel=2))
    return inimigos


def desenhar_oceano(superficie, offset_y):
    for x in range(0, LARGURA, 64):
        for y in range(-64, ALTURA + 64, 64):
            superficie.blit(IMG_OCEAN, (x, y + offset_y))


def main():
    estado = "MENU"  # MENU, JOGANDO, VITORIA, GAMEOVER
    jogador = Jogador()
    fase = 1
    pontos = 0
    inimigos = []
    projeteis = []
    particulas = []
    oceano_y = 0

    while True:
        CLOCK.tick(FPS)
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if estado == "MENU" and evento.key == pygame.K_RETURN:
                    jogador = Jogador()
                    fase = 1
                    pontos = 0
                    inimigos = gerar_fase(fase)
                    projeteis.clear()
                    particulas.clear()
                    estado = "JOGANDO"

                elif estado == "JOGANDO" and evento.key == pygame.K_SPACE:
                    jogador.atirar(projeteis)

                elif estado in ("VITORIA", "GAMEOVER") and evento.key == pygame.K_r:
                    estado = "MENU"

        # Animação contínua das ondas
        oceano_y = (oceano_y + 0.5) % 64
        desenhar_oceano(TELA, int(oceano_y))

        if estado == "MENU":
            titulo = FONTE_TITULO.render("BATALHA NAVAL RETRÔ", True, (255, 220, 60))
            sub1 = FONTE_SUB.render("W/A/S/D ou Setas: Navegar | ESPAÇO: Atirar", True, (255, 255, 255))
            sub2 = FONTE_SUB.render("Pressione ENTER para Iniciar a Missão", True, (100, 255, 150))
            TELA.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 60)))
            TELA.blit(sub1, sub1.get_rect(center=(LARGURA // 2, ALTURA // 2 + 10)))
            TELA.blit(sub2, sub2.get_rect(center=(LARGURA // 2, ALTURA // 2 + 60)))

        elif estado == "JOGANDO":
            jogador.atualizar(teclas, particulas)

            # Atualiza projéteis e colisões
            for p in projeteis[:]:
                p.atualizar()
                if not p.ativo:
                    projeteis.remove(p)
                    continue

                if p.dono == 'player':
                    for inimigo in inimigos[:]:
                        if p.get_rect().colliderect(inimigo.get_rect()):
                            inimigo.hp -= 15
                            p.ativo = False
                            criar_explosao(p.x, p.y, particulas, quantidade=6)
                            if inimigo.hp <= 0:
                                criar_explosao(inimigo.x, inimigo.y, particulas, quantidade=35 if inimigo.eh_boss else 20)
                                pontos += 1000 if inimigo.eh_boss else 200
                                inimigos.remove(inimigo)
                            break
                elif p.dono == 'enemy':
                    if p.get_rect().colliderect(jogador.get_rect()):
                        jogador.hp -= 12
                        p.ativo = False
                        criar_explosao(p.x, p.y, particulas, quantidade=8)
                        if jogador.hp <= 0:
                            criar_explosao(jogador.x, jogador.y, particulas, quantidade=40)
                            estado = "GAMEOVER"

            # Atualiza inimigos
            for inimigo in inimigos:
                inimigo.atualizar(jogador, projeteis)

            # Avança de fase
            if len(inimigos) == 0:
                if fase < 3:
                    fase += 1
                    jogador.hp = min(jogador.hp_max, jogador.hp + 30)  # Repara parte do casco
                    inimigos = gerar_fase(fase)
                else:
                    estado = "VITORIA"

            # Desenha tudo
            for part in particulas[:]:
                part.atualizar()
                part.desenhar(TELA)
                if part.duracao <= 0:
                    particulas.remove(part)

            for inimigo in inimigos:
                inimigo.desenhar(TELA)

            jogador.desenhar(TELA)

            for p in projeteis:
                p.desenhar(TELA)

            # HUD Superior
            pygame.draw.rect(TELA, (10, 25, 45), (0, 0, LARGURA, 42))
            txt_hp = FONTE_HUD.render(f"BLINDAGEM: {max(0, jogador.hp)}%", True, (100, 255, 120) if jogador.hp > 35 else (255, 80, 80))
            txt_fase = FONTE_HUD.render(f"FASE: {fase}/3" + (" (CHEFÃO!)" if fase == 3 else ""), True, (255, 220, 60))
            txt_pts = FONTE_HUD.render(f"PONTOS: {pontos}", True, (255, 255, 255))

            TELA.blit(txt_hp, (20, 10))
            TELA.blit(txt_fase, (340, 10))
            TELA.blit(txt_pts, (700, 10))

            # Barra de vida gigante do Chef