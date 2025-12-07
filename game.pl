:- use_module(library(http/thread_httpd)).
:- use_module(library(http/http_dispatch)).
:- use_module(library(http/http_json)).
:- use_module(library(http/http_files)).
:- use_module(library(http/http_error)).

% --- Game State ---
:- dynamic mario/2.
:- dynamic velocity/2.
:- dynamic item/3.
:- dynamic enemy/4.
:- dynamic score/1.
:- dynamic game_state/1.

% --- Configuration ---
map_width(30).
map_height(10).
gravity(1).
jump_force(3).

% --- Map Data ---
solid(_, Y) :- Y =< 1.
solid(X, 4) :- between(10, 15, X).
solid(X, 7) :- between(20, 25, X).
solid(1, _) :- true.
solid(30, _) :- true.

% --- HTTP Handlers ---
:- http_handler(root(.), http_reply_from_files('.', []), [prefix]).
:- http_handler(root(tick), handle_tick, []).
:- http_handler(root(init), handle_init, []).

% --- Server Control ---
server(Port) :-
    http_server(http_dispatch, [port(Port)]).

% --- Game Logic (Adapted) ---
init_game :-
    retractall(mario(_, _)),
    retractall(velocity(_, _)),
    retractall(item(_, _, _)),
    retractall(enemy(_, _, _, _)),
    retractall(score(_)),
    retractall(game_state(_)),
    
    assert(mario(3, 2)),
    assert(velocity(0, 0)),
    assert(score(0)),
    assert(game_state(running)),
    
    assert(item(12, 5, coin)),
    assert(item(22, 8, coin)),
    assert(item(28, 2, star)),
    % enemy(X, Y, Type, Direction) - Direction: 1 (right), -1 (left)
    assert(enemy(18, 2, goomba, -1)).

process_input("left") :- move_mario(-0.5, 0).
process_input("right") :- move_mario(0.5, 0).
process_input("jump") :- jump.
process_input(_).

handle_tick(Request) :-
    http_read_json_dict(Request, Dict),
    Action = Dict.action,
    
    (   game_state(running) ->
        process_input(Action),
        update_physics,
        update_enemies,
        check_interactions,
        check_game_over
    ;   true
    ),
    
    mario(X, Y),
    score(S),
    game_state(State),
    findall(_{x: Ix, y: Iy, type: It}, item(Ix, Iy, It), Items),
    findall(_{x: Ex, y: Ey, type: Et}, enemy(Ex, Ey, Et, _), Enemies),
    
    reply_json_dict(_{
        mario: _{x: X, y: Y},
        items: Items,
        enemies: Enemies,
        score: S,
        state: State
    }).

update_enemies :-
    findall(enemy(X, Y, T, D), enemy(X, Y, T, D), Enemies),
    update_enemy_list(Enemies).

update_enemy_list([]).
update_enemy_list([enemy(X, Y, T, D)|Rest]) :-
    Speed = 0.1,
    NX is X + (D * Speed),
    
    % Check bounds/collision
    CheckX is round(NX),
    CheckY is round(Y),
    GroundY is round(Y - 1),
    
    (   (solid(CheckX, CheckY) ; \+ solid(CheckX, GroundY)) ->
        % Hit wall or edge of platform -> Reverse
        NewD is D * -1,
        FinalX = X
    ;   NewD = D,
        FinalX = NX
    ),
    
    retract(enemy(X, Y, T, D)),
    assert(enemy(FinalX, Y, T, NewD)),
    update_enemy_list(Rest).

move_mario(DX, DY) :-
    mario(X, Y),
    NX is X + DX,
    NY is Y + DY,
    CheckX is round(NX),
    CheckY is round(NY),
    \+ solid(CheckX, CheckY),
    retract(mario(X, Y)),
    assert(mario(NX, NY)).

jump :-
    mario(X, Y),
    GroundY is round(Y - 1),
    CheckX is round(X),
    solid(CheckX, GroundY),
    retract(velocity(VX, _)),
    jump_force(JF),
    assert(velocity(VX, JF)).

update_physics :-
    mario(X, Y),
    velocity(VX, VY),
    gravity(G),
    NewVY is VY - 0.2,
    NewY is Y + NewVY,
    
    CheckX is round(X),
    CheckNewY is round(NewY),
    
    (   NewY > Y, \+ solid(CheckX, CheckNewY) ->
        FinalY = NewY, FinalVY = NewVY
    ;   NewY < Y ->
        (   solid(CheckX, CheckNewY) ->
            FinalY = CheckNewY + 1, FinalVY = 0
        ;   FinalY = NewY, FinalVY = NewVY
        )
    ;   FinalY = Y, FinalVY = NewVY
    ),
    
    retract(mario(X, Y)),
    assert(mario(X, FinalY)),
    retract(velocity(VX, VY)),
    assert(velocity(VX, FinalVY)).

check_interactions :-
    mario(X, Y),
    RX is round(X), RY is round(Y),
    (   item(RX, RY, Type) ->
        retract(item(RX, RY, Type)),
        score(S), NS is S + 100,
        retract(score(S)), assert(score(NS))
    ;   true
    ),
    (   enemy(EX, EY, _, _) ->
        % Simple box collision
        AbsDX is abs(EX - X),
        AbsDY is abs(EY - Y),
        (   AbsDX < 0.8, AbsDY < 0.8 ->
            retract(game_state(_)),
            assert(game_state(lost))
        ;   true
        )
    ;   true
    ).

check_game_over :-
    mario(X, _),
    map_width(W),
    (   X >= W ->
        retract(game_state(_)),
        assert(game_state(won))
    ;   true
    ).
