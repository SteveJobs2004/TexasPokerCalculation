import random
from collections import Counter
import time

# --- 参数配置 ---
NUM_SIMULATIONS = 50000   # 模拟局数
NUM_PLAYERS = 5           # 总玩家人数 (包含 P1)

# 输入: 玩家 P1 的手牌 (必须是2张)
# 格式: (点数, 花色) -> 11=J, 12=Q, 13=K, 14=A
# 花色: 'H'=红桃, 'D'=方块, 'C'=梅花, 'S'=黑桃
#P1_HAND = [(8, 'H'), (2, 'S')]  
P1_HAND = [(11, 'H'), (2, 'S')]  
# 输入: 当前已知的公共牌 (可以是 0 到 5 张)
COMMUNITY_CARDS = [(8, 'D'), (11, 'S'), (5, 'D')]  # 黑桃Q, 黑桃J, 方块5 (买皇家同花顺的面)

# --------------------------------

RANKS = list(range(2, 15))
SUITS = ['H', 'D', 'C', 'S']
FULL_DECK = [(rank, suit) for rank in RANKS for suit in SUITS]

def evaluate_7cards(cards):
    """
    评估7张牌，返回可比大小的元组结构和牌型名称
    返回: ((牌型等级, [比大小的牌值...]), "牌型名称")
    牌型等级: 9=皇家同花顺 ... 0=高牌
    """
    ranks = sorted([c[0] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    
    # 1. 统计同花
    is_flush = False
    flush_suit = None
    suit_counts = Counter(suits)
    for s, count in suit_counts.items():
        if count >= 5:
            is_flush = True
            flush_suit = s
            break

    # 辅助函数：找顺子的最大牌
    def get_straight_high(r_list):
        unique_r = sorted(list(set(r_list)), reverse=True)
        if 14 in unique_r:
            unique_r.append(1)  # A 可以算作 1
        for i in range(len(unique_r) - 4):
            if unique_r[i] - unique_r[i+4] == 4:
                return unique_r[i]
        return None

    # 2. 判断同花顺/皇家同花顺
    if is_flush:
        flush_cards = [c[0] for c in cards if c[1] == flush_suit]
        sf_high = get_straight_high(flush_cards)
        if sf_high:
            if sf_high == 14:
                return (9, []), "Royal Flush"
            return (8, [sf_high]), "Straight Flush"

    # 统计各个点数的数量，按数量降序、点数降序排列
    rank_counts = Counter(ranks)
    sorted_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # 3. 四条
    if sorted_counts[0][1] == 4:
        quad_rank = sorted_counts[0][0]
        kicker = max([r for r in ranks if r != quad_rank])
        return (7, [quad_rank, kicker]), "Four of a Kind"

    # 4. 葫芦
    if sorted_counts[0][1] == 3 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        trip_rank = sorted_counts[0][0]
        pair_rank = sorted_counts[1][0]
        return (6, [trip_rank, pair_rank]), "Full House"

    # 5. 同花
    if is_flush:
        flush_cards = sorted([c[0] for c in cards if c[1] == flush_suit], reverse=True)
        return (5, flush_cards[:5]), "Flush"

    # 6. 顺子
    straight_high = get_straight_high(ranks)
    if straight_high:
        return (4, [straight_high]), "Straight"

    # 7. 三条
    if sorted_counts[0][1] == 3:
        trip_rank = sorted_counts[0][0]
        kickers = sorted([r for r in ranks if r != trip_rank], reverse=True)[:2]
        return (3, [trip_rank] + kickers), "Three of a Kind"

    # 8. 两对
    if sorted_counts[0][1] == 2 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        pair1 = sorted_counts[0][0]
        pair2 = sorted_counts[1][0]
        kicker = max([r for r in ranks if r != pair1 and r != pair2])
        return (2, [pair1, pair2, kicker]), "Two Pair"

    # 9. 一对
    if sorted_counts[0][1] == 2:
        pair_rank = sorted_counts[0][0]
        kickers = sorted([r for r in ranks if r != pair_rank], reverse=True)[:3]
        return (1, [pair_rank] + kickers), "One Pair"

    # 10. 高牌
    return (0, ranks[:5]), "High Card"


def run_winrate_simulation():
    print(f"玩家总数: {NUM_PLAYERS}")
    print(f"P1 手牌: {P1_HAND}")
    print(f"已知公共牌: {COMMUNITY_CARDS} (共 {len(COMMUNITY_CARDS)} 张)")
    print(f"开始蒙特卡罗模拟... (局数: {NUM_SIMULATIONS})")
    
    start_time = time.time()
    
    # 组装已知的卡牌
    known_cards = P1_HAND + COMMUNITY_CARDS
    # 从牌堆中剔除已知卡牌
    remaining_deck = [card for card in FULL_DECK if card not in known_cards]
    
    # 需要补齐的公共牌数量
    missing_community_count = 5 - len(COMMUNITY_CARDS)
    # 对手需要的底牌总数量
    opponents_cards_count = (NUM_PLAYERS - 1) * 2
    cards_to_draw_per_sim = missing_community_count + opponents_cards_count
    
    # 胜负平统计
    wins = 0
    ties = 0
    losses = 0
    
    # 失败时对手牌型的统计
    losing_reasons = Counter()

    for _ in range(NUM_SIMULATIONS):
        # 抽出这一局需要的所有未知牌
        drawn_cards = random.sample(remaining_deck, cards_to_draw_per_sim)
        
        # 分配公共牌
        new_community = drawn_cards[:missing_community_count]
        final_community = COMMUNITY_CARDS + new_community
        
        # 分配对手牌
        opponents_pool = drawn_cards[missing_community_count:]
        
        # 计算 P1 的最终牌型得分
        p1_score, p1_name = evaluate_7cards(P1_HAND + final_community)
        
        # 寻找对手的最强牌型
        max_opp_score = (-1, [])
        max_opp_name = ""
        
        for i in range(NUM_PLAYERS - 1):
            opp_hand = opponents_pool[i*2 : i*2+2]
            opp_score, opp_name = evaluate_7cards(opp_hand + final_community)
            
            # 由于元组 (等级, [核心牌]) 支持直接比对大小，直接求最大即可
            if opp_score > max_opp_score:
                max_opp_score = opp_score
                max_opp_name = opp_name
                
        # 胜负平裁定
        if p1_score > max_opp_score:
            wins += 1
        elif p1_score == max_opp_score:
            ties += 1
        else:
            losses += 1
            losing_reasons[max_opp_name] += 1

    end_time = time.time()
    
    # --- 输出分析报告 ---
    print("\n" + "="*45)
    print(f"模拟完成！耗时: {end_time - start_time:.2f} 秒")
    print("="*45)
    print(f"P1 获胜概率 (Win) : {(wins / NUM_SIMULATIONS) * 100:.2f}%")
    print(f"P1 平局概率 (Tie) : {(ties / NUM_SIMULATIONS) * 100:.2f}%")
    print(f"P1 失败概率 (Loss): {(losses / NUM_SIMULATIONS) * 100:.2f}%")
    print("="*45)
    
    if losses > 0:
        print("\n当 P1 失败时，击败 P1 的最强牌型分布：")
        print(f"{'对手牌型 (Hand)':<20} | {'出现次数':<10} | {'占比 (%)'}")
        print("-" * 45)
        # 按出现频率降序输出
        for hand_name, count in losing_reasons.most_common():
            prob = (count / losses) * 100
            print(f"{hand_name:<20} | {count:<10} | {prob:.2f}%")

if __name__ == "__main__":
    run_winrate_simulation()