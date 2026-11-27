import os
import wave
import math
import struct
import random
import pygame

# Inicializa o Pygame apenas para gerar as imagens
pygame.init()

# Garante que as pastas existam
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

def criar_sprite_pixelado(matriz, cores, escala=4):
    """Converte uma matriz de texto em uma imagem Pixel Art ampliada."""
    altura = len(matriz)
    largura = len(matriz[0])
    superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
    
    for y, linha in enumerate(matriz):
        for x, char in enumerate(linha):
            if char in cores:
                superficie.set_at((x, y), cores[char])
                
    return pygame.transform.scale(superficie, (largura * escala, altura * escala))

# --- 1. GERANDO AS IMAGENS EM PIXEL ART ---

# Navio do Jogador (Destróier Retrô)
matriz_jogador = [
    "....CC....",
    "...CCCC...",
    "...CWWC...",
    "..CCCCCC..",
    "..CGGGGCC.",
    ".CCCCCCCC.",
    ".CCRRRRCC.",
    ".CCCCCCCC.",
    ".CGGGGGCC.",
    "..CCCCCC..",
    "...CCCC..."
]
cores_jogador = {
    'C': (140, 155, 170), # Cinza naval
    'W': (230, 240, 255), # Proa clara
    'G': (70, 80, 90),    # Torres de canhão
    'R': (220, 60, 60)    # Detalhe vermelho
}
img_jogador = criar_sprite_pixelado(matriz_jogador, cores_jogador, escala=5)
pygame.image.save(img_jogador, "assets/images/player_ship.png")

# Navio Inimigo Comum (Fragata)
matriz_inimigo = [
    "...EEEE...",
    "..EEEEEE..",
    ".EEGGGGEE.",
    ".EEEEEEEE.",
    "..EEOOEE..",
    "..EEEEEE..",
    "...EEEE...",
    "....EE...."
]
cores_inimigo = {
    'E': (90, 45, 45),    # Casco escuro
    'G': (40, 40, 40),    # Canhões
    'O': (255, 140, 0)    # Detalhe laranja
}
img_inimigo = criar_sprite_pixelado(matriz_inimigo, cores_inimigo, escala=5)
pygame.image.save(img_inimigo, "assets/images/enemy_ship.png")

# Chefão (Encouraçado Gigante)
matriz_boss = [
    "....BBBBBBBB....",
    "..BBBBBBBBBBBB..",
    ".BBBBGGGGGBBBBB.",
    "BBBBBBBBBBBBBBBB",
    "BBBBRRRRRRRRBBBB",
    "BBBBGGGGGGGGBBBB",
    "BBBBBBBBBBBBBBBB",
    ".BBBBGGGGGBBBBB.",
    "..BBBBBBBBBBBB..",
    "....BBBBBBBB...."
]
cores_boss = {
    'B': (55, 60, 75),    # Blindagem pesada
    'G': (30, 30, 35),    # Mega canhões
    'R': (200, 30, 30)    # Núcleo/Ponte de comando
}
img_boss = criar_sprite_pixelado(matriz_boss, cores_boss, escala=7)
pygame.image.save(img_boss, "assets/images/boss_ship.png")

# Textura do Oceano Retrô (Tile 64x64)
mar = pygame.Surface((64, 64))
mar.fill((15, 65, 125))
for _ in range(25):
    px = random.randrange(0, 60, 4)
    py = random.randrange(0, 60, 4)
    pygame.draw.rect(mar, (25, 85, 155), (px, py, 8, 4))
pygame.image.save(mar, "assets/images/ocean_tile.png")

# --- 2. GERANDO OS SONS 8-BIT (.WAV) ---

def salvar_som(nome_arquivo, amostras, taxa=22050):
    with wave.open(nome_arquivo, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(taxa)
        for amostra in amostras:
            valor = max(-32767, min(32767, int(amostra * 32767)))
            wav_file.writeframes(struct.pack('<h', valor))

# Som de Tiro de Canhão (Onda quadrada descendente)
amostras_tiro = []
for i in range(int(22050 * 0.18)):
    t = i / 22050
    freq = 320 - (t * 1400)
    onda = 0.4 if math.sin(2 * math.pi * freq * t) > 0 else -0.4
    amostras_tiro.append(onda * (1 - t / 0.18))
salvar_som("assets/sounds/shoot.wav", amostras_tiro)

# Som de Explosão (Ruído branco com decaimento)
amostras_explosao = []
for i in range(int(22050 * 0.45)):
    t = i / 22050
    ruido = random.uniform(-0.6, 0.6)
    amostras_explosao.append(ruido * ((1 - t / 0.45) ** 1.5))
salvar_som("assets/sounds/explosion.wav", amostras_explosao)

print("Assets Pixel Art e Sons 8-bit gerados com sucesso nas pastas 'assets/'!")