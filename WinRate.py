from poker_calculator import simulate_winrate

# --- 参数配置 ---
NUM_SIMULATIONS = 50_000
NUM_PLAYERS = 5

# 输入: 玩家 P1 的手牌 (必须是2张)
# 格式: (点数, 花色) -> 11=J, 12=Q, 13=K, 14=A
# 花色: 'H'=红桃, 'D'=方块, 'C'=梅花, 'S'=黑桃
P1_HAND = [(11, "H"), (2, "S")]

# 输入: 当前已知的公共牌 (可以是 0 到 5 张)
COMMUNITY_CARDS = [(8, "D"), (11, "S"), (5, "D")]


def run_winrate_simulation() -> None:
    print(f"玩家总数: {NUM_PLAYERS}")
    print(f"P1 手牌: {P1_HAND}")
    print(f"已知公共牌: {COMMUNITY_CARDS} (共 {len(COMMUNITY_CARDS)} 张)")
    print(f"开始蒙特卡罗模拟... (局数: {NUM_SIMULATIONS})")

    result = simulate_winrate(P1_HAND, COMMUNITY_CARDS, NUM_PLAYERS, NUM_SIMULATIONS)

    print("\n" + "=" * 45)
    print(f"模拟完成！耗时: {result.elapsed_seconds:.2f} 秒")
    print("=" * 45)
    print(f"P1 获胜概率 (Win) : {result.win_rate * 100:.2f}%")
    print(f"P1 平局概率 (Tie) : {result.tie_rate * 100:.2f}%")
    print(f"P1 失败概率 (Loss): {result.loss_rate * 100:.2f}%")
    print("=" * 45)

    if result.losses > 0:
        print("\n当 P1 失败时，击败 P1 的最强牌型分布：")
        print(f"{'对手牌型 (Hand)':<20} | {'出现次数':<10} | {'占比 (%)'}")
        print("-" * 45)
        for hand_name, count in result.losing_reasons.most_common():
            probability = (count / result.losses) * 100
            print(f"{hand_name:<20} | {count:<10} | {probability:.2f}%")


if __name__ == "__main__":
    run_winrate_simulation()
