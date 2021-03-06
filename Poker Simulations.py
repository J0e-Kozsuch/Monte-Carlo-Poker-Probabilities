import numpy as np
import pandas as pd
import math as m
import os
import random as r


def reformat_numbers(x):
    '''
    Allign one and two digit numbers to consistently have two as a string
    '''
    x=str(x).strip()
    if len(x)<2:
        return '0'+x
    return x



class best_poker_hand:
    
    def __init__(self,a_deck,a_hand,after_what=None):
             
        self.flop=a_deck.flop
        self.turn=a_deck.turn
        self.river=a_deck.river
        self.hand=a_hand.cards
        
        self.best_hand=None
        self.first=None
        self.second=None
        self.third=None
        self.fourth=None
        self.fifth=None

        self.number=None

        if self.hand==[]:
            raise Exception("Trying to calculate best hand yet hand has no cards.")

        # Assemble poker hand given after which deal the round has been played.
        if after_what==None:
            if self.flop==[]:
                self.cards=self.hand
            elif self.turn==None:
                self.cards=self.hand+self.flop
            elif self.river==None:
                self.cards=self.hand+self.flop+[self.turn]
            else:
                self.cards=self.hand+self.flop+[self.turn]+[self.river]

        elif str(after_what).lower()=="deal":
            self.cards=self.hand

        elif str(after_what).lower()=="flop":
            self.cards=self.hand+self.flop

        elif str(after_what).lower()=="turn":
            self.cards=self.hand+self.flop+[self.turn]

        elif str(after_what).lower()=="river":
            self.cards=self.hand+self.flop+[self.turn]+[self.river]

        else:
            raise Exception("Calculating best hand variable after_what must be ['deal','flop','turn','river']")
        

    def calculate_best_hand(self):
        '''
        Determine best hand (string) and the top cards that contribute to its scoring.
        '''

        # cards_df is rank and suit of cards in poker hand, sorted by rank
        cards_df=pd.DataFrame(columns=['rank','suit'])
        for a_card in self.cards:
            cards_df=pd.concat((cards_df,pd.DataFrame(data=[[a_card.rank,a_card.suit]],columns=['rank','suit'])),axis=0)

        cards_df.sort_values(['rank'],inplace=True,ascending=False)

        cards_df.reset_index(inplace=True,drop=True)

        # rank variables are used to determine pairings.
        rank_count_series=cards_df['rank'].value_counts()
        
        first_rank=rank_count_series.index[0]
        first_count=rank_count_series.iloc[0]

        self.first=first_rank
        unique_ranks=rank_count_series.shape[0]

        # If the highest number of recurrence of one rank is 1, start with high card.
        if first_count==1:
            self.best_hand='High Card'
            rank_list=list(rank_count_series.index[1:])
            self.second=rank_count_series.index[1]
            if unique_ranks>2:
                self.second=rank_list[0]
                self.third=rank_list[1]
                self.fourth=rank_list[2]
                self.fifth=rank_list[3]
            else:
                return None

        # If the highest number of recurrence of one rank is 2, start with pair and check for two pair.
        elif first_count==2:
        
            if rank_count_series.iloc[1]==1:
                self.best_hand='Pair'
                
                if unique_ranks>1:
                    rank_list=list(rank_count_series.index[1:])
                    rank_list.sort(reverse=True)
                    self.second=rank_list[0]
                    self.third=rank_list[1]
                    self.fourth=rank_list[2]
                else:
                    return None
                        

            if rank_count_series.iloc[1]==2:
                self.best_hand='Two Pair'
                if rank_count_series.iloc[2]==2:
                    pair_list=list(rank_count_series.index[:3])
                    pair_list.sort(reverse=True)
                    self.first=pair_list.pop(0)
                    self.second=pair_list.pop(0)
                    non_pair_list=list(rank_count_series.index[3:])+pair_list
                    non_pair_list.sort(reverse=True)
                    self.third=non_pair_list[0]
                    return None
                else:
                    rank_list=list(rank_count_series.index[:2])
                    rank_list.sort(reverse=True)
                    self.first=rank_list[0]
                    self.second=rank_list[1]

                    self.third=max(list(rank_count_series.index[2:]))
                    
                
        # If the highest number of recurrence of one rank is 3, start with three of a kind and check for three of a kind.
        elif first_count==3:
        
            if rank_count_series.iloc[1]==1:
                self.best_hand='Three Kind'
                rank_list=list(rank_count_series.index[1:])
                rank_list.sort(reverse=True)
                self.second=rank_list[0]
                self.third=rank_list[1]  

            if rank_count_series.iloc[1]==2:
                self.best_hand='Full House'
                if rank_count_series.iloc[2]==2:
                    self.second=max(rank_count_series.index[1],rank_count_series.index[2])
                    return None
                
                self.second=rank_count_series.index[1]
                
                return None

            if rank_count_series.iloc[1]==3:
                self.best_hand='Full House'
                self.first=max(list(rank_count_series.index[0:2]))
                self.second=max(list(rank_count_series.index[0:2]))
                return None

        # If the highest number of recurrence of one rank is 4, four of a kind is the best hand possible.
        elif first_count==4:
            self.best_hand='Four Kind'
            rank_list=list(rank_count_series.index[1:])
            rank_list.sort(reverse=True)
            self.second=rank_list[0]

            return None

        # If there are less than 5 unique ranks, flushes and straights are not possible. 
        if unique_ranks<5:
            return None

        #Check for flush by looking at suit value counts.
        suit_count_df=cards_df['suit'].value_counts()
        
        if suit_count_df.iloc[0]>4:
            flush_suit=suit_count_df.index[0]
            flush_cards_df=cards_df[cards_df['suit']==flush_suit]
            flush_cards_list=flush_cards_df['rank'].tolist()
            flush_cards_list.sort(reverse=True)
            self.first=flush_cards_list[0]
            self.second=flush_cards_list[1]
            self.third=flush_cards_list[2]
            self.fourth=flush_cards_list[3]
            self.fifth=flush_cards_list[4]
            self.best_hand='Flush'

        # Before checking for straight, create duplicate Ace row with rank 1 rather than 14
        for i in self.cards:
            if i.rank==14:
                cards_df=pd.concat((cards_df,pd.DataFrame(data=[[1,i.suit]],columns=['rank','suit'])),axis=0)
                cards_df.reset_index(drop=True,inplace=True)

        
        # If flush was found, check for straight flush
        if self.best_hand=='Flush':
            flush_cards_df=cards_df[cards_df['suit']==flush_suit]
            flush_cards_list=flush_cards_df['rank'].tolist()
            flush_cards_list.sort(reverse=True)
            flush_cards_count=len(flush_cards_list)
            streak=1
            high_card=flush_cards_list[0]
            for i in range(1,flush_cards_count):
                if flush_cards_list[i-1]-flush_cards_list[i]>1:
                    if flush_cards_count-i<5:
                        return None
                    high_card=flush_cards_list[i]
                    streak=1

                else:
                    streak+=1
                    if streak==5:
                        self.best_hand='Straight Flush'
                        self.first=high_card
                        
                        return None
                    
        #Cheack for straight
        cards_list=cards_df['rank'].unique().tolist()
        cards_list.sort(reverse=True)
        cards_count=len(cards_list)         
        streak=1
        high_card=cards_list[0]
        
        for i in range(1,cards_count):
            if cards_list[i-1]-cards_list[i]>1:
                if cards_count-i<5:
                    return None
                high_card=cards_list[i]
                streak=1


            else:
                streak+=1
                if streak==5:
                    self.best_hand='Straight'
                    self.first=high_card
                    self.second=None
                    self.third=None
                    self.fourth=None
                    self.fifth=None
                    
                    return None


    def calculate_hand_number(self):
        '''
        Calculate a number reflecting hand strength for comparison.
        The better the best poker hand, the higher the exponent in 10^b.
        The tie-breaking cards are added as digits below the highest value.
        '''
        
        if self.number!=None:
            return None
        num_str=''
        if self.best_hand==None:
            self.calculate_best_hand()

        if self.best_hand=='High Card':
            for i in [self.first,self.second,self.third,self.fourth,self.fifth]:
                if i==None:
                    num_str+='00'
                else:
                    num_str+=reformat_numbers(i)

        
        elif self.best_hand=='Pair':
            for i in [self.first,self.second,self.third,self.fourth]:
                if i==None:
                    num_str+='00'
                else:
                    num_str+=reformat_numbers(i)

            num_str+='000'
        
        elif self.best_hand=='Two Pair':
            for i in [self.first,self.second,self.third]:
                if i==None:
                    num_str+='00'
                else:
                    num_str+=reformat_numbers(i)

            num_str+='000000'

        elif self.best_hand=='Three Kind':
            for i in [self.first,self.second,self.third]:
                if i==None:
                    num_str+='00'
                else:
                    num_str+=reformat_numbers(i)

            num_str+='0000000'

        elif self.best_hand=='Straight':
            for i in [self.first]:
                num_str+=reformat_numbers(i)

            num_str+='000000000000'

        elif self.best_hand=='Flush':
            for i in [self.first,self.second,self.third,self.fourth,self.fifth]:
                num_str+=reformat_numbers(i)

            num_str+='00000'

        elif self.best_hand=='Full House':
            for i in [self.first,self.second]:
                num_str+=reformat_numbers(i)

            num_str+='000000000000'

        elif self.best_hand=='Four Kind':
            for i in [self.first,self.second]:
                num_str+=reformat_numbers(i)

            num_str+='0000000000000'

        elif self.best_hand=='Straight Flush':
            for i in [self.first]:
                num_str+=reformat_numbers(i)

            num_str+='0000000000000000'

        self.number=int(num_str)
    

            
        
        
                
    

class card:

    def __init__(self,suit,rank):
        if suit not in ['H','S','C','D']:
            raise Exception( "Card has incorrect suit "+str(suit)+", must be within ['H','D','C','S'].")

        if rank not in list(range(2,15)):
            raise Exception("Card has incorrect rank "+str(rank)+", must be integer 2-14")

        self.suit=suit
        self.rank=rank


class hand:
    
    def __init__(self):
        self.cards=[]
        self.best_hand=None
        self.hand_number=None

        self.first=None
        self.second=None
        self.third=None
        self.fourth=None
        self.fifth=None
        

    def receive_cards(self,deck):
        ''' Deal oneself cards given deck object.'''
        if len(self.cards)>0:
            raise Exception("Hand already has cards.")
        
        self.cards.append(deck.deal_card())
        self.cards.append(deck.deal_card())

    def assign_best_poker_hand(self,deck):
        '''
        Create best poker hand object and assign best hand and hand num.
        '''
        var=best_poker_hand(deck,self)
        var.calculate_hand_number()
        self.best_hand=var.best_hand
        self.first=var.first
        self.second=var.second
        self.third=var.third
        self.fourth=var.fourth
        self.fifth=var.fifth
        self.hand_number=var.number
        

class deck:
    
    def __init__(self):
        self.cards=[]
        for suit in ['H','S','C','D']:
            for rank in range(2,15):
                self.cards.append(card(suit,rank))
        self.flop=[]
        self.turn=None
        self.river=None

    def deal_flop(self):
        '''
        Deal the flop.
        '''
        if self.flop!=[]:
            raise Exception("Flop has already been dealt")
    
        self.flop.append(self.deal_card())
        self.flop.append(self.deal_card())
        self.flop.append(self.deal_card())

    def deal_turn(self):
        '''
        Deal the turn.
        '''
        if self.turn!=None:
            raise Exception("Turn has already been dealt")

        if self.flop==[]:
            raise Exception("Can't deal turn if flop has not been dealt.")
   
        self.turn = self.deal_card()


    def deal_river(self):
        '''
        Deal the river.
        '''
        if self.river!=None:
            raise Exception("River has already been dealt")

        if self.turn==None:
            raise Exception("Can't deal river if turn has not been dealt.")
  
        self.river = self.deal_card()

        
    def retrieve_cards(self):
        '''
        Pickup all dealt cards and reset community cards.
        Hands must be reset as well.
        '''
        self.cards=[]
        for suit in ['H','S','C','D']:
            for rank in range(2,15):
                self.cards.append(card(suit,rank))

        self.flop=[]
        self.turn=None
        self.river=None

    def shuffle(self):
        '''
        Shuffle the cards currently in the deck.
        '''
        r.shuffle(self.cards)
        deck_after_second_shuffle=[]

        while len(self.cards)>0:
            deck_after_second_shuffle.append(self.cards.pop(np.random.randint(0,len(self.cards))))

        self.cards=deck_after_second_shuffle                                        
            

    def deal_card(self):
        '''
        Deal a card from deck.
        '''
        try:
            return self.cards.pop(0)
        except Exception as e:
            print("Deal card error: "+e)





def round_simulations():
    deck1=deck()

    hand_dict={i:0 for i in ['Straight','High Card','Flush','Straight Flush','Four Kind','Three Kind','Pair','Two Pair','Full House']}

    for players in range(MIN_PLAYERS_SIMULATED, MAX_PLAYERS_SIMULATED+1):

        print("Number of Players: ____________________________ "+str(players))
        hands_df=pd.DataFrame(columns=['Num Hands','Best Hand','Hand Number','First','Second',
                                  'Card 1 Rank','Card 1 Suit','Card 2 Rank','Card 2 Suit','Won Hand',
                                       'flop_1_rank','flop_1_suit','flop_2_rank','flop_2_suit',
                                       'flop_3_rank','flop_3_suit','turn_rank','turn_suit',
                                       'river_rank','river_suit'])


        for i in range(SIMULATED_ROUNDS):
            deck1.shuffle()
            deck1.deal_flop()
            deck1.deal_turn()
            deck1.deal_river()

            hands=[]
            highest_num=0
            best_hand_index=0
            card1=None
            card2=None
            
            for j in range(players):
                hands.append(hand())
                hands[j].receive_cards(deck1)
                hands[j].assign_best_poker_hand(deck1)

                if hands[j].hand_number>highest_num:
                    best_hand_index=j
                    highest_num=hands[j].hand_number
                    tie=False

                elif hands[j].hand_number==highest_num:
                    tie=True

            best_hand=hands[best_hand_index]
            
            if tie:
                winner_val=0.5
            else:
                winner_val=1
                
            new_row=pd.DataFrame(data=[[players,best_hand.best_hand,best_hand.hand_number,best_hand.first,best_hand.second,
                                    best_hand.cards[0].rank,best_hand.cards[0].suit,
                                    best_hand.cards[1].rank,best_hand.cards[1].suit,winner_val,
                                    deck1.flop[0].rank,deck1.flop[0].suit,deck1.flop[1].rank,
                                    deck1.flop[1].suit,deck1.flop[2].rank,deck1.flop[2].suit,
                                    deck1.turn.rank,deck1.turn.suit,deck1.river.rank,deck1.river.suit]],
                             columns=['Num Hands','Best Hand','Hand Number','First','Second',
                              'Card 1 Rank','Card 1 Suit','Card 2 Rank','Card 2 Suit','Won Hand',
                                      'flop_1_rank','flop_1_suit','flop_2_rank','flop_2_suit',
                                       'flop_3_rank','flop_3_suit','turn_rank','turn_suit',
                                       'river_rank','river_suit'])

            hands_df=pd.concat((hands_df,new_row),axis=0)
            
            hands.remove(best_hand)

            for hand_var in hands:
                if hand_var.hand_number==highest_num:
                    hand_outcome=0.5
                else:
                    hand_outcome=0
                    
                new_row=pd.DataFrame(data=[[players,hand_var.best_hand,hand_var.hand_number,hand_var.first,hand_var.second,
                                        hand_var.cards[0].rank,hand_var.cards[0].suit,
                                        hand_var.cards[1].rank,hand_var.cards[1].suit,hand_outcome,
                                            deck1.flop[0].rank,deck1.flop[0].suit,deck1.flop[1].rank,
                                            deck1.flop[1].suit,deck1.flop[2].rank,deck1.flop[2].suit,
                                            deck1.turn.rank,deck1.turn.suit,deck1.river.rank,deck1.river.suit]],
                                 columns=['Num Hands','Best Hand','Hand Number','First','Second',
                                  'Card 1 Rank','Card 1 Suit','Card 2 Rank','Card 2 Suit','Won Hand',
                                          'flop_1_rank','flop_1_suit','flop_2_rank','flop_2_suit',
                                       'flop_3_rank','flop_3_suit','turn_rank','turn_suit',
                                       'river_rank','river_suit'])


                hands_df=pd.concat((hands_df,new_row),axis=0)

            deck1.retrieve_cards()

            if i%5000==0:
                print("Rounds Completed: "+str(i)+' / '+str(SIMULATED_ROUNDS))


        hands_df.to_csv(str(players)+"_players_best_hands_with_table.csv",index=False)

     
SIMULATED_ROUNDS = 10000
MIN_PLAYERS_SIMULATED = 2
MAX_PLAYERS_SIMULATED = 5

round_simulations()

