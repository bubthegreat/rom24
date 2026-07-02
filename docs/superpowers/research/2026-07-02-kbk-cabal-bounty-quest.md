# KBK Cabal / Bounty / Quest Systems — C Research (Phase 3 ground truth)

Source: /home/bub/Development/kbk/src/ (tables.c/h, morecabal.c, bounty.c, queststore.c,
act_wiz.c, fight.c, save.c, db.c, lookup.c).

## Cabals

- **cabal_type** (tables.h:41-54): name, who_name, long_name, hall (room vnum),
  item_vnum (cabal power item), altar_vnum/key_vnum (0, reserved), max_members (50),
  independent/status (FALSE), induct (TRUE).
- **cabal_table** (tables.c:42-55), index 0 = none, 1-9: ancient (hall ROOM_VNUM_ANCIENT=3804
  region, item 3801), knight (item 4502), arcana, rager, outlaw, empire, bounty, sylvan,
  enforcer. Recall vnums merc.h:1773-1779: outlaw 9904, enforcer 23603, rager 5706,
  arcana 5800, ancient 3804, knight 4504.
- **Fields:** CHAR_DATA.cabal (sh_int, 0=none/1-9), CHAR_DATA.quest_credits (long),
  PC_DATA.induct (0=member, CABAL_LEADER flag). Global cabal_members[]/cabal_max[]
  rebuilt at boot from player loads.
- **cabal_lookup** (lookup.c:97-108): prefix match over table, returns 0 on miss.
- **Cabal items:** sys/citems.txt lines `cabal_number guardian_mob_vnum` (-1 ends);
  load_cabal_items (db.c:2094-2120) creates cabal_table[n].item_vnum object onto that
  guardian. save_cabal_items rewrites the ledger. Guardians = NPCs with
  ACT_INNER_GUARDIAN / ACT_OUTER_GUARDIAN act flags (merc.h:3256-3257 macros).
- **do_induct** (act_wiz.c:485-603): permission = level 56+ or CABAL_LEADER of own cabal;
  target online; "none" = outcast (decrement count, set cabal-group skills learned=-2,
  group_remove, cabal=0); induct = capacity + eligibility checks, set cabal, grant cabal
  group (group named after the cabal, e.g. group "ancient"), increment count.
- Commands: induct, cabalstat, allcabals (imm 53+).

## Bounty

- **bounty_table** (tables.c:1016-1023): neophyte 0 / hunter 200 / master 500 / sensei
  1000 credits; rank groups named after ranks ("hunter"/"master"/"sensei" — these exist in
  rom24's converted GROUPS).
- **Fields:** PC_DATA.bounty (gold on head, cumulative), PC_DATA.bounty_credits.
- **do_bounty** (bounty.c:174-223): place ≥1000 gold on a PC (not self/immortal/not by
  bounty-cabal member... note: check is `ch->cabal == CABAL_BOUNTY` can't place); deducts
  gold; records to ledger. Imm variant `bounty <player> clear`.
- **Ledger:** KBK uses SQLite table bounties(amount, placer, victim, timestamp)
  (record_bounty bounty.c:225, pay_bounty 264). rom24 port decision: plain JSON/text
  ledger under SYSTEM area (spec allows "operational system files").
- **bounty_credit** (bounty.c:97-135): add credits; on crossing a rank threshold, learn
  that rank-group's skills at 70%.
- **pay_bounty** (bounty.c:264-303): on PvP kill — killer must be CABAL_BOUNTY member and
  victim carries bounty: killer gets gold; credit = URANGE(3, bounty/5000, 10), ×1.6 if
  victim in a cabal, ×2 if victim is leader/empire rank; bounty cleared.
- Commands: bounty, credits (show/rank; imm can set), topbounties (top 10 from ledger).

## Quest store

- **quest_reward** struct (tables.h:139-153): keyword, price, type (ARMOR/WEAPON/BOOST/
  MISC), set flags, vnum, description, acc_class[13]/acc_race[24]/acc_align/acc_ethos,
  function pointer. Table at tables.c:1025+ (~100 rewards).
- **Earning** (fight.c): gain at kill sites 3811/4265/4445 via quest_credit_compute
  (fight.c:4476-4516): NPC victim with preset quest_credits → that amount; else NPC →
  level/18; PC victim much higher level → (level/18)/3; scaled down for groups
  (divide by group_amount - 2 for large groups); no self-kill credit.
- **do_redeem / do_redeeminfo** (queststore.c:134+/38+): must be at ROOM_VNUM_ALTAR;
  "list" shows eligible rewards (class/race/align/ethos gates); redeem deducts credits
  and calls the reward function. Reward functions (queststore.c:645+, ~40): typically
  check_already_has(vnum, keyword) → create_object(vnum, level 55) → owner-lock to
  ch.original_name → obj_to_char + flavor act. gsn_questdodge: a skill granted by some
  rewards; check_questdodge (fight.c:3200-3282) gives damage avoidance.

## Persistence

Player-file keys (save.c): Cabal <name>~ (153), QuestCredits (211), Bounty (262),
BCredits (263); loads at 1022-1029, 1307. rom24: Pc.to_json auto-serializes __dict__ —
new Pc fields (cabal, quest_credits, bounty, bounty_credits, induct) persist for free.
citems + bounty ledger = operational system files (persist per spec). Cabal member
counts in-memory, rebuilt from player data.

## rom24 readiness

Already loaded from area data: npc.cabal (raw word), room.cabal (raw word), item.cabal
(int), npc.quest_credit_reward. Missing: Pc fields above, cabal_table constant,
cabal_lookup, guardian act-flag handling (KBK act flags INNER/OUTER_GUARDIAN are
extended bits — verify how rom24's Bit parsed them from area data), earning/payout hooks
in fight.py, the 6 commands, reward functions.
