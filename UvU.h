#include <array>
#include "player.h"



class Game{
    private:
        int Tokens;
        static const int Piles;
        int Mode;
        array<int,Piles> tokens_in_piles;
        Player player1,player2;
        Player* current_player;
    public:
        Game() : Tokens(0), Mode(0), tokens_in_piles({}), current_player(nullptr){};
        void distribute_tokens();
        void set_turn( Player p1 , Player p2 );
        void player_removes_from_pile( char A, int B );
        void check_game_status();
        ~Game();
        void play_game();

};
