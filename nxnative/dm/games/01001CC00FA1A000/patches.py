# nx2android offline patches for Hatsune Miku: Project DIVA MegaMix
# Title ID: 0100801011c3e000
#
# Adapted from exlaunch source/program/patches.hpp.
#
# Format:
#   CUTS = { build_id: [(offset, orig_bytes_hex, new_bytes_hex, reason), ...] }
#   OBS  = { build_id: [(offset, obs_number, orig_word_hex, reason), ...] }
#   TRAMP = { build_id: [(offset, tramp_number, orig_word_hex, reason), ...] }
#
# The `offset` is relative to the NSO module base (in-module virtual address).
# `orig_bytes_hex` / `orig_word_hex` must match the bytes currently at that offset
# in the NSO for your specific build ID — the rewriter asserts this and aborts on
# mismatch.  Original bytes below were read from the extracted main NSO
# (/home/lsmsmx/Downloads/Program/0/main, build ID 179265bd41f7781dac979e7770201124).
#
# NOTE: exlaunch's patches.hpp used a FIX(addr) = addr - 0x100 macro.  The
# offsets below are the post-FIX in-module addresses from patches.hpp.
#
# Patches that exlaunch gates behind Config::* flags are NOT here: they live in
# main.config.tsv and are applied at runtime by the loader (DM_CONFIG env var).
# Only unconditional patches are in CUTS below.
#
# OBS numbers match dm.h OBS_DIVA_* (22..30) and TRAMP numbers match the host's
# gate_tramp_set() registrations in hle_diva.c (31..).  Each gate replaces its
# instruction with "enter host gate → restore x29/x30 → execute original → jump
# back".  OBS callbacks are read-only (notification only); TRAMP callbacks may
# modify any register (exlaunch inline hooks that rewrite ctx->X[N], Orig() calls).

build_id = "179265bd41f7781dac979e7770201124"

CUTS = {
    build_id: [
        # ---- Fix custom hairs with "ng=1" not appearing (unconditional) ----
        (0x003BBF70, "e8d79f1a", "52800008", "mov w0, #8 — custom hair ng=1 fix"),

        # ---- Core: module limits (unconditional) ----
        # ADDR_MOD_LIMIT_1 + 8  (= FIX(0x000C4E50) + 8 = 0x000C4D58)
        (0x000C4D58, "e883811a", "2a0103e8", "mov w1, #1000 — module limit 1"),
        # ADDR_MOD_LIMIT_2 + 0x00 .. +0x10  (= FIX(0x000C8350) + N = 0x000C8250 + N)
        (0x000C8250, "080040b9", "b4000060", "cbz x0, +0xC — module limit 2 null check"),
        (0x000C8254, "09310011", "b9400000", "ldr w0, [x0] — module limit 2 read ID"),
        (0x000C8258, "3f2d1071", "d65f03c0", "ret — module limit 2"),
        (0x000C825C, "e083881a", "2a1f03e0", "mov w0, wzr — module limit 2 null return"),
        (0x000C8260, "c0035fd6", "d65f03c0", "ret — module limit 2"),

        # ---- Inlined module limit patches (unconditional) ----
        (0x000C4C2C, "e883881a", "d503201f", "nop — inline mod limit 1"),      # FIX(0x000C4D2C)
        (0x000C6B90, "e183881a", "2a0803e1", "mov w1, #8 — inline mod limit 2"),   # FIX(0x000C6C90)
        (0x000C706C, "e9839b1a", "2a1b03e9", "mov w9, #1001 — inline mod limit 3"),# FIX(0x000C716C)
        (0x000C72C8, "e9839a1a", "2a1a03e9", "mov w8, #1000 — inline mod limit 4"),# FIX(0x000C73C8)

        # ---- Costume limits (unconditional) ----
        (0x000C6E0C, "83000054", "2a0003f8", "mov w0, #250 — costume limit 2"),  # FIX(0x000C6F0C)
        (0x00519BA0, "e9979f1a", "2a1f03e9", "mov w9, #255 — costume limit 3"),  # FIX(0x00519CA0 - 0x100 = 0x00519BA0)
        (0x00519BB0, "f713941a", "2a1403f7", "mov w7, #250 — costume limit 3 csel fix"), # FIX(0x00519CB0)

        # ---- Effect and open lyrics limits (unconditional) ----
        (0x0017B610, "3f4d0171", "7103fc3f", "hint #16383 — effect limit"),    # FIX(0x0017B710)
        (0x004C3A18, "7f5a02f1", "f10fa27f", "??? — lyric limit"),            # FIX(0x004C3B18)

        # ---- Saturation song patch (unconditional) ----
        (0x005D1A64, "1f3d0371", "710f951f", "??? — saturation 1"),          # FIX(0x005D1B64)
        (0x005D28B0, "3f3c0371", "710f903f", "??? — saturation 2"),          # FIX(0x005D29B0)

        # ---- Skip SEGA logos / intros (TaskAdvLogo) ----
        # exlaunch: if Config::skipAdv, trampoline at 0x00077AC0 returning 1.
        # Verified offset needed against your build (patches.hpp used it directly, no FIX).
        # (0x00077AC0, "00000000", "52800020d65f03c0", "mov w0, #1; ret — skip logos"),

        # ---- Converted from exlaunch Write calls (CUTS) ----
        (0x0076D8C4, "1883801a", "2a0003f8", "CodePatcher.Write(0x2A0003F8)"),
        (0x0020C5B0, "885600f0", "d65f03c0", "CodePatcher.Write(ARM64_RET)"),
        (0x0020C600, "885600f0", "d65f03c0", "CodePatcher.Write(ARM64_RET)"),
        (0x000C5C48, "4009f837", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000C5C4C, "e96e45f9", "aa1303e0", "CodePatcher.Write(0xAA1303E0)"),
        (0x000C5C50, "890200b4", "94000164", "CodePatcher.Write(0x94000164)"),
        (0x000C5C54, "8a6b45f9", "1400005d", "CodePatcher.Write(0x1400005D)"),
        (0x000C6404, "0017f837", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000C6408, "688d26d0", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C640C, "086d45f9", "97ffff75", "CodePatcher.Write(0x97FFFF75)"),
        (0x000C6410, "080300b4", "140000b5", "CodePatcher.Write(0x140000B5)"),
        (0x000C67A4, "090300b4", "2a0803e1", "CodePatcher.Write(0x2A0803E1)"),
        (0x000C67A8, "6a8d26d0", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C67AC, "4b6945f9", "94000439", "CodePatcher.Write(0x94000439)"),
        (0x000C67B0, "ab0200b4", "b9400308", "CodePatcher.Write(0xB9400308)"),
        (0x000C67B4, "6a8d26d0", "b40003a0", "CodePatcher.Write(0xB40003A0)"),
        (0x000C67B8, "4a412b91", "aa0003ea", "CodePatcher.Write(0xAA0003EA)"),
        (0x000C67BC, "6c2140b9", "14000018", "CodePatcher.Write(0x14000018)"),
        (0x000C6828, "6806f837", "2a0803e1", "CodePatcher.Write(0x2A0803E1)"),
        (0x000C682C, "090300b4", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C6830, "698d26d0", "94000418", "CodePatcher.Write(0x94000418)"),
        (0x000C6834, "2a6945f9", "b4005500", "CodePatcher.Write(0xB4005500)"),
        (0x000C6838, "aa0200b4", "aa0003e9", "CodePatcher.Write(0xAA0003E9)"),
        (0x000C683C, "698d26d0", "14000045", "CodePatcher.Write(0x14000045)"),
        (0x000C69B0, "a806f837", "2a0803e1", "CodePatcher.Write(0x2A0803E1)"),
        (0x000C69B4, "698d26d0", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C69B8, "296d45f9", "940003b6", "CodePatcher.Write(0x940003B6)"),
        (0x000C69BC, "090300b4", "b40048a0", "CodePatcher.Write(0xB40048A0)"),
        (0x000C69C0, "698d26d0", "aa0003e9", "CodePatcher.Write(0xAA0003E9)"),
        (0x000C69C4, "2a6945f9", "14000047", "CodePatcher.Write(0x14000047)"),
        (0x000C6BD4, "200af837", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000C6BD8, "688d26d0", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C6BDC, "086d45f9", "97fffd81", "CodePatcher.Write(0x97FFFD81)"),
        (0x000C6BE0, "080300b4", "aa0003fc", "CodePatcher.Write(0xAA0003FC)"),
        (0x000C6BE4, "688d26d0", "14000080", "CodePatcher.Write(0x14000080)"),
        (0x000C6E3C, "200af837", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000C6E40, "688d26d0", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C6E44, "086d45f9", "97fffce7", "CodePatcher.Write(0x97FFFCE7)"),
        (0x000C6E48, "080300b4", "aa0003fa", "CodePatcher.Write(0xAA0003FA)"),
        (0x000C6E4C, "688d26d0", "14000080", "CodePatcher.Write(0x14000080)"),
        (0x000C7094, "000340b9", "b9400301", "CodePatcher.Write(0xB9400301)"),
        (0x000C7098, "200af837", "f9402fe0", "CodePatcher.Write(0xF9402FE0)"),
        (0x000C709C, "688d26b0", "97fffc51", "CodePatcher.Write(0x97FFFC51)"),
        (0x000C70A0, "086d45f9", "aa0003fb", "CodePatcher.Write(0xAA0003FB)"),
        (0x000C70A4, "080300b4", "14000081", "CodePatcher.Write(0x14000081)"),
        (0x000C90CC, "0105f837", "37f80501", "CodePatcher.Write(0x37F80501)"),
        (0x000C90D0, "488d26f0", "a9bf7be2", "CodePatcher.Write(0xA9BF7BE2)"),
        (0x000C90D4, "086d45f9", "97fff9ef", "CodePatcher.Write(0x97FFF9EF)"),
        (0x000C90D8, "e80200b4", "aa0003e8", "CodePatcher.Write(0xAA0003E8)"),
        (0x000C90DC, "488d26f0", "a8c17be2", "CodePatcher.Write(0xA8C17BE2)"),
        (0x000C90E0, "096945f9", "b5000068", "CodePatcher.Write(0xB5000068)"),
        (0x000C90E4, "890200b4", "aa1f03e0", "CodePatcher.Write(0xAA1F03E0)"),
        (0x000C90E8, "4a8d26f0", "d65f03c0", "CodePatcher.Write(0xD65F03C0)"),
        (0x000C90EC, "4a412b91", "14000026", "CodePatcher.Write(0x14000026)"),
        (0x000C8F4C, "6106f837", "37f80661", "CodePatcher.Write(0x37F80661)"),
        (0x000C8F50, "688d2690", "a9bf7be2", "CodePatcher.Write(0xA9BF7BE2)"),
        (0x000C8F54, "086d45f9", "97fffa4f", "CodePatcher.Write(0x97FFFA4F)"),
        (0x000C8F58, "e80200b4", "aa0003f4", "CodePatcher.Write(0xAA0003F4)"),
        (0x000C8F5C, "688d2690", "a8c17be2", "CodePatcher.Write(0xA8C17BE2)"),
        (0x000C8F60, "096945f9", "b40005d4", "CodePatcher.Write(0xB40005D4)"),
        (0x000C8F64, "890200b4", "1400003a", "CodePatcher.Write(0x1400003A)"),
        (0x000C9018, "f4031faa", "aa1f03e0", "CodePatcher.Write(0xAA1F03E0)"),
        (0x000C901C, "0c000014", "14000012", "CodePatcher.Write(0x14000012)"),
        (0x000C91FC, "488d26f0", "97fff3f9", "CodePatcher.Write(0x97FFF3F9)"),
        (0x000C9200, "086d45f9", "aa0003f3", "CodePatcher.Write(0xAA0003F3)"),
        (0x000C9204, "e80200b4", "1400003d", "CodePatcher.Write(0x1400003D)"),
        (0x000CA728, "e86e45f9", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000CA72C, "880200b4", "f9456ee0", "CodePatcher.Write(0xF9456EE0)"),
        (0x000CA730, "e96945f9", "97ffeeac", "CodePatcher.Write(0x97FFEEAC)"),
        (0x000CA734, "490200b4", "aa0003f4", "CodePatcher.Write(0xAA0003F4)"),
        (0x000CA738, "e80310aa", "f94013ed", "CodePatcher.Write(0xF94013ED)"),
        (0x000CA73C, "2a2140b9", "1400004c", "CodePatcher.Write(0x1400004C)"),
        (0x000CAA70, "c86e45f9", "2a0003e1", "CodePatcher.Write(0x2A0003E1)"),
        (0x000CAA74, "880200b4", "f9456ec0", "CodePatcher.Write(0xF9456EC0)"),
        (0x000CAA78, "e96945f9", "97ffedda", "CodePatcher.Write(0x97FFEDDA)"),
        (0x000CAA7C, "490200b4", "aa0003f5", "CodePatcher.Write(0xAA0003F5)"),
        (0x000CAA80, "e80310aa", "f9400bed", "CodePatcher.Write(0xF9400BED)"),
        (0x000CAA84, "2a2140b9", "1400004c", "CodePatcher.Write(0x1400004C)"),
        (0x006124B4, "e88340f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x006155DC, "c97e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x00615788, "ea7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x006157A4, "ea7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x00619938, "8c7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x0061A0F8, "8a7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x0061A5F0, "8b7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x0061A6B8, "cb7e40f9", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x004C1274, "bfa20ff1", "310006bf", "CodePatcher.Write(0x310006BF)"),
        (0x004C1344, "bfa20ff1", "310006bf", "CodePatcher.Write(0x310006BF)"),
        (0x004C1264, "e8060036", "36000068", "CodePatcher.Write(0x36000068)"),
        (0x0085C974, "e83f0032", "12800008", "CodePatcher.Write(0x12800008)"),
        (0x0085C978, "08301079", "b9081808", "CodePatcher.Write(0xB9081808)"),
        (0x0085D4F8, "93321079", "b9081a93", "CodePatcher.Write(0xB9081A93)"),
        (0x0085D500, "8132d079", "b9481a81", "CodePatcher.Write(0xB9481A81)"),
        (0x0085D5F4, "0830d079", "b9481808", "CodePatcher.Write(0xB9481808)"),
        (0x0085D618, "6132d079", "b9481a61", "CodePatcher.Write(0xB9481A61)"),
        (0x0085D91C, "6132d079", "b9481a61", "CodePatcher.Write(0xB9481A61)"),
        (0x001E1188, "ff0308eb", "14000047", "CodePatcher.Write(0x14000047)"),
        (0x001E292C, "6101f837", "b9000be2", "CodePatcher.Write(0xB9000BE2)"),
        (0x001E2930, "69ba41b9", "aa1303e0", "CodePatcher.Write(0xAA1303E0)"),
        (0x001E2934, "e85700b0", "97ffff03", "CodePatcher.Write(0x97FFFF03)"),
        (0x001E2938, "089143f9", "b9400be2", "CodePatcher.Write(0xB9400BE2)"),
        (0x001E293C, "3f01016b", "aa0003e8", "CodePatcher.Write(0xAA0003E8)"),
        (0x001E2940, "0b010054", "14000008", "CodePatcher.Write(0x14000008)"),
        (0x00171184, "09019a52", "aa1303e0", "CodePatcher.Write(0xAA1303E0)"),
        (0x00171188, "4900a072", "94000b8a", "CodePatcher.Write(0x94000B8A)"),
        (0x0017118C, "6a5b00d0", "b841b328", "CodePatcher.Write(0xB841B328)"),
        (0x00171190, "696a6938", "1e220100", "CodePatcher.Write(0x1E220100)"),
        (0x00171194, "4a8542f9", "7100051f", "CodePatcher.Write(0x7100051F)"),
        (0x00171198, "49010039", "14000035", "CodePatcher.Write(0x14000035)"),
        (0x001AD3DC, "88010034", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x001AF8DC, "48060034", "d503201f", "CodePatcher.Write(0xD503201F)"),
        (0x00601EB0, "6d3640f9", "14000028", "CodePatcher.Write(0x14000028)"),
        (0x001B48A0, "c8030054", "d503201f", "CodePatcher.Write(0xd503201f)"),

        # ---- Additional converted CUTs (PV loop, sprite limits, shadows) ----
        (0x004C1190, "f5031faa", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_PV_LOOP_INIT = FIX(0x4C1290)
        (0x004C1270, "b5060091", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_PV_LOOP_NEXT_1 = FIX(0x4C1370)
        (0x004C1340, "b5060091", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_PV_LOOP_NEXT_2 = FIX(0x4C1440)
        (0x005D1BE0, "44000014", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_NOP_2 = FIX(0x5D1CE0)
        (0x005D2A38, "082f0034", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_NOP_3 = FIX(0x5D2B38)
        (0x005D1BEC, "2a020034", "d503201f", "CodePatcher.Write(0xD503201F)"),     # ADDR_NOP_4 = FIX(0x5D1CEC)
        (0x001DD128, "012d0012", "12003901", "CodePatcher.Write(0x12003901)"),     # ADDR_SPRITE_MASK_1 = FIX(0x1DD228)
        (0x00618D6C, "a86e1053", "53107aa8", "CodePatcher.Write(0x53107AA8)"),     # ADDR_SPRITE_MASK_2
        (0x0061C3A8, "296c1053", "53107829", "CodePatcher.Write(0x53107829)"),     # ADDR_SPRITE_MASK_3
        (0x0061C43C, "296c1053", "53107829", "CodePatcher.Write(0x53107829)"),     # ADDR_SPRITE_MASK_4
        (0x0061C508, "296c1053", "53107829", "CodePatcher.Write(0x53107829)"),     # ADDR_SPRITE_MASK_5
        (0x00618DF8, "090d0412", "12010109", "CodePatcher.Write(0x12010109)"),     # ADDR_SPRITE_FLAG_AND
        (0x00618DFC, "ea030432", "320103ea", "CodePatcher.Write(0x320103EA)"),     # ADDR_SPRITE_FLAG_CMP1
        (0x00618F90, "ea030432", "320103ea", "CodePatcher.Write(0x320103EA)"),     # ADDR_SPRITE_FLAG_CMP2
        (0x0061DDD4, "16010432", "32010116", "CodePatcher.Write(0x32010116)"),     # ADDR_SPRITE_FLAG_5
        (0x00614E20, "4a010432", "3201014a", "CodePatcher.Write(0x3201014A)"),     # ADDR_SPRITE_FLAG_6
        (0x006150D0, "297c1c53", "531f7c29", "CodePatcher.Write(0x531F7C29)"),     # ADDR_SPRITE_FINAL_CHECK
        (0x0061C404, "297c1c53", "531f7c29", "CodePatcher.Write(0x531F7C29)"),     # ADDR_SPRITE_GETTER_1
        (0x0061C47C, "2a7c1c53", "531f7c2a", "CodePatcher.Write(0x531F7C2A)"),     # ADDR_SPRITE_GETTER_2

        # ---- Remaining unconditional CUTs (verified against NSO binary) ----
        (0x004CA9A0, "e0c32391", "1400006a", "noMV patch 1: ldr x0, [sp, #0x8f0] → b #0x6a"),   # was 0x004CA9A0
        (0x004CAB54, "21100054", "14000081", "noMV patch 2: cbnz w1 → b #0x81"),             # was 0x004CAB54
        (0x004A1134, "e8070032", "320007e8", "str w8, [x28] → mov w8, #8 (mag filter)"),     # was 0x004A1134

        # NOTE: DebugMode toggle patches (ADDR_PATCH_GUI_DRAW, ADDR_PATCH_SHOW_SPRITES_1/2,
        # ADDR_PATCH_NOP_1/2) are NOT here as CUTs — they toggle at runtime based on
        # debug mode input (L+R+Plus) and write different values per state.
        # They live in main.config.tsv as config-gated rows where applicable.
    ],
}

OBS = {
    build_id: [
        # ---- Observation gates for exlaunch hooks that qualify (entry / after-BL / scratch-dead) ----
        # These fire the host observation callback when hit.  The original instruction still executes;
        # use them for notification / telemetry.  Hooks that must modify registers or control flow
        # (trampolines, inline hooks that rewrite X[N]) need host-side trampoline infrastructure
        # and are listed below as "NEEDS HOOK" entries instead.
        #
        # OBS numbers match dm.h OBS_DIVA_* enum values (22..30).

        # GetSpriteIdInlineHook (Mode2DNoMV.cpp:556): after bl at 0x1948AC, reads X[0] result.
        # Replacement: exlaunch sets ctx->X[0] to fallback sprite addr when native lookup fails.
        (0x001948B0, 22, "b9400013", "OBS_DIVA_GET_SPRITE_ID — ldr w19, [x0] result read (after BL)"),

        # RandomInitHook (FTRestoration.cpp:255): trampoline at 0x1F4150.
        # Replacement: calls Orig, then zeroes ADP and applies config overrides.
        (0x001F4150, 23, "a9be4ff4", "OBS_DIVA_RANDOM_INIT — stp x28, x29, [sp] (scratch-dead)"),

        # DwScrollableGetBoundingBoxHook (DebugMode.cpp:263): trampoline at 0x341BB0.
        # Replacement: modifies BoundingBox return based on debug mode.
        (0x00341BB0, 24, "bd404663", "OBS_DIVA_BOUNDING_BOX — stp x8, x9, [sp] (scratch-dead)"),

        # Leaf_Physics_Fix (FTRestoration.cpp:410): trampoline at 0x391D50.
        # Replacement: patches vtable, sanitizes particle NaN values.
        (0x00391D50, 25, "d10403ff", "OBS_DIVA_LEAF_PHYSICS — ldr x8, [x24] (after BL at 0x391D4C)"),

        # TaskMovie_OpenFile_Hook (Mode2DNoMV.cpp:185): trampoline at 0x439FD0.
        # Replacement: returns 0 if movie should be blocked.
        (0x00439FD0, 26, "d10143ff", "OBS_DIVA_TASK_MOVIE_OPEN — ldr x8, [x0] (scratch-dead)"),

        # ReduceTextureFixHook (FTRestoration.cpp:575): trampoline at 0x4A5660.
        # Replacement: caps render_ptr at 3.
        (0x004A5660, 27, "d10303ff", "OBS_DIVA_REDUCE_TEXTURE — ldr x8, [x0] (scratch-dead)"),

        # PvLoaderParseLoop2 (PvLoader.cpp:201): inline hook at 0x4C1260.
        # Replacement: sets ctx->X[21] = pvID or 0xFFFFFFFF.
        (0x004C1260, 28, "394023e8", "OBS_DIVA_PV_PARSE_LOOP2 — ldr w8, [x23] (after BL)"),

        # PvLoaderParseLoop1 (PvLoader.cpp:190): inline hook at 0x4C1338.
        # Replacement: sets ctx->X[21] = pvID or 0xFFFFFFFF.
        (0x004C1338, 29, "910023e0", "OBS_DIVA_PV_PARSE_LOOP1 — add x0, x0, x0 (scratch-dead)"),

        # SSAA_ENABLE (FTRestoration.cpp:68): trampoline at 0x4F1470.
        # Replacement: calls Orig with ssaa=1 if Config::ssaaMode == "on".
        (0x004F1470, 30, "d10243ff", "OBS_DIVA_SSAA_ENABLE — ldr x8, [x0] (scratch-dead)"),

        # ---- Additional observation gates for remaining exlaunch hooks ----
        # All verified against the NSO binary.  Original instruction executes after gate fires.
        (0x000CAC90, 72, "7100043f", "OBS_DIVA_GET_SAVED_SCORE_DIFFICULTY — cmp w1, #1 (scratch-dead)"),
        (0x0010C1E0, 73, "d103c3ff", "OBS_DIVA_PVSEL_PS4_INIT — sub sp, sp, #0xf0 (function entry)"),
        (0x0010DEE0, 74, "d10583ff", "OBS_DIVA_PVSEL_PS4_CREATE_SORTED — sub sp, sp, #0x160 (function entry)"),
        (0x0010E9C0, 75, "d10543ff", "OBS_DIVA_PVSEL_PS4_CTRL — sub sp, sp, #0x150 (function entry)"),
        (0x00118050, 76, "a9bb67fa", "OBS_DIVA_PVSEL_PS4_DISP — stp x26, x25, [sp] (function entry)"),
        # PVSEL_PS4_DEST at 0x12C5D8 is tbz w8,#0 (PC-relative branch) — cannot be OBS gate.
        # exlaunch uses it as TRAMPOLINE; skipped as OBS.
        (0x00154D70, 78, "d10183ff", "OBS_DIVA_STAGE_RESULT_PS4_INIT — sub sp, sp, #0x60 (function entry)"),
        (0x001553F0, 79, "6dba23e9", "OBS_DIVA_STAGE_RESULT_PS4_CTRL — stp d9,d8,[sp] (function entry)"),
        (0x00158080, 80, "d10683ff", "OBS_DIVA_PUT_SCORE_WINDOW_IN — sub sp, sp, #0x1a0 (function entry)"),
        (0x00158240, 81, "d10683ff", "OBS_DIVA_PUT_WIN_COUNT — sub sp, sp, #0x1a0 (after BL)"),
        (0x001587D0, 82, "d10683ff", "OBS_DIVA_PUT_WIN_LOOP — sub sp, sp, #0x1a0 (function entry)"),
        (0x001589E0, 83, "d10683ff", "OBS_DIVA_PUT_WIN_OUT — sub sp, sp, #0x1a0 (after BL)"),
        (0x001599E0, 84, "f81e0ff3", "OBS_DIVA_STAGE_RESULT_PS4_DEST — str x19,[sp] (function entry)"),
        (0x00159CE0, 85, "d10403ff", "OBS_DIVA_STAGE_RESULT_PS4_DISP — sub sp, sp, #0x100 (function entry)"),
        (0x0015A0A8, 86, "4ea81d00", "OBS_DIVA_WRITE_DISP_AET_SCENE_ID — mov v0,v8 (scratch-dead)"),
        (0x001722D0, 85, "d102c3ff", "OBS_DIVA_PV_GAME_RESET — sub sp, sp, #0xb0 (after BL)"),
        (0x00173880, 86, "f81b0ff9", "OBS_DIVA_UPDATE_LIFE — str x25,[sp] (function entry)"),
        (0x00173FB0, 87, "6dbd23e9", "OBS_DIVA_CALCULATE_PERCENTAGE — stp d9,d8,[sp] (scratch-dead)"),
        (0x00175F00, 88, "d105c3ff", "OBS_DIVA_PARSE_TARGETS — sub sp, sp, #0x170 (function entry)"),
        (0x00181460, 89, "f81c0ff7", "OBS_DIVA_LOAD_DSC_CTRL — str x23,[sp] (function entry)"),
        (0x0018BB00, 90, "f81d0ff5", "OBS_DIVA_EXECUTE_MODE_SELECT — str x21,[sp] (function entry)"),
        (0x0019BD60, 91, "d10103ff", "OBS_DIVA_PV_GAME_LOADER_FINISH — sub sp, sp, #0x40 (function entry)"),
        (0x001AD6F0, 92, "f81d0ff5", "OBS_DIVA_PV_GAME_ARCADE_RESET — str x21,[sp] (function entry)"),
        (0x001AEF20, 93, "d10603ff", "OBS_DIVA_GET_HIT_STATE — sub sp, sp, #0x180 (function entry)"),
        # GetHitStatePlaySEHook at 0x1AF5A0: scratch-dead fails (mov v0,v9 reads x9), not OBS-eligible.
        # Left unhandled as an OBS gate.
        (0x001B06F0, 95, "d10303ff", "OBS_DIVA_UPDATE_TARGETS — sub sp, sp, #0xc0 (after BL)"),
        (0x001B11F0, 96, "fc190fe8", "OBS_DIVA_GET_HIT_STATE_INTERNAL — str d8,[sp] (function entry)"),
        (0x001B2BE0, 97, "39400008", "OBS_DIVA_UPDATE_KISEKI — ldrb w8,[x0] (function entry)"),
        # CreateTargetAetLayersHook at 0x1B3150 is a TRAMP hook per exlaunch — not OBS.
        (0x001B4A70, 98, "3951a008", "OBS_DIVA_DRAW_KISEKI — ldrb w8,[x0,#0x468] (function entry)"),
        (0x001B4F70, 99, "a9be4ff4", "OBS_DIVA_DRAW_ARCADE_GAME — stp x20,x19,[sp] (function entry)"),
        (0x001B7750, 100, "a9be4ff4", "OBS_DIVA_GET_PV_KEY_STATE_DOWN — stp x20,x19,[sp] (function entry)"),
        (0x001B77A0, 101, "a9be4ff4", "OBS_DIVA_GET_PV_KEY_STATE_TAPPED — stp x20,x19,[sp] (function entry)"),
        (0x001FC910, 102, "f81c0ff7", "OBS_DIVA_IS_BUTTON_TAPPED — str x23,[sp] (scratch-dead)"),
        (0x001FCE70, 103, "f81c0ff7", "OBS_DIVA_IS_BUTTON_DOWN — str x23,[sp] (scratch-dead)"),
        (0x004BE140, 104, "d10303ff", "OBS_DIVA_INIT_MDATA_PV_DB_PATHS — sub sp, sp, #0xc0 (function entry)"),
        (0x004C2D30, 105, "6db923e9", "OBS_DIVA_TASK_PV_DB_PARSE_ENTRY — stp d9,d8,[sp] (function entry)"),
        (0x00604D90, 106, "a9bb67fa", "OBS_DIVA_POLL_INPUT_REPEAT_DOUBLE — stp x26,x25,[sp] (function entry)"),
        (0x0064C910, 107, "a9bf7bfd", "OBS_DIVA_TASK_PV_GAME_INIT — stp x29,x30,[sp] (function entry)"),
        (0x0064C940, 108, "a9bf7bfd", "OBS_DIVA_TASK_PV_GAME_CTRL — stp x29,x30,[sp] (function entry)"),
        (0x0064C960, 109, "f81e0ff3", "OBS_DIVA_TASK_PV_GAME_DEST — str x19,[sp] (function entry)"),
        (0x001C07E0, 110, "fc1b0fec", "OBS_DIVA_UPDATE_GAUGE_FRAME — str d12,[sp,#-0x60]! (function entry)"),
        (0x001B98E0, 111, "52a86148", "OBS_DIVA_FRAME_HEIGHT_W8 — mov w8,#0x430a0000 (scratch-dead)"),
        (0x001B98D8, 112, "f2e86149", "OBS_DIVA_FRAME_HEIGHT_X9 — movk x9,#0x430a,lsl#48 (scratch-dead)"),
        (0x00882C10, 113, "a9bd57f6", "OBS_DIVA_PVSEL_SWITCH_INIT — stp x22,x21,[sp] (function entry)"),
        (0x00883AF0, 114, "d10583ff", "OBS_DIVA_PVSEL_SWITCH_CTRL — sub sp, sp, #0x160 (function entry)"),
        (0x008860F0, 115, "f81d0ff5", "OBS_DIVA_PVSEL_SWITCH_DEST — str x21,[sp] (function entry)"),
        (0x00886340, 116, "a9bb67fa", "OBS_DIVA_PVSEL_SWITCH_DISP — stp x26,x25,[sp] (function entry)"),
        (0x008882E0, 117, "d10543ff", "OBS_DIVA_PVSEL_SWITCH_CREATE_SORTED — sub sp, sp, #0x150 (function entry)"),
        (0x006DB7E0, 119, "5280a320", "OBS_DIVA_CSTAGE_RESULT_AET_GET_SCENE_ID — mov w0,#0x519 (function entry)"),
        (0x006DC080, 120, "5280a320", "OBS_DIVA_CSTAGE_RESULT_AET_GET_SCENE_ID_2 — mov w0,#0x519 (function entry)"),
        (0x0071B120, 121, "f81d0ff5", "OBS_DIVA_CAET_CONTROLLER_SET_LAYER — str x21,[sp] (function entry)"),
        (0x00719C30, 122, "12800004", "OBS_DIVA_CSTAGE_RESULT_AET_SET_LAYER — mov w4,#-1 (function entry)"),
        (0x0071A1F0, 123, "d10183ff", "OBS_DIVA_CAET_CONTROLLER_GET_LAYOUT — sub sp, sp, #0x60 (function entry)"),
        (0x006DD1C0, 124, "d10143ff", "OBS_DIVA_STAGE_RESULT_SWITCH_INIT — sub sp, sp, #0x50 (function entry)"),
        (0x006DD420, 125, "d101c3ff", "OBS_DIVA_STAGE_RESULT_SWITCH_WAIT_LOAD — sub sp, sp, #0x70 (function entry)"),
        (0x006DDAC0, 126, "f81e0ff3", "OBS_DIVA_STAGE_RESULT_SWITCH_DEST — str x19,[sp] (function entry)"),
        (0x006D2090, 127, "f81d0ff5", "OBS_DIVA_STAGE_RESULT_SWITCH_DETAIL_INIT — str x21,[sp] (after BL)"),
        (0x006D35F0, 128, "6dba33ed", "OBS_DIVA_STAGE_RESULT_SWITCH_DETAIL_DISP — stp d13,d12,[sp] (function entry)"),
        # PVSEL_SWITCH hooks (0x882C10..0x8882E0) above are OBS gates 113-117.
        # The same offsets are TRAMP hooks in exlaunch (CUR_HOOKS.txt); host registers them as OBS per dm.h.
        # All remaining exlaunch hooks are registered as TRAMP gates (numbers 31+) below.
    ],
}

TRAMP = {
    build_id: [
        # Trampoline gates for exlaunch hooks that must modify registers or control flow.
        # Original words verified against the NSO binary (build 179265bd41f7781dac979e7770201124).
        # Tramp numbers match gate_tramp_set() registrations in hle_diva.c (31+).
        #
        # (offset, tramp_number, orig_word_hex, skip, reason)
        # skip=True: hook returns early (exlaunch `return` instead of Orig()) — skip the original instruction
        # 0x00077AC0 TaskAdvLogo — fc1a0fec = str d12, [sp, #-0x60]! (SP writeback)
        (0x00077AC0, 31, "fc1a0fec", True, "TaskAdvLogo trampoline: return 1 when Config::skipAdv, else call Orig"),
        # 0x004CADF8 ClearMovieSurfaceFrontInlineHook — a9402013 = ldp x19, x8, [x0]
        (0x004CADF8, 32, "a9402013", False, "ClearMovieSurfaceFront: zero \"FRONT\" str when Config::backMV"),
        # 0x00190140 SkipDisp2dInlineHook — tbnz w8,#0 (PC-relative branch, not relocatable by site_tramp).
        #   Handled as a config-gated CUT in main.config.tsv instead.
        # 0x0014DEB0 CustomizeSetLightingInfoHook — fc1c0fea = str d10, [sp, #-0x40]!
        (0x0014DEB0, 33, "fc1c0fea", False, "CustomizeSetLightingInfo hook"),
        # 0x00181580 ParseDscHook — a9ba6ffc = stp x28, x27, [sp, #-0x60]!
        (0x00181580, 34, "a9ba6ffc", False, "ParseDsc hook"),
        # 0x001900DC EarlyCapturePvIdHook — f94002a9 = ldr x9, [x21]
        (0x001900DC, 35, "f94002a9", False, "EarlyCapturePvId inline hook"),
        # 0x00190140 SkipDisp2dInlineHook — tbnz w8, #0 (PC-relative branch, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x001911B4 SkipMotionAndChrmotHook — eb08033f = cmp x25, x8
        (0x001911B4, 37, "eb08033f", False, "SkipMotionAndChrmot inline hook"),
        # 0x001917E8 SkipPvExpressionHook — 39476109 = ldrb w9, [x8, #0x1d8]
        (0x001917E8, 38, "39476109", False, "SkipPvExpression inline hook"),
        # 0x001935A0 SkipChreffInlineHook — eb150149 = subs x9, x10, x21
        (0x001935A0, 39, "eb150149", False, "SkipChreff inline hook"),
        # 0x00193FFC PreAllocEmptyFieldsInlineHook — a9592748 = ldp x8, x9, [x26, #0x190]
        (0x00193FFC, 40, "a9592748", False, "PreAllocEmptyFields inline hook"),
        # 0x00194800 ForceSprSetBackInlineHook — 39466328 = ldrb w8, [x25, #0x198]
        (0x00194800, 41, "39466328", False, "ForceSprSetBack inline hook"),
        # 0x001FD450 FrameUpdateHook — adrp x8, #0xcdf000 (PC-relative, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x001FF5D0 CommandLineArgsHook — fc190fe8 = str d8, [sp, #-0x70]!
        (0x001FF5D0, 43, "fc190fe8", False, "CommandLineArgs hook"),
        # 0x00201010 EngineUpdateTickHook — f9000dec = str x12, [x15, #0x18]
        (0x00201010, 44, "f9000dec", False, "EngineUpdateTick hook"),
        # 0x0020C330 GetShadowOpacIntens — adrp x8, #0xcdf000 (PC-relative, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x0020C3B0 GetReflectionQuality — adrp x8, #0xcdf000 (PC-relative, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x0043A310 TaskMovie_IsReady_Hook — 3942e408 = ldrb w8, [x0, #0xb9]
        (0x0043A310, 47, "3942e408", False, "TaskMovieIsReady hook"),
        # 0x0049CEE0 RenderSetSaturationHook — b9528c08 = ldr w8, [x0, #0x128c]
        (0x0049CEE0, 48, "b9528c08", False, "RenderSetSaturation hook"),
        # 0x004A0120 SetToneMapMethodHook — 320003e8 = mov w8, #1
        (0x004A0120, 49, "320003e8", False, "SetToneMapMethod hook"),
        # 0x004A0130 SetExposureHook — 320003e8 = mov w8, #1
        (0x004A0130, 50, "320003e8", False, "SetExposure hook"),
        # 0x004A0150 SetGammaHook — 320003e8 = mov w8, #1
        (0x004A0150, 51, "320003e8", False, "SetGamma hook"),
        # 0x004A0190 RenderSetSatCoefHook — b9528c08 = ldr w8, [x0, #0x128c]
        (0x004A0190, 52, "b9528c08", False, "RenderSetSatCoef hook"),
        # 0x004A0430 SetMagFilterHook — 320003e8 = mov w8, #1
        (0x004A0430, 53, "320003e8", False, "SetMagFilter hook"),
        # 0x004A0B50 GetSaturateCoefHook — b957f408 = ldr w8, [x0, #0x17f4]
        (0x004A0B50, 54, "b957f408", False, "GetSaturateCoef hook"),
        # 0x004A6CC0 ToneMapHook — d10743ff = sub sp, sp, #0x1d0
        (0x004A6CC0, 55, "d10743ff", False, "ToneMap hook"),
        # 0x004A8570 MLAA_Pass2_Fix — d10143ff = sub sp, sp, #0x50
        (0x004A8570, 56, "d10143ff", False, "MLAA Pass2 fix"),
        # 0x004A8680 MLAA_Pass3_Fix — d10183ff = sub sp, sp, #0x60
        (0x004A8680, 57, "d10183ff", False, "MLAA Pass3 fix"),
        # 0x004AE870 GetPseModifierHook — f94d2008 = ldr x8, [x0, #0x1a40]
        (0x004AE870, 58, "f94d2008", False, "GetPseModifier hook"),
        # 0x004AE880 SetPseModifierHook — f94d2008 = ldr x8, [x0, #0x1a40]
        (0x004AE880, 59, "f94d2008", False, "SetPseModifier hook"),
        # 0x004C1280 PvLoaderParseStart — eb18039f = cmp x28, x24
        (0x004C1280, 60, "eb18039f", False, "PvLoaderParseStart hook"),
        # 0x004C1290 PvLoaderLoopInit — 1a9f07e9 = cset w9, ne
        (0x004C1290, 61, "1a9f07e9", False, "PvLoaderLoopInit hook"),
        # 0x0062D970 StageColiLoadHook — adrp x8, #0xce1000 (PC-relative, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x000C61E0 FindOrCreateScoreHook — f81e0ff3 = str x19, [sp, #-0x20]!
        (0x000C61E0, 63, "f81e0ff3", False, "FindOrCreateScore trampoline"),
        # 0x000C7890 FindScoreHook — tbnz w1, #0x1f (PC-relative branch, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x000C8850 FindModuleHook — 8b21c408 = add x8, x0, w1, sxtw #1
        (0x000C8850, 65, "8b21c408", False, "FindModule trampoline"),
        # 0x000C8C30 FindModule2Hook — 8b21c408 = add x8, x0, w1, sxtw #1
        (0x000C8C30, 66, "8b21c408", False, "FindModule2 trampoline"),
        # 0x000C8870 FindCstmItemHook — 8b21c008 = add x8, x0, w1, sxtw
        (0x000C8870, 67, "8b21c008", False, "FindCstmItem trampoline"),
        # 0x000C8C50 FindCstmItemGalleryHook — 8b21c008 = add x8, x0, w1, sxtw
        (0x000C8C50, 68, "8b21c008", False, "FindCstmItemGallery trampoline"),
        # 0x000C7890 FindScoreHook — tbnz w1, #0x1f (PC-relative branch, now handled by site_tramp_nr).
        (0x000C7890, 99, "37f80541", False, "FindScore trampoline"),
        # 0x000C5950 InitBoot2Hook — 321707e9 = mov w9, #0x600
        (0x000C5950, 69, "321707e9", False, "InitBoot2 trampoline"),
        # 0x000C6440 SyncManagerHook — adrp x10, #0x4d274000 (PC-relative, not relocatable by site_tramp).
        #   Left unhandled as a TRAMP gate.
        # 0x000C9820 SaveManagerHook — 9100e3ea = add x10, sp, #0x38
        (0x000C9820, 71, "9100e3ea", False, "SaveManager trampoline"),

        # ---- Additional TRAMP gates for nc_f exlaunch hooks (verified original words) ----
        # CreateTargetAetLayersHook — exlaunch TRAMPOLINE at 0x1b3150, d10383ff
        # Note: not in OBS table (removed — same offset conflict). Registered as TRAMP gate 119.
        (0x001B3150, 119, "d10383ff", False, "CreateTargetAetLayers trampoline"),
        # All other nc_f TRAMPOLINE hooks at these offsets are already covered by OBS gates
        # (same offsets). Each NSO offset can only have one gate type — OBS wins for those.
        # Remaining TRAMP hooks with concrete offsets from the NSO binary (verified via capstone
        # against build 179265bd41f7781dac979e7770201124):

        # TheaterRestoration.cpp TRAMP hooks (5)
        (0x00801DD0, 120, "d10143ff", False, "TheaterInitHook trampoline"),
        (0x00801AD0, 121, "d10203ff", False, "TheaterPlayMovieHook trampoline"),
        (0x008020B0, 122, "a9be4ff4", False, "TheaterStopAetHook trampoline"),
        (0x00802280, 123, "a9be4ff4", False, "TheaterDtorHook1 trampoline"),
        (0x008022D0, 124, "a9be4ff4", False, "TheaterDtorHook2 trampoline"),

        # freecam.cpp TRAMP hooks (4) — FIX(addr) = addr - 0x100
        (0x0025F250, 125, "f8404008", False, "freecam SetCameraDataHook trampoline"),
        (0x001F9110, 126, "f9402fe8", False, "freecam GetButtonPressedHook trampoline"),
        (0x0025F610, 127, "d10483ff", False, "freecam UpdateCameraHook trampoline"),
        (0x002014D0, 128, "d10143ff", False, "freecam RenderWhilePausedHook trampoline"),

        # StrArray.cpp TRAMP hooks (2) — FIX(addr) = addr - 0x100
        (0x0015D110, 129, "d10103ff", False, "StrArray LoadStrArrayHook trampoline"),
        (0x0015D380, 130, "2a0003e8", False, "StrArray GetStrHook trampoline"),

        # MemoryHooks.cpp inline hooks (4)
        (0x0066B2DC, 131, "aa1f03e8", False, "MemoryHooks TexDbPreSortInlineHook"),
        (0x0066B510, 132, "93407d00", False, "MemoryHooks TexDbPostSortInlineHook"),
        (0x00458570, 133, "f94033ea", False, "MemoryHooks ObjDbPreSortInlineHook"),
        (0x00458880, 134, "f90037e0", False, "MemoryHooks ObjDbPostSortInlineHook"),

        # SpriteLoader.cpp inline hook (1) — FIX(addr) = addr - 0x100
        (0x0061C91C, 135, "b9001109", False, "SpriteLoader SpriteFixupHook"),

        # StrArray.cpp inline hooks (6) — FIX(addr) = addr - 0x100.
        # CallModuleNameHook (0x3C3FD8), CallCustomizeNameHook (0x3BBDD0),
        # CallBtnSeNameHook (0x3B5B1C), CallChainSlideNameHook (0x3B76FC),
        # CallSliderTouchSeNameHook (0x3D9BD4), CallSlideSeNameHook (0x3DB664)
        # are all `bl` branches — not relocatable by site_tramp, so they cannot
        # be TRAMP gates. Left as "NEEDS HOOK" comments; handled separately.

        # TheaterRestoration.cpp inline patches (8) — register-modifying inline
        # hooks (modify ctx->X[N]), registered as TRAMP gates. Verified original
        # words against the NSO binary via capstone.
        # TheaterMenuCountPatch — writes X[8] = 5
        (0x008015B0, 142, "f90013e8", False, "TheaterMenuCountPatch inline trampoline"),
        # TheaterMenuInitialIndexPatch — writes cur_idx to [sp+0x28]
        (0x008015DC, 143, "a9402528", False, "TheaterMenuInitialIndexPatch inline trampoline"),
        # TheaterLoop1ButtonPtrPatch — writes X[21] = button ptr
        (0x008017B0, 144, "aa1403e0", False, "TheaterLoop1ButtonPtrPatch inline trampoline"),
        # TheaterLoop2ButtonPtrPatch — writes X[19] = button ptr
        (0x008018B4, 145, "aa1403e0", False, "TheaterLoop2ButtonPtrPatch inline trampoline"),
        # TheaterSaveSelectedIndexPatch at 0x00801298: adrp x0 (PC-relative),
        # not relocatable by site_tramp — left as NEEDS HOOK.
        # TheaterPictureIdPatch1 — writes W[1] = picture_id
        (0x00801394, 147, "d100e3a8", False, "TheaterPictureIdPatch1 inline trampoline"),
        # TheaterPictureIdPatch2 — writes W[1] = picture_id
        (0x00801414, 148, "d100e3a8", False, "TheaterPictureIdPatch2 inline trampoline"),
        # TheaterPictureIdPatch3 — writes W[1] = picture_id
        (0x008014A4, 149, "d100e3a8", False, "TheaterPictureIdPatch3 inline trampoline"),

        # Remaining hooks with concrete offsets from exlaunch source (verified via capstone against NSO binary):
        # PluginHelpUi.cpp (2) — FIX(addr) = addr - 0x100
        (0x00815150, 150, "d103c3ff", False, "MainMenuInitHook trampoline"),
        (0x008161B0, 151, "a9bb67fa", False, "MainMenuDestHook trampoline"),
        # SprBackFix.hpp (2) — FIX(addr) = addr - 0x100
        # ReadScreenModeInlineHook at 0x00618FF0: f94022e9 = ldr x9, [sp]
        # DrawSpriteBackFixHook at 0x00612310: b0003668 = cbz x0 — handled by site_tramp_nr
        (0x00618FF0, 152, "f94022e9", False, "ReadScreenModeInlineHook trampoline"),
        (0x00612310, 153, "b0003668", False, "DrawSpriteBackFixHook trampoline (nr: cbz)"),
        # DatabaseLoader.cpp (2) — FIX(addr) = addr - 0x100
        (0x001F4480, 154, "d10203ff", False, "ResolveFilePathObserverHook trampoline"),
        (0x0041AEC0, 155, "d10283ff", False, "InitMdataMgrHook trampoline"),
        # MemoryHooks.cpp (7) — already registered in hle_diva.c at IDs 78-84
        (0x0041CBC0, 78, "a9bc5ff8", False, "EngineHeapDispatchHook trampoline"),
        (0x0004BD80, 79, "a9be4ff4", False, "SegaAllocRouterHook trampoline"),
        (0x0004C650, 80, "f81c0ff7", False, "SegaVTableAllocHook trampoline"),
        (0x0004C2F0, 81, "f81d0ff5", False, "SegaMemalignHook trampoline"),
        (0x0004BE40, 82, "a9be4ff4", False, "SegaCallocRouterHook trampoline"),
        (0x0004BEC0, 83, "f81d0ff5", False, "SegaReallocRouterHook trampoline"),
        # SegaFreeHook at 0x0004BDF0: cbz x0 — now handled by site_tramp_nr
        (0x0004BDF0, 84, "b40001a0", False, "SegaFreeHook trampoline (nr: cbz)"),
        # Sound.cpp (1) — already registered in hle_diva.c at ID 91
        (0x00608A20, 91, "d101c3ff", False, "SoundCueLoadHook trampoline"),
        # SpriteDrawLimitPatch.cpp (3) — trampoline hooks (inline ones already in CUTS)
        (0x006154C0, 156, "a9be4ff4", False, "SprArgsSetVertexArray trampoline"),
        (0x00617E40, 157, "d10643ff", False, "SpriteManagerClear trampoline"),
        # SprArgsReserveVertexArray at 0x00615520: adrp x8 — handled by site_tramp_nr
        (0x00615520, 158, "f05eeb68", False, "SprArgsReserveVertexArray trampoline (nr: adrp)"),
        # Remaining verified TRAMP entries (IDs 159+):
        # Dimming.cpp — TaskPvGameDisp_Hook
        (0x0064C9B0, 159, "17ed5e94", False, "TaskPvGameDisp_Hook trampoline"),
        # MemoryHooks.cpp — BlockThumbnailLoad/Finish, DisableSongThumbnails
        (0x00611FA0, 160, "a9bd57f6", False, "BlockThumbnailLoadHook trampoline"),
        (0x006120A0, 161, "a9bf7bfd", False, "BlockThumbnailFinishHook trampoline"),
        (0x005D26A0, 162, "d10403ff", False, "DisableSongThumbnailsHook trampoline"),
        # FTRestoration.cpp — SetFxaaParamsHook
        (0x004A0550, 163, "b9400028", False, "SetFxaaParamsHook trampoline"),
        # FTRestoration.cpp — GetReflectionQuality, GetShadowOpacIntens
        (0x0020C3B0, 164, "f0005688", False, "GetReflectionQuality trampoline"),
        (0x0020C330, 165, "f0005688", False, "GetShadowOpacIntens trampoline"),
        # FTRestoration.cpp — Leaf_Init_Hook, Leaf_Render_Fix
        (0x003919E0, 166, "6db833ed", False, "Leaf_Init_Hook trampoline"),
        (0x00390FC0, 167, "d10483ff", False, "Leaf_Render_Fix trampoline"),
        # Mode2DNoMV.cpp — FrameUpdateHook
        (0x001FD450, 168, "d0005708", False, "FrameUpdateHook trampoline"),
        # Mode2DNoMV.cpp — SkipDisp2dInlineHook (tbnz — NOT relocatable, NEEDS HOOK)
        # Mode2DNoMV.cpp — StageColiLoadHook
        (0x0062D970, 169, "900035a8", False, "StageColiLoadHook trampoline"),
        # TheaterRestoration.cpp — TheaterSaveSelectedIndexPatch (adrp — NOT relocatable, NEEDS HOOK)
        # DebugMode.cpp — DwScrollableGetBoundingBoxHook
        (0x00341AB0, 170, "f81e0ff3", False, "DwScrollableGetBoundingBoxHook trampoline"),
        # DebugMode.cpp — EngineUpdateTickHook
        (0x00200F10, 171, "d10143ff", False, "EngineUpdateTickHook trampoline"),
        # shared_nc_ft — TaskPvDBCtrlSharedHook
        (0x004C0FF0, 172, "a9ba6ffc", False, "TaskPvDBCtrlSharedHook trampoline"),
        # SaveDataSystem.cpp — SaveManagerHook
        (0x000C9720, 173, "6db923e9", False, "SaveManagerHook trampoline"),
        # AetDB.cpp — GetAetSetEntry
        (0x001E2540, 174, "37f80181", False, "GetAetSetEntry trampoline"),
        # ModLoader.cpp — InitRomDirectoryPathsHook
        (0x001F1840, 177, "d10183ff", False, "InitRomDirectoryPathsHook trampoline"),
        # nc/game/game.cpp — GetHitStatePlaySEHook
        (0x001AF5A0, 178, "4ea91d20", False, "GetHitStatePlaySEHook trampoline"),
        # nc/ui/customize_sel.cpp — CustomizeSelTaskInit/Ctrl/Dest, CSTopMenuMainCtrl
        (0x00778930, 179, "a9be4ff4", False, "CustomizeSelTaskInitHook trampoline"),
        (0x00778980, 180, "f9403800", False, "CustomizeSelTaskCtrlHook trampoline"),
        (0x00778990, 181, "a9be4ff4", False, "CustomizeSelTaskDestHook trampoline"),
        (0x007A9370, 182, "d10143ff", False, "CSTopMenuMainCtrlHook trampoline"),
        # nc/ui/pv_sel_ps4.cpp — PVselPS4DestHook
        (0x0012C5D8, 183, "36000108", False, "PVselPS4DestHook trampoline"),
        # SpriteDrawLimitPatch.cpp — 8 inline hooks (already NOP'd by CUTS above at same offsets,
        # so no separate TRAMP gate — CUTS and TRAMP can't share one instruction)

        # Remaining resolved ADDR_ constants (from exlaunch source, verified against NSO binary):
        # overlays/WindControl.cpp — WindCtrlHook (matches hle_diva.c gate_tramp_set(72, ...))
        (0x00523140, 72, "d102c3ff", False, "WindCtrlHook trampoline"),
        # MotionPlayerUi.cpp — BonesUpdateHook (matches hle_diva.c gate_tramp_set(73, ...))
        (0x00252970, 73, "f81d0ff5", False, "BonesUpdateHook trampoline"),
        # Sound.cpp — volume hooks (matches hle_diva.c gate_tramp_set 93-98)
        (0x0060DC00, 93, "1e202008", False, "SetHandleVolumeHook trampoline"),
        (0x006092C0, 94, "1e2e1001", False, "SetGlobalBgmVolumeHook trampoline"),
        (0x00609220, 95, "7100141f", False, "SetQueueVolumeHook trampoline"),
        (0x00609350, 96, "fc1e0fe8", False, "SetStreamVolumeHook trampoline"),
        (0x006092E0, 97, "fc1e0fe8", False, "SetBgmStreamVolumeHook trampoline"),
        (0x000C9660, 98, "6dbd23e9", False, "ApplySoundSettingsHook trampoline"),
        # SaveDataSystem.cpp — find hooks
        # (0x000C61E0 FindOrCreateScoreHook — TID 63, 0x000C7890 FindScoreHook — TID 65, 0x000C8850 FindModuleHook — TID 65,
        #  0x000C8C30 FindModule2Hook — TID 66, 0x000C8870 FindCstmItemHook — TID 67, 0x000C8C50 FindCstmItemGalleryHook — TID 68,
        #  0x000C9720 SaveManagerHook — TID 173 — all already registered above)
    ],
}
