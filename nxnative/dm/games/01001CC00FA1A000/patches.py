# nx2android offline patches for Hatsune Miku: Project DIVA MegaMix
# Title ID: 01001CC00FA1A000
#
# Intentionally empty: subsdk9 (the exlaunch plugin, loaded as a guest NSO module)
# applies all of its own patches and hooks from
#   ExlSD:/MikuMikuSwitchPlugin/config.toml
# at runtime via its own Config::init(). The host does NOT recreate any of them —
# no CUTS, no OBS gates, no TRAMP gates. subsdk9 source lives in exlaunch/.
#
# build_id must match the build that patch_nso.py rewrote (main.nso's build ID).
# patch_nso.py applies CUTS/OBS/TRAMP whose build_id matches a rewritten module;
# with everything empty here, no host-side patches are applied to any module.

build_id = "179265bd41f7781dac979e7770201124"

CUTS = {
    build_id: [],
}

OBS = {
    build_id: [],
}

TRAMP = {
    build_id: [],
}
