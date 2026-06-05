import random
from collections import Counter
import time

# --- 参数配置 ---
NUM_SIMULATIONS = 1000000  # 模拟的总局数
NUM_PLAYERS = 7           # 玩家人数 

# 定义扑克的牌面和花色
# 11=J, 12=Q, 13=K, 14=A
RANKS = list(range(2, 15))
SUITS = ['H', 'D', 'C', 'S']  # 红桃(Hearts), 方块(Diamonds), 梅花(Clubs), 黑桃(Spades)

# 生成一副完整的扑克牌 (52张)
DECK = [(rank, suit) for rank in RANKS for suit in SUITS]

def evaluate_hand(cards):
    """
    评估7张牌中的最大牌型
    cards: 包含7个元组的列表，例如 [(14, 'H'), (2, 'D'), ...]
    返回: 牌型的字符串名称
    """
    ranks = [card[0] for card in cards]
    suits = [card[1] for card in cards]
    
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    
    # 1. 判断是否含有同花 (Flush)
    is_flush = False
    flush_suit = None
    for suit, count in suit_counts.items():
        if count >= 5:
            is_flush = True
            flush_suit = suit
            break
            
    # 辅助函数：判断一组去重的牌点中是否包含顺子
    def check_straight(unique_ranks):
        # A 可以作为 1 (A-2-3-4-5)
        if 14 in unique_ranks:
            unique_ranks.add(1)
        
        sorted_ranks = sorted(list(unique_ranks), reverse=True)
        # 遍历查找是否有连续的5张牌
        # 因为已经去重并降序排列，如果索引 i 和 i+4 的牌差值为 4，则必为顺子
        for i in range(len(sorted_ranks) - 4):
            if sorted_ranks[i] - sorted_ranks[i+4] == 4:
                return True, sorted_ranks[i] # 返回 True 和 顺子的最大牌
        return False, 0

    # 2. 判断是否含有顺子 (Straight)
    is_straight, _ = check_straight(set(ranks))
    
    # 3. 判断同花顺 (Straight Flush) / 皇家同花顺 (Royal Flush)
    is_straight_flush = False
    if is_flush:
        # 提取出所有组成同花的牌
        flush_cards = [card[0] for card in cards if card[1] == flush_suit]
        is_straight_flush, sf_high_rank = check_straight(set(flush_cards))
        
    # 按照相同点数的数量降序排列 (例如四条会是 [4, 1, 1, 1], 葫芦会是 [3, 2, 1, 1] 等)
    counts = sorted(rank_counts.values(), reverse=True)

    # 4. 判定最终牌型 (从大到小)
    if is_straight_flush:
        if sf_high_rank == 14:
            return "Royal Flush"     # 皇家同花顺
        return "Straight Flush"      # 同花顺
    elif counts[0] == 4:
        return "Four of a Kind"      # 四条 (金刚)
    elif counts[0] == 3 and counts[1] >= 2:
        return "Full House"          # 葫芦
    elif is_flush:
        return "Flush"               # 同花
    elif is_straight:
        return "Straight"            # 顺子
    elif counts[0] == 3:
        return "Three of a Kind"     # 三条
    elif counts[0] == 2 and counts[1] >= 2:
        return "Two Pair"            # 两对
    elif counts[0] == 2:
        return "One Pair"            # 一对
    else:
        return "High Card"           # 高牌

def run_simulation(num_simulations, num_players):
    print(f"开始模拟... 总局数: {num_simulations}, 玩家数: {num_players}")
    start_time = time.time()
    
    # 统计所有玩家出现的牌型总数
    hand_results = Counter()
    
    for _ in range(num_simulations):
        # 每一局需要抽取的卡牌总数: 5张公共牌 + 每位玩家2张底牌
        cards_needed = 5 + num_players * 2
        # 使用 random.sample 可以不破坏原数组的情况下直接抽出不重复的牌，效率极高
        drawn_cards = random.sample(DECK, cards_needed)
        
        community_cards = drawn_cards[0:5]
        
        for p in range(num_players):
            # 获取当前玩家的2张底牌
            player_cards = drawn_cards[5 + p*2 : 5 + p*2 + 2]
            # 玩家的7张可用牌
            total_cards = community_cards + player_cards
            
            # 评估牌型并记录
            best_hand = evaluate_hand(total_cards)
            hand_results[best_hand] += 1
            
    end_time = time.time()
    
    # 计算并输出概率
    total_hands_evaluated = num_simulations * num_players
    print(f"\n模拟完成！耗时: {end_time - start_time:.2f} 秒")
    print("-" * 40)
    print(f"{'牌型 (Hand)':<20} | {'出现次数':<10} | {'概率 (%)'}")
    print("-" * 40)
    
    # 按照德州扑克牌型大小顺序列出
    hand_order = [
        "Royal Flush", "Straight Flush", "Four of a Kind", "Full House", 
        "Flush", "Straight", "Three of a Kind", "Two Pair", "One Pair", "High Card"
    ]
    
    for hand in hand_order:
        count = hand_results[hand]
        probability = (count / total_hands_evaluated) * 100
        print(f"{hand:<20} | {count:<10} | {probability:.4f}%")

if __name__ == "__main__":
    run_simulation(NUM_SIMULATIONS, NUM_PLAYERS)