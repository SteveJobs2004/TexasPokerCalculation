from poker_calculator import HAND_ORDER, simulate_hand_type_distribution

# --- 参数配置 ---
NUM_SIMULATIONS = 1_000_000
NUM_PLAYERS = 7


def run_simulation(num_simulations: int, num_players: int) -> None:
    print(f"开始模拟... 总局数: {num_simulations}, 玩家数: {num_players}")

    result = simulate_hand_type_distribution(num_simulations, num_players)

    print(f"\n模拟完成！耗时: {result.elapsed_seconds:.2f} 秒")
    print("-" * 40)
    print(f"{'牌型 (Hand)':<20} | {'出现次数':<10} | {'概率 (%)'}")
    print("-" * 40)

    for hand_name in HAND_ORDER:
        count = result.hand_counts[hand_name]
        probability = result.rate(hand_name) * 100
        print(f"{hand_name:<20} | {count:<10} | {probability:.4f}%")


if __name__ == "__main__":
    run_simulation(NUM_SIMULATIONS, NUM_PLAYERS)
