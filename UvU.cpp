#include <iostream>
#include <random>
#include "UvU.h"

using namespace std;

void Game::distribute_tokens(){
    int a = Tokens;
    for (int i=0;i<Piles;i++){
        tokens_in_piles[i]=1;
    }
    a -= Piles;//tokens left
    default_random_engine engine(static_cast<unsigned int>(time(0)));
    uniform_int_distribution<int> randomInt(0,Piles - 1);

    while(a>0){
        int pile_number = randomInt(engine);
        tokens_in_piles[pile_number]++;
        a--;
    }
}