# TexasPokerCalculation

简易德州扑克动态获胜概率计算器。

## 项目结构

- `poker_calculator.py`: 共享的牌型评估与蒙特卡罗模拟逻辑
- `WinRateWithUI.py`: Streamlit 可视化胜率计算器
- `WinRate.py`: 命令行胜率模拟入口
- `TypeRate.py`: 命令行牌型分布模拟入口
- `tests/`: 核心逻辑的单元测试

## 运行

```bash
streamlit run WinRateWithUI.py
```

```bash
python WinRate.py
python TypeRate.py
python -m unittest discover
```
