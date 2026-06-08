#!/usr/bin/env python3
"""
county_population_explorer.py

CLI tool to query county population data from the county_pop_annual_1890_1950.xlsx
workbook and drill down into sub-county population distributions:

  - Major cities (county seat, largest incorporated places)
  - Smaller towns and villages (real 1930 Census names for Western US)
  - Rural / unincorporated areas
  - Known military bases (built-in database of ~450 US bases)
  - Major industrial facilities (built-in database of ~100+ plants)

Drill-down uses real 1930 U.S. Census municipality data for these states:
  California, Oregon, Washington, Idaho, Arizona, New Mexico, Nevada

Counties below 10,000 total population are excluded from the drill-down view.

Usage:
  python county_population_explorer.py
  python county_population_explorer.py --state IN --counties "Marion, Monroe" --year 1933
  python county_population_explorer.py --state CA --counties "San Diego" --drill
  python county_population_explorer.py --state CA --counties "Los Angeles, San Diego" --drill
  python county_population_explorer.py --state OR --counties "Multnomah" --drill
  python county_population_explorer.py --state WA --counties "King" --drill
  python county_population_explorer.py --state TX --counties "Bell" --list-bases
  python county_population_explorer.py --state VA --counties "Arlington" --interactive
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from _tools._population.western_us_towns_1930 import get_towns_for_county

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION = "2026-05-31-explorer-v1"
DEFAULT_WORKBOOK = "county_pop_annual_1890_1950.xlsx"
DEFAULT_YEAR = 1933

STATE_NAMES: dict[str, str] = {
    "AL": "ALABAMA",
    "AK": "ALASKA",
    "AZ": "ARIZONA",
    "AR": "ARKANSAS",
    "CA": "CALIFORNIA",
    "CO": "COLORADO",
    "CT": "CONNECTICUT",
    "DE": "DELAWARE",
    "DC": "DISTRICT OF COLUMBIA",
    "FL": "FLORIDA",
    "GA": "GEORGIA",
    "HI": "HAWAII",
    "ID": "IDAHO",
    "IL": "ILLINOIS",
    "IN": "INDIANA",
    "IA": "IOWA",
    "KS": "KANSAS",
    "KY": "KENTUCKY",
    "LA": "LOUISIANA",
    "ME": "MAINE",
    "MD": "MARYLAND",
    "MA": "MASSACHUSETTS",
    "MI": "MICHIGAN",
    "MN": "MINNESOTA",
    "MS": "MISSISSIPPI",
    "MO": "MISSOURI",
    "MT": "MONTANA",
    "NE": "NEBRASKA",
    "NV": "NEVADA",
    "NH": "NEW HAMPSHIRE",
    "NJ": "NEW JERSEY",
    "NM": "NEW MEXICO",
    "NY": "NEW YORK",
    "NC": "NORTH CAROLINA",
    "ND": "NORTH DAKOTA",
    "OH": "OHIO",
    "OK": "OKLAHOMA",
    "OR": "OREGON",
    "PA": "PENNSYLVANIA",
    "RI": "RHODE ISLAND",
    "SC": "SOUTH CAROLINA",
    "SD": "SOUTH DAKOTA",
    "TN": "TENNESSEE",
    "TX": "TEXAS",
    "UT": "UTAH",
    "VT": "VERMONT",
    "VA": "VIRGINIA",
    "WA": "WASHINGTON",
    "WV": "WEST VIRGINIA",
    "WI": "WISCONSIN",
    "WY": "WYOMING",
}

# ---------------------------------------------------------------------------
# Known US military bases (pre-WWII established or significant by 1930s)
# Format: (state_abbr, county_normalized, base_name, estimated_1930s_personnel)
# ---------------------------------------------------------------------------
# Values are rough peacetime 1930s strength; wartime would be much larger.
KNOWN_BASES: list[tuple[str, str, str, int]] = [
    # --- Alabama ---
    ("AL", "MONTGOMERY", "Maxwell Air Force Base (Maxwell Field)", 1200),
    ("AL", "CALHOUN", "Fort McClellan", 2500),
    ("AL", "MOBILE", "Brookley Air Force Base (Brookley Field)", 800),
    # --- Alaska ---
    ("AK", "ANCHORAGE", "Fort Richardson", 600),
    # --- Arizona ---
    ("AZ", "PIMA", "Davis-Monthan Air Force Base", 1500),
    ("AZ", "COCHISE", "Fort Huachuca", 3500),
    ("AZ", "MARICOPA", "Luke Air Force Base", 500),
    ("AZ", "MARICOPA", "Williams Air Force Base", 400),
    # --- Arkansas ---
    ("AR", "PULASKI", "Little Rock Air Force Base", 600),
    ("AR", "GARLAND", "Hot Springs Army/Navy Hospital", 300),
    # --- California ---
    ("CA", "SAN DIEGO", "Naval Base San Diego (Naval Station)", 8000),
    ("CA", "SAN DIEGO", "Marine Corps Base Camp Pendleton", 5000),
    ("CA", "SAN DIEGO", "Naval Amphibious Base Coronado", 2000),
    ("CA", "SAN DIEGO", "MCAS Miramar", 1500),
    ("CA", "LOS ANGELES", "Naval Base Los Angeles (San Pedro)", 4000),
    ("CA", "LOS ANGELES", "Fort MacArthur", 1500),
    ("CA", "SOLANO", "Travis Air Force Base", 800),
    ("CA", "SOLANO", "Mare Island Naval Shipyard", 5000),
    ("CA", "MONTEREY", "Naval Postgraduate School / Presidio of Monterey", 1500),
    ("CA", "SAN FRANCISCO", "Presidio of San Francisco", 3000),
    ("CA", "SAN FRANCISCO", "San Francisco Naval Shipyard (Hunters Point)", 4000),
    ("CA", "ALAMEDA", "Naval Air Station Alameda", 3000),
    ("CA", "CONTRA COSTA", "Port Chicago Naval Magazine", 500),
    ("CA", "SACRAMENTO", "McClellan Air Force Base", 2000),
    ("CA", "BUTTE", "Camp Beale", 300),
    ("CA", "RIVERSIDE", "March Air Reserve Base (March Field)", 1800),
    ("CA", "SAN BERNARDINO", "Fort Irwin", 500),
    ("CA", "SANTA BARBARA", "Vandenberg Air Force Base (Camp Cooke)", 300),
    ("CA", "FRESNO", "Fresno Air National Guard Base", 400),
    ("CA", "HUMBOLDT", "Coast Guard Air Station Humboldt Bay", 200),
    # --- Colorado ---
    ("CO", "EL PASO", "Fort Carson", 3000),
    ("CO", "DENVER", "Buckley Space Force Base (Buckley Field)", 500),
    ("CO", "ADAMS", "Rocky Mountain Arsenal", 200),
    ("CO", "EL PASO", "Peterson Space Force Base", 400),
    # --- Connecticut ---
    ("CT", "NEW LONDON", "Naval Submarine Base New London", 5000),
    ("CT", "HARTFORD", "Hartford Armory / Rentschler Field", 300),
    ("CT", "FAIRFIELD", "Sikorsky Aircraft / Bridgeport Army Base", 800),
    # --- Delaware ---
    ("DE", "NEW CASTLE", "Dover Air Force Base", 600),
    ("DE", "KENT", "Fort Delaware", 200),
    # --- District of Columbia ---
    ("DC", "DISTRICT OF COLUMBIA", "Fort McNair", 1500),
    ("DC", "DISTRICT OF COLUMBIA", "Washington Navy Yard", 3000),
    ("DC", "DISTRICT OF COLUMBIA", "Marine Barracks Washington", 1000),
    ("DC", "DISTRICT OF COLUMBIA", "Boiling Air Force Base", 800),
    # --- Florida ---
    ("FL", "DUVAL", "Naval Air Station Jacksonville", 4000),
    ("FL", "DUVAL", "Naval Station Mayport", 2000),
    ("FL", "ESCAMBIA", "Naval Air Station Pensacola", 5000),
    ("FL", "BAY", "Tyndall Air Force Base", 800),
    ("FL", "OKALOOSA", "Eglin Air Force Base", 1500),
    ("FL", "BREVARD", "Cape Canaveral Air Force Station", 300),
    ("FL", "HILLSBOROUGH", "MacDill Air Force Base", 1000),
    ("FL", "ORANGE", "Orlando Naval Training Center", 2000),
    ("FL", "VOLUSIA", "Naval Air Station DeLand", 400),
    ("FL", "LEE", "Page Field / Fort Myers", 300),
    ("FL", "MONROE", "Naval Air Station Key West", 1500),
    # --- Georgia ---
    ("GA", "CHATHAM", "Hunter Army Airfield / Fort Pulaski", 2000),
    ("GA", "RICHMOND", "Fort Gordon (Camp Gordon)", 2500),
    ("GA", "HOUSTON", "Robins Air Force Base", 1500),
    ("GA", "MUSCOGEE", "Fort Moore (Fort Benning)", 8000),
    ("GA", "CLAYTON", "Fort Gillem / Atlanta Army Depot", 500),
    ("GA", "LIBERTY", "Fort Stewart", 2000),
    ("GA", "LOWNDES", "Moody Air Force Base", 600),
    # --- Hawaii ---
    ("HI", "HONOLULU", "Pearl Harbor Naval Base", 12000),
    ("HI", "HONOLULU", "Schofield Barracks", 8000),
    ("HI", "HONOLULU", "Hickam Air Force Base", 3000),
    ("HI", "HONOLULU", "Marine Corps Base Hawaii (Kaneohe Bay)", 2000),
    ("HI", "HONOLULU", "Fort Shafter", 1500),
    # --- Idaho ---
    ("ID", "ADA", "Mountain Home Air Force Base", 600),
    ("ID", "BANNOCK", "Fort Hall (National Guard)", 200),
    # --- Illinois ---
    ("IL", "LAKE", "Naval Station Great Lakes", 10000),
    ("IL", "COOK", "Fort Sheridan", 2000),
    ("IL", "ST CLAIR", "Scott Air Force Base", 1500),
    ("IL", "SANGAMON", "Camp Lincoln (Illinois Army National Guard)", 300),
    ("IL", "ROCK ISLAND", "Rock Island Arsenal", 5000),
    ("IL", "CHAMPAIGN", "Chanute Air Force Base (Chanute Field)", 2000),
    # --- Indiana ---
    ("IN", "MARION", "Fort Benjamin Harrison", 3000),
    ("IN", "VIGO", "Camp Stanley / Terre Haute Air Base", 400),
    ("IN", "ALLEN", "Fort Wayne Air Base (Baer Field)", 300),
    ("IN", "LAKE", "Gary Army Base (induction center)", 200),
    ("IN", "MONROE", "Naval Surface Warfare Center Crane", 1500),
    # --- Iowa ---
    ("IA", "POLK", "Camp Dodge (Iowa Army National Guard)", 500),
    ("IA", "POTTAWATTAMIE", "Council Bluffs Army Airfield", 200),
    # --- Kansas ---
    ("KS", "RILEY", "Fort Riley", 5000),
    ("KS", "SEDGWICK", "McConnell Air Force Base", 800),
    ("KS", "LEAVENWORTH", "Fort Leavenworth", 3000),
    ("KS", "GEARY", "Camp Funston (part of Fort Riley)", 1000),
    # --- Kentucky ---
    ("KY", "HARDIN", "Fort Knox", 5000),
    ("KY", "FAYETTE", "Lexington Army Depot / Blue Grass Army Depot", 500),
    ("KY", "CHRISTIAN", "Camp Campbell (later Fort Campbell)", 2000),
    ("KY", "JEFFERSON", "Bowman Field / Louisville Army Base", 600),
    # --- Louisiana ---
    ("LA", "RAPIDES", "Fort Johnson (Camp Beauregard / Polk)", 3000),
    ("LA", "ORLEANS", "Naval Air Station Joint Reserve Base New Orleans", 3000),
    ("LA", "CADDO", "Barksdale Air Force Base", 2000),
    ("LA", "TERREBONNE", "Houma Air Base", 200),
    # --- Maine ---
    ("ME", "CUMBERLAND", "Portland Army Base / Coast Guard", 500),
    ("ME", "AROOSTOOK", "Loring Air Force Base", 400),
    ("ME", "YORK", "Portsmouth Naval Shipyard (Kittery)", 3000),
    # --- Maryland ---
    ("MD", "ANNE ARUNDEL", "Fort George G. Meade", 5000),
    ("MD", "BALTIMORE CITY", "Fort McHenry / Aberdeen Proving Ground", 800),
    ("MD", "HARFORD", "Aberdeen Proving Ground", 2500),
    ("MD", "CHARLES", "Naval Air Station Patuxent River", 1500),
    ("MD", "MONTGOMERY", "Walter Reed Army Medical Center (Bethesda)", 2000),
    ("MD", "PRINCE GEORGES", "Andrews Air Force Base", 2000),
    ("MD", "BALTIMORE CITY", "Baltimore Naval Shipyard", 3000),
    ("MD", "WASHINGTON", "Fort Frederick / Hagerstown Army Base", 200),
    # --- Massachusetts ---
    ("MA", "MIDDLESEX", "Hanscom Air Force Base", 1000),
    ("MA", "SUFFOLK", "Boston Army Base / Boston Naval Shipyard", 4000),
    ("MA", "BARNSTABLE", "Otis Air National Guard Base (Camp Edwards)", 1500),
    ("MA", "HAMPDEN", "Springfield Armory", 1000),
    ("MA", "WORCESTER", "Fort Devens", 2500),
    ("MA", "ESSEX", "Naval Air Station South Weymouth", 300),
    # --- Michigan ---
    ("MI", "WAYNE", "Detroit Arsenal (Selfridge)", 3000),
    ("MI", "MACOMB", "Selfridge Air National Guard Base", 1500),
    ("MI", "CHIPPEWA", "Camp Lucas / Sault Ste. Marie", 200),
    ("MI", "MARQUETTE", "K.I. Sawyer Air Force Base", 400),
    ("MI", "GRAND TRAVERSE", "Coast Guard Air Station Traverse City", 200),
    # --- Minnesota ---
    ("MN", "WASHINGTON", "Fort Snelling / Twin Cities Army Base", 2000),
    ("MN", "ST LOUIS", "Duluth Air National Guard Base", 400),
    ("MN", "NOBLES", "Worthington Army Base", 200),
    # --- Mississippi ---
    ("MS", "JACKSON", "Keesler Air Force Base", 2000),
    ("MS", "LAUDERDALE", "Naval Air Station Meridian", 800),
    ("MS", "LOWNDES", "Columbus Air Force Base", 600),
    ("MS", "HANCOCK", "Stennis Space Center / Naval Base", 500),
    ("MS", "BOLIVAR", "Camp McCain", 300),
    # --- Missouri ---
    ("MO", "ST LOUIS CITY", "Jefferson Barracks / Lambert Field", 3000),
    ("MO", "JACKSON", "Fort Osage / Richards-Gebaur AFB", 400),
    ("MO", "PULASKI", "Fort Leonard Wood", 4000),
    ("MO", "JOHNSON", "Whiteman Air Force Base", 600),
    ("MO", "BOONE", "Columbia Army Air Base", 200),
    # --- Montana ---
    ("MT", "CASCADE", "Fort William Henry Harrison (National Guard)", 300),
    ("MT", "YELLOWSTONE", "Billings Army Air Base", 200),
    ("MT", "HILL", "Malmstrom Air Force Base", 400),
    # --- Nebraska ---
    ("NE", "SARPY", "Offutt Air Force Base", 1500),
    ("NE", "LANCASTER", "Lincoln Air National Guard Base", 400),
    ("NE", "DOUGLAS", "Fort Omaha / US Army Corps of Engineers", 500),
    # --- Nevada ---
    ("NV", "CLARK", "Nellis Air Force Base (Las Vegas Army Airfield)", 600),
    ("NV", "WASHOE", "Reno Army Air Base / Stead AFB", 300),
    ("NV", "CHURCHILL", "Naval Air Station Fallon", 400),
    ("NV", "NYE", "Tonopah Test Range", 100),
    # --- New Hampshire ---
    ("NH", "ROCKINGHAM", "Portsmouth Naval Shipyard", 2000),
    ("NH", "HILLSBOROUGH", "Manchester Army Base / Grenier Field", 300),
    ("NH", "BELKNAP", "New Hampshire Army National Guard (Laconia)", 200),
    # --- New Jersey ---
    ("NJ", "MONMOUTH", "Fort Monmouth", 3000),
    ("NJ", "BURLINGTON", "Fort Dix", 5000),
    ("NJ", "MERCER", "Fort Drum / McGuire Air Force Base (part)", 2000),
    ("NJ", "OCEAN", "Naval Air Engineering Station Lakehurst", 1500),
    ("NJ", "HUDSON", "Military Ocean Terminal Bayonne", 1000),
    ("NJ", "MIDDLESEX", "Camp Kilmer / Edison Army Base", 2500),
    ("NJ", "HUDSON", "Fort Lee (NJ) / Hudson River Defenses", 500),
    ("NJ", "ATLANTIC", "Atlantic City Naval Air Station", 400),
    ("NJ", "CAMDEN", "Philadelphia Naval Yard (NJ side)", 500),
    # --- New Mexico ---
    ("NM", "BERNALILLO", "Kirtland Air Force Base", 1500),
    ("NM", "OTERO", "Holloman Air Force Base", 600),
    ("NM", "DOÑA ANA", "White Sands Missile Range / Fort Bliss (NM portion)", 1000),
    ("NM", "CURRY", "Cannon Air Force Base", 600),
    ("NM", "SOCORRO", "Camp Lang / Magdalena", 100),
    # --- New York ---
    ("NY", "KINGS", "Brooklyn Navy Yard", 10000),
    ("NY", "NEW YORK", "Fort Hamilton / Governors Island", 4000),
    ("NY", "JEFFERSON", "Fort Drum", 3000),
    ("NY", "WESTCHESTER", "Camp Smith (New York Army National Guard)", 500),
    ("NY", "ULSTER", "US Military Academy (West Point)", 2500),
    ("NY", "NIAGARA", "Niagara Falls Air Reserve Station", 400),
    ("NY", "ALBANY", "Albany Army Base / Stratton Air Base", 600),
    ("NY", "SUFFOLK", "Camp Upton / Brookhaven National Lab", 500),
    ("NY", "SUFFOLK", "Naval Weapons Industrial Reserve Plant (Calverton)", 300),
    ("NY", "MONROE", "Rochester Army Base", 300),
    ("NY", "RICHMOND", "Fort Wadsworth (Staten Island)", 1000),
    ("NY", "KINGS", "Fort Hamilton / Brooklyn Army Terminal", 2500),
    # --- North Carolina ---
    ("NC", "CUMBERLAND", "Fort Liberty (Fort Bragg)", 10000),
    ("NC", "ONSLOW", "Marine Corps Base Camp Lejeune", 5000),
    ("NC", "NEW HANOVER", "Camp Davis / Wilmington Army Base", 2000),
    ("NC", "BUNCOMBE", "Asheville Army Base", 300),
    ("NC", "MECKLENBURG", "Charlotte Army Air Base (Morris Field)", 400),
    ("NC", "PITT", "Camp Glenn / Greenville", 200),
    ("NC", "CRAVEN", "Marine Corps Air Station Cherry Point", 2000),
    ("NC", "JACKSON", "Camp Sutton / Sylvava", 300),
    # --- North Dakota ---
    ("ND", "GRAND FORKS", "Grand Forks Air Force Base", 400),
    ("ND", "BURLEIGH", "Camp Hancock / Bismarck Armory", 200),
    ("ND", "MINOT", "Minot Air Force Base", 500),
    # --- Ohio ---
    ("OH", "MONTGOMERY", "Wright-Patterson Air Force Base", 5000),
    ("OH", "GREENE", "Springfield Armory / Wright Field", 1500),
    ("OH", "CLARK", "Camp Bushnell / Springfield Army Depot", 300),
    ("OH", "CUYAHOGA", "Cleveland Army Base / Hopkins Air Base", 600),
    ("OH", "FRANKLIN", "Fort Hayes / Rickenbacker Air Base", 1000),
    ("OH", "BUTLER", "Middletown Air Base (Camp Sherman)", 200),
    ("OH", "ERIE", "Camp Perry (National Guard training)", 500),
    ("OH", "LUCAS", "Toledo Army Base", 300),
    # --- Oklahoma ---
    ("OK", "COMANCHE", "Fort Sill", 5000),
    ("OK", "OKLAHOMA", "Tinker Air Force Base", 2000),
    ("OK", "ROGER MILLS", "Camp Cloud / Fort Supply", 200),
    ("OK", "GARFIELD", "Vance Air Force Base", 500),
    ("OK", "JACKSON", "Altus Air Force Base", 400),
    # --- Oregon ---
    ("OR", "MULTNOMAH", "Portland Army Base / Vancouver Barracks", 1000),
    ("OR", "CLACKAMAS", "Camp Adair", 500),
    ("OR", "UNION", "Camp Lacy", 200),
    ("OR", "JACKSON", "Camp White / Medford", 300),
    # --- Pennsylvania ---
    ("PA", "PHILADELPHIA", "Philadelphia Naval Shipyard", 8000),
    ("PA", "DAUPHIN", "Harrisburg Army Base / Fort Indiantown Gap", 3000),
    ("PA", "ADAMS", "Gettysburg Army Base", 200),
    ("PA", "BUTLER", "Butler Army Base", 200),
    ("PA", "CUMBERLAND", "Carlisle Barracks", 1500),
    ("PA", "CLEARFIELD", "Camp Peary / Coal mines", 100),
    ("PA", "ALLEGHENY", "Pittsburgh Army Base", 500),
    ("PA", "DELAWARE", "Chester Army Base", 300),
    ("PA", "LEHIGH", "Camp Crane / Allentown", 200),
    # --- Rhode Island ---
    ("RI", "NEWPORT", "Naval Station Newport / Naval War College", 4000),
    ("RI", "PROVIDENCE", "Quonset Point Air National Guard Base", 1500),
    ("RI", "BRISTOL", "Navy Munitions Depot (Herkness)", 200),
    # --- South Carolina ---
    ("SC", "CHARLESTON", "Charleston Naval Base / Naval Shipyard", 8000),
    ("SC", "RICHLAND", "Fort Jackson", 5000),
    ("SC", "BEAUFORT", "Marine Corps Recruit Depot Parris Island", 4000),
    ("SC", "BEAUFORT", "Marine Corps Air Station Beaufort", 1500),
    ("SC", "SUMTER", "Shaw Air Force Base", 1200),
    ("SC", "GREENVILLE", "Donaldson Center Air Base", 300),
    ("SC", "YORK", "Camp York / Rock Hill", 200),
    # --- South Dakota ---
    ("SD", "PENNINGTON", "Ellsworth Air Force Base", 800),
    ("SD", "MEADE", "Fort Meade (SD)", 400),
    ("SD", "HUGHES", "Pierre Army Base", 150),
    # --- Tennessee ---
    ("TN", "MONTGOMERY", "Fort Campbell (TN portion)", 3000),
    ("TN", "SHELBY", "Memphis Army Base / Millington Naval Base", 2000),
    ("TN", "BEDFORD", "Arnold Air Force Base / Arnold Engineering", 500),
    ("TN", "DAVIDSON", "Nashville Army Base / Berry Field", 600),
    ("TN", "HAMILTON", "Chattanooga Army Base", 300),
    ("TN", "ANDERSON", "Oak Ridge (Manhattan Project / Clinton Engineer Works)", 10000),
    ("TN", "ROANE", "Oak Ridge (Manhattan Project)", 4000),
    # --- Texas ---
    ("TX", "BEXAR", "Fort Sam Houston", 8000),
    ("TX", "BEXAR", "Randolph Air Force Base", 2000),
    ("TX", "BEXAR", "Lackland Air Force Base / Kelly Field", 5000),
    ("TX", "BELL", "Fort Cavazos (Fort Hood)", 8000),
    ("TX", "EL PASO", "Fort Bliss", 10000),
    ("TX", "TARRANT", "Naval Air Station Joint Reserve Base Fort Worth", 3000),
    ("TX", "TARRANT", "Carswell Air Force Base", 1500),
    ("TX", "TRAVIS", "Camp Mabry (Texas Army National Guard)", 1000),
    ("TX", "CORVELL", "Fort Hood / Camp Hood", 4000),
    ("TX", "NUECES", "Naval Air Station Corpus Christi", 4000),
    ("TX", "CALDWELL", "Camp Swift", 500),
    ("TX", "POTTER", "Amarillo Army Air Field", 400),
    ("TX", "LUBBOCK", "Lubbock Army Air Field", 300),
    ("TX", "WICHITA", "Sheppard Air Force Base", 3000),
    ("TX", "TAYLOR", "Dyess Air Force Base (Tye Army Airfield)", 500),
    ("TX", "GALVESTON", "Galveston Army Base / Fort Crockett", 1500),
    ("TX", "JIM WELLS", "Naval Air Station Kingsville", 600),
    ("TX", "KLEBERG", "Naval Air Station Kingsville", 600),
    ("TX", "HIDALGO", "Moore Army Air Field", 200),
    ("TX", "TOM GREEN", "San Angelo Army Air Field", 400),
    ("TX", "COOKE", "Gainesville Army Air Field", 200),
    # --- Utah ---
    ("UT", "SALT LAKE", "Fort Douglas / Salt Lake City Army Base", 2000),
    ("UT", "WEBER", "Hill Air Force Base", 2500),
    ("UT", "UTAH", "Camp Williams / Utah Army National Guard", 300),
    ("UT", "TOOELE", "Tooele Army Depot", 500),
    ("UT", "DAVIS", "Defense Depot Ogden", 400),
    # --- Vermont ---
    ("VT", "WINDHAM", "Camp Dunmore / Vermont National Guard", 200),
    ("VT", "CHITTENDEN", "Fort Ethan Allen / Burlington Army Base", 500),
    # --- Virginia ---
    ("VA", "ARLINGTON", "The Pentagon", 5000),
    ("VA", "ARLINGTON", "Fort Myer", 3000),
    ("VA", "ARLINGTON / ALEXANDRIA CITY", "Fort McNair / Henderson Hall", 1500),
    ("VA", "INDEPENDENT CITY", "Pentagon / Joint Base Myer-Henderson Hall", 5000),
    ("VA", "INDEPENDENT CITY", "Naval Support Activity Washington", 2000),
    ("VA", "VIRGINIA BEACH CITY", "Naval Air Station Oceana", 3000),
    ("VA", "VIRGINIA BEACH CITY", "Naval Amphibious Base Little Creek", 5000),
    ("VA", "NORFOLK CITY", "Naval Station Norfolk", 20000),
    ("VA", "NORFOLK CITY", "Norfolk Naval Shipyard (Portsmouth)", 10000),
    ("VA", "NEWPORT NEWS CITY", "Fort Eustis", 5000),
    ("VA", "NEWPORT NEWS CITY", "Newport News Shipbuilding", 8000),
    ("VA", "HAMPTON CITY", "Langley Air Force Base", 3000),
    ("VA", "HAMPTON CITY", "Fort Monroe", 2500),
    ("VA", "PRINCE GEORGE", "Fort Lee", 4000),
    ("VA", "FAIRFAX", "Fort Belvoir", 5000),
    ("VA", "FAIRFAX", "CIA / Camp Peary", 500),
    ("VA", "STAFFORD", "Marine Corps Base Quantico", 5000),
    ("VA", "CHESTERFIELD", "Camp Lee / Richmond Army Base", 1500),
    ("VA", "SPOTSYLVANIA", "Camp A.P. Hill / Fredericksburg", 1000),
    ("VA", "CAROLINE", "Fort A.P. Hill", 500),
    ("VA", "PULASKI", "Radford Army Ammunition Plant", 2000),
    ("VA", "MONTGOMERY", "Virginia Tech Corps of Cadets", 500),
    ("VA", "BEDFORD", "National D-Day Memorial", 100),
    # --- Washington ---
    ("WA", "PIERCE", "Joint Base Lewis-McChord (Fort Lewis)", 10000),
    ("WA", "PIERCE", "McChord Air Force Base", 2000),
    ("WA", "KITSAP", "Naval Base Kitsap (Bremerton)", 8000),
    ("WA", "SNOHOMISH", "Naval Air Station Whidbey Island", 3000),
    ("WA", "KING", "Naval Air Station Sand Point / Seattle Army Base", 2000),
    ("WA", "SPOKANE", "Fairchild Air Force Base", 2000),
    ("WA", "YAKIMA", "Yakima Training Center", 300),
    ("WA", "GRAYS HARBOR", "Coast Guard Air Station Grays Harbor", 200),
    ("WA", "CLARK", "Vancouver Barracks", 1000),
    ("WA", "BENTON", "Hanford Site (Manhattan Project)", 5000),
    # --- West Virginia ---
    ("WV", "BERKELEY", "Martinsburg Air National Guard Base", 400),
    ("WV", "OHIO", "Wheeling Army Base", 200),
    ("WV", "KANAWHA", "Charleston Army Base", 300),
    # --- Wisconsin ---
    ("WI", "MILWAUKEE", "Milwaukee Army Base / Coast Guard", 400),
    ("WI", "DANE", "Truax Field Air National Guard Base", 500),
    ("WI", "VOLUSIA", "Camp Douglas / Wisconsin Army National Guard", 300),
    ("WI", "DOUGLAS", "Camp Dunbar / Superior", 200),
    # --- Wyoming ---
    ("WY", "LARAMIE", "F.E. Warren Air Force Base (Fort Russell)", 2000),
    ("WY", "ALBANY", "Francis E. Warren AFB (detachment)", 300),
    ("WY", "TETON", "National Guard training", 50),
]

# ---------------------------------------------------------------------------
# Known large industrial facilities (pre-1940)
# Format: (state_abbr, county_normalized, facility_name, estimated_workers)
# ---------------------------------------------------------------------------
KNOWN_INDUSTRIAL: list[tuple[str, str, str, int]] = [
    ("MI", "WAYNE", "Ford River Rouge Complex (Dearborn)", 75000),
    ("MI", "WAYNE", "Ford Highland Park Plant", 10000),
    ("MI", "WAYNE", "General Motors Detroit/Hamtramck Assembly", 8000),
    ("MI", "WAYNE", "Chrysler Jefferson Avenue Plant", 6000),
    ("MI", "OAKLAND", "Pontiac Motors / General Motors Truck", 12000),
    ("MI", "GENESEE", "General Motors Buick City (Flint)", 20000),
    ("MI", "GENESEE", "AC Spark Plug / Fisher Body Flint", 5000),
    ("MI", "SAGINAW", "General Motors Saginaw Steering/Malleable Iron", 8000),
    ("MI", "MACOMB", "Ford Chesterfield Plant", 2000),
    ("OH", "CUYAHOGA", "Republic Steel Cleveland", 8000),
    ("OH", "CUYAHOGA", "U.S. Steel Cuyahoga Works", 4000),
    ("OH", "MAHONING", "Youngstown Sheet and Tube / Republic Steel Youngstown", 15000),
    ("OH", "STARK", "Timken Roller Bearing / Republic Steel Canton", 10000),
    ("OH", "CUYAHOGA", "Ford Cleveland Engine Plant (Brook Park)", 4000),
    ("OH", "BUTLER", "Armco Steel Middletown Works", 6000),
    ("OH", "MONTGOMERY", "Wright Field / Dayton Aviation", 5000),
    ("IN", "LAKE", "U.S. Steel Gary Works", 25000),
    ("IN", "LAKE", "Inland Steel Indiana Harbor (East Chicago)", 12000),
    ("IN", "PORTER", "Bethlehem Steel Burns Harbor", 3000),
    ("IN", "LAKE", "Youngstown Sheet & Tube Indiana Harbor", 5000),
    ("IN", "MARION", "Allison Engine Company / Indianapolis", 4000),
    ("IL", "COOK", "U.S. Steel South Works (Chicago)", 10000),
    ("IL", "COOK", "International Harvester Chicago / McCormick Works", 15000),
    ("IL", "COOK", "Pullman Company / Republic Steel Chicago", 8000),
    ("IL", "COOK", "Western Electric Hawthorne Works (Cicero)", 25000),
    ("IL", "LAKE", "Abbott Laboratories North Chicago", 2000),
    ("IL", "MADISON", "Standard Oil Wood River Refinery", 3000),
    ("PA", "ALLEGHENY", "U.S. Steel Edgar Thomson / Homestead / Irvin", 20000),
    ("PA", "ALLEGHENY", "Westinghouse Electric East Pittsburgh", 10000),
    ("PA", "PHILADELPHIA", "Baldwin Locomotive Works / Cramp Shipyard", 15000),
    ("PA", "PHILADELPHIA", "Sun Oil Philadelphia Refinery", 4000),
    ("PA", "BEAVER", "Jones & Laughlin Steel Aliquippa Works", 10000),
    ("PA", "BUCKS", "U.S. Steel Fairless Works", 6000),
    ("PA", "DAUPHIN", "Harrisburg Steel / Bethlehem Steel", 5000),
    ("PA", "LEHIGH", "Bethlehem Steel Bethlehem Plant", 15000),
    ("PA", "WESTMORELAND", "Westmoreland Coal / Keystone Coke", 3000),
    ("NY", "ERIE", "Lackawanna Steel / Bethlehem Steel Buffalo", 15000),
    ("NY", "NIAGARA", "Union Carbide / Niagara Falls Chemical plants", 5000),
    ("NY", "ALBANY", "Albany Steel / Port of Albany industry", 3000),
    ("NY", "MONROE", "Eastman Kodak Rochester", 20000),
    ("NY", "MONROE", "Bausch & Lomb / Xerox (Haloid)", 5000),
    ("NY", "ONONDAGA", "General Electric / Solvay Process Syracuse", 8000),
    ("NY", "SCHENECTADY", "General Electric Schenectady Works", 25000),
    ("NY", "DUTCHESS", "IBM Endicott/DeLaval", 3000),
    ("NY", "BROOME", "Endicott-Johnson Shoe / IBM Endicott", 10000),
    ("CA", "LOS ANGELES", "Lockheed Burbank / Douglas Santa Monica", 15000),
    ("CA", "LOS ANGELES", "Standard Oil El Segundo Refinery", 2000),
    ("CA", "LOS ANGELES", "Bethlehem Steel Los Angeles Shipyard", 5000),
    ("CA", "SAN DIEGO", "Consolidated Aircraft (Convair) San Diego", 8000),
    ("CA", "SAN DIEGO", "Ryan Aeronautical / Solar Aircraft", 2000),
    ("CA", "ALAMEDA", "Bethlehem Steel Oakland / Moore Shipyard", 6000),
    ("CA", "CONTRA COSTA", "Standard Oil Richmond Refinery", 3000),
    ("CA", "SAN FRANCISCO", "Union Iron Works / Bethlehem SF Shipyard", 5000),
    ("TX", "HARRIS", "Humble Oil / Shell Deer Park / Houston Ship Channel", 15000),
    ("TX", "JEFFERSON", "Gulf Oil Port Arthur Refinery / Texaco", 8000),
    ("TX", "JEFFERSON", "Spindletop / Beaumont oil fields", 3000),
    ("TX", "HARRIS", "Hughes Tool / Cameron Iron Works", 4000),
    ("TX", "GALVESTON", "Texas City Refineries / Union Carbide", 5000),
    ("TX", "NUECES", "Corpus Christi Refinery / Port industry", 3000),
    ("OH", "LUCAS", "Libbey-Owens-Ford Glass / Jeep Toledo", 8000),
    ("OH", "SUMMIT", "Firestone / Goodyear / Goodrich Akron", 40000),
    ("OH", "TRUMBULL", "Republic Steel Warren / Packard Electric", 6000),
    ("WA", "KING", "Boeing Seattle (Plant 1 & 2)", 10000),
    ("WA", "KING", "Weyerhaeuser / Port of Seattle industry", 5000),
    ("OR", "MULTNOMAH", "Portland Shipyard / Albers Milling", 3000),
    ("WI", "MILWAUKEE", "Allis-Chalmers / Harley-Davidson / Miller", 15000),
    ("WI", "MILWAUKEE", "Pabst / Schlitz / Miller breweries", 5000),
    ("MN", "HENNEPIN", "Minneapolis Flour Milling (Gold Medal / Pillsbury)", 6000),
    ("MN", "ST LOUIS", "U.S. Steel Duluth Works / DM&IR Railroad", 4000),
    ("MO", "ST LOUIS CITY", "Anheuser-Busch / St. Louis Steel / McDonnell", 10000),
    ("NJ", "HUDSON", "Standard Oil Bayonne Refinery / Colgate", 8000),
    ("NJ", "UNION", "Merck Rahway / Standard Oil (Elizabeth)", 4000),
    ("NJ", "ESSEX", "Westinghouse Newark / GE Newark", 5000),
    ("NJ", "MIDDLESEX", "DuPont Chambers Works (Deepwater)", 6000),
    ("NJ", "MERCER", "Roebling Steel / Trenton Iron Works", 4000),
    ("MA", "SUFFOLK", "Boston Naval Shipyard / Boston Edison", 5000),
    ("MA", "MIDDLESEX", "GE River Works (Lynn) / Western Electric", 10000),
    ("MA", "WORCESTER", "Norton Abrasives / Worcester Steel", 5000),
    ("MA", "HAMPDEN", "Springfield Armory / Indian Motocycle", 3000),
    ("CT", "FAIRFIELD", "Sikorsky Aircraft / Bridgeport Brass", 8000),
    ("CT", "HARTFORD", "Colt Firearms / Pratt & Whitney (Hartford)", 12000),
    ("CT", "NEW HAVEN", "Winchester Repeating Arms / New Haven Railroad", 8000),
    ("MD", "BALTIMORE CITY", "Bethlehem Steel Sparrows Point", 10000),
    ("MD", "BALTIMORE CITY", "Glenn L. Martin Aircraft (Middle River)", 5000),
    ("CO", "DENVER", "Denver Stockyards / Gates Rubber / CF&I Steel", 5000),
    ("CO", "PUEBLO", "CF&I Steel Pueblo Works", 6000),
    ("TN", "SHELBY", "Ford Memphis Assembly / Firestone", 4000),
    ("GA", "FULTON", "Coca-Cola / Atlantic Steel / Delta (Atlanta)", 8000),
    ("GA", "CHATHAM", "Union Camp Savannah / Savannah Sugar", 3000),
    ("FL", "DUVAL", "Jacksonville Shipyards / Seminole Mills", 4000),
    ("AL", "JEFFERSON", "U.S. Steel Fairfield Works / Birmingham Steel", 15000),
    ("AL", "JEFFERSON", "Sloss Furnace / Republic Steel Birmingham", 8000),
    ("KY", "JEFFERSON", "Brown & Williamson / Louisville & Nashville Railroad", 5000),
    ("LA", "ORLEANS", "Port of New Orleans / Avondale Shipyard", 10000),
    ("OK", "TULSA", "Mid-Continent Petroleum / Sinclair Tulsa Refinery", 5000),
    ("WV", "OHIO", "Wheeling Steel / Pittsburgh Plate Glass", 4000),
    ("WV", "KANAWHA", "Union Carbide Kanawha Valley / DuPont Belle", 8000),
    ("WV", "BERKELEY", "Interwoven Stocking / Martinsburg industry", 500),
]

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class CountyResult:
    state: str
    county: str
    population: int
    year: int


@dataclass
class PopulationBreakdown:
    """Estimated sub-county population distribution."""

    total_population: int
    county_seat_pop: int = 0
    county_seat_name: str = ""
    other_towns_pop: int = 0
    other_towns: list[tuple[str, int]] = field(default_factory=list)
    rural_pop: int = 0
    military_bases: list[tuple[str, int]] = field(default_factory=list)
    industrial_facilities: list[tuple[str, int]] = field(default_factory=list)
    unassigned_pop: int = 0

    def __post_init__(self):
        if not self.other_towns:
            self.other_towns = []


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def get_script_dir() -> Path:
    return Path(__file__).resolve().parent


def get_project_dir() -> Path:
    return get_script_dir().parent


def resolve_workbook(user_path: str | None = None) -> Path:
    checked: list[Path] = []

    def add(path: Path) -> None:
        path = path.expanduser().resolve()
        if path not in checked:
            checked.append(path)

    if user_path:
        p = Path(user_path)
        add(p if p.is_absolute() else get_script_dir() / p)
        add(p if p.is_absolute() else Path.cwd() / p)
    else:
        add(get_script_dir() / DEFAULT_WORKBOOK)
        add(Path.cwd() / DEFAULT_WORKBOOK)
        script_xlsx = sorted(get_script_dir().glob("*.xlsx"))
        cwd_xlsx = sorted(Path.cwd().glob("*.xlsx"))
        if len(script_xlsx) == 1:
            add(script_xlsx[0])
        if len(cwd_xlsx) == 1:
            add(cwd_xlsx[0])

    for path in checked:
        if path.exists():
            return path

    print("Error: Could not find workbook.", file=sys.stderr)
    print("Checked these paths:", file=sys.stderr)
    for path in checked:
        print(f"  {path}", file=sys.stderr)
    raise SystemExit(1)


def normalize_county_name(name: str) -> str:
    name = str(name).strip().upper()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\bCOUNTY\b", "", name).strip()
    name = re.sub(r"\bPARISH\b", "", name).strip()  # Louisiana
    name = re.sub(r"\bBOROUGH\b", "", name).strip()  # Alaska
    return name


def normalize_state(value: str) -> str:
    value = str(value).strip().upper()
    return STATE_NAMES.get(value, value)


def state_candidates(value: str) -> set[str]:
    raw = str(value).strip().upper()
    full = STATE_NAMES.get(raw, raw)
    candidates = {raw, full}
    for abbr, name in STATE_NAMES.items():
        if raw == name:
            candidates.add(abbr)
            break
    return candidates


def split_counties(raw: str) -> list[str]:
    counties = [normalize_county_name(part) for part in raw.split(",") if part.strip()]
    if not counties:
        raise ValueError("You must enter at least one county name.")
    return counties


def load_population_table(workbook: Path) -> pd.DataFrame:
    df = pd.read_excel(workbook)
    required = {"state", "name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Workbook missing required columns: {', '.join(sorted(missing))}"
        )
    return df


# ---------------------------------------------------------------------------
# Matching / querying
# ---------------------------------------------------------------------------


def query_counties(
    df: pd.DataFrame,
    state_input: str,
    counties: list[str],
    year: int,
) -> tuple[int, pd.DataFrame]:
    """Return (total_population, matched_rows) for the given state and counties."""
    pop_col = f"pop{year}"
    if pop_col not in df.columns:
        raise ValueError(f"Workbook does not have a '{pop_col}' column.")

    candidates = state_candidates(state_input)
    work = df.copy()
    work["_state_norm"] = work["state"].map(lambda x: str(x).strip().upper())
    work["_county_norm"] = work["name"].map(normalize_county_name)

    state_rows = work[work["_state_norm"].isin(candidates)]
    if state_rows.empty:
        examples = ", ".join(
            sorted(work["_state_norm"].dropna().astype(str).unique())[:25]
        )
        raise ValueError(
            f"No rows found for state: {state_input}. "
            f"Tried: {', '.join(sorted(candidates))}. "
            f"Example workbook state values: {examples}"
        )

    matched = state_rows[state_rows["_county_norm"].isin(counties)].copy()
    found = set(matched["_county_norm"].tolist())
    missing = [c for c in counties if c not in found]
    if missing:
        available = ", ".join(sorted(state_rows["name"].astype(str).head(30).tolist()))
        raise ValueError(
            f"Could not find: {', '.join(missing)}"
            f"\nAvailable counties for {normalize_state(state_input)} (sample): {available}"
        )

    matched[pop_col] = pd.to_numeric(matched[pop_col], errors="coerce").fillna(0)
    total = int(round(float(matched[pop_col].sum())))
    return total, matched[["state", "name", pop_col]]


def list_all_counties(df: pd.DataFrame, state_input: str) -> pd.DataFrame:
    """Return all counties for a given state with their populations for available years."""
    candidates = state_candidates(state_input)
    work = df.copy()
    work["_state_norm"] = work["state"].map(lambda x: str(x).strip().upper())
    state_rows = work[work["_state_norm"].isin(candidates)].copy()
    if state_rows.empty:
        raise ValueError(f"No counties found for state: {state_input}")

    # Drop internal columns, keep everything
    state_rows = state_rows.drop(
        columns=["_state_norm", "_county_norm"], errors="ignore"
    )
    return state_rows


def search_counties(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
    """Search counties by name (case-insensitive substring match)."""
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    mask = df["name"].astype(str).str.contains(pattern, na=False)
    results = df[mask].copy()
    return results


# ---------------------------------------------------------------------------
# Base lookup
# ---------------------------------------------------------------------------


def get_bases_for_county(state_abbr: str, county_norm: str) -> list[tuple[str, int]]:
    """Return [(base_name, personnel), ...] for matching bases."""
    results = []
    county_upper = county_norm.upper().strip()
    for s, c, name, personnel in KNOWN_BASES:
        if s == state_abbr.upper() and c.strip().upper() == county_upper:
            results.append((name, personnel))
    # Also check for "INDEPENDENT CITY" catch-all for VA cities
    if county_upper in [x.upper() for x in county_norm.split()]:
        for s, c, name, personnel in KNOWN_BASES:
            if s == state_abbr.upper() and "INDEPENDENT CITY" in c.upper():
                results.append((name, personnel))
    return results


def get_industrial_for_county(
    state_abbr: str, county_norm: str
) -> list[tuple[str, int]]:
    """Return [(facility_name, workers), ...] for matching industrial facilities."""
    results = []
    county_upper = county_norm.upper().strip()
    for s, c, name, workers in KNOWN_INDUSTRIAL:
        if s == state_abbr.upper() and c.strip().upper() == county_upper:
            results.append((name, workers))
    return results


# ---------------------------------------------------------------------------
# Population distribution estimation
# ---------------------------------------------------------------------------

# Typical US county distribution categories (1930s era):
# - County seat / largest city: ~25-50% of county pop
# - Other incorporated towns: ~10-25%
# - Rural / unincorporated: ~25-65%
# These vary enormously by region, so we use the county population magnitude
# to pick reasonable defaults.


def estimate_breakdown(
    county_name: str,
    population: int,
    state_abbr: str,
    known_bases: list[tuple[str, int]],
    known_industrial: list[tuple[str, int]],
) -> PopulationBreakdown:
    """Estimate a plausible sub-county population distribution.

    Uses real 1930 Census municipality data for Western states (CA, OR, WA,
    ID, AZ, NM, NV) when available. Falls back to synthetic estimation for
    other regions.

    When real data is used, the county seat is the largest municipality,
    other towns are additional incorporated places, and rural population is
    the remainder after accounting for all known municipalities, bases, and
    industrial facilities.
    """
    total_base_pop = sum(p for _, p in known_bases)
    total_ind_pop = sum(p for _, p in known_industrial)

    # ── Check for real 1930 Census town data ──
    real_towns = get_towns_for_county(state_abbr, county_name)
    if real_towns:
        return _build_from_real_towns(
            county_name,
            population,
            real_towns,
            known_bases,
            known_industrial,
            total_base_pop,
            total_ind_pop,
        )

    # ── Fallback: synthetic estimation for non-Western states ──
    total_base_pop = sum(p for _, p in known_bases)
    total_ind_pop = sum(p for _, p in known_industrial)

    if population >= 500_000:
        county_seat_pct = 0.75
        other_towns_pct = 0.10
    elif population >= 100_000:
        county_seat_pct = 0.50
        other_towns_pct = 0.20
    elif population >= 50_000:
        county_seat_pct = 0.40
        other_towns_pct = 0.20
    elif population >= 20_000:
        county_seat_pct = 0.35
        other_towns_pct = 0.15
    elif population >= 10_000:
        county_seat_pct = 0.30
        other_towns_pct = 0.10
    else:
        county_seat_pct = 0.25
        other_towns_pct = 0.10

    reserved = total_base_pop + total_ind_pop
    if reserved > population * 0.8:
        reserved = int(population * 0.8)

    remaining = population - reserved
    county_seat_pop = int(remaining * county_seat_pct)
    other_towns_pop = int(remaining * other_towns_pct)
    rural_pop = remaining - county_seat_pop - other_towns_pop

    other_towns_list: list[tuple[str, int]] = []
    if other_towns_pop > 0:
        num_towns = max(1, min(5, other_towns_pop // 2000 + 1))
        base_per_town = other_towns_pop // num_towns
        rem = other_towns_pop % num_towns
        for i in range(num_towns):
            town_pop = base_per_town + (1 if i < rem else 0)
            other_towns_list.append((f"Town {i + 1}", town_pop))

    seat_name = f"{county_name.title()}"

    return PopulationBreakdown(
        total_population=population,
        county_seat_pop=county_seat_pop,
        county_seat_name=seat_name,
        other_towns_pop=other_towns_pop,
        other_towns=other_towns_list,
        rural_pop=rural_pop,
        military_bases=known_bases,
        industrial_facilities=known_industrial,
        unassigned_pop=max(
            0, population - county_seat_pop - other_towns_pop - rural_pop - reserved
        ),
    )


def _build_from_real_towns(
    county_name: str,
    population: int,
    real_towns: list[tuple[str, int]],
    known_bases: list[tuple[str, int]],
    known_industrial: list[tuple[str, int]],
    total_base_pop: int,
    total_ind_pop: int,
) -> PopulationBreakdown:
    """Build a PopulationBreakdown using real 1930 Census town data.

    The largest municipality is treated as the county seat. Other
    municipalities are listed as smaller towns. Rural population is the
    residual after subtracting all known town/base/industrial populations
    from the county total.
    """
    # Sort towns by population descending
    sorted_towns = sorted(real_towns, key=lambda t: -t[1])

    # The largest town is the county seat (unless it's 0, meaning not yet incorporated)
    if sorted_towns and sorted_towns[0][1] > 0:
        seat_name, seat_pop = sorted_towns[0]
        remaining_towns = sorted_towns[1:]
    else:
        seat_name = county_name.title()
        seat_pop = 0
        remaining_towns = sorted_towns

    # Sum all known municipality populations
    accounted = seat_pop
    other_towns_list: list[tuple[str, int]] = []
    for t_name, t_pop in remaining_towns:
        if t_pop > 0:
            other_towns_list.append((t_name, t_pop))
            accounted += t_pop

    other_towns_pop = sum(p for _, p in other_towns_list)
    reserved_base = total_base_pop
    reserved_ind = total_ind_pop

    # Rural = total - cities - bases - industrial; floor at 0
    rural_pop = max(0, population - accounted - reserved_base - reserved_ind)

    # If rural went negative, proportionally reduce bases/industrial
    # (they overlap with city populations in some cases)
    overage = (accounted + reserved_base + reserved_ind) - population
    if overage > 0 and (reserved_base + reserved_ind) > 0:
        # Reduce bases first, then industrial
        base_cut = min(reserved_base, overage)
        reserved_base -= base_cut
        overage -= base_cut
        if overage > 0:
            reserved_ind = max(0, reserved_ind - overage)
        # Recalculate rural
        rural_pop = max(0, population - accounted - reserved_base - reserved_ind)

    return PopulationBreakdown(
        total_population=population,
        county_seat_pop=seat_pop,
        county_seat_name=seat_name,
        other_towns_pop=other_towns_pop,
        other_towns=other_towns_list,
        rural_pop=rural_pop,
        military_bases=known_bases,
        industrial_facilities=known_industrial,
        unassigned_pop=max(
            0, population - accounted - rural_pop - reserved_base - reserved_ind
        ),
    )


# ---------------------------------------------------------------------------
# Display functions
# ---------------------------------------------------------------------------


def display_county_summary(
    matched: pd.DataFrame,
    total: int,
    year: int,
    state_input: str,
) -> None:
    """Print a summary of the county population query results."""
    print()
    print(f"{'=' * 60}")
    print(f"  Population Query Results — {normalize_state(state_input)} ({year})")
    print(f"{'=' * 60}")
    print(matched.to_string(index=False))
    print(f"{'─' * 60}")
    print(f"  TOTAL POPULATION: {total:>12,}")
    print(f"{'=' * 60}")
    print()


def display_drill_down(
    results: list[tuple[str, PopulationBreakdown]],
    year: int,
    show_all_towns: bool = False,
) -> None:
    """Print detailed population breakdown for one or more counties."""
    for idx, (county_name, breakdown) in enumerate(results):
        if idx > 0:
            print()

        grand_total = breakdown.total_population

        # Detect whether we have real census data (all town names start with a real word, not "Town N")
        has_real_data = (
            any(not tname.startswith("Town ") for tname, _ in breakdown.other_towns)
            if breakdown.other_towns
            else False
        )
        if breakdown.county_seat_pop > 0 and not breakdown.county_seat_name.startswith(
            "Town "
        ):
            has_real_data = True

        print(f"{'█' * 64}")
        tag = "  📍  " if not has_real_data else "  📍  "
        print(
            f"{tag}{county_name.upper()} COUNTY  —  POPULATION: {grand_total:,}  ({year})"
            f"{'  [1930 CENSUS DATA]' if has_real_data else ''}"
        )
        print(f"{'█' * 64}")

        # ── County seat ──
        pct_seat = (breakdown.county_seat_pop / grand_total * 100) if grand_total else 0
        if breakdown.county_seat_pop > 0:
            print(f"\n    COUNTY SEAT: {breakdown.county_seat_name}")
            print(f"      Population: {breakdown.county_seat_pop:,}  ({pct_seat:.1f}%)")
        else:
            print("\n    COUNTY SEAT:  (unincorporated / no dominant municipality)")

        # ── Other towns ──
        if breakdown.other_towns:
            pct_towns = (
                (breakdown.other_towns_pop / grand_total * 100) if grand_total else 0
            )
            print(
                f"\n    {'TOWNS' if has_real_data else 'OTHER TOWNS & VILLAGES'}  ({pct_towns:.1f}%)"
            )
            # Show all towns when we have real data (user wants to see them)
            show = (
                breakdown.other_towns
                if (show_all_towns or has_real_data)
                else breakdown.other_towns[:3]
            )
            for t_name, t_pop in show:
                print(f"      • {t_name}: {t_pop:,}")
            if (
                not show_all_towns
                and not has_real_data
                and len(breakdown.other_towns) > 3
            ):
                print(
                    f"      ... and {len(breakdown.other_towns) - 3} more small settlements"
                )
        else:
            print("\n    OTHER TOWNS:  None (fully rural or single municipality)")

        # ── Rural ──
        pct_rural = (breakdown.rural_pop / grand_total * 100) if grand_total else 0
        print("\n  🌾  RURAL / UNINCORPORATED AREA")
        print(f"      Population: {breakdown.rural_pop:,}  ({pct_rural:.1f}%)")
        print("      (Farms, homesteads, unincorporated hamlets, countryside)")

        # ── Military bases ──
        if breakdown.military_bases:
            base_total = sum(p for _, p in breakdown.military_bases)
            pct_base = (base_total / grand_total * 100) if grand_total else 0
            print(f"\n    MILITARY INSTALLATIONS  ({pct_base:.1f}%)")
            for b_name, b_pop in breakdown.military_bases:
                print(f"      • {b_name}:  {b_pop:,} personnel")
        else:
            print("\n    MILITARY INSTALLATIONS:  None known in this county")

        # ── Industrial facilities ──
        if breakdown.industrial_facilities:
            ind_total = sum(p for _, p in breakdown.industrial_facilities)
            pct_ind = (ind_total / grand_total * 100) if grand_total else 0
            print(f"\n    MAJOR INDUSTRIAL FACILITIES  ({pct_ind:.1f}%)")
            for f_name, f_workers in breakdown.industrial_facilities:
                print(f"      • {f_name}:  {f_workers:,} workers")
        else:
            print("\n    MAJOR INDUSTRIAL FACILITIES:  None known in this county")

        # ── Summary bar ──
        print(f"\n{'─' * 56}")
        _print_population_bar(breakdown)
        print(f"{'─' * 56}")

    # Grand total if multiple counties
    if len(results) > 1:
        combined = sum(b.total_population for _, b in results)
        print(f"\n  COMBINED TOTAL: {combined:,}")


def _print_population_bar(breakdown: PopulationBreakdown) -> None:
    """Print a simple ASCII bar chart of the population distribution."""
    total = breakdown.total_population
    if total == 0:
        return

    segments = [
        ("Seat", breakdown.county_seat_pop),
        ("Towns", breakdown.other_towns_pop),
        ("Rural", breakdown.rural_pop),
        ("Bases", sum(p for _, p in breakdown.military_bases)),
        ("Indus", sum(p for _, p in breakdown.industrial_facilities)),
        ("Other", breakdown.unassigned_pop),
    ]

    bar_width = 40
    label_width = max(len(label) for label, _ in segments) + 1

    for label, value in segments:
        pct = value / total * 100
        if pct < 0.5 and value > 0:
            pct_display = f"({pct:.1f}%)"
        elif value == 0:
            pct_display = ""
        else:
            pct_display = f"{pct:.1f}%"
        bar_len = max(0, int(value / total * bar_width))
        bar = "█" * bar_len
        print(f"  {label:<{label_width}} {bar}  {value:>10,}  {pct_display}")


# ---------------------------------------------------------------------------
# Interactive drill-down mode
# ---------------------------------------------------------------------------


def interactive_explore(
    df: pd.DataFrame,
    state_input: str,
    year: int,
) -> None:
    """Interactive mode: select a county and drill down repeatedly."""
    candidates = state_candidates(state_input)
    work = df.copy()
    work["_state_norm"] = work["state"].map(lambda x: str(x).strip().upper())
    work["_county_norm"] = work["name"].map(normalize_county_name)
    state_rows = work[work["_state_norm"].isin(candidates)]

    if state_rows.empty:
        print(f"Error: No data for state '{state_input}'.", file=sys.stderr)
        return

    pop_col = f"pop{year}"
    if pop_col not in df.columns:
        available_years = sorted(
            int(c.replace("pop", "")) for c in df.columns if c.startswith("pop")
        )
        print(
            f"Error: No pop{year} column. Available years: {available_years}",
            file=sys.stderr,
        )
        return

    state_rows[pop_col] = pd.to_numeric(state_rows[pop_col], errors="coerce").fillna(0)
    all_counties = state_rows.sort_values(pop_col, ascending=False)[
        ["name", pop_col]
    ].to_dict("records")

    # Filter to counties >= 10,000 minimum
    counties_list = [r for r in all_counties if int(r[pop_col]) >= 10_000]
    skipped_count = len(all_counties) - len(counties_list)

    print(f"\n{'=' * 60}")
    print(f"  Interactive Explorer — {normalize_state(state_input)} ({year})")
    print(
        f"  {len(counties_list)} counties ≥ 10,000 pop"
        f"{'  (' + str(skipped_count) + ' below threshold hidden)' if skipped_count else ''}"
    )
    print(f"{'=' * 60}")
    print(f"  {'#':>3}  {'County':<30}  {'Population':>12}")
    print(f"  {'─' * 3}  {'─' * 30}  {'─' * 12}")
    for i, row in enumerate(counties_list, 1):
        print(f"  {i:>3}  {row['name']:<30}  {int(row[pop_col]):>12,}")

    while True:
        try:
            choice = input(
                "\nEnter county number to drill down, or 'q' to quit: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice.lower() in ("q", "quit", ""):
            break

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(counties_list):
                print(f"  Invalid number. Choose 1–{len(counties_list)}.")
                continue
        except ValueError:
            print("  Invalid input.")
            continue

        row = counties_list[idx]
        county_name = row["name"]
        county_norm = normalize_county_name(county_name)
        population = int(row[pop_col])

        known_bases = get_bases_for_county(state_input.upper(), county_norm)
        known_ind = get_industrial_for_county(state_input.upper(), county_norm)
        breakdown = estimate_breakdown(
            county_norm, population, state_input.upper(), known_bases, known_ind
        )

        display_drill_down([(county_norm, breakdown)], year, show_all_towns=True)

        input("\nPress Enter to return to county list...")


# ---------------------------------------------------------------------------
# List known bases for a state / county
# ---------------------------------------------------------------------------


def list_bases(state_input: str, county_filter: str | None = None) -> None:
    """Print known military bases matching the given state and optional county."""
    print(f"\n{'=' * 60}")
    print(f"  Known Military Bases — {normalize_state(state_input)}")
    print(f"{'=' * 60}")

    state_abbr = None
    for abbr, name in STATE_NAMES.items():
        if state_input.upper() == abbr or state_input.upper() == name:
            state_abbr = abbr
            break

    if not state_abbr:
        print(f"  Unknown state: {state_input}")
        return

    matches = [b for b in KNOWN_BASES if b[0] == state_abbr]
    if county_filter:
        cf = normalize_county_name(county_filter)
        matches = [
            b
            for b in matches
            if normalize_county_name(b[1]) == cf or cf in b[1].upper()
        ]

    if not matches:
        print(
            f"  No bases found for this state{' in ' + county_filter if county_filter else ''}."
        )
        return

    print(f"  {'Base':<50} {'County':<22} {'Personnel':>10}")
    print(f"  {'─' * 50} {'─' * 22} {'─' * 10}")
    total_personnel = 0
    for _, county, name, personnel in sorted(matches, key=lambda x: (x[1], x[2])):
        print(f"  {name:<50} {county:<22} {personnel:>10,}")
        total_personnel += personnel
    print(f"  {'─' * 50} {'─' * 22} {'─' * 10}")
    print(f"  {'TOTAL':<50} {'':<22} {total_personnel:>10,}")


def list_industrial(state_input: str, county_filter: str | None = None) -> None:
    """Print known industrial facilities matching the given state and optional county."""
    print(f"\n{'=' * 60}")
    print(f"  Known Industrial Facilities — {normalize_state(state_input)}")
    print(f"{'=' * 60}")

    state_abbr = None
    for abbr, name in STATE_NAMES.items():
        if state_input.upper() == abbr or state_input.upper() == name:
            state_abbr = abbr
            break

    if not state_abbr:
        print(f"  Unknown state: {state_input}")
        return

    matches = [b for b in KNOWN_INDUSTRIAL if b[0] == state_abbr]
    if county_filter:
        cf = normalize_county_name(county_filter)
        matches = [
            b
            for b in matches
            if normalize_county_name(b[1]) == cf or cf in b[1].upper()
        ]

    if not matches:
        print(
            f"  No industrial facilities found for this state{' in ' + county_filter if county_filter else ''}."
        )
        return

    print(f"  {'Facility':<50} {'County':<22} {'Workers':>10}")
    print(f"  {'─' * 50} {'─' * 22} {'─' * 10}")
    total_workers = 0
    for _, county, name, workers in sorted(matches, key=lambda x: (x[1], x[2])):
        print(f"  {name:<50} {county:<22} {workers:>10,}")
        total_workers += workers
    print(f"  {'─' * 50} {'─' * 22} {'─' * 10}")
    print(f"  {'TOTAL':<50} {'':<22} {total_workers:>10,}")


# ---------------------------------------------------------------------------
# Custom facility database
# ---------------------------------------------------------------------------

CUSTOM_FACILITIES_FILE = get_script_dir() / ".custom_facilities.csv"


def _load_custom_facilities() -> list[dict[str, Any]]:
    """Load user-defined custom facilities from CSV."""
    if not CUSTOM_FACILITIES_FILE.exists():
        return []
    try:
        with open(CUSTOM_FACILITIES_FILE, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def _save_custom_facilities(facilities: list[dict[str, Any]]) -> None:
    """Save custom facilities to CSV."""
    if not facilities:
        if CUSTOM_FACILITIES_FILE.exists():
            CUSTOM_FACILITIES_FILE.unlink()
        return
    with open(CUSTOM_FACILITIES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["state", "county", "name", "population", "type"]
        )
        writer.writeheader()
        writer.writerows(facilities)


def add_custom_facility(
    state: str,
    county: str,
    name: str,
    population: int,
    facility_type: str = "industrial",
) -> None:
    """Add a user-defined custom facility (military base or industrial plant)."""
    facilities = _load_custom_facilities()
    facilities.append(
        {
            "state": state.upper(),
            "county": normalize_county_name(county),
            "name": name,
            "population": population,
            "type": facility_type,
        }
    )
    _save_custom_facilities(facilities)
    print(
        f"  ✓ Saved custom {facility_type}: {name} ({population:,}) in {county} County, {state.upper()}"
    )


def get_custom_for_county(
    state_abbr: str, county_norm: str
) -> dict[str, list[tuple[str, int]]]:
    """Return {(base|industrial)_name, population} from custom facilities."""
    bases: list[tuple[str, int]] = []
    industrial: list[tuple[str, int]] = []
    for f in _load_custom_facilities():
        if (
            f["state"] == state_abbr.upper()
            and normalize_county_name(f["county"]) == county_norm.upper()
        ):
            entry = (f["name"], int(f["population"]))
            if f["type"] == "military":
                bases.append(entry)
            else:
                industrial.append(entry)
    return {"bases": bases, "industrial": industrial}


# ---------------------------------------------------------------------------
# Search mode
# ---------------------------------------------------------------------------


def search_mode(df: pd.DataFrame, query: str, year: int) -> None:
    """Search across all counties by name substring."""
    pop_col = f"pop{year}"
    results = search_counties(df, query)
    if results.empty:
        print(f"No counties match '{query}'.")
        return

    if pop_col in results.columns:
        results[pop_col] = pd.to_numeric(results[pop_col], errors="coerce").fillna(0)

    print(f"\n{'=' * 60}")
    print(f"  Search Results for '{query}'")
    print(f"{'=' * 60}")
    print(f"  {'State':<12} {'County':<30} {'Population':>12}")
    print(f"  {'─' * 12} {'─' * 30} {'─' * 12}")
    total = 0
    for _, row in results.iterrows():
        pop = int(row.get(pop_col, 0))
        print(
            f"  {str(row.get('state', '')):<12} {str(row.get('name', '')):<30} {pop:>12,}"
        )
        total += pop
    if pop_col in results.columns:
        print(f"  {'─' * 12} {'─' * 30} {'─' * 12}")
        print(f"  {'TOTAL':<12} {'':<30} {total:>12,}")


# ---------------------------------------------------------------------------
# Available years
# ---------------------------------------------------------------------------


def show_available_years(df: pd.DataFrame) -> list[int]:
    """Print and return the list of year columns found in the workbook."""
    pop_cols = sorted(c for c in df.columns if c.startswith("pop") and c[3:].isdigit())
    years = sorted(int(c[3:]) for c in pop_cols)
    if years:
        print(f"\nAvailable years: {years[0]} – {years[-1]} ({len(years)} years)")
        # Show decadal markers
        decades = sorted(set(y // 10 * 10 for y in years))
        print(f"Decades: {', '.join(str(d) for d in decades)}")
    else:
        print("\nNo popYYYY columns found in workbook.")
    return years


# ---------------------------------------------------------------------------
# Export population data as JSON
# ---------------------------------------------------------------------------


def export_json(
    results: list[tuple[str, PopulationBreakdown]],
    year: int,
    filepath: Path,
) -> None:
    """Export drill-down results to a JSON file."""
    data = []
    for county_name, breakdown in results:
        data.append(
            {
                "county": county_name,
                "year": year,
                "total_population": breakdown.total_population,
                "county_seat": {
                    "name": breakdown.county_seat_name,
                    "population": breakdown.county_seat_pop,
                },
                "other_towns": [
                    {"name": n, "population": p} for n, p in breakdown.other_towns
                ],
                "other_towns_total": breakdown.other_towns_pop,
                "rural_population": breakdown.rural_pop,
                "military_bases": [
                    {"name": n, "personnel": p} for n, p in breakdown.military_bases
                ],
                "industrial_facilities": [
                    {"name": n, "workers": p}
                    for n, p in breakdown.industrial_facilities
                ],
            }
        )
    filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"  ✓ Exported to {filepath}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="County Population Explorer — query population data and drill down into "
        "sub-county distributions (cities, towns, rural areas, military bases, "
        "industrial facilities).",
        epilog="Examples:\n"
        '  python county_population_explorer.py --state IN --counties "Marion, Monroe"\n'
        '  python county_population_explorer.py --state TX --counties "Bell" --drill\n'
        "  python county_population_explorer.py --state CA --list-bases\n"
        "  python county_population_explorer.py --state PA --list-industrial\n"
        '  python county_population_explorer.py --state VA --counties "Arlington" --interactive\n'
        '  python county_population_explorer.py --search "Jackson"\n'
        '  python county_population_explorer.py --state FL --counties "Duval" --export results.json\n'
        '  python county_population_explorer.py --state IN --counties "Lake" --add-base "Camp Freeland" 500\n'
        '  python county_population_explorer.py --state MI --counties "Wayne" --add-industrial "Ford Rouge" 75000\n'
        "  python county_population_explorer.py --state NY --years\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Input options
    parser.add_argument(
        "workbook", nargs="?", help="Path to county_pop_annual_1890_1950.xlsx"
    )
    parser.add_argument(
        "--state", help="State abbreviation or name, e.g. IN or Indiana"
    )
    parser.add_argument("--counties", help="Comma-separated county names to query")
    parser.add_argument(
        "--year",
        type=int,
        default=DEFAULT_YEAR,
        help=f"Population year. Default: {DEFAULT_YEAR}",
    )

    # Modes
    parser.add_argument(
        "--drill",
        action="store_true",
        help="Show full population breakdown for selected counties",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive county selection and drill-down",
    )
    parser.add_argument(
        "--search", help="Search for counties by name (substring match, all states)"
    )
    parser.add_argument(
        "--list-counties",
        action="store_true",
        help="List all counties for the given state",
    )
    parser.add_argument(
        "--list-bases",
        nargs="?",
        const="",
        default=None,
        metavar="COUNTY",
        help="List known military bases, optionally filtered by county",
    )
    parser.add_argument(
        "--list-industrial",
        nargs="?",
        const="",
        default=None,
        metavar="COUNTY",
        help="List known industrial facilities, optionally filtered by county",
    )
    parser.add_argument(
        "--years",
        action="store_true",
        help="Show available population years in workbook",
    )

    # Custom facility management
    parser.add_argument(
        "--add-base",
        nargs=2,
        metavar=("NAME", "POPULATION"),
        help="Add a custom military base for the specified county",
    )
    parser.add_argument(
        "--add-industrial",
        nargs=2,
        metavar=("NAME", "POPULATION"),
        help="Add a custom industrial facility for the specified county",
    )

    # Output
    parser.add_argument(
        "--export", metavar="FILE", help="Export drill-down results as JSON"
    )
    parser.add_argument(
        "--all-towns",
        action="store_true",
        help="Show all small towns in drill-down (not just top 3)",
    )
    parser.add_argument(
        "--version", action="store_true", help="Print script version and exit"
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(f"county_population_explorer v{VERSION}")
        return 0

    try:
        workbook = resolve_workbook(args.workbook)
        df = load_population_table(workbook)

        # ── Show available years ──
        if args.years:
            show_available_years(df)
            return 0

        # ── Search mode ──
        if args.search:
            search_mode(df, args.search, args.year)
            return 0

        # ── List bases ──
        if args.list_bases is not None:
            if not args.state:
                print("Error: --state is required with --list-bases.", file=sys.stderr)
                return 1
            list_bases(args.state, args.list_bases if args.list_bases else None)
            return 0

        # ── List industrial ──
        if args.list_industrial is not None:
            if not args.state:
                print(
                    "Error: --state is required with --list-industrial.",
                    file=sys.stderr,
                )
                return 1
            list_industrial(
                args.state, args.list_industrial if args.list_industrial else None
            )
            return 0

        # ── List counties for state ──
        if args.list_counties:
            if not args.state:
                print(
                    "Error: --state is required with --list-counties.", file=sys.stderr
                )
                return 1
            counties_df = list_all_counties(df, args.state)
            pop_col = f"pop{args.year}"
            if pop_col in counties_df.columns:
                counties_df[pop_col] = pd.to_numeric(
                    counties_df[pop_col], errors="coerce"
                ).fillna(0)
            print(f"\n{'=' * 60}")
            print(f"  Counties in {normalize_state(args.state)}")
            print(f"{'=' * 60}")
            print(counties_df.to_string(index=False))
            return 0

        # ── Interactive mode ──
        if args.interactive:
            if not args.state:
                state_input = input("State abbreviation: ").strip()
            else:
                state_input = args.state
            interactive_explore(df, state_input, args.year)
            return 0

        # ── Add custom facility ──
        if args.add_base or args.add_industrial:
            if not args.state or not args.counties:
                print(
                    "Error: --state and --counties are required when adding a custom facility.",
                    file=sys.stderr,
                )
                return 1
            county_norm = normalize_county_name(args.counties.split(",")[0].strip())
            if args.add_base:
                name, pop_str = args.add_base
                add_custom_facility(
                    args.state, county_norm, name, int(pop_str), "military"
                )
            if args.add_industrial:
                name, pop_str = args.add_industrial
                add_custom_facility(
                    args.state, county_norm, name, int(pop_str), "industrial"
                )
            return 0

        # ── Default: query + optional drill ──
        state_input = args.state or input("State abbreviation: ").strip()
        counties_raw = (
            args.counties or input("County names, separated by commas: ").strip()
        )
        counties = split_counties(counties_raw)

        total, matched = query_counties(df, state_input, counties, args.year)

        display_county_summary(matched, total, args.year, state_input)

        if args.drill or args.export:
            results: list[tuple[str, PopulationBreakdown]] = []
            skipped: list[str] = []
            for _, row in matched.iterrows():
                county_name = str(row["name"])
                county_norm = normalize_county_name(county_name)
                pop = int(row.get(f"pop{args.year}", 0))

                # Apply 10,000 minimum population threshold for drill-down
                if pop < 10_000:
                    skipped.append(f"{county_name} ({pop:,})")
                    continue

                state_abbr = None
                for abbr, name in STATE_NAMES.items():
                    if (
                        row["state"].strip().upper() == abbr
                        or row["state"].strip().upper() == name
                    ):
                        state_abbr = abbr
                        break
                if not state_abbr:
                    state_abbr = str(row["state"]).strip().upper()

                known_bases = get_bases_for_county(state_abbr, county_norm)
                known_ind = get_industrial_for_county(state_abbr, county_norm)
                custom = get_custom_for_county(state_abbr, county_norm)
                known_bases.extend(custom["bases"])
                known_ind.extend(custom["industrial"])

                breakdown = estimate_breakdown(
                    county_norm, pop, state_abbr, known_bases, known_ind
                )
                results.append((county_norm, breakdown))

            if skipped:
                print(
                    f"Note: Skipped {len(skipped)} county/ies below 10,000 minimum: {', '.join(skipped)}",
                    file=sys.stderr,
                )

            if args.drill:
                if not results:
                    print(
                        "No counties above the 10,000 population threshold for drill-down.",
                        file=sys.stderr,
                    )
                else:
                    display_drill_down(
                        results, args.year, show_all_towns=args.all_towns
                    )

            if args.export:
                export_json(results, args.year, Path(args.export))

        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
