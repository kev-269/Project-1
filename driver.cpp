#include <iostream>
#include "UvU.h"
#include "player.h"
using namespace std;


int main(){
    Game GAME;
    Player ply1;
    Player ply2;
    string S1;
    cout << "Name 1:"; cin>>S1;
    ply1.set_name(S1);
    string S2;
    cout << "Name 2:"; cin>>S2;
    ply2.set_name(S2);

    cout<<endl<<endl<<ply1.get_name()<<ply2.get_name();


}
