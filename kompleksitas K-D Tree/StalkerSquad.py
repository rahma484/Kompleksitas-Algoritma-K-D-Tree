import pygame
import random
import time

pygame.init()
W, H = 800, 500
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Impact", 24)

class KDNode:
    def __init__(self, point, axis, left=None, right=None):
        self.point = point  
        self.axis = axis   
        self.left = left
        self.right = right

def build_kdtree(points, depth=0):
    if not points:
        return None
    
    axis = depth % 2
    
    points.sort(key=lambda p: p[axis])
    mid = len(points) // 2
    
    return KDNode(
        point=points[mid],
        axis=axis,
        left=build_kdtree(points[:mid], depth + 1),
        right=build_kdtree(points[mid+1:], depth + 1)
    )

def get_nearest(node, target, best=None):
    if node is None:
        return best

    dist_sq = (node.point[0] - target[0])**2 + (node.point[1] - target[1])**2
    
    
    if best is None or dist_sq < best[1]:
        best = (node.point, dist_sq)

    diff = target[node.axis] - node.point[node.axis]
    near_branch = node.left if diff < 0 else node.right
    far_branch = node.right if diff < 0 else node.left

    best = get_nearest(near_branch, target, best)

    if diff**2 < best[1]:
        best = get_nearest(far_branch, target, best)

    return best

def reset_game():
    player_pos = [W // 2, H // 2]

    enemies_list = [[random.randint(50, W - 50), random.randint(50, H - 50)] for _ in range(10)]
    start_time = time.time()
    is_alive = True
    score = 0
    return player_pos, enemies_list, start_time, is_alive, score


player, enemies, start, alive, score = reset_game()
running = True

while running:
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            player, enemies, start, alive, score = reset_game()

    if alive:
        
        mx, my = pygame.mouse.get_pos()
        player = [mx, my]
        
        elapsed = time.time() - start
        can_move = elapsed > 3  
        if can_move:
            score += 1

            if enemies:
                
                tree_root = build_kdtree(enemies.copy())
                
                nearest_result = get_nearest(tree_root, player)
                
                if nearest_result:
                    nearest_point = nearest_result[0]
                    
                    for enemy in enemies:
                        if enemy is nearest_point: 
                            enemy[0] += (player[0] - enemy[0]) * 0.03
                            enemy[1] += (player[1] - enemy[1]) * 0.03
                            
                            dist_sq_chk = (player[0] - enemy[0])**2 + (player[1] - enemy[1])**2
                            if dist_sq_chk < 400: 
                                alive = False
                            break 

    screen.fill((20, 20, 40)) 

    nearest_ref = None
    if alive and enemies:
      
        temp_tree = build_kdtree(enemies.copy())
        res = get_nearest(temp_tree, player)
        if res: nearest_ref = res[0]

    for e in enemies:
       
        is_chaser = (e is nearest_ref) if nearest_ref else False
        color = (255, 50, 50) if is_chaser else (100, 100, 200)
        radius = 10 if is_chaser else 8
        pygame.draw.circle(screen, color, (int(e[0]), int(e[1])), radius)

    pygame.draw.circle(screen, (50, 255, 100), (int(player[0]), int(player[1])), 12)

    if not alive:
        text = font.render("GAME OVER - Press 'R' to Restart", True, (255, 50, 50))
        screen.blit(text, (W//2 - 150, H//2))
    elif elapsed < 3:
        text = font.render(f"Start in: {3 - int(elapsed)}", True, (255, 200, 50))
        screen.blit(text, (W//2 - 40, H//2 - 50))
    
    score_text = font.render(f"Score: {score}", True, (200, 200, 200))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()