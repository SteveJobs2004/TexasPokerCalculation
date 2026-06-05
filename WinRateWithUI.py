import streamlit as st

from poker_calculator import (
    FULL_DECK,
    format_card,
    localized_hand_name,
    simulate_winrate,
)

CARD_NAMES = {card: format_card(card) for card in FULL_DECK}
SIMULATION_OPTIONS = [20_000, 50_000, 100_000, 500_000, 1_000_000]


st.set_page_config(page_title="德州扑克概率计算器", page_icon="🃏", layout="wide")
st.title("🃏 德州扑克动态胜率计算器 ")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ 模拟参数设置")
    num_players = st.slider("玩家总人数", min_value=2, max_value=9, value=5)
    num_simulations = st.select_slider(
        "蒙特卡罗模拟局数",
        options=SIMULATION_OPTIONS,
        value=20_000,
    )
    st.info("💡 提示：模拟局数越大，结果越精确，但计算等待时间越长。网页端建议使用 20,000 次。")

col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 选择你的手牌 (必须选 2 张)")
    p1_selection = st.multiselect(
        "点击下拉框选择扑克牌：",
        options=FULL_DECK,
        format_func=lambda card: CARD_NAMES[card],
        max_selections=2,
        key="p1_cards",
    )

with col2:
    st.subheader("🌐 选择公共牌 (0 到 5 张)")
    available_for_community = [card for card in FULL_DECK if card not in p1_selection]
    community_selection = st.multiselect(
        "点击下拉框选择公共牌：",
        options=available_for_community,
        format_func=lambda card: CARD_NAMES[card],
        max_selections=5,
        key="community_cards",
    )

st.markdown("### 🎲 当前牌面")
p1_text = "  ".join(CARD_NAMES[card] for card in p1_selection) if p1_selection else "尚未选择"
community_text = (
    "  ".join(CARD_NAMES[card] for card in community_selection)
    if community_selection
    else "发牌前 (Pre-Flop)"
)
st.info(f"**你的手牌:** {p1_text}  \n**公共牌面:** {community_text}")

if st.button("开始计算胜率", type="primary", use_container_width=True):
    if len(p1_selection) != 2:
        st.error("错误：你必须选择正好 2 张手牌才能开始计算！")
    else:
        with st.spinner("正在进行运算，请稍候..."):
            try:
                result = simulate_winrate(
                    p1_selection,
                    community_selection,
                    num_players,
                    num_simulations,
                )
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"✅ 模拟完成！运算耗时: {result.elapsed_seconds:.2f} 秒")

                st.markdown("### 📊 胜率分析报告")
                result_col1, result_col2, result_col3 = st.columns(3)
                result_col1.metric("🏆 获胜概率 (Win)", f"{result.win_rate * 100:.2f}%")
                result_col2.metric("🤝 平局概率 (Tie)", f"{result.tie_rate * 100:.2f}%")
                result_col3.metric("💔 失败概率 (Loss)", f"{result.loss_rate * 100:.2f}%")

                if result.losses > 0:
                    st.markdown("#### ☠️ 失败原因分析 (对手用什么牌击败了你)")
                    reasons_data = [
                        {
                            "击败你的牌型": localized_hand_name(hand_name),
                            "击败你的概率 (%)": f"{(count / result.losses) * 100:.2f}%",
                        }
                        for hand_name, count in result.losing_reasons.most_common()
                    ]
                    st.dataframe(reasons_data, use_container_width=True)
