from __future__ import annotations

import random
import time
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence, TypeVar

Card = tuple[int, str]
Score = tuple[int, tuple[int, ...]]
T = TypeVar("T")


class RandomSource(Protocol):
    def sample(self, population: Sequence[T], k: int) -> list[T]:
        ...

RANKS = list(range(2, 15))
SUITS = ["S", "H", "D", "C"]
FULL_DECK: list[Card] = [(rank, suit) for rank in RANKS for suit in SUITS]
FULL_DECK_SET = set(FULL_DECK)

HAND_ORDER = [
    "Royal Flush",
    "Straight Flush",
    "Four of a Kind",
    "Full House",
    "Flush",
    "Straight",
    "Three of a Kind",
    "Two Pair",
    "One Pair",
    "High Card",
]

HAND_NAMES_ZH = {
    "Royal Flush": "皇家同花顺 (Royal Flush)",
    "Straight Flush": "同花顺 (Straight Flush)",
    "Four of a Kind": "四条 (Four of a Kind)",
    "Full House": "葫芦 (Full House)",
    "Flush": "同花 (Flush)",
    "Straight": "顺子 (Straight)",
    "Three of a Kind": "三条 (Three of a Kind)",
    "Two Pair": "两对 (Two Pair)",
    "One Pair": "一对 (One Pair)",
    "High Card": "高牌 (High Card)",
}

SUIT_SYMBOLS = {"S": "♠️", "H": "♥️", "D": "♦️", "C": "♣️"}
RANK_SYMBOLS = {11: "J", 12: "Q", 13: "K", 14: "A"}


@dataclass
class WinRateResult:
    wins: int
    ties: int
    losses: int
    losing_reasons: Counter[str]
    elapsed_seconds: float

    @property
    def total(self) -> int:
        return self.wins + self.ties + self.losses

    @property
    def win_rate(self) -> float:
        return self._rate(self.wins)

    @property
    def tie_rate(self) -> float:
        return self._rate(self.ties)

    @property
    def loss_rate(self) -> float:
        return self._rate(self.losses)

    def _rate(self, count: int) -> float:
        return count / self.total if self.total else 0.0


@dataclass
class HandTypeDistribution:
    hand_counts: Counter[str]
    total_hands: int
    elapsed_seconds: float

    def rate(self, hand_name: str) -> float:
        return self.hand_counts[hand_name] / self.total_hands if self.total_hands else 0.0


def format_card(card: Card) -> str:
    rank, suit = card
    return f"{SUIT_SYMBOLS[suit]} {RANK_SYMBOLS.get(rank, str(rank))}"


def localized_hand_name(hand_name: str) -> str:
    return HAND_NAMES_ZH.get(hand_name, hand_name)


def evaluate_7cards(cards: Sequence[Card]) -> tuple[Score, str]:
    """Return a comparable poker score and the English hand name."""
    cards = list(cards)
    if len(cards) < 5:
        raise ValueError("At least 5 cards are required to evaluate a poker hand.")
    _validate_cards(cards)

    ranks = sorted((card[0] for card in cards), reverse=True)
    suits = [card[1] for card in cards]

    flush_suit = _find_flush_suit(suits)
    if flush_suit:
        flush_ranks = [rank for rank, suit in cards if suit == flush_suit]
        straight_flush_high = _straight_high(flush_ranks)
        if straight_flush_high:
            if straight_flush_high == 14:
                return (9, ()), "Royal Flush"
            return (8, (straight_flush_high,)), "Straight Flush"

    rank_counts = Counter(ranks)
    sorted_counts = sorted(rank_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)

    if sorted_counts[0][1] == 4:
        quad_rank = sorted_counts[0][0]
        kicker = max(rank for rank in ranks if rank != quad_rank)
        return (7, (quad_rank, kicker)), "Four of a Kind"

    if sorted_counts[0][1] == 3 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        return (6, (sorted_counts[0][0], sorted_counts[1][0])), "Full House"

    if flush_suit:
        flush_ranks = sorted((rank for rank, suit in cards if suit == flush_suit), reverse=True)
        return (5, tuple(flush_ranks[:5])), "Flush"

    straight_high = _straight_high(ranks)
    if straight_high:
        return (4, (straight_high,)), "Straight"

    if sorted_counts[0][1] == 3:
        trip_rank = sorted_counts[0][0]
        kickers = tuple(rank for rank in ranks if rank != trip_rank)[:2]
        return (3, (trip_rank,) + kickers), "Three of a Kind"

    if sorted_counts[0][1] == 2 and len(sorted_counts) > 1 and sorted_counts[1][1] >= 2:
        first_pair = sorted_counts[0][0]
        second_pair = sorted_counts[1][0]
        kicker = max(rank for rank in ranks if rank not in (first_pair, second_pair))
        return (2, (first_pair, second_pair, kicker)), "Two Pair"

    if sorted_counts[0][1] == 2:
        pair_rank = sorted_counts[0][0]
        kickers = tuple(rank for rank in ranks if rank != pair_rank)[:3]
        return (1, (pair_rank,) + kickers), "One Pair"

    return (0, tuple(ranks[:5])), "High Card"


def simulate_winrate(
    player_hand: Sequence[Card],
    community_cards: Sequence[Card],
    num_players: int,
    num_simulations: int,
    rng: RandomSource = random,
) -> WinRateResult:
    player_hand = list(player_hand)
    community_cards = list(community_cards)
    _validate_simulation_inputs(player_hand, community_cards, num_players, num_simulations)

    start_time = time.perf_counter()
    known_cards = player_hand + community_cards
    remaining_deck = [card for card in FULL_DECK if card not in known_cards]
    missing_community_count = 5 - len(community_cards)
    opponents_cards_count = (num_players - 1) * 2
    cards_to_draw = missing_community_count + opponents_cards_count

    wins = 0
    ties = 0
    losses = 0
    losing_reasons: Counter[str] = Counter()

    for _ in range(num_simulations):
        drawn_cards = rng.sample(remaining_deck, cards_to_draw)
        final_community = community_cards + drawn_cards[:missing_community_count]
        opponents_pool = drawn_cards[missing_community_count:]
        player_score, _ = evaluate_7cards(player_hand + final_community)

        max_opponent_score: Score = (-1, ())
        max_opponent_name = ""
        for index in range(num_players - 1):
            opponent_hand = opponents_pool[index * 2 : index * 2 + 2]
            opponent_score, opponent_name = evaluate_7cards(opponent_hand + final_community)
            if opponent_score > max_opponent_score:
                max_opponent_score = opponent_score
                max_opponent_name = opponent_name

        if player_score > max_opponent_score:
            wins += 1
        elif player_score == max_opponent_score:
            ties += 1
        else:
            losses += 1
            losing_reasons[max_opponent_name] += 1

    return WinRateResult(
        wins=wins,
        ties=ties,
        losses=losses,
        losing_reasons=losing_reasons,
        elapsed_seconds=time.perf_counter() - start_time,
    )


def simulate_hand_type_distribution(
    num_simulations: int,
    num_players: int,
    rng: RandomSource = random,
) -> HandTypeDistribution:
    _validate_player_count(num_players)
    _validate_positive_simulations(num_simulations)

    start_time = time.perf_counter()
    hand_counts: Counter[str] = Counter()
    cards_needed = 5 + num_players * 2

    for _ in range(num_simulations):
        drawn_cards = rng.sample(FULL_DECK, cards_needed)
        community_cards = drawn_cards[:5]

        for player_index in range(num_players):
            start = 5 + player_index * 2
            player_cards = drawn_cards[start : start + 2]
            _, hand_name = evaluate_7cards(community_cards + player_cards)
            hand_counts[hand_name] += 1

    return HandTypeDistribution(
        hand_counts=hand_counts,
        total_hands=num_simulations * num_players,
        elapsed_seconds=time.perf_counter() - start_time,
    )


def _find_flush_suit(suits: Sequence[str]) -> str | None:
    for suit, count in Counter(suits).items():
        if count >= 5:
            return suit
    return None


def _straight_high(ranks: Iterable[int]) -> int | None:
    unique_ranks = sorted(set(ranks), reverse=True)
    if 14 in unique_ranks:
        unique_ranks.append(1)

    for index in range(len(unique_ranks) - 4):
        if unique_ranks[index] - unique_ranks[index + 4] == 4:
            return unique_ranks[index]
    return None


def _validate_simulation_inputs(
    player_hand: Sequence[Card],
    community_cards: Sequence[Card],
    num_players: int,
    num_simulations: int,
) -> None:
    if len(player_hand) != 2:
        raise ValueError("Player hand must contain exactly 2 cards.")
    if len(community_cards) > 5:
        raise ValueError("Community cards cannot contain more than 5 cards.")

    _validate_player_count(num_players)
    _validate_positive_simulations(num_simulations)
    _validate_cards(list(player_hand) + list(community_cards))


def _validate_player_count(num_players: int) -> None:
    if num_players < 2:
        raise ValueError("At least 2 players are required.")
    if num_players > 10:
        raise ValueError("Texas Hold'em supports at most 10 players.")


def _validate_positive_simulations(num_simulations: int) -> None:
    if num_simulations <= 0:
        raise ValueError("Number of simulations must be positive.")


def _validate_cards(cards: Sequence[Card]) -> None:
    invalid_cards = [card for card in cards if card not in FULL_DECK_SET]
    if invalid_cards:
        raise ValueError(f"Invalid cards: {invalid_cards}")
    if len(set(cards)) != len(cards):
        raise ValueError("Cards cannot contain duplicates.")
