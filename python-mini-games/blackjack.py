import random

def calculate_hand_value(hand):
    ace_count = hand.count('A')
    total = 0
    for card in hand:
        if card.isdigit():
            total += int(card)
        elif card in ('J', 'Q', 'K'):
            total += 10
        elif card == 'A':
            total += 11
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total

def deal_card(deck):
    return deck.pop()

def play_blackjack():
    deck = [str(i) for i in range(2, 11)] * 4 + ['J'] * 4 + ['Q'] * 4 + ['K'] * 4 + ['A'] * 4
    random.shuffle(deck)

    player_hand = []
    dealer_hand = []

    for _ in range(2):
        player_hand.append(deal_card(deck))
        dealer_hand.append(deal_card(deck))

    print("Your hand:", player_hand)
    player_total = calculate_hand_value(player_hand)
    print("Your total:", player_total)
    dealer_total = calculate_hand_value(dealer_hand)
    print("Dealer showing:", dealer_hand[0])


    if player_total == 21:
        print("\nBlackjack!")
        if dealer_total == 21:
            print("\nDealer Blackjack! Push!");
        else:
            print("\nYou win!")
        return

    while player_total < 21:
        action = input("Hit or stand? (h/s): ")
        if action.lower() == 'h':
            player_hand.append(deal_card(deck))
            player_total = calculate_hand_value(player_hand)
            print("\nYour hand:", player_hand)
            print("Your total:", player_total)
            if player_total > 21:
                print("\nBust! You lose.")
                return
        else:
            break

    print("\nDealer's hand:", dealer_hand)
    print("Dealer's total:", dealer_total)

    while dealer_total < 17:
        dealer_hand.append(deal_card(deck))
        dealer_total = calculate_hand_value(dealer_hand)
        print("\nDealer hits")
        print("\nDealer's hand:", dealer_hand)
        print("Dealer's total:", dealer_total)
        if dealer_total > 21:
            print("\nDealer busts! You win!")
            return

    if player_total > dealer_total or dealer_total > 21:
        print("You win!")
    elif player_total == dealer_total:
        print("\nPush!")
    else:
        print("\nYou lose.")

if __name__ == "__main__":
    play_blackjack()
