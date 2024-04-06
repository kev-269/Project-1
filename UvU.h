#include <array>
#include "player.h"
#ifndef
#define


class Game{
    private:
        int Tokens;
        const int Piles;
        int Mode;
        array<int,Piles> tokens_in_piles;
        Player player1,player2;
        Player* current_player;
    public:
        void distribute_tokens();
        void set_turn( Player p1 , Player p2 );
        void player_removes_from_pile( char A, int B );
        void check_game_status();
        ~game();
        void play_game()

};
#endif