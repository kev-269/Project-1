#include <array>
#ifndef
#define

class Game{
    private:
        int Tokens;
        const int Piles;
        int Mode;
        array<int,Piles> tokens_in_piles;
    public:
        void distribute_tokens();


};