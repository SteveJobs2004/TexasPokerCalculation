import streamlit as st
import random
import time
from collections import Counter

# ==========================================
# 1. 核心数据与扑克逻辑定义
# ==========================================
RANKS = list(range(2, 15))
SUITS = ['S', 'H', 'D', 'C']  # 黑桃, 红桃, 方块, 梅花
SUIT_SYMBOLS = {'S': '♠️', 'H': '♥️', 'D': '♦️', 'C': '♣️'}
RANK_SYMBOLS = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}

# 生成格式化的卡牌字典，例如: {(14, 'S'): '♠️ A', (10, 'H'): '♥️ 10'}
FULL_DECK = [(rank, suit) for rank in RANKS for suit in SUITS]
CARD_NAMES = {
    card: f"{SUIT_SYMBOLS[card[1]]} {RANK_SYMBOLS.get(card[0], str(card[0]))}"
    for card in FULL_DECK
}

def evaluate_7cards(cards):
    """评估7张牌，返回可比大小的元组结构和牌型名称"""
    ranks = sorted([c[0] for c in cards], reverse=True)
    suits = [c[1] for c in cards]
    
    is_flush = False
    flush_suit = None
    suit_counts = Counter(suits)
    for s, count in suit_counts.items():
        if count >= 5:
            is_flush = True
            flush_suit = s
            break

    def get_straight_high(r_list):
        unique_r = sorted(list(set(r_list)), reverse=True)
        if 14 in unique_r:
            unique_r.append(1)
        for i in range(len(unique_r) - 4):
            if unique_r[i] - unique_r[i+4] == 4:
                return unique_r[i]
        return None

    if is_flush:
        flush_cards = [c[0] for c in cards if c[1] == flush_suit]
        sf_high = get_straight_high(flush_cards)
        if sf_high:
            if sf_high == 14: return (9, []), "皇家同花顺 (Royal Flush)"
            return (8, [sf_high]), "同花顺 (Straight Flush)"

    rank_counts = Counter(ranks)
    sorted_counts = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

    if sorted_counts[0][1] == 4:
        return (7, [sorted_counts[0][0], max([r for r in ranks if r != sorted_counts[0][0]])]), "四条 (Four of a Kind)"

    if sorted_counts[0][1] == 3 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        return (6, [sorted_counts[0][0], sorted_counts[1][0]]), "葫芦 (Full House)"

    if is_flush:
        flush_cards = sorted([c[0] for c in cards if c[1] == flush_suit], reverse=True)
        return (5, flush_cards[:5]), "同花 (Flush)"

    straight_high = get_straight_high(ranks)
    if straight_high:
        return (4, [straight_high]), "顺子 (Straight)"

    if sorted_counts[0][1] == 3:
        kickers = sorted([r for r in ranks if r != sorted_counts[0][0]], reverse=True)[:2]
        return (3, [sorted_counts[0][0]] + kickers), "三条 (Three of a Kind)"

    if sorted_counts[0][1] == 2 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        kicker = max([r for r in ranks if r != sorted_counts[0][0] and r != sorted_counts[1][0]])
        return (2, [sorted_counts[0][0], sorted_counts[1][0], kicker]), "两对 (Two Pair)"

    if sorted_counts[0][1] == 2:
        kickers = sorted([r for r in ranks if r != sorted_counts[0][0]], reverse=True)[:3]
        return (1, [sorted_counts[0][0]] + kickers), "一对 (One Pair)"

    return (0, ranks[:5]), "高牌 (High Card)"

# ==========================================
# 2. 页面配置与 UI 渲染
# ==========================================
st.set_page_config(page_title="德州扑克概率计算器", page_icon="🃏", layout="wide")
st.title("🃏 德州扑克动态胜率计算器 ")
st.markdown("---")

# 侧边栏：参数设置
with st.sidebar:
    st.header("⚙️ 模拟参数设置")
    num_players = st.slider("玩家总人数", min_value=2, max_value=9, value=5)
    num_simulations = st.select_slider("蒙特卡罗模拟局数", options=[20000, 50000, 100000, 500000, 100000], value=20000)
    st.info("💡 提示：模拟局数越大，结果越精确，但计算等待时间越长。网页端建议使用 20,000 次。")

# 主界面：选牌区域
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 选择你的手牌 (必须选 2 张)")
    # 使用 multiselect 实现点击选择标签式交互，自动防止重复
    p1_selection = st.multiselect(
        "点击下拉框选择扑克牌：",
        options=list(CARD_NAMES.keys()),
        format_func=lambda x: CARD_NAMES[x],
        max_selections=2,
        key="p1_cards"
    )

with col2:
    st.subheader("🌐 选择公共牌 (0 到 5 张)")
    # 动态过滤，已选为手牌的牌不再出现在公共牌选项中，实现物理上不重牌
    available_for_community = [c for c in FULL_DECK if c not in p1_selection]
    community_selection = st.multiselect(
        "点击下拉框选择公共牌：",
        options=available_for_community,
        format_func=lambda x: CARD_NAMES[x],
        max_selections=5,
        key="community_cards"
    )

# 展示已选卡牌的视觉反馈
st.markdown("### 🎲 当前牌面")
p1_str = "  ".join([CARD_NAMES[c] for c in p1_selection]) if p1_selection else "尚未选择"
comm_str = "  ".join([CARD_NAMES[c] for c in community_selection]) if community_selection else "发牌前 (Pre-Flop)"
st.info(f"**你的手牌:** {p1_str}  \n**公共牌面:** {comm_str}")

# ==========================================
# 3. 运行模拟逻辑
# ==========================================
if st.button("开始计算胜率", type="primary", use_container_width=True):
    if len(p1_selection) != 2:
        st.error("⚠️ 错误：你必须选择正好 2 张手牌才能开始计算！")
    else:
        with st.spinner('正在进行运算，请稍候...'):
            start_time = time.time()
            
            known_cards = p1_selection + community_selection
            remaining_deck = [card for card in FULL_DECK if card not in known_cards]
            
            missing_community = 5 - len(community_selection)
            opponents_cards_count = (num_players - 1) * 2
            cards_to_draw = missing_community + opponents_cards_count
            
            wins, ties, losses = 0, 0, 0
            losing_reasons = Counter()

            for _ in range(num_simulations):
                drawn = random.sample(remaining_deck, cards_to_draw)
                new_comm = drawn[:missing_community]
                final_comm = community_selection + new_comm
                
                opponents_pool = drawn[missing_community:]
                p1_score, p1_name = evaluate_7cards(p1_selection + final_comm)
                
                max_opp_score = (-1, [])
                max_opp_name = ""
                
                for i in range(num_players - 1):
                    opp_hand = opponents_pool[i*2 : i*2+2]
                    opp_score, opp_name = evaluate_7cards(opp_hand + final_comm)
                    if opp_score > max_opp_score:
                        max_opp_score = opp_score
                        max_opp_name = opp_name
                        
                if p1_score > max_opp_score:
                    wins += 1
                elif p1_score == max_opp_score:
                    ties += 1
                else:
                    losses += 1
                    losing_reasons[max_opp_name] += 1

            end_time = time.time()
            
            # --- 渲染计算结果 ---
            st.success(f"✅ 模拟完成！运算耗时: {end_time - start_time:.2f} 秒")
            
            st.markdown("### 📊 胜率分析报告")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("🏆 获胜概率 (Win)", f"{(wins/num_simulations)*100:.2f}%")
            res_col2.metric("🤝 平局概率 (Tie)", f"{(ties/num_simulations)*100:.2f}%")
            res_col3.metric("💔 失败概率 (Loss)", f"{(losses/num_simulations)*100:.2f}%")
            
            if losses > 0:
                st.markdown("#### ☠️ 失败原因分析 (对手用什么牌击败了你)")
                # 将 Counter 转换为漂亮的表格
                reasons_data = []
                for name, count in losing_reasons.most_common():
                    reasons_data.append({
                        "击败你的牌型": name,
                        "击败你的概率 (%)": f"{(count / losses) * 100:.2f}%"
                    })
                st.dataframe(reasons_data, use_container_width=True)