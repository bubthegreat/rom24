# KBK Prog System — C Research (Phase 3 ground truth)

Source: /home/bub/Development/kbk/src/ (mprog.c, iprog.c, rprog.c, merc.h, dispatch sites).
Python side: rom24 loads `#IMPROGS` bindings as inert `(progtype, progname)` tuples on
npc/item/room templates (`data_loader.load_improgs`). `pyprogs.py` has a working signal
system (`emit_signal`/`register_signal`) with only the "say" signal wired (do_say.py:18).

## Trigger types (merc.h:318-345)

| Kind | Trigger | Fired when | Signature (C) | Veto? |
|---|---|---|---|---|
| MPROG | BRIBE | gold given to npc | (mob, ch, amount) | no |
| MPROG | ENTRY | npc enters room | (mob) | no |
| MPROG | GREET | pc/npc enters room w/ mob present (only if room has PC) | (mob, ch) | no |
| MPROG | GIVE | object given to npc | (mob, ch, obj) | no |
| MPROG | FIGHT | violence pulse while fighting, if mob.wait<=0 (fight.c:267) | (mob, victim) | no |
| MPROG | DEATH | mob dies (fight.c:4034) | (mob, killer) -> bool | **TRUE prevents death** (position=POS_STANDING) |
| MPROG | PULSE | mobile pulse (update.c:600) | (mob) | no |
| MPROG | SPEECH | someone says in room, speaker != mob (act_comm.c:930) | (mob, ch, speech) | no |
| MPROG | ATTACK | mob attacked (fight.c:3622) | (mob, attacker) | no |
| MPROG | MOVE | someone moves through mob's room, PRE-move (act_move.c:294) | (ch, mob, from_room, direction) -> bool | **FALSE blocks movement** |
| IPROG | WEAR/REMOVE | equip/unequip | (obj, ch) | no |
| IPROG | GET/DROP | pick up / drop | (obj, ch) | no |
| IPROG | SAC | sacrifice | (obj, ch) -> bool | TRUE prevents |
| IPROG | GIVE | give obj | (obj, from, to) -> bool | TRUE prevents |
| IPROG | GREET | someone enters room; fires for items CARRIED by chars present (act_move.c:486) | (obj, ch=enterer) | no |
| IPROG | FIGHT | violence pulse, owner fighting (fight.c:264) | (obj, ch=owner) | no |
| IPROG | DEATH | owner dies (fight.c:4026) | (obj, victim) -> bool | **TRUE prevents death** |
| IPROG | SPEECH | say in room; fires for room contents AND the SPEAKER's carried items (ch->carrying only, act_comm.c:939-946) | (obj, ch=speaker, speech) | no |
| IPROG | ENTRY | carrier enters room, POST-move (act_move.c:498) | (obj) | no |
| IPROG | PULSE | every pulse (update.c:2248) | (obj, isTick) | no |
| IPROG | INVOKE | `invoke <worn item>` command (iprog.c:488 do_invoke) | (obj, ch, argument) | no |
| RPROG | SPEECH | say in room (act_comm.c:949) | (room, ch, speech) | no |
| RPROG | ENTRY | char_to_room (handler.c:2009) | (room, ch) | no |

progtype words in #IMPROGS data map via mprog_set/iprog_set/rprog_set (db2.c): e.g.
"greet_prog"→GREET, "fight_prog"→FIGHT, etc. (mprog.c:87-188, iprog.c:350-464, rprog.c).

## Registered prog implementations

- **mprog_table (mprog.c:60-85), 22 entries:** guardians (greet/death/attack/move outer,
  greet/death inner), centurion greet, battlefield greets (soldier/paladin/troll/goblin),
  elthian speech+greet, obsidian_prince death, mercenary fights (warrior/thief/assassin),
  sequestered pulse+fight, enforcer speech, animate_weapon/armor fights.
- **iprog registry (iprog.c:199-348), ~148 entries:** wear/remove/fight/invoke/get/sac/
  give/speech/pulse/drop/entry/greet/death _prog families (phylacteries, tattoos, cabal
  items, quest rewards, Obsidian keys, sword_infinity).
- **rprog_table (rprog.c:39-76), 2 entries:** speech_prog_realm_dead, rprog_entry_esiraen_fall.

## Area-data census (grep of src/area/kbk #IMPROGS)

fight 44 · invoke 39 · greet 26 · remove 23 · wear 21 · death 21 · move 9 · give 9 ·
attack 9 · speech 7 · pulse 7 · get 7 · entry 2 · sac 1. Port priority follows this order.

## Representative implementations (verbatim C)

```c
void greet_prog_outer_guardian(CHAR_DATA *mob, CHAR_DATA *ch) {
    if (IS_NPC(ch) || ch->invis_level > LEVEL_HERO - 1) return;
    if (mob->cabal == ch->cabal)
        do_say(mob, cabal_messages[ch->cabal].entrygreeting);
}
```

death_prog_outer_guardian (mprog.c:227-278): announces via do_cb; if the INNER guardian
carries a cabal item belonging to the killer's cabal (and mob's cabal differs), item
returns to that cabal's guardian, killer's group each gain +3 quest_credits with a {Y
message, cabal_shudder fires, save_cabal_items(); returns FALSE (death proceeds).

wear_prog_crystal_tiara (iprog.c:529): act to room + send_to_char (pure flavor).
invoke_prog_tattoo_detlef (iprog.c:580-634): heal (level*2)*8 capped, dispel
blindness/poison/plague, apply gsn_phat_blunt affect — representative of invoke complexity.

## rom24 hook points (python)

| C dispatch | Python site | Status |
|---|---|---|
| speech progs | commands/do_say.py:18 (emit_signal "say") | signal exists, extend |
| entry/greet/move | handler_ch.py move (~21-104) + handler_room.py put (~100) | not hooked |
| fight pulse | fight.py violence loop (~260) | not hooked |
| attack | fight.py damage (~486-550) | not hooked |
| death | fight.py raw_kill (~1161) | not hooked |
| pulse | update.py (~840+) | not hooked |
| wear/remove/get/drop | equip/get/drop command+handler paths | not hooked |
| invoke | no do_invoke command exists | create |
