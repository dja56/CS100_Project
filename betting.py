import main
import player
import dealer
import trainer
import math


chips = 100

def raiseBet(raiseAmount):
    if raiseAmount < 0:
        print("Enter a proper number")
        raiseBet(int(input("Enter Bet Amount: ")))
    elif raiseAmount == 0:
        print("You can't raise by nothing")
    bet += raiseAmount
    return bet

def lowerBet(lowerAmount):
    bet -= lowerAmount
