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

# --- IDEOLOGY DEFINITIONS (STRICTLY CONSTRAINED TO 7 MAIN GROUPS) ---
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

# --- GEOMETRY DEFAULTS ---
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


# --- SHAPE MATH LOGIC ---
def get_semicircle_layout(num_seats, cx, cy, ir, or_, rows, full_circle=False):
    coords = []
    if rows < 1:
        rows = 1
    radii = (
        [or_] if rows == 1 else [ir + r * (or_ - ir) / (rows - 1) for r in range(rows)]
    )
    multiplier = 2 if full_circle else 1
    arc_lengths = [multiplier * math.pi * r for r in radii]
    total_arc = sum(arc_lengths) if sum(arc_lengths) > 0 else 1
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
    if cols < 1:
        cols = 1
    coords = []
    for i in range(num_seats):
        coords.append((sx + (i % cols) * dx, sy + (i // cols) * dy))
    return coords


# --- GENERATION LOGIC ---
def generate_fix_cascade(type_name, is_overflow):
    s = f"\n\t# Cascade {'overflows' if is_overflow else 'deficits'} for {type_name}\n"
    s += f"\tif = {{\n\t\tlimit = {{ check_variable = {{ [tag]_{type_name}_sum {'<' if not is_overflow else '>'} [tag]_{type_name}_max }} }}\n"

    if is_overflow:
        s += f"\t\tset_temp_variable = {{ [tag]_diff = [tag]_{type_name}_sum }}\n"
        s += f"\t\tsubtract_from_temp_variable = {{ [tag]_diff = [tag]_{type_name}_max }}\n"
    else:
        s += f"\t\tset_temp_variable = {{ [tag]_diff = [tag]_{type_name}_max }}\n"
        s += f"\t\tsubtract_from_temp_variable = {{ [tag]_diff = [tag]_{type_name}_sum }}\n"

    for parent, _, s_var, h_var, _ in IDEOLOGY_GROUPS:
        var = s_var if type_name == "senate" else h_var
        s += f"\t\tif = {{\n\t\t\tlimit = {{ check_variable = {{ [tag]_diff > 0 }} }}\n"
        if is_overflow:
            s += f"\t\t\tif = {{\n\t\t\t\tlimit = {{ check_variable = {{ {var} > [tag]_diff }} }}\n"
            s += f"\t\t\t\tsubtract_from_variable = {{ {var} = [tag]_diff }}\n"
            s += f"\t\t\t\tset_temp_variable = {{ [tag]_diff = 0 }}\n"
            s += f"\t\t\t}}\n\t\t\telse = {{\n"
            s += f"\t\t\t\tsubtract_from_temp_variable = {{ [tag]_diff = {var} }}\n"
            s += f"\t\t\t\tset_variable = {{ {var} = 0 }}\n"
            s += f"\t\t\t}}\n"
        else:
            s += f"\t\t\tadd_to_variable = {{ {var} = [tag]_diff }}\n"
            s += f"\t\t\tset_temp_variable = {{ [tag]_diff = 0 }}\n"
        s += f"\t\t}}\n"
    s += f"\t}}\n"
    return s


def generate_initialization(tag, sub_weights):
    s = f"\n[TAG]_initialize_subideology_shares = {{\n"
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        weights = [sub_weights.get(sub, 0) for sub, badge in subs]
        tot = sum(weights) or 1
        ratios = [w / tot for w in weights]
        for i, (sub_id, badge) in enumerate(subs):
            s += (
                f"\tset_variable = {{ [tag]_{sub_id}_share = {round(ratios[i], 3)} }}\n"
            )
    s += "}\n"
    return s.replace("[TAG]", tag.upper()).replace("[tag]", tag.lower())


def generate_subideology_split(type_name):
    s = f"\n\t# --- {type_name.capitalize()} Subideology Split (Dynamic) ---\n"
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        var = s_var if type_name == "senate" else h_var
        for i, (sub_id, badge) in enumerate(subs):
            sub_var = f"[tag]_{sub_id}_{type_name}_seats"
            if i == len(subs) - 1:
                s += f"\tset_variable = {{ {sub_var} = {var} }}\n"
                for j in range(i):
                    s += f"\tsubtract_from_variable = {{ {sub_var} = [tag]_{subs[j][0]}_{type_name}_seats }}\n"
                s += f"\tif = {{ limit = {{ check_variable = {{ {sub_var} < 0 }} }} set_variable = {{ {sub_var} = 0 }} }}\n"
            else:
                s += f"\tset_variable = {{ {sub_var} = {var} }}\n\tmultiply_variable = {{ {sub_var} = [tag]_{sub_id}_share }}\n\tround_variable = {sub_var}\n"
    return s


def generate_calculate_party_seats(tag, s_max, h_max):
    s = f"\n[TAG]_calculate_party_seats = {{\n\tset_temp_variable = {{ [tag]_senate_max = {s_max} }}\n\tset_temp_variable = {{ [tag]_senate_sum = 0 }}\n"
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        s += f"\n\tset_temp_variable = {{ [tag]_t = party_popularity@{parent} }}\n\tmultiply_temp_variable = {{ [tag]_t = [tag]_senate_max }}\n\tround_temp_variable = [tag]_t\n\tset_variable = {{ {s_var} = [tag]_t }}\n\tadd_to_temp_variable = {{ [tag]_senate_sum = {s_var} }}\n"
    s += generate_fix_cascade("senate", True)
    s += generate_fix_cascade("senate", False)
    s += generate_subideology_split("senate")

    s += f"\n\tset_temp_variable = {{ [tag]_house_max = {h_max} }}\n\tset_temp_variable = {{ [tag]_house_sum = 0 }}\n"
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        s += f"\n\tset_temp_variable = {{ [tag]_t = party_popularity@{parent} }}\n\tmultiply_temp_variable = {{ [tag]_t = [tag]_house_max }}\n\tround_temp_variable = [tag]_t\n\tset_variable = {{ {h_var} = [tag]_t }}\n\tadd_to_temp_variable = {{ [tag]_house_sum = {h_var} }}\n"
    s += generate_fix_cascade("house", True)
    s += generate_fix_cascade("house", False)
    s += generate_subideology_split("house")
    s += "}\n"
    return s.replace("[TAG]", tag.upper()).replace("[tag]", tag.lower())


def generate_localisation(tag):
    t, T = tag.lower(), tag.upper()
    s = "l_english:\n"
    s += f' {t}_senate_seat_tt:0 "{T} State Senate Seat"\n'
    s += f' {t}_house_seat_tt:0 "{T} State House Seat"\n'
    s += f' {t}_senate_seat_combined_tt:0 "[Get{T}SenateSeatName]\\n[Get{T}SenatePartyName]"\n'
    s += f' {t}_house_seat_combined_tt:0 "[Get{T}HouseSeatName]\\n[Get{T}HousePartyName]"\n'
    s += f' {t}_senate_seat_number_fallback:0 "Senate Seat [?seat_idx|+1|0]"\n'
    s += f' {t}_house_seat_number_fallback:0 "House Seat [?house_idx|+1|0]"\n'

    # Custom Subideology Roster Names
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        for sub_id, badge in subs:
            formatted_name = (
                sub_id.replace("_", " ")
                .title()
                .replace("Subideology", "Caucus")
                .replace("Ideology", "Movement")
            )
            s += f' {t}_{sub_id}_roster_name:0 "{formatted_name}"\n'

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
        s += f' {t}_senate_party_frame_{i}:0 "{name}"\n'
        s += f' {t}_house_party_frame_{i}:0 "{name}"\n'
    s += f' {T}_CONGRESS_TITLE:0 "{T} Legislature"\n'
    s += f' {T}_SENATE_SECTION:0 "Senate"\n'
    s += f' {T}_HOUSE_SECTION:0 "House"\n'
    return s


def generate_scripted_locs(tag):
    t, T = tag.lower(), tag.upper()
    s = ""
    for ch, lower, idx in [
        ("Senate", "senate", "seat_idx"),
        ("House", "house", "house_idx"),
    ]:
        s += f'defined_text = {{\n\tname = Get{T}{ch}SeatName\n\ttext = {{\n\t\tlocalization_key = "{t}_{lower}_seat_number_fallback"\n\t}}\n}}\n'
        s += f'defined_text = {{\n\tname = Get{T}{ch}PartyName\n\ttext = {{\n\t\tlocalization_key = "{t}_{lower}_party_frame_[?{t}_{lower}_gui_frame^{idx}]"\n\t}}\n}}\n'
    return s


def generate_gui_setup(tag, type_name, coords):
    s = f"\n[TAG]_{type_name}_gui_setup = {{\n\tclear_array = [tag]_{type_name}_gui_x\n\tclear_array = [tag]_{type_name}_gui_y\n\tclear_array = [tag]_{type_name}_gui_frame\n"
    for x, y in coords:
        s += f"\tadd_to_array = {{ [tag]_{type_name}_gui_x = {int(x)} }}\n\tadd_to_array = {{ [tag]_{type_name}_gui_y = {int(y)} }}\n"
    for _ in coords:
        s += f"\tadd_to_array = {{ [tag]_{type_name}_gui_frame = 0 }}\n"
    s += "}\n"
    return s.replace("[TAG]", tag.upper()).replace("[tag]", tag.lower())


def generate_all(tag, mod_dir, sen_c, hse_c, weights, scale):
    T, t = tag.upper(), tag.lower()

    # 1. Effects
    eff = generate_initialization(tag, weights)
    eff += generate_calculate_party_seats(tag, len(sen_c), len(hse_c))

    # Roster building (Now with parallel custom names array)
    eff += f"\n[TAG]_build_roster = {{\n\tclear_array = [tag]_roster_tokens\n\tclear_array = [tag]_roster_names_array\n\tclear_array = [tag]_roster_frames\n\tclear_array = [tag]_roster_colors\n\tclear_array = [tag]_roster_senate_seats\n\tclear_array = [tag]_roster_house_seats\n"
    for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
        for sub_id, badge in subs:
            eff += f"\n\tif = {{\n\t\tlimit = {{ OR = {{ check_variable = {{ [tag]_{sub_id}_senate_seats > 0 }} check_variable = {{ [tag]_{sub_id}_house_seats > 0 }} }} }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_tokens = token:{sub_id} }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_names_array = token:[tag]_{sub_id}_roster_name }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_frames = {badge} }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_colors = {color} }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_senate_seats = [tag]_{sub_id}_senate_seats }}\n"
            eff += f"\t\tadd_to_array = {{ [tag]_roster_house_seats = [tag]_{sub_id}_house_seats }}\n\t}}"
    eff += "\n}\n"

    eff += generate_gui_setup(tag, "senate", sen_c) + generate_gui_setup(
        tag, "house", hse_c
    )

    for ch in ("senate", "house"):
        eff += f"\n[TAG]_{ch}_reload = {{\n"
        for i, (name, *_) in enumerate(IDEOLOGY_GROUPS, 1):
            eff += f"\tset_temp_variable = {{ [tag]_p{i} = [tag]_{name.split('_')[0]}_{ch}_seats }}\n"
        eff += "\n".join(
            f"\tadd_to_temp_variable = {{ [tag]_p{i} = [tag]_p{i - 1} }}"
            for i in range(2, 8)
        )
        eff += f"\n\tclear_array = [tag]_{ch}_gui_frame\n"
        for i in range(1, 8):
            eff += f"\tresize_array = {{ array = [tag]_{ch}_gui_frame value = {i} size = [tag]_p{i} }}\n"
        eff += "}\n"

    eff += f"\n[TAG]_recalculate_all_seats = {{\n\t[TAG]_calculate_party_seats = yes\n\t[TAG]_build_roster = yes\n\t[TAG]_senate_gui_setup = yes\n\t[TAG]_house_gui_setup = yes\n\t[TAG]_senate_reload = yes\n\t[TAG]_house_reload = yes\n}}\n"
    eff = eff.replace("[TAG]", T).replace("[tag]", t)

    # 2. GUI Structure (Wiring roster names to the new array)
    gui = f"""guiTypes = {{
	containerWindowType = {{
		name = "{t}_congress_gui"
		position = {{ x = 545 y = 4 }}
		size = {{ width = 380 height = 460 }}
		background = {{ name = "congress_panel_bg" quadTextureSprite = "GFX_tiled_bg" }}
		clipping = no
		iconType = {{ name = "title_header_icon" spriteType = "GFX_congress_header" position = {{ x = 0 y = 3 }} }}
		instantTextboxType = {{ name = "congress_title" position = {{ x = 0 y = 8 }} font = "hoi_24header" text = "{T}_CONGRESS_TITLE" maxWidth = 310 maxHeight = 20 format = centre }}
		instantTextboxType = {{ name = "senate_section_label" position = {{ x = 21 y = 45 }} font = "hoi_18mbs" text = "{T}_SENATE_SECTION" maxWidth = 170 maxHeight = 16 format = left }}
		gridBoxType = {{ name = "{t}_senate_diagram_container" position = {{ x = 16 y = 70 }} size = {{ width = 290 height = 155 }} slotsize = {{ width = 100%% height = 1 }} max_slots_horizontal = 1 add_horizontal = no }}
		instantTextboxType = {{ name = "house_section_label" position = {{ x = 21 y = 245 }} font = "hoi_18mbs" text = "{T}_HOUSE_SECTION" maxWidth = 170 maxHeight = 16 format = left }}
		gridBoxType = {{ name = "{t}_house_diagram_container" position = {{ x = 18 y = 270 }} size = {{ width = 295 height = 175 }} slotsize = {{ width = 100%% height = 1 }} max_slots_horizontal = 1 add_horizontal = no }}
		buttonType = {{ name = "open_roster_button" position = {{ x = 270 y = 8 }} quadTextureSprite = "GFX_button_94x31" buttonFont = "hoi_16mbs" buttonText = "Roster" clicksound = click_default }}
		buttonType = {{ name = "congress_close_button" position = {{ x = 354 y = 6 }} quadTextureSprite = "GFX_closebutton" buttonFont = "Main_14_black" clicksound = click_default }}
	}}
	containerWindowType = {{
		name = "{t}_congress_roster_panel"
		position = {{ x = 925 y = 4 }}
		size = {{ width = 300 height = 460 }}
		background = {{ name = "roster_bg" quadTextureSprite = "GFX_tiled_bg" }}
		instantTextboxType = {{ name = "roster_title" position = {{ x = 0 y = 15 }} font = "hoi_24header" text = "Active Subideologies" maxWidth = 300 format = center }}
		
		containerWindowType = {{
			name = "{t}_roster_scroll_area"
			position = {{ x = 10 y = 50 }}
			size = {{ width = 280 height = 400 }}
			verticalScrollbar = "right_vertical_slider"
			margin = {{ top = 5 bottom = 5 }}
			smooth_scrolling = yes
			scroll_wheel_factor = 40
			background = {{ name = "Background" quadTextureSprite = "GFX_tiled_window_transparent" }}
			
			gridBoxType = {{
				name = "{t}_roster_grid"
				position = {{ x = 0 y = 0 }}
				size = {{ width = 100%% height = 100%% }}
				slotsize = {{ width = 270 height = 65 }}
				max_slots_horizontal = 1
				add_horizontal = no
				format = "UPPER_LEFT"
			}}
		}}
	}}
	containerWindowType = {{
		name = "{t}_senate_gui_seat"
		position = {{ x = 40 y = 0 }}
		clipping = no
		iconType = {{ name = "{t}_senate_seat_icon" spriteType = "GFX_seat_icon" frame = 0 scale = {scale} pdx_tooltip = "{t}_senate_seat_combined_tt" }}
	}}
	containerWindowType = {{
		name = "{t}_house_gui_seat"
		position = {{ x = 35 y = 0 }}
		clipping = no
		iconType = {{ name = "{t}_house_seat_icon" spriteType = "GFX_seat_icon" frame = 0 scale = {scale} pdx_tooltip = "{t}_house_seat_combined_tt" }}
	}}
	containerWindowType = {{
		name = "{t}_roster_entry"
		size = {{ width = 270 height = 60 }}
		background = {{ name = "bg" quadTextureSprite = "GFX_tiled_window_transparent" }}
		iconType = {{ name = "roster_color_icon" spriteType = "GFX_seat_icon" position = {{ x = 5 y = 20 }} }}
		iconType = {{ name = "roster_badge_icon" spriteType = "GFX_subideology_badge_large" position = {{ x = 30 y = 5 }} scale = 0.7 }}
		instantTextboxType = {{ name = "roster_name" position = {{ x = 85 y = 10 }} font = "hoi_16mbs" text = "[?{t}_roster_names_array^roster_idx.GetTokenLocalizedKey]" maxWidth = 180 maxHeight = 16 fixedsize = yes }}
		instantTextboxType = {{ name = "roster_seats" position = {{ x = 85 y = 30 }} font = "hoi_16mbs" text = "Senate: [?{t}_roster_senate_seats^roster_idx|Y0] | House: [?{t}_roster_house_seats^roster_idx|Y0]" maxWidth = 180 maxHeight = 16 }}
	}}
}}"""

    # 3. Scripted GUI Structure
    sgui = f"""scripted_gui = {{
	{t}_congress_button_container = {{ window_name = "congress_button_container" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no tag = {T} }}
		effects = {{ congress_button_click = {{ if = {{ limit = {{ tag = {T} }} {T}_recalculate_all_seats = yes }} if = {{ limit = {{ NOT = {{ has_country_flag = congress_visible }} }} set_country_flag = congress_visible }} else = {{ clr_country_flag = congress_visible clr_country_flag = congress_roster_visible }} }} }} }}
	
	{t}_congress_screen_container = {{ window_name = "{t}_congress_gui" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no has_country_flag = congress_visible tag = {T} }}
		dynamic_lists = {{ {t}_senate_diagram_container = {{ array = {t}_senate_gui_x change_scope = no entry_container = {t}_senate_gui_seat index = seat_idx }} {t}_house_diagram_container = {{ array = {t}_house_gui_x change_scope = no entry_container = {t}_house_gui_seat index = house_idx }} }}
		properties = {{ {t}_senate_seat_icon = {{ x = {t}_senate_gui_x^seat_idx y = {t}_senate_gui_y^seat_idx frame = {t}_senate_gui_frame^seat_idx }} {t}_house_seat_icon = {{ x = {t}_house_gui_x^house_idx y = {t}_house_gui_y^house_idx frame = {t}_house_gui_frame^house_idx }} }}
		effects = {{ congress_close_button_click = {{ clr_country_flag = congress_visible clr_country_flag = congress_roster_visible }} open_roster_button_click = {{ if = {{ limit = {{ has_country_flag = congress_roster_visible }} clr_country_flag = congress_roster_visible }} else = {{ set_country_flag = congress_roster_visible }} }} }} }}
	
	{t}_congress_roster_panel_visibility = {{ window_name = "{t}_congress_roster_panel" context_type = player_context parent_window_token = politics_tab visible = {{ is_ai = no has_country_flag = congress_visible has_country_flag = congress_roster_visible tag = {T} }} }}
	
	{t}_congress_roster_scroll_container = {{ window_name = "{t}_roster_scroll_area" parent_window_name = "{t}_congress_roster_panel" context_type = player_context visible = {{ always = yes }}
		dynamic_lists = {{ {t}_roster_grid = {{ array = {t}_roster_tokens change_scope = no entry_container = {t}_roster_entry index = roster_idx }} }}
		properties = {{ roster_badge_icon = {{ frame = {t}_roster_frames^roster_idx }} roster_color_icon = {{ frame = {t}_roster_colors^roster_idx }} }} }}
}}"""

    # 4. Safe Non-Destructive File Exports
    out = mod_dir if mod_dir else f"_tools/gui/congress/output_{T}"

    os.makedirs(f"{out}/common/scripted_effects", exist_ok=True)
    os.makedirs(f"{out}/common/scripted_guis", exist_ok=True)
    os.makedirs(f"{out}/common/scripted_localisation", exist_ok=True)
    os.makedirs(f"{out}/interface/congress", exist_ok=True)
    os.makedirs(f"{out}/localisation/english", exist_ok=True)

    # Note: Generating tag-specific filenames ensures it never overwrites generic mod files
    with open(
        f"{out}/common/scripted_effects/{t}_congress_setup.txt", "w", encoding="utf-8"
    ) as f:
        f.write(eff)
    with open(
        f"{out}/common/scripted_guis/{t}_congress_gui.txt", "w", encoding="utf-8"
    ) as f:
        f.write(sgui)
    with open(
        f"{out}/common/scripted_localisation/{t}_congress_scripted_locs.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(generate_scripted_locs(tag))
    with open(
        f"{out}/interface/congress/{t}_congress_gui.gui", "w", encoding="utf-8"
    ) as f:
        f.write(gui)
    with open(
        f"{out}/localisation/english/{t}_congress_l_english.yml",
        "w",
        encoding="utf-8-sig",
    ) as f:
        f.write(generate_localisation(tag))

    return out


# --- TKINTER APP ---
class CollapsiblePanel(ttk.Frame):
    def __init__(self, parent, title, on_randomize=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.show = tk.BooleanVar(value=False)
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill="x", pady=2)
        self.toggle_btn = ttk.Checkbutton(
            self.header_frame,
            width=3,
            text="+",
            command=self.toggle,
            variable=self.show,
            style="Toolbutton",
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
        if self.show.get():
            self.content_frame.pack(fill="x", expand=True, padx=20, pady=2)
            self.toggle_btn.config(text="-")
        else:
            self.content_frame.forget()
            self.toggle_btn.config(text="+")


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


class LayoutEditor(ttk.Frame):
    def __init__(self, parent, title, hardcoded_x, hardcoded_y):
        super().__init__(parent)
        self.hardcoded_x = hardcoded_x
        self.hardcoded_y = hardcoded_y
        self.num_seats_var = tk.IntVar(value=len(hardcoded_x))
        self.shape_var = tk.StringVar(value="Default")

        self.cx_var = tk.IntVar(value=140)
        self.cy_var = tk.IntVar(value=160)
        self.ir_var = tk.IntVar(value=60)
        self.or_var = tk.IntVar(value=130)
        self.rows_var = tk.IntVar(value=4)

        self.sx_var = tk.IntVar(value=10)
        self.sy_var = tk.IntVar(value=10)
        self.dx_var = tk.IntVar(value=15)
        self.dy_var = tk.IntVar(value=15)
        self.cols_var = tk.IntVar(value=15)

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
        self.canvas.bind("<Visibility>", lambda e: self.draw_preview())

        self.params_frame = ttk.Frame(self)
        self.params_frame.pack(fill=tk.X, pady=5)
        self.semi_frame = ttk.Frame(self.params_frame)
        self.grid_frame = ttk.Frame(self.params_frame)

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
                full_circle=True,
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


class CongressApp:
    def __init__(self, root):
        self.root = root
        root.title("Advanced HOI4 Parliament Generator")
        root.geometry("520x720")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # TAB 1: General & Roster
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="1. Setup & Roster")
        top_f = ttk.Frame(tab1, padding=10)
        top_f.pack(fill=tk.X)

        ttk.Label(top_f, text="Country TAG:").grid(row=0, column=0, sticky=tk.W)
        self.tag_var = tk.StringVar(value="WSH")
        ttk.Entry(top_f, textvariable=self.tag_var, width=8).grid(
            row=0, column=1, padx=5, sticky=tk.W
        )

        ttk.Label(top_f, text="Mod Directory:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.dir_var = tk.StringVar(value="")
        ttk.Entry(top_f, textvariable=self.dir_var, width=25).grid(
            row=1, column=1, padx=5, sticky=tk.W
        )
        ttk.Button(top_f, text="Browse...", command=self.browse_mod_dir).grid(
            row=1, column=2, padx=5
        )

        btn_frame = ttk.Frame(top_f)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky=tk.W)
        ttk.Button(
            btn_frame, text="Load History Defaults", command=self.load_history
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            btn_frame, text="Randomize All Weights", command=self.randomize_all
        ).pack(side=tk.LEFT)

        sf = ScrollableFrame(tab1)
        sf.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.sub_vars = {}
        for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
            sub_ids = [s[0] for s in subs]
            panel = CollapsiblePanel(
                sf.scrollable_frame,
                title=parent.replace("_ideology", "").upper().replace("_", " "),
                on_randomize=lambda s=sub_ids: self.randomize_group(s),
            )
            panel.pack(fill="x", pady=2)
            n = len(subs)
            for i, (sub, badge) in enumerate(subs):
                rf = ttk.Frame(panel.content_frame)
                rf.pack(fill="x", pady=2)
                ttk.Label(rf, text=sub, width=30).pack(side="left")
                v = tk.IntVar(value=(n - i))
                ttk.Entry(rf, textvariable=v, width=5).pack(side="left")
                self.sub_vars[sub] = v

        # TAB 2 & 3: Chamber Layouts
        self.senate_editor = LayoutEditor(
            self.notebook, "Senate", HARDCODED_SENATE_X, HARDCODED_SENATE_Y
        )
        self.notebook.add(self.senate_editor, text="2. Senate Geometry")
        self.house_editor = LayoutEditor(
            self.notebook, "House", HARDCODED_HOUSE_X, HARDCODED_HOUSE_Y
        )
        self.notebook.add(self.house_editor, text="3. House Geometry")

        # BOTTOM GENERATE BAR
        bot_f = ttk.Frame(root, relief=tk.RAISED, borderwidth=1)
        bot_f.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)
        ttk.Label(bot_f, text="Icon GUI Scale:").pack(side=tk.LEFT, padx=(10, 0))
        self.scale_var = tk.DoubleVar(value=1.0)
        ttk.Entry(bot_f, textvariable=self.scale_var, width=5).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(bot_f, text="Generate Mod Files", command=self.generate).pack(
            side=tk.RIGHT, padx=10
        )

    def browse_mod_dir(self):
        path = filedialog.askdirectory(title="Select Target Mod Folder")
        if path:
            self.dir_var.set(path)

    def load_history(self):
        filepath = filedialog.askopenfilename(
            title="Select Country History File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        filename = os.path.basename(filepath)
        tag_match = re.match(r"^([A-Z]{3})\b", filename, re.IGNORECASE)
        if tag_match:
            self.tag_var.set(tag_match.group(1).upper())
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            content = re.sub(r"#.*", "", content)
            match = re.search(r"set_popularities\s*=\s*\{([^}]+)\}", content)
            if not match:
                return messagebox.showwarning(
                    "Not Found",
                    "Could not find 'set_popularities = { ... }' in the selected file.",
                )
            pairs = re.findall(
                r"([a-zA-Z0-9_]+)\s*=\s*([0-9]+(?:\.[0-9]+)?)", match.group(1)
            )
            if not pairs:
                return messagebox.showwarning(
                    "Not Found",
                    "Could not parse any key/value popularities inside the block.",
                )

            temp_vars = {k: 0 for k in self.sub_vars.keys()}
            touched_parents = set()
            found_any = False

            for key, val in pairs:
                weight = float(val)
                parent_match = next((g for g in IDEOLOGY_GROUPS if g[0] == key), None)
                if parent_match:
                    subs = parent_match[4]
                    n = len(subs)
                    for i, (sub_id, _) in enumerate(subs):
                        temp_vars[sub_id] += int(round(weight * (n - i)))
                    touched_parents.add(parent_match[0])
                    found_any = True
                elif key in self.sub_vars:
                    temp_vars[key] += int(round(weight))
                    for parent, _, _, _, subs in IDEOLOGY_GROUPS:
                        if any(s[0] == key for s in subs):
                            touched_parents.add(parent)
                            break
                    found_any = True

            if found_any:
                for parent, color, s_var, h_var, subs in IDEOLOGY_GROUPS:
                    n = len(subs)
                    if parent in touched_parents:
                        for sub_id, _ in subs:
                            self.sub_vars[sub_id].set(temp_vars[sub_id])
                    else:
                        for i, (sub_id, _) in enumerate(subs):
                            self.sub_vars[sub_id].set(n - i)
                messagebox.showinfo(
                    "Success", "Popularities loaded & distributed from history file!"
                )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Found popularities, but none matched the known ideology/subideology keys.",
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def randomize_group(self, sub_ids):
        for sid in sub_ids:
            self.sub_vars[sid].set(random.randint(0, 10))

    def randomize_all(self):
        for v in self.sub_vars.values():
            v.set(random.randint(0, 10))

    def generate(self):
        tag = self.tag_var.get().strip()
        mod_dir = self.dir_var.get().strip()
        if len(tag) != 3:
            return messagebox.showerror("Error", "TAG must be 3 letters.")
        try:
            weights = {k: v.get() for k, v in self.sub_vars.items()}
            sc = self.scale_var.get()
        except:
            return messagebox.showerror("Error", "Check numerical inputs.")
        out = generate_all(
            tag,
            mod_dir,
            self.senate_editor.get_coords(),
            self.house_editor.get_coords(),
            weights,
            sc,
        )
        messagebox.showinfo(
            "Success",
            f"Mod files generated safely without overwriting global configs:\n'{out}'",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = CongressApp(root)
    root.mainloop()
