#include <iostream>
#include <random>
#include "player.h"
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
void Game::set_turn(Player p1,Player p2){
    if (current_player == &p1)current_player = &p2;
    else if (current_player == &p2)current_player = &p1;
    else current_player =&p1;

}
void Game::player_removes_from_pile(char A,int B){
    token_in_piles[A-65] -= B;
    Tokens -=B;
}
void Game::check_game_status(){
    if (Tokens==0){
        cout << currentPlayer->getName() << " wins the game!\n";
        exit(0);
    }
}

void Game::play_game() {

    cout << "Current state: ";
    for (int i = 0; i < Piles; ++i) {
        cout << static_cast<char>('A' + i) << ": ";
        for (int j = 0; j < tokens_in_piles[i]; j++) {
            cout << "O";
        }
        cout <<endl;
    }


    char pile;
    int tokens;
    std::cout << currentPlayer->getName() << "'s turn. Choose a pile and number of tokens: ";
    std::cin >> pile >> tokens;
    player_removes_from_pile(pile, tokens);


    check_game_status();


    currentPlayer = (currentPlayer == &player1) ? &player2 : &player1;


    play_game();
}