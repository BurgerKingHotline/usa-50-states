######################################################################
# FAIR WARNING FOR END USER
# THIS IS UNDER DEVELOPMENT AS OF WRITING 6/8/2026 @ 4PM PST
# COMMIT ALL CHANGES BEFORE RUNNING THIS SCRIPT. YOU HAVE BEEN WARNED.
######################################################################

import os
import re
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# --- IDEOLOGY DEFINITIONS ---
IDEOLOGY_GROUPS = [
    (
        "conservatism_ideology",
        1,
        "[tag]_conservative_senate_seats",
        "[tag]_conservative_house_seats",
        [("conservatism_subideology", 9), ("christian_democracy", 7)],
    ),
    (
        "populism_ideology",
        2,
        "[tag]_agrarian_senate_seats",
        "[tag]_agrarian_house_seats",
        [("populism_subideology", 26), ("agrarian_populism", 1)],
    ),
    (
        "democratic",
        3,
        "[tag]_liberal_senate_seats",
        "[tag]_liberal_house_seats",
        [
            ("liberalism", 20),
            ("conservatism", 9),
            ("socialism", 28),
            ("populism", 26),
            ("liberal_integrationism", 19),
        ],
    ),
    (
        "socialism_ideology",
        4,
        "[tag]_socialist_senate_seats",
        "[tag]_socialist_house_seats",
        [("socialism_subideology", 28), ("farmer_laborism", 28)],
    ),
    (
        "communism",
        5,
        "[tag]_communist_senate_seats",
        "[tag]_communist_house_seats",
        [
            ("marxism", 21),
            ("leninism", 18),
            ("stalinism", 29),
            ("anti_revisionism", 4),
            ("anarchist_communism", 3),
            ("buddhist_socialism", 5),
        ],
    ),
    (
        "fascism",
        6,
        "[tag]_fascist_senate_seats",
        "[tag]_fascist_house_seats",
        [
            ("fascism_ideology", 14),
            ("nazism", 23),
            ("gen_nazism", 15),
            ("falangism", 13),
            ("rexism", 27),
            ("emperor_fascism", 12),
            ("integral_nationalism", 16),
            ("civil_nationalism", 8),
        ],
    ),
    (
        "neutrality",
        7,
        "[tag]_nonaligned_senate_seats",
        "[tag]_nonaligned_house_seats",
        [
            ("despotism", 11),
            ("oligarchism", 24),
            ("anarchism", 2),
            ("moderatism", 22),
            ("centrism", 6),
            ("japan_militarism_ideology", 17),
            ("corporate_technocracy", 10),
            ("organical_statism", 25),
        ],
    ),
]

HARDCODED_SENATE_X = [
    0,
    29,
    59,
    88,
    6,
    38,
    18,
    69,
    57,
    100,
    37,
    90,
    60,
    84,
    88,
    120,
    117,
    116,
    117,
    148,
    149,
    148,
    144,
    177,
    181,
    205,
    175,
    228,
    165,
    208,
    196,
    247,
    227,
    259,
    176,
    206,
    236,
    265,
]
HARDCODED_SENATE_Y = [
    131,
    131,
    131,
    131,
    101,
    98,
    73,
    103,
    70,
    110,
    49,
    80,
    30,
    50,
    16,
    98,
    68,
    39,
    9,
    9,
    39,
    68,
    98,
    16,
    50,
    30,
    80,
    49,
    110,
    70,
    103,
    73,
    98,
    101,
    131,
    131,
    131,
    131,
]
HARDCODED_HOUSE_X = [
    0,
    16,
    31,
    47,
    63,
    79,
    3,
    19,
    35,
    51,
    8,
    67,
    25,
    84,
    42,
    17,
    59,
    33,
    76,
    27,
    52,
    45,
    93,
    70,
    40,
    66,
    88,
    58,
    55,
    84,
    106,
    81,
    74,
    71,
    103,
    100,
    91,
    99,
    89,
    121,
    119,
    109,
    108,
    118,
    118,
    128,
    127,
    137,
    137,
    137,
    137,
    147,
    147,
    157,
    156,
    166,
    166,
    155,
    154,
    185,
    175,
    184,
    174,
    172,
    203,
    201,
    193,
    169,
    190,
    219,
    216,
    187,
    209,
    234,
    204,
    181,
    230,
    222,
    247,
    199,
    241,
    215,
    258,
    232,
    191,
    250,
    207,
    266,
    223,
    239,
    256,
    271,
    196,
    211,
    227,
    243,
    259,
    274,
]
HARDCODED_HOUSE_Y = [
    136,
    136,
    136,
    136,
    136,
    136,
    117,
    117,
    117,
    118,
    98,
    119,
    99,
    121,
    99,
    80,
    101,
    82,
    103,
    64,
    82,
    67,
    107,
    85,
    49,
    68,
    90,
    53,
    36,
    73,
    96,
    56,
    42,
    26,
    80,
    63,
    34,
    47,
    17,
    89,
    73,
    28,
    12,
    58,
    42,
    25,
    9,
    87,
    71,
    40,
    56,
    9,
    25,
    42,
    58,
    12,
    28,
    73,
    89,
    17,
    47,
    34,
    63,
    80,
    26,
    42,
    56,
    96,
    73,
    36,
    53,
    90,
    68,
    49,
    85,
    107,
    67,
    82,
    64,
    103,
    82,
    101,
    80,
    99,
    121,
    99,
    119,
    98,
    118,
    117,
    117,
    117,
    136,
    136,
    136,
    136,
    136,
    136,
]


# --- GEOMETRY MATH ---
def get_semicircle_layout(num_seats, cx, cy, ir, or_, rows, full_circle=False):
    coords = []
    rows = max(1, rows)
    radii = (
        [or_] if rows == 1 else [ir + r * (or_ - ir) / (rows - 1) for r in range(rows)]
    )
    multiplier = 2 if full_circle else 1
    arc_lengths = [multiplier * math.pi * r for r in radii]
    total_arc = max(1, sum(arc_lengths))
    seats_per_row = []
    remaining = num_seats
    for i in range(rows):
        if i == rows - 1:
            seats_per_row.append(remaining)
        else:
            seats = int(round(num_seats * (arc_lengths[i] / total_arc)))
            seats_per_row.append(seats)
            remaining -= seats
    for i, r in enumerate(radii):
        row_seats = seats_per_row[i]
        if row_seats == 1:
            angle = math.pi / 2 if not full_circle else 0
            coords.append(
                (
                    int(round(cx + r * math.cos(angle))),
                    int(round(cy - r * math.sin(angle))),
                )
            )
        elif row_seats > 1:
            for s in range(row_seats):
                angle = (
                    (math.pi - (s * math.pi / (row_seats - 1)))
                    if not full_circle
                    else (s * 2 * math.pi / row_seats)
                )
                coords.append(
                    (
                        int(round(cx + r * math.cos(angle))),
                        int(round(cy - r * math.sin(angle))),
                    )
                )
    return coords


def get_grid_layout(num_seats, sx, sy, dx, dy, cols):
    cols = max(1, cols)
    return [(sx + (i % cols) * dx, sy + (i // cols) * dy) for i in range(num_seats)]


# --- HOI4 FILE PATCHING UTILITY ---
def _find_block_extent(text, name):
    pattern = re.compile(r"^" + re.escape(name) + r"\s*=\s*\{", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None
    depth = 1
    i = m.end()
    while i < len(text) and depth > 0:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return (m.start(), i)


def patch_hoi4_blocks(filepath, new_content, encoding="utf-8"):
    content = ""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding=encoding, errors="ignore") as f:
            content = f.read()

    remaining = new_content
    while remaining.strip():
        m = re.search(r"^([A-Za-z0-9_]+)\s*=\s*\{", remaining, re.MULTILINE)
        if not m:
            break
        name = m.group(1)
        depth = 1
        j = m.end()
        while j < len(remaining) and depth > 0:
            if remaining[j] == "{":
                depth += 1
            elif remaining[j] == "}":
                depth -= 1
            j += 1
        block = remaining[m.start() : j].strip()
        remaining = remaining[j:]

        extent = _find_block_extent(content, name)
        if extent:
            s, e = extent
            content = content[:s] + block + "\n" + content[e:].lstrip("\n")
        else:
            content = content.rstrip("\n") + "\n\n" + block + "\n"

    with open(filepath, "w", encoding=encoding) as f:
        f.write(content)


# --- GENERATION STRINGS ---
def gen_fix_cascade(t_name, is_over):
    s = f"\n\t# Cascade {'overflows' if is_over else 'deficits'} for {t_name}\n\tif = {{\n\t\tlimit = {{ check_variable = {{ [tag]_{t_name}_sum {'<' if not is_over else '>'} [tag]_{t_name}_max }} }}\n"
    s += f"\t\tset_temp_variable = {{ [tag]_diff = {'[tag]_' + t_name + '_sum' if is_over else '[tag]_' + t_name + '_max'} }}\n\t\tsubtract_from_temp_variable = {{ [tag]_diff = {'[tag]_' + t_name + '_max' if is_over else '[tag]_' + t_name + '_sum'} }}\n"
    for _, _, s_var, h_var, _ in IDEOLOGY_GROUPS:
        var = s_var if t_name == "senate" else h_var
        s += f"\t\tif = {{\n\t\t\tlimit = {{ check_variable = {{ [tag]_diff > 0 }} }}\n"
        if is_over:
            s += f"\t\t\tif = {{\n\t\t\t\tlimit = {{ check_variable = {{ {var} > [tag]_diff }} }}\n\t\t\t\tsubtract_from_variable = {{ {var} = [tag]_diff }}\n\t\t\t\tset_temp_variable = {{ [tag]_diff = 0 }}\n\t\t\t}}\n\t\t\telse = {{\n\t\t\t\tsubtract_from_temp_variable = {{ [tag]_diff = {var} }}\n\t\t\t\tset_variable = {{ {var} = 0 }}\n\t\t\t}}\n"
        else:
            s += f"\t\t\tadd_to_variable = {{ {var} = [tag]_diff }}\n\t\t\tset_temp_variable = {{ [tag]_diff = 0 }}\n"
        s += f"\t\t}}\n"
    return s + "\t}\n"


def gen_effects(tag, s_max, h_max, weights):
    T, t = tag.upper(), tag.lower()

    eff = f"\n{T}_calculate_party_seats = {{\n"

    for t_name, t_max in [("senate", s_max), ("house", h_max)]:
        eff += f"\n\t# --- {t_name.upper()} SEATS ---\n"
        eff += f"\tset_temp_variable = {{ {t}_{t_name}_max = {t_max} }}\n\tset_temp_variable = {{ {t}_{t_name}_sum = 0 }}\n"

        for p, _, s_var, h_var, _ in IDEOLOGY_GROUPS:
            var = (
                s_var.replace("[tag]", t)
                if t_name == "senate"
                else h_var.replace("[tag]", t)
            )
            eff += f"\n\tset_temp_variable = {{ {t}_t = party_popularity@{p} }}\n\tmultiply_temp_variable = {{ {t}_t = {t}_{t_name}_max }}\n\tround_temp_variable = {t}_t\n\tset_variable = {{ {var} = {t}_t }}\n\tadd_to_temp_variable = {{ {t}_{t_name}_sum = {var} }}\n"

        eff += gen_fix_cascade(t_name, True).replace("[tag]", t)
        eff += gen_fix_cascade(t_name, False).replace("[tag]", t)

        eff += f"\n\t# --- {t_name.upper()} SUBIDEOLOGIES ---\n"
        for _, _, s_var, h_var, subs in IDEOLOGY_GROUPS:
            var = (
                s_var.replace("[tag]", t)
                if t_name == "senate"
                else h_var.replace("[tag]", t)
            )
            wt = [weights.get(sub, 0) for sub, _ in subs]
            tot = sum(wt) or 1
            ratios = [w / tot for w in wt]
            for i, (sub_id, _) in enumerate(subs):
                sub_var = f"{t}_{sub_id}_{t_name}_seats"
                if i == len(subs) - 1:
                    eff += f"\tset_variable = {{ {sub_var} = {var} }}\n"
                    for j in range(i):
                        eff += f"\tsubtract_from_variable = {{ {sub_var} = {t}_{subs[j][0]}_{t_name}_seats }}\n"
                    eff += f"\tif = {{ limit = {{ check_variable = {{ {sub_var} < 0 }} }} set_variable = {{ {sub_var} = 0 }} }}\n"
                else:
                    eff += f"\tset_variable = {{ {sub_var} = {var} }}\n\tmultiply_variable = {{ {sub_var} = {round(ratios[i], 3)} }}\n\tround_variable = {sub_var}\n"

    eff += "}\n"

    eff += f"\n{T}_build_roster = {{\n\tclear_array = {t}_roster_tokens\n\tclear_array = {t}_roster_names_array\n\tclear_array = {t}_roster_frames\n\tclear_array = {t}_roster_colors\n\tclear_array = {t}_roster_senate_seats\n\tclear_array = {t}_roster_house_seats\n"
    for _, color, _, _, subs in IDEOLOGY_GROUPS:
        for sub_id, badge in subs:
            eff += f"\n\tif = {{\n\t\tlimit = {{ OR = {{ check_variable = {{ {t}_{sub_id}_senate_seats > 0 }} check_variable = {{ {t}_{sub_id}_house_seats > 0 }} }} }}\n"
            eff += f"\t\tadd_to_array = {{ {t}_roster_tokens = token:{sub_id} }}\n"
            # Direct token storage for dynamic list lookup
            eff += f"\t\tadd_to_array = {{ {t}_roster_names_array = token:{t}_{sub_id}_roster_name }}\n"
            eff += f"\t\tadd_to_array = {{ {t}_roster_frames = {badge} }}\n\t\tadd_to_array = {{ {t}_roster_colors = {color} }}\n"
            eff += f"\t\tadd_to_array = {{ {t}_roster_senate_seats = {t}_{sub_id}_senate_seats }}\n\t\tadd_to_array = {{ {t}_roster_house_seats = {t}_{sub_id}_house_seats }}\n\t}}"
    eff += "\n}\n"
    eff += f"\n{T}_recalculate_all_seats = {{\n\t{T}_calculate_party_seats = yes\n\t{T}_build_roster = yes\n\t{T}_senate_gui_setup = yes\n\t{T}_house_gui_setup = yes\n\t{T}_senate_reload = yes\n\t{T}_house_reload = yes\n}}\n"
    return eff


def build_mod_files(mod_dir, tag, sen_c, hse_c, weights, scale):
    T, t = tag.upper(), tag.lower()

    # Generate Effects
    eff = gen_effects(tag, len(sen_c), len(hse_c), weights)

    # Generate GUI setup functions
    for ch, coords in [("senate", sen_c), ("house", hse_c)]:
        eff += f"\n{T}_{ch}_gui_setup = {{\n\tclear_array = {t}_{ch}_gui_x\n\tclear_array = {t}_{ch}_gui_y\n\tclear_array = {t}_{ch}_gui_frame\n"
        for x, y in coords:
            eff += f"\tadd_to_array = {{ {t}_{ch}_gui_x = {int(x)} }}\n\tadd_to_array = {{ {t}_{ch}_gui_y = {int(y)} }}\n"
        for _ in coords:
            eff += f"\tadd_to_array = {{ {t}_{ch}_gui_frame = 0 }}\n"
        eff += "}\n"

        eff += f"\n{T}_{ch}_reload = {{\n"
        for i, (_, _, s_var, h_var, _) in enumerate(IDEOLOGY_GROUPS, 1):
            var = (
                s_var.replace("[tag]", t)
                if ch == "senate"
                else h_var.replace("[tag]", t)
            )
            eff += f"\tset_temp_variable = {{ {t}_p{i} = {var} }}\n"
        eff += "\n".join(
            f"\tadd_to_temp_variable = {{ {t}_p{i} = {t}_p{i - 1} }}"
            for i in range(2, 8)
        )
        eff += f"\n\tclear_array = {t}_{ch}_gui_frame\n"
        for i in range(1, 8):
            eff += f"\tresize_array = {{ array = {t}_{ch}_gui_frame value = {i} size = {t}_p{i} }}\n"
        eff += "}\n"

    # Generate Scripted GUIs
    sgui = f"""scripted_gui = {{
\t{t}_congress_button_container = {{ window_name = "congress_button_container" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no tag = {T} }}
\t\teffects = {{ congress_button_click = {{ if = {{ limit = {{ tag = {T} }} {T}_recalculate_all_seats = yes }} if = {{ limit = {{ NOT = {{ has_country_flag = congress_visible }} }} set_country_flag = congress_visible }} else = {{ clr_country_flag = congress_visible clr_country_flag = congress_roster_visible }} }} }} }}
\t
\t{t}_congress_screen_container = {{ window_name = "{t}_congress_gui" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no has_country_flag = congress_visible tag = {T} }}
\t\tdynamic_lists = {{ {t}_senate_diagram_container = {{ array = {t}_senate_gui_x change_scope = no entry_container = {t}_senate_gui_seat index = seat_idx }} {t}_house_diagram_container = {{ array = {t}_house_gui_x change_scope = no entry_container = {t}_house_gui_seat index = house_idx }} }}
\t\tproperties = {{ {t}_senate_seat_icon = {{ x = {t}_senate_gui_x^seat_idx y = {t}_senate_gui_y^seat_idx frame = {t}_senate_gui_frame^seat_idx }} {t}_house_seat_icon = {{ x = {t}_house_gui_x^house_idx y = {t}_house_gui_y^house_idx frame = {t}_house_gui_frame^house_idx }} }}
\t\teffects = {{ congress_close_button_click = {{ clr_country_flag = congress_visible clr_country_flag = congress_roster_visible }} open_roster_button_click = {{ if = {{ limit = {{ has_country_flag = congress_roster_visible }} clr_country_flag = congress_roster_visible }} else = {{ set_country_flag = congress_roster_visible }} }} }} }}
\t
\t{t}_congress_roster_panel = {{ window_name = "{t}_congress_roster_panel" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no has_country_flag = congress_visible has_country_flag = congress_roster_visible tag = {T} }}
\t\tdynamic_lists = {{ {t}_roster_grid = {{ array = {t}_roster_tokens change_scope = no entry_container = {t}_roster_entry index = roster_idx }} }}
\t\tproperties = {{ roster_badge_icon = {{ frame = {t}_roster_frames^roster_idx }} roster_color_icon = {{ frame = {t}_roster_colors^roster_idx }} }} }}
}}"""

    # Generate Layout GUI (Note the array variable lookup for the string)
    gui = f"""guiTypes = {{
\tcontainerWindowType = {{
\t\tname = "{t}_congress_gui"
\t\tposition = {{ x = 545 y = 4 }}
\t\tsize = {{ width = 380 height = 460 }}
\t\tbackground = {{ name = "congress_panel_bg" quadTextureSprite = "GFX_tiled_bg" }}
\t\tclipping = no
\t\ticonType = {{ name = "title_header_icon" spriteType = "GFX_congress_header" position = {{ x = 0 y = 3 }} }}
\t\tinstantTextboxType = {{ name = "congress_title" position = {{ x = 0 y = 8 }} font = "hoi_24header" text = "{T}_CONGRESS_TITLE" maxWidth = 310 maxHeight = 20 format = centre }}
\t\tinstantTextboxType = {{ name = "senate_section_label" position = {{ x = 21 y = 45 }} font = "hoi_18mbs" text = "{T}_SENATE_SECTION" maxWidth = 170 maxHeight = 16 format = left }}
\t\tgridBoxType = {{ name = "{t}_senate_diagram_container" position = {{ x = 16 y = 70 }} size = {{ width = 290 height = 155 }} slotsize = {{ width = 100%% height = 1 }} max_slots_horizontal = 1 add_horizontal = no }}
\t\tinstantTextboxType = {{ name = "house_section_label" position = {{ x = 21 y = 245 }} font = "hoi_18mbs" text = "{T}_HOUSE_SECTION" maxWidth = 170 maxHeight = 16 format = left }}
\t\tgridBoxType = {{ name = "{t}_house_diagram_container" position = {{ x = 18 y = 270 }} size = {{ width = 295 height = 175 }} slotsize = {{ width = 100%% height = 1 }} max_slots_horizontal = 1 add_horizontal = no }}
\t\tbuttonType = {{ name = "open_roster_button" position = {{ x = 270 y = 8 }} quadTextureSprite = "GFX_button_94x31" buttonFont = "hoi_16mbs" buttonText = "Roster" clicksound = click_default }}
\t\tbuttonType = {{ name = "congress_close_button" position = {{ x = 354 y = 6 }} quadTextureSprite = "GFX_closebutton" buttonFont = "Main_14_black" clicksound = click_default }}
\t}}
\tcontainerWindowType = {{
\t\tname = "{t}_congress_roster_panel"
\t\tposition = {{ x = 925 y = 4 }}
\t\tsize = {{ width = 300 height = 460 }}
\t\tbackground = {{ name = "roster_bg" quadTextureSprite = "GFX_tiled_bg" }}
\t\tinstantTextboxType = {{ name = "roster_title" position = {{ x = 0 y = 15 }} font = "hoi_24header" text = "Active Subideologies" maxWidth = 300 format = center }}
\t\tcontainerWindowType = {{ name = "{t}_roster_scroll_area" position = {{ x = 10 y = 50 }} size = {{ width = 280 height = 400 }} verticalScrollbar = "right_vertical_slider" margin = {{ top = 5 bottom = 5 }} smooth_scrolling = yes scroll_wheel_factor = 40 background = {{ name = "Background" quadTextureSprite = "GFX_tiled_window_transparent" }}
\t\t\tgridBoxType = {{ name = "{t}_roster_grid" position = {{ x = 0 y = 0 }} size = {{ width = 100%% height = 100%% }} slotsize = {{ width = 270 height = 65 }} max_slots_horizontal = 1 add_horizontal = no format = "UPPER_LEFT" }}
\t\t}}
\t}}
\tcontainerWindowType = {{ name = "{t}_senate_gui_seat" position = {{ x = 40 y = 0 }} clipping = no iconType = {{ name = "{t}_senate_seat_icon" spriteType = "GFX_seat_icon" frame = 1 scale = {scale} pdx_tooltip = "{t}_senate_seat_combined_tt" }} }}
\tcontainerWindowType = {{ name = "{t}_house_gui_seat" position = {{ x = 35 y = 0 }} clipping = no iconType = {{ name = "{t}_house_seat_icon" spriteType = "GFX_seat_icon" frame = 1 scale = {scale} pdx_tooltip = "{t}_house_seat_combined_tt" }} }}
\tcontainerWindowType = {{ name = "{t}_roster_entry" size = {{ width = 270 height = 60 }} background = {{ name = "bg" quadTextureSprite = "GFX_tiled_window_transparent" }}
\t\ticonType = {{ name = "roster_color_icon" spriteType = "GFX_seat_icon" position = {{ x = 5 y = 20 }} }}
\t\ticonType = {{ name = "roster_badge_icon" spriteType = "GFX_subideology_badge_large" position = {{ x = 30 y = 5 }} scale = 0.7 }}
\t\tinstantTextboxType = {{ name = "roster_name" position = {{ x = 85 y = 10 }} font = "hoi_16mbs" text = "[?{t}_roster_names_array^roster_idx.GetTokenLocalizedKey]" maxWidth = 180 maxHeight = 16 fixedsize = yes }}
\t\tinstantTextboxType = {{ name = "roster_seats" position = {{ x = 85 y = 30 }} font = "hoi_16mbs" text = "Senate: [?{t}_roster_senate_seats^roster_idx|Y0] | House: [?{t}_roster_house_seats^roster_idx|Y0]" maxWidth = 180 maxHeight = 16 }}
\t}}
}}"""

    # Generate Localisation
    loc = "l_english:\n"
    loc += f' {t}_senate_seat_tt:0 "{T} State Senate Seat"\n {t}_house_seat_tt:0 "{T} State House Seat"\n'
    loc += f' {t}_senate_seat_combined_tt:0 "[Get{T}SenateSeatName]\\n[Get{T}SenatePartyName]"\n'
    loc += f' {t}_house_seat_combined_tt:0 "[Get{T}HouseSeatName]\\n[Get{T}HousePartyName]"\n'
    loc += f' {t}_senate_seat_number_fallback:0 "Senate Seat [?seat_idx|+1|0]"\n {t}_house_seat_number_fallback:0 "House Seat [?house_idx|+1|0]"\n'

    for _, _, _, _, subs in IDEOLOGY_GROUPS:
        for sub_id, _ in subs:
            # We explicitly define the localization string for the exact token that was pushed to the array
            loc += f' {t}_{sub_id}_roster_name:0 "{sub_id.replace("_", " ").title().replace("Subideology", "Caucus").replace("Ideology", "Movement")}"\n'

    for i, name in enumerate(
        [
            "Conservative",
            "Agrarian",
            "Liberal",
            "Socialist",
            "Communist",
            "Fascist",
            "Non-Aligned",
        ],
        1,
    ):
        loc += f' {t}_senate_party_frame_{i}:0 "{name}"\n {t}_house_party_frame_{i}:0 "{name}"\n'
    loc += f' {T}_CONGRESS_TITLE:0 "{T} Legislature"\n {T}_SENATE_SECTION:0 "Senate"\n {T}_HOUSE_SECTION:0 "House"\n'

    sloc = f'defined_text = {{\n\tname = Get{T}SenateSeatName\n\ttext = {{\n\t\tlocalization_key = "{t}_senate_seat_number_fallback"\n\t}}\n}}\n'
    sloc += f'defined_text = {{\n\tname = Get{T}HouseSeatName\n\ttext = {{\n\t\tlocalization_key = "{t}_house_seat_number_fallback"\n\t}}\n}}\n'
    sloc += f'defined_text = {{\n\tname = Get{T}SenatePartyName\n\ttext = {{\n\t\tlocalization_key = "{t}_senate_party_frame_[?{t}_senate_gui_frame^seat_idx]"\n\t}}\n}}\n'
    sloc += f'defined_text = {{\n\tname = Get{T}HousePartyName\n\ttext = {{\n\t\tlocalization_key = "{t}_house_party_frame_[?{t}_house_gui_frame^house_idx]"\n\t}}\n}}\n'

    # Save Isolated Files (Non-Destructive)
    os.makedirs(f"{mod_dir}/common/scripted_effects", exist_ok=True)
    os.makedirs(f"{mod_dir}/common/scripted_guis", exist_ok=True)
    os.makedirs(f"{mod_dir}/common/scripted_localisation", exist_ok=True)
    os.makedirs(f"{mod_dir}/interface/congress", exist_ok=True)
    os.makedirs(f"{mod_dir}/localisation/english", exist_ok=True)

    # Smart-patch: replaces only the named congress blocks, preserving manual edits
    patch_hoi4_blocks(f"{mod_dir}/common/scripted_effects/{T}_congress_setup.txt", eff)
    # Full overwrite for strictly generated output files
    with open(
        f"{mod_dir}/common/scripted_guis/{T}_congress_gui.txt", "w", encoding="utf-8"
    ) as f:
        f.write(sgui)
    with open(
        f"{mod_dir}/common/scripted_localisation/{T}_congress_scripted_locs.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(sloc)
    with open(
        f"{mod_dir}/interface/congress/{T}_congress.gui", "w", encoding="utf-8"
    ) as f:
        f.write(gui)
    with open(
        f"{mod_dir}/localisation/english/{T}_congress_l_english.yml",
        "w",
        encoding="utf-8-sig",
    ) as f:
        f.write(loc)

    # Inject into Country History WITHOUT modifying set_popularities
    history_dir = os.path.join(mod_dir, "history", "countries")
    if os.path.exists(history_dir):
        target_file = next(
            (
                os.path.join(history_dir, file)
                for file in os.listdir(history_dir)
                if file.upper().startswith(T)
            ),
            None,
        )
        if target_file:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Inject hooks safely before set_popularities
            hook_str = f"{T}_recalculate_all_seats = yes\n\t"
            if (
                f"{T}_recalculate_all_seats = yes" not in content
                and "set_popularities" in content
            ):
                content = content.replace(
                    "set_popularities", f"{hook_str}set_popularities", 1
                )

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)


# --- GUI APP ---
class CollapsiblePanel(ttk.Frame):
    def __init__(self, parent, title, on_randomize=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._expanded = False
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", pady=2)
        self.toggle_btn = tk.Button(
            self.header_frame, text="+", width=2, relief=tk.FLAT, command=self.toggle
        )
        self.toggle_btn.pack(side="left")
        ttk.Label(self.header_frame, text=title, font=("Helvetica", 10, "bold")).pack(
            side="left", padx=5
        )
        if on_randomize:
            ttk.Button(self.header_frame, text="Randomize", command=on_randomize).pack(
                side="right"
            )
        self.content_frame = ttk.Frame(self)

    def toggle(self):
        self._expanded = not self._expanded
        if self._expanded:
            self.content_frame.pack(fill="x", expand=True, padx=20, pady=2)
            self.toggle_btn.config(text="-")
        else:
            self.content_frame.pack_forget()
            self.toggle_btn.config(text="+")


class LayoutEditor(ttk.Frame):
    def __init__(self, parent, title, hardcoded_x, hardcoded_y):
        super().__init__(parent)
        self.hardcoded_x = hardcoded_x
        self.hardcoded_y = hardcoded_y
        self.num_seats_var = tk.IntVar(value=len(hardcoded_x))
        self.shape_var = tk.StringVar(value="Default")
        self.cx_var, self.cy_var, self.ir_var, self.or_var, self.rows_var = (
            tk.IntVar(value=140),
            tk.IntVar(value=160),
            tk.IntVar(value=60),
            tk.IntVar(value=130),
            tk.IntVar(value=4),
        )
        self.sx_var, self.sy_var, self.dx_var, self.dy_var, self.cols_var = (
            tk.IntVar(value=10),
            tk.IntVar(value=10),
            tk.IntVar(value=15),
            tk.IntVar(value=15),
            tk.IntVar(value=15),
        )

        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=5)
        ttk.Label(top_frame, text="Max Seats:").pack(side=tk.LEFT)
        ttk.Entry(top_frame, textvariable=self.num_seats_var, width=5).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(top_frame, text="Shape:").pack(side=tk.LEFT, padx=5)
        shape_cb = ttk.Combobox(
            top_frame,
            textvariable=self.shape_var,
            values=["Default", "Semicircle", "Circle", "Grid"],
            state="readonly",
            width=12,
        )
        shape_cb.pack(side=tk.LEFT)
        shape_cb.bind("<<ComboboxSelected>>", self.on_shape_change)

        self.canvas = tk.Canvas(
            self, width=420, height=280, bg="#2a2a2a", relief=tk.SUNKEN, bd=2
        )
        self.canvas.pack(pady=5)
        self.canvas.bind("<Map>", lambda e: self.after(50, self.draw_preview))

        self.params_frame = ttk.Frame(self)
        self.params_frame.pack(fill=tk.X, pady=5)
        self.semi_frame, self.grid_frame = (
            ttk.Frame(self.params_frame),
            ttk.Frame(self.params_frame),
        )

        self.build_scale(self.semi_frame, "Center X", self.cx_var, 0, 400).grid(
            row=0, column=0, padx=5, sticky="ew"
        )
        self.build_scale(self.semi_frame, "Center Y", self.cy_var, 0, 400).grid(
            row=0, column=1, padx=5, sticky="ew"
        )
        self.build_scale(self.semi_frame, "Inner Radius", self.ir_var, 0, 300).grid(
            row=1, column=0, padx=5, sticky="ew"
        )
        self.build_scale(self.semi_frame, "Outer Radius", self.or_var, 10, 300).grid(
            row=1, column=1, padx=5, sticky="ew"
        )
        self.build_scale(self.semi_frame, "Total Rows", self.rows_var, 1, 15).grid(
            row=2, column=0, columnspan=2, padx=5, sticky="ew"
        )
        self.build_scale(self.grid_frame, "Start X", self.sx_var, 0, 400).grid(
            row=0, column=0, padx=5, sticky="ew"
        )
        self.build_scale(self.grid_frame, "Start Y", self.sy_var, 0, 400).grid(
            row=0, column=1, padx=5, sticky="ew"
        )
        self.build_scale(self.grid_frame, "Spacing X", self.dx_var, 1, 50).grid(
            row=1, column=0, padx=5, sticky="ew"
        )
        self.build_scale(self.grid_frame, "Spacing Y", self.dy_var, 1, 50).grid(
            row=1, column=1, padx=5, sticky="ew"
        )
        self.build_scale(self.grid_frame, "Columns", self.cols_var, 1, 50).grid(
            row=2, column=0, columnspan=2, padx=5, sticky="ew"
        )

        for f in (self.semi_frame, self.grid_frame):
            f.columnconfigure(0, weight=1)
            f.columnconfigure(1, weight=1)
        self.num_seats_var.trace_add("write", lambda *a: self.draw_preview())
        self.on_shape_change()

    def build_scale(self, parent, label, var, from_, to_):
        f = ttk.Frame(parent)
        ttk.Label(f, text=label).pack(side=tk.LEFT)
        tk.Scale(
            f,
            variable=var,
            from_=from_,
            to=to_,
            orient=tk.HORIZONTAL,
            command=lambda v: self.draw_preview(),
            showvalue=False,
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        return f

    def on_shape_change(self, *args):
        self.semi_frame.pack_forget()
        self.grid_frame.pack_forget()
        s = self.shape_var.get()
        if s in ("Semicircle", "Circle"):
            self.semi_frame.pack(fill=tk.X)
        elif s == "Grid":
            self.grid_frame.pack(fill=tk.X)
        self.draw_preview()

    def get_coords(self):
        try:
            num = self.num_seats_var.get()
        except:
            num = len(self.hardcoded_x)
        s = self.shape_var.get()

        if s == "Default":
            coords = list(zip(self.hardcoded_x, self.hardcoded_y))
            if num <= len(coords):
                return coords[:num]
            padded = coords.copy()
            while len(padded) < num:
                padded.append((padded[-1][0] + 5, padded[-1][1]))
            return padded
        elif s == "Semicircle":
            return get_semicircle_layout(
                num,
                self.cx_var.get(),
                self.cy_var.get(),
                self.ir_var.get(),
                self.or_var.get(),
                self.rows_var.get(),
            )
        elif s == "Circle":
            return get_semicircle_layout(
                num,
                self.cx_var.get(),
                self.cy_var.get(),
                self.ir_var.get(),
                self.or_var.get(),
                self.rows_var.get(),
                True,
            )
        else:
            return get_grid_layout(
                num,
                self.sx_var.get(),
                self.sy_var.get(),
                self.dx_var.get(),
                self.dy_var.get(),
                self.cols_var.get(),
            )

    def draw_preview(self):
        try:
            self.canvas.delete("all")
            for x, y in self.get_coords():
                self.canvas.create_oval(
                    x - 3, y - 3, x + 3, y + 3, fill="#00d8ff", outline="white"
                )
        except:
            pass


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind(
            "<Enter>",
            lambda e: canvas.bind_all(
                "<MouseWheel>",
                lambda ev: canvas.yview_scroll(-1 * (ev.delta // 120), "units"),
            ),
        )
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


class CongressApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced HOI4 Parliament Generator")
        root.geometry("520x720")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="1. Setup & Roster")
        top_f = ttk.Frame(tab1, padding=10)
        top_f.pack(fill=tk.X)

        ttk.Label(top_f, text="Mod Directory:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.dir_var = tk.StringVar(value="")
        ttk.Entry(top_f, textvariable=self.dir_var, width=35).grid(
            row=0, column=1, padx=5, sticky=tk.W
        )
        ttk.Button(top_f, text="Browse...", command=self.browse_mod_dir).grid(
            row=0, column=2, padx=5
        )

        ttk.Label(top_f, text="Country TAG:").grid(row=1, column=0, sticky=tk.W)
        self.tag_var = tk.StringVar(value="WSH")
        ttk.Entry(top_f, textvariable=self.tag_var, width=10).grid(
            row=1, column=1, padx=5, sticky=tk.W
        )
        ttk.Button(top_f, text="Load from History", command=self.load_history).grid(
            row=1, column=2, padx=5
        )

        sf = ScrollableFrame(tab1)
        sf.pack(fill=tk.BOTH, expand=True, pady=10)

        self.sub_vars = {}
        for parent, _, _, _, subs in IDEOLOGY_GROUPS:
            panel = CollapsiblePanel(
                sf.scrollable_frame,
                title=parent.replace("_ideology", "").upper().replace("_", " "),
            )
            panel.pack(fill="x", pady=2)
            n = len(subs)
            for i, (sub, _) in enumerate(subs):
                rf = ttk.Frame(panel.content_frame)
                rf.pack(fill="x", pady=2)
                ttk.Label(rf, text=sub, width=30).pack(side="left")
                v = tk.IntVar(value=(n - i))
                ttk.Entry(rf, textvariable=v, width=5).pack(side="left")
                self.sub_vars[sub] = v

        self.senate_editor = LayoutEditor(
            self.notebook, "Senate", HARDCODED_SENATE_X, HARDCODED_SENATE_Y
        )
        self.notebook.add(self.senate_editor, text="2. Senate Geometry")
        self.house_editor = LayoutEditor(
            self.notebook, "House", HARDCODED_HOUSE_X, HARDCODED_HOUSE_Y
        )
        self.notebook.add(self.house_editor, text="3. House Geometry")
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        bot_f = ttk.Frame(root, relief=tk.RAISED, borderwidth=1)
        bot_f.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)
        ttk.Label(bot_f, text="Icon GUI Scale:").pack(side=tk.LEFT, padx=(10, 0))
        self.scale_var = tk.DoubleVar(value=1.0)
        ttk.Entry(bot_f, textvariable=self.scale_var, width=5).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(
            bot_f, text="Generate Mod Files (In-Place)", command=self.generate
        ).pack(side=tk.RIGHT, padx=10)

    def browse_mod_dir(self):
        path = filedialog.askdirectory(title="Select Target Mod Folder")
        if path:
            self.dir_var.set(path)

    def _on_tab_changed(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 1:
            self.senate_editor.draw_preview()
        elif idx == 2:
            self.house_editor.draw_preview()

    def load_history(self):
        mod_dir = self.dir_var.get().strip()
        tag = self.tag_var.get().strip()
        if not mod_dir or len(tag) != 3:
            return messagebox.showerror(
                "Error", "Please provide a valid Mod Directory and TAG."
            )

        history_dir = os.path.join(mod_dir, "history", "countries")
        if not os.path.exists(history_dir):
            return messagebox.showerror(
                "Error", f"No history folder found at: {history_dir}"
            )

        target_file = next(
            (
                os.path.join(history_dir, file)
                for file in os.listdir(history_dir)
                if file.upper().startswith(tag.upper())
            ),
            None,
        )
        if not target_file:
            return messagebox.showwarning(
                "Not Found", f"No history file found for TAG {tag}"
            )

        with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        match = re.search(
            r"set_popularities\s*=\s*\{([^}]+)\}", re.sub(r"#.*", "", content)
        )
        if not match:
            return messagebox.showwarning(
                "Not Found", "Could not find set_popularities in the history file."
            )

        pairs = re.findall(
            r"([a-zA-Z0-9_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)", match.group(1)
        )
        temp_vars = {k: 0 for k in self.sub_vars.keys()}
        found = False

        for key, val in pairs:
            weight = float(val)
            parent_match = next((g for g in IDEOLOGY_GROUPS if g[0] == key), None)
            if parent_match:
                for i, (sub_id, _) in enumerate(parent_match[4]):
                    temp_vars[sub_id] += int(round(weight * (len(parent_match[4]) - i)))
                found = True
            elif key in self.sub_vars:
                temp_vars[key] += int(round(weight))
                found = True

        if found:
            for k, v in temp_vars.items():
                self.sub_vars[k].set(v)
            messagebox.showinfo(
                "Success", "Popularities loaded successfully from the history file!"
            )

    def generate(self):
        tag = self.tag_var.get().strip()
        mod_dir = self.dir_var.get().strip()
        if len(tag) != 3 or not mod_dir:
            return messagebox.showerror(
                "Error", "Valid 3-letter TAG and Mod Directory required."
            )
        try:
            weights = {k: v.get() for k, v in self.sub_vars.items()}
            build_mod_files(
                mod_dir,
                tag,
                self.senate_editor.get_coords(),
                self.house_editor.get_coords(),
                weights,
                self.scale_var.get(),
            )
            messagebox.showinfo(
                "Success",
                "Mod files updated/generated safely!\nHistory File & UI hooked correctly.",
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred during generation:\n{str(e)}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = CongressApp(root)
    root.mainloop()
