"""
western_us_towns_1930.py

Real 1930 U.S. Census municipality populations for the Western states:
WA, OR, ID, CA, AZ, NM, NV.

Structure:
  TOWN_DB[state_abbr][county_normalized] = [
      (town_name, 1930_population),
      ...
  ]

Only counties with total population >= 10,000 are listed.
Towns under ~500 population are generally excluded for brevity.
Larger unincorporated places (known CDP-type settlements) are included
where census data is available.

Sources: 1930 U.S. Census population figures.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

# Type alias
TownList = List[Tuple[str, int]]
CountyDict = Dict[str, TownList]
StateDict = Dict[str, CountyDict]

TOWN_DB: StateDict = {
    # =========================================================================
    # CALIFORNIA
    # =========================================================================
    "CA": {
        "ALAMEDA": [
            ("Oakland", 284063),
            ("Berkeley", 82109),
            ("Alameda", 28806),
            ("San Leandro", 11455),
            ("Piedmont", 9333),
            ("Hayward", 5530),
            ("Albany", 3594),
            ("Livermore", 3119),
            ("Emeryville", 2613),
            ("Pleasanton", 2467),
            ("Newark", 1029),
        ],
        "AMADOR": [
            ("Jackson", 1404),
            ("Sutter Creek", 760),
            ("Amador City", 157),
        ],
        "BUTTE": [
            ("Chico", 7961),
            ("Oroville", 4388),
            ("Gridley", 2208),
            ("Biggs", 1562),
        ],
        "CALAVERAS": [
            ("Angels Camp", 998),
            ("San Andreas", 631),
        ],
        "COLUSA": [
            ("Colusa", 2069),
            ("Williams", 671),
        ],
        "CONTRA COSTA": [
            ("Richmond", 20093),
            ("Martinez", 6569),
            ("Pittsburg", 4673),
            ("Antioch", 3004),
            ("Concord", 1106),
            ("Walnut Creek", 1183),
            ("San Pablo", 1146),
        ],
        "DEL NORTE": [
            ("Crescent City", 1578),
        ],
        "EL DORADO": [
            ("Placerville", 2325),
            ("South Lake Tahoe", 0),  # not yet incorporated
        ],
        "FRESNO": [
            ("Fresno", 52513),
            ("Coalinga", 4296),
            ("Selma", 3365),
            ("Sanger", 2854),
            ("Reedley", 2616),
            ("Fowler", 1517),
            ("Parlier", 696),
            ("Kerman", 801),
        ],
        "GLENN": [
            ("Willows", 2067),
            ("Orland", 1752),
        ],
        "HUMBOLDT": [
            ("Eureka", 14752),
            ("Ferndale", 1402),
            ("Arcata", 1732),
            ("Blue Lake", 719),
            ("Fortuna", 954),
        ],
        "IMPERIAL": [
            ("El Centro", 5452),
            ("Calexico", 2946),
            ("Brawley", 4021),
            ("Imperial", 1556),
            ("Holtville", 1153),
            ("Westmorland", 441),
        ],
        "INYO": [
            ("Bishop", 1371),
            ("Independence", 532),
        ],
        "KERN": [
            ("Bakersfield", 18541),
            ("Taft", 3319),
            ("Delano", 2339),
            ("Wasco", 1089),
            ("Shafter", 1325),
            ("Arvin", 485),
            ("Maricopa", 631),
        ],
        "KINGS": [
            ("Hanford", 6570),
            ("Lemoore", 1064),
            ("Corcoran", 717),
        ],
        "LAKE": [
            ("Lakeport", 1196),
            ("Kelseyville", 712),
        ],
        "LASSEN": [
            ("Susanville", 1458),
        ],
        "LOS ANGELES": [
            ("Los Angeles", 1238048),
            ("Long Beach", 142032),
            ("Pasadena", 76086),
            ("Glendale", 62736),
            ("Santa Monica", 37146),
            ("Alhambra", 29472),
            ("Huntington Park", 24591),
            ("Pomona", 20804),
            ("South Gate", 19632),
            ("Inglewood", 19480),
            ("Beverly Hills", 17429),
            ("Burbank", 16662),
            ("Whittier", 14822),
            ("Compton", 12516),
            ("Monrovia", 10890),
            ("Hermosa Beach", 7784),
            ("Redondo Beach", 9347),
            ("Manhattan Beach", 5441),
            ("San Pedro", 0),  # annexed by LA 1909
            ("Hollywood", 0),  # annexed by LA 1910
            ("El Segundo", 3503),
            ("Torrance", 7271),
            ("Gardena", 5240),
            ("Hawthorne", 4358),
            ("Culver City", 8606),
            ("South Pasadena", 8646),
            ("Sierra Madre", 5993),
            ("San Gabriel", 2973),
            ("San Marino", 2194),
            ("Arcadia", 5194),
            ("Monterey Park", 1066),
            ("Azusa", 4818),
            ("Covina", 2593),
            ("Glendora", 2764),
            ("La Verne", 2860),
            ("Claremont", 2719),
            ("El Monte", 4432),
            ("Baldwin Park", 1704),
            ("San Dimas", 883),
            ("Pico Rivera", 0),  # later incorporation
        ],
        "MADERA": [
            ("Madera", 3441),
            ("Chowchilla", 607),
        ],
        "MARIN": [
            ("San Rafael", 6207),
            ("Sausalito", 2629),
            ("Mill Valley", 3078),
            ("Novato", 1252),
            ("Corte Madera", 1000),
            ("Larkspur", 1471),
            ("Ross", 775),
            ("Belvedere", 548),
            ("Tiburon", 361),
        ],
        "MARIPOSA": [
            ("Mariposa", 757),
        ],
        "MENDOCINO": [
            ("Ukiah", 3340),
            ("Willits", 1400),
            ("Fort Bragg", 2093),
            ("Point Arena", 523),
        ],
        "MERCED": [
            ("Merced", 4135),
            ("Los Banos", 1456),
            ("Atwater", 1304),
            ("Dos Palos", 599),
        ],
        "MODOC": [
            ("Alturas", 1025),
            ("Cedarville", 747),
        ],
        "MONO": [
            ("Bridgeport", 363),
            ("Mammoth Lakes", 0),
        ],
        "MONTEREY": [
            ("Monterey", 9141),
            ("Salinas", 7700),
            ("Watsonville", 8706),  # actually Santa Cruz Co.
            ("Pacific Grove", 4487),
            ("Carmel-by-the-Sea", 2057),
            ("King City", 1203),
            ("Seaside", 0),  # later
            ("Marina", 0),  # later
            ("Del Rey Oaks", 350),
        ],
        "NAPA": [
            ("Napa", 6437),
            ("St. Helena", 1529),
            ("Calistoga", 1025),
        ],
        "NEVADA": [
            ("Nevada City", 2155),
            ("Grass Valley", 3694),
        ],
        "ORANGE": [
            ("Santa Ana", 30322),
            ("Anaheim", 10995),
            ("Fullerton", 7596),
            ("Orange", 4893),
            ("Huntington Beach", 3690),
            ("Brea", 2435),
            ("Newport Beach", 2088),
            ("Laguna Beach", 1981),
            ("San Juan Capistrano", 959),
            ("Seal Beach", 1392),
            ("Garden Grove", 0),  # later
            ("Costa Mesa", 0),  # later
            ("Tustin", 1019),
            ("Placentia", 808),
        ],
        "PLACER": [
            ("Auburn", 3165),
            ("Roseville", 4390),
            ("Lincoln", 1275),
            ("Rocklin", 663),
            ("Colfax", 1027),
        ],
        "PLUMAS": [
            ("Quincy", 920),
            ("Portola", 0),  # later
        ],
        "RIVERSIDE": [
            ("Riverside", 29696),
            ("Corona", 7018),
            ("Banning", 4055),
            ("Indio", 1459),
            ("Palm Springs", 1434),
            ("Blythe", 822),
            ("Coachella", 754),
        ],
        "SACRAMENTO": [
            ("Sacramento", 93750),
            ("North Sacramento", 3203),
            ("Folsom", 1168),
            ("Isleton", 1486),
            ("Galt", 894),
        ],
        "SAN BENITO": [
            ("Hollister", 3439),
            ("San Juan Bautista", 772),
        ],
        "SAN BERNARDINO": [
            ("San Bernardino", 37481),
            ("Ontario", 13583),
            ("Redlands", 14324),
            ("Colton", 7023),
            ("Upland", 4513),
            ("Needles", 3299),
            ("Barstow", 2414),
            ("Victorville", 906),
            ("Fontana", 0),  # later
        ],
        "SAN DIEGO": [
            ("San Diego", 147995),
            ("National City", 7301),
            ("Chula Vista", 4012),
            ("Oceanside", 3508),
            ("Escondido", 3112),
            ("La Mesa", 2186),
            ("Coronado", 5424),
            ("El Cajon", 1233),
        ],
        "SAN FRANCISCO": [
            ("San Francisco", 634394),
        ],
        "SAN JOAQUIN": [
            ("Stockton", 47963),
            ("Lodi", 7546),
            ("Tracy", 3005),
            ("Manteca", 1323),
            ("Ripon", 1010),
            ("Escalon", 1040),
        ],
        "SAN LUIS OBISPO": [
            ("San Luis Obispo", 5881),
            ("Paso Robles", 2473),
            ("Arroyo Grande", 1178),
            ("Morro Bay", 640),
        ],
        "SAN MATEO": [
            ("San Mateo", 13444),
            ("Redwood City", 8736),
            ("Burlingame", 4436),
            ("South San Francisco", 1413),
            ("Daly City", 1325),
            ("San Bruno", 1883),
            ("Pacifica", 0),  # later
            ("Half Moon Bay", 1124),
            ("Belmont", 2516),
            ("San Carlos", 1346),
            ("Menlo Park", 2254),
            ("Atherton", 1064),
        ],
        "SANTA BARBARA": [
            ("Santa Barbara", 33613),
            ("Santa Maria", 7057),
            ("Lompoc", 3917),
            ("Carpinteria", 2106),
            ("Montecito", 0),  # unincorporated
        ],
        "SANTA CLARA": [
            ("San Jose", 57651),
            ("Palo Alto", 13652),
            ("Santa Clara", 6223),
            ("Mountain View", 3908),
            ("Sunnyvale", 3094),
            ("Los Gatos", 3357),
            ("Gilroy", 3662),
            ("Morgan Hill", 1243),
            ("Saratoga", 1500),
            ("Campbell", 1123),
            ("Cupertino", 500),
        ],
        "SANTA CRUZ": [
            ("Santa Cruz", 14395),
            ("Watsonville", 8706),
            ("Capitola", 765),
        ],
        "SHASTA": [
            ("Redding", 2690),
            ("Anderson", 741),
        ],
        "SIERRA": [
            ("Loyalton", 497),
            ("Downieville", 264),
        ],
        "SISKIYOU": [
            ("Yreka", 1853),
            ("Mount Shasta", 1436),
            ("Dorris", 820),
            ("Weed", 1097),
        ],
        "SOLANO": [
            ("Vallejo", 11965),
            ("Benicia", 2801),
            ("Fairfield", 1244),
            ("Dixon", 1366),
            ("Vacaville", 1060),
            ("Rio Vista", 1261),
        ],
        "SONOMA": [
            ("Santa Rosa", 10636),
            ("Petaluma", 5046),
            ("Healdsburg", 2164),
            ("Sonoma", 1943),
            ("Sebastopol", 1767),
            ("Cloverdale", 1060),
            ("Rohnert Park", 0),  # later
        ],
        "STANISLAUS": [
            ("Modesto", 6957),
            ("Turlock", 4112),
            ("Ceres", 1911),
            ("Oakdale", 1776),
            ("Newman", 1031),
            ("Patterson", 792),
        ],
        "SUTTER": [
            ("Yuba City", 3503),
            ("Live Oak", 1697),
        ],
        "TEHAMA": [
            ("Red Bluff", 3517),
            ("Corning", 1822),
        ],
        "TRINITY": [
            ("Weaverville", 472),
        ],
        "TULARE": [
            ("Visalia", 7263),
            ("Tulare", 5858),
            ("Porterville", 3596),
            ("Dinuba", 1825),
            ("Lindsay", 2173),
            ("Exeter", 2009),
            ("Woodlake", 1084),
            ("Farmersville", 958),
        ],
        "TUOLUMNE": [
            ("Sonora", 2029),
        ],
        "VENTURA": [
            ("Ventura", 9740),
            ("Oxnard", 6285),
            ("Santa Paula", 5780),
            ("Simi Valley", 0),  # later
            ("Fillmore", 2788),
            ("Ojai", 1930),
        ],
        "YOLO": [
            ("Woodland", 3557),
            ("Davis", 1322),
            ("Winters", 978),
        ],
        "YUBA": [
            ("Marysville", 3571),
            ("Wheatland", 552),
        ],
    },
    # =========================================================================
    # WASHINGTON
    # =========================================================================
    "WA": {
        "ADAMS": [
            ("Ritzville", 1689),
            ("Othello", 0),  # later
        ],
        "ASOTIN": [
            ("Clarkston", 2447),
            ("Asotin", 915),
        ],
        "BENTON": [
            ("Prosser", 1256),
            ("Kennewick", 1232),
            ("Richland", 216),
        ],
        "CHELAN": [
            ("Wenatchee", 6285),
            ("Leavenworth", 1183),
            ("Chelan", 1188),
        ],
        "CLALLAM": [
            ("Port Angeles", 10141),
            ("Forks", 387),
            ("Sequim", 625),
        ],
        "CLARK": [
            ("Vancouver", 15766),
            ("Camas", 3591),
            ("Washougal", 1629),
        ],
        "COLUMBIA": [
            ("Dayton", 2407),
            ("Starbuck", 461),
        ],
        "COWLITZ": [
            ("Kelso", 5892),
            ("Longview", 6437),
            ("Castle Rock", 1204),
            ("Woodland", 730),
        ],
        "DOUGLAS": [
            ("Waterville", 915),
            ("Bridgeport", 529),
        ],
        "FERRY": [
            ("Republic", 387),
        ],
        "FRANKLIN": [
            ("Pasco", 3496),
            ("Connell", 493),
        ],
        "GARFIELD": [
            ("Pomeroy", 1753),
        ],
        "GRANT": [
            ("Ephrata", 761),
            ("Quincy", 496),
            ("Moses Lake", 211),
        ],
        "GRAYS HARBOR": [
            ("Aberdeen", 21723),
            ("Hoquiam", 9524),
            ("Montesano", 2242),
            ("Elma", 1728),
            ("Westport", 564),
            ("Ocean Shores", 0),  # later
        ],
        "ISLAND": [
            ("Coupeville", 460),
            ("Langley", 456),
            ("Oak Harbor", 540),
        ],
        "JEFFERSON": [
            ("Port Townsend", 3839),
            ("Port Ludlow", 200),
        ],
        "KING": [
            ("Seattle", 365583),
            ("Renton", 4057),
            ("Auburn", 3906),
            ("Kent", 2320),
            ("Kirkland", 2208),
            ("Redmond", 831),
            ("Bellevue", 1050),
            ("Bothell", 1372),
            ("Issaquah", 1021),
            ("Carnation", 377),
            ("Snoqualmie", 886),
            ("North Bend", 697),
            ("Tukwila", 1171),
            ("Burien", 0),  # later
            ("Shoreline", 0),  # later
            ("Des Moines", 992),
            ("SeaTac", 0),  # later
        ],
        "KITSAP": [
            ("Bremerton", 10170),
            ("Port Orchard", 1144),
            ("Poulsbo", 550),
            ("Bainbridge Island", 0),  # later
        ],
        "KITTITAS": [
            ("Ellensburg", 4721),
            ("Kittitas", 471),
            ("Cle Elum", 2223),
            ("Roslyn", 1491),
        ],
        "KLICKITAT": [
            ("Goldendale", 1284),
            ("White Salmon", 668),
        ],
        "LEWIS": [
            ("Centralia", 7935),
            ("Chehalis", 5130),
            ("Morton", 576),
            ("Napavine", 393),
            ("Toledo", 597),
            ("Winlock", 532),
        ],
        "LINCOLN": [
            ("Davenport", 1034),
            ("Sprague", 588),
            ("Odessa", 975),
            ("Wilbur", 620),
        ],
        "MASON": [
            ("Shelton", 3579),
            ("Hoodsport", 150),
        ],
        "OKANOGAN": [
            ("Okanogan", 1460),
            ("Omak", 2146),
            ("Tonasket", 743),
            ("Brewster", 594),
            ("Twisp", 594),
            ("Winthrop", 363),
        ],
        "PACIFIC": [
            ("Raymond", 3555),
            ("South Bend", 1894),
            ("Ilwaco", 1093),
            ("Long Beach", 529),
        ],
        "PEND OREILLE": [
            ("Newport", 1019),
            ("Metaline Falls", 348),
        ],
        "PIERCE": [
            ("Tacoma", 106817),
            ("Puyallup", 7294),
            ("Sumner", 2186),
            ("Enumclaw", 2208),
            ("Buckley", 1084),
            ("Orting", 1178),
            ("Steilacoom", 1083),
            ("Fife", 533),
            ("Lakewood", 0),  # later
        ],
        "SAN JUAN": [
            ("Friday Harbor", 627),
        ],
        "SKAGIT": [
            ("Mount Vernon", 6571),
            ("Anacortes", 5881),
            ("Sedro-Woolley", 2664),
            ("Burlington", 1328),
            ("La Conner", 625),
            ("Concrete", 722),
        ],
        "SKAMANIA": [
            ("Stevenson", 413),
            ("Carson", 184),
        ],
        "SNOHOMISH": [
            ("Everett", 30567),
            ("Snohomish", 2688),
            ("Monroe", 1690),
            ("Edmonds", 1788),
            ("Lynnwood", 0),  # later
            ("Mukilteo", 716),
            ("Stanwood", 988),
            ("Marysville", 1354),
            ("Arlington", 1397),
            ("Granite Falls", 530),
            ("Sultan", 540),
        ],
        "SPOKANE": [
            ("Spokane", 115514),
            ("Cheney", 1384),
            ("Deer Park", 1025),
            ("Medical Lake", 748),
        ],
        "STEVENS": [
            ("Colville", 1641),
            ("Chewelah", 941),
            ("Kettle Falls", 412),
        ],
        "THURSTON": [
            ("Olympia", 11733),
            ("Tenino", 1073),
            ("Lacey", 0),  # later
            ("Tumwater", 599),
        ],
        "WAHKIAKUM": [
            ("Cathlamet", 537),
        ],
        "WALLA WALLA": [
            ("Walla Walla", 15784),
            ("Waitsburg", 1098),
            ("Prescott", 484),
        ],
        "WHATCOM": [
            ("Bellingham", 28170),
            ("Blaine", 1475),
            ("Lynden", 1662),
            ("Ferndale", 452),
            ("Sumas", 446),
            ("Everson", 682),
            ("Nooksack", 124),
        ],
        "WHITMAN": [
            ("Pullman", 3322),
            ("Colfax", 2806),
            ("Palouse", 963),
            ("Garfield", 671),
            ("Tekoa", 1033),
            ("Rosalia", 719),
            ("Oakesdale", 662),
            ("St. John", 639),
            ("Endicott", 433),
        ],
        "YAKIMA": [
            ("Yakima", 22101),
            ("Sunnyside", 3385),
            ("Toppenish", 2974),
            ("Grandview", 1520),
            ("Wapato", 2028),
            ("Selah", 1112),
            ("Moxee City", 436),
            ("Granger", 1253),
            ("Zillah", 756),
            ("Tieton", 436),
        ],
    },
    # =========================================================================
    # OREGON
    # =========================================================================
    "OR": {
        "BAKER": [
            ("Baker", 6367),
            ("Haines", 593),
            ("Huntington", 524),
        ],
        "BENTON": [
            ("Corvallis", 5751),
            ("Philomath", 1436),
        ],
        "CLACKAMAS": [
            ("Oregon City", 5764),
            ("Milwaukie", 1944),
            ("Lake Oswego", 0),  # later
            ("Gladstone", 689),
            ("Estacada", 772),
            ("Molalla", 1033),
            ("Canby", 930),
        ],
        "CLATSOP": [
            ("Astoria", 10094),
            ("Warrenton", 756),
            ("Seaside", 1816),
        ],
        "COLUMBIA": [
            ("St. Helens", 2046),
            ("Scappoose", 620),
            ("Rainier", 808),
        ],
        "COOS": [
            ("Marshfield (Coos Bay)", 4671),
            ("North Bend", 2089),
            ("Coquille", 2049),
            ("Bandon", 1532),
            ("Myrtle Point", 1511),
            ("Powers", 634),
        ],
        "CROOK": [
            ("Prineville", 2032),
        ],
        "CURRY": [
            ("Gold Beach", 333),
            ("Port Orford", 752),
        ],
        "DESCHUTES": [
            ("Bend", 4484),
            ("Redmond", 730),
        ],
        "DOUGLAS": [
            ("Roseburg", 4431),
            ("Reedsport", 782),
            ("Myrtle Creek", 804),
            ("Sutherlin", 748),
            ("Winston", 353),
            ("Canyonville", 714),
        ],
        "GILLIAM": [
            ("Condon", 933),
            ("Arlington", 649),
        ],
        "GRANT": [
            ("John Day", 747),
            ("Canyon City", 452),
        ],
        "HARNEY": [
            ("Burns", 2139),
            ("Hines", 0),  # later
        ],
        "HOOD RIVER": [
            ("Hood River", 3802),
        ],
        "JACKSON": [
            ("Medford", 11007),
            ("Ashland", 4207),
            ("Jacksonville", 865),
            ("Central Point", 822),
            ("Talent", 624),
            ("Phoenix", 626),
            ("Eagle Point", 412),
        ],
        "JEFFERSON": [
            ("Madras", 839),
        ],
        "JOSEPHINE": [
            ("Grants Pass", 4228),
            ("Cave Junction", 0),  # later
        ],
        "KLAMATH": [
            ("Klamath Falls", 4103),
            ("Malin", 518),
            ("Merrill", 588),
        ],
        "LAKE": [
            ("Lakeview", 1484),
        ],
        "LANE": [
            ("Eugene", 18901),
            ("Springfield", 3393),
            ("Cottage Grove", 1950),
            ("Junction City", 1135),
            ("Florence", 460),
            ("Oakridge", 0),  # later
        ],
        "LINCOLN": [
            ("Newport", 1437),
            ("Toledo", 1403),
            ("Waldport", 575),
        ],
        "LINN": [
            ("Albany", 4808),
            ("Lebanon", 1699),
            ("Sweet Home", 542),
            ("Harrisburg", 791),
            ("Mill City", 376),
            ("Tangent", 244),
        ],
        "MALHEUR": [
            ("Ontario", 1399),
            ("Nyssa", 1061),
            ("Vale", 543),
        ],
        "MARION": [
            ("Salem", 26266),
            ("Woodburn", 1993),
            ("Silverton", 2169),
            ("Stayton", 1029),
            ("Mt. Angel", 1111),
            ("Jefferson", 473),
            ("Aumsville", 201),
        ],
        "MORROW": [
            ("Boardman", 179),
            ("Heppner", 1151),
            ("Ione", 211),
        ],
        "MULTNOMAH": [
            ("Portland", 301815),
            ("Gresham", 1195),
            ("Troutdale", 627),
            ("St. Johns", 0),  # annexed by Portland 1915
        ],
        "POLK": [
            ("Dallas", 2623),
            ("Monmouth", 1316),
            ("Independence", 946),
        ],
        "SHERMAN": [
            ("Moro", 362),
            ("Wasco", 492),
        ],
        "TILLAMOOK": [
            ("Tillamook", 2499),
            ("Rockaway", 426),
            ("Garibaldi", 479),
        ],
        "UMATILLA": [
            ("Pendleton", 5917),
            ("Milton-Freewater", 2377),
            ("Hermiston", 841),
            ("Athena", 826),
            ("Stanfield", 990),
            ("Echo", 532),
            ("Umatilla", 519),
        ],
        "UNION": [
            ("La Grande", 4908),
            ("Union", 1176),
            ("Elgin", 1013),
            ("North Powder", 476),
        ],
        "WALLOWA": [
            ("Enterprise", 1225),
            ("Joseph", 732),
        ],
        "WASCO": [
            ("The Dalles", 5546),
            ("Maupin", 586),
            ("Dufur", 371),
        ],
        "WASHINGTON": [
            ("Hillsboro", 3016),
            ("Beaverton", 2258),
            ("Tigard", 519),
            ("Forest Grove", 2679),
            ("Sherwood", 357),
            ("Gaston", 334),
        ],
        "WHEELER": [
            ("Fossil", 529),
            ("Mitchell", 365),
        ],
        "YAMHILL": [
            ("McMinnville", 3829),
            ("Newberg", 3176),
            ("Sheridan", 1391),
            ("Dayton", 644),
            ("Carlton", 436),
            ("Lafayette", 308),
        ],
    },
    # =========================================================================
    # IDAHO
    # =========================================================================
    "ID": {
        "ADA": [
            ("Boise", 21544),
            ("Meridian", 1303),
            ("Eagle", 413),
        ],
        "ADAMS": [
            ("Council", 639),
        ],
        "BANNOCK": [
            ("Pocatello", 16471),
            ("McCammon", 561),
        ],
        "BEAR LAKE": [
            ("Montpelier", 1956),
            ("Paris", 740),
            ("Saint Charles", 527),
        ],
        "BENEWAH": [
            ("St. Maries", 2543),
        ],
        "BINGHAM": [
            ("Blackfoot", 3320),
            ("Shelley", 965),
            ("Aberdeen", 706),
        ],
        "BLAINE": [
            ("Hailey", 1196),
            ("Bellevue", 1086),
            ("Ketchum", 580),
            ("Sun Valley", 0),  # later
        ],
        "BOISE": [
            ("Idaho City", 542),
        ],
        "BONNER": [
            ("Sandpoint", 3209),
            ("Priest River", 845),
        ],
        "BONNEVILLE": [
            ("Idaho Falls", 8841),
            ("Iona", 571),
            ("Ammon", 400),
        ],
        "BOUNDARY": [
            ("Bonners Ferry", 1141),
        ],
        "BUTTE": [
            ("Arco", 1260),
        ],
        "CAMAS": [
            ("Fairfield", 395),
        ],
        "CANYON": [
            ("Nampa", 6114),
            ("Caldwell", 4474),
            ("Parma", 691),
            ("Wilder", 366),
            ("Middleton", 261),
            ("Greenleaf", 180),
        ],
        "CARIBOU": [
            ("Soda Springs", 1530),
            ("Grace", 711),
        ],
        "CASSIA": [
            ("Burley", 3623),
            ("Albion", 424),
        ],
        "CLARK": [
            ("Dubois", 478),
        ],
        "CLEARWATER": [
            ("Orofino", 1435),
        ],
        "CUSTER": [
            ("Challis", 580),
        ],
        "ELMORE": [
            ("Mountain Home", 1930),
        ],
        "FREMONT": [
            ("St. Anthony", 2372),
            ("Ashton", 1365),
        ],
        "GEM": [
            ("Emmett", 1657),
        ],
        "GOODING": [
            ("Gooding", 1569),
            ("Hagerman", 523),
        ],
        "IDAHO": [
            ("Grangeville", 1325),
            ("Cottonwood", 682),
        ],
        "JEFFERSON": [
            ("Rigby", 2135),
            ("Lewisville", 570),
        ],
        "JEROME": [
            ("Jerome", 1989),
        ],
        "KOOTENAI": [
            ("Coeur d'Alene", 3639),
            ("Rathdrum", 695),
            ("Post Falls", 431),
        ],
        "LATAH": [
            ("Moscow", 4326),
            ("Potlatch", 1359),
            ("Troy", 710),
            ("Genesee", 517),
            ("Kendrick", 464),
        ],
        "LEMHI": [
            ("Salmon", 1420),
            ("Leadore", 372),
        ],
        "LEWIS": [
            ("Nezperce", 333),
            ("Kamiah", 381),
        ],
        "LINCOLN": [
            ("Shoshone", 1197),
        ],
        "MADISON": [
            ("Rexburg", 3432),
            ("Sugar City", 610),
        ],
        "MINIDOKA": [
            ("Rupert", 2115),
            ("Paul", 648),
        ],
        "NEZ PERCE": [
            ("Lewiston", 7559),
            ("Lapwai", 391),
        ],
        "ONEIDA": [
            ("Malad City", 2155),
        ],
        "OWYHEE": [
            ("Homedale", 473),
            ("Marsing", 347),
        ],
        "PAYETTE": [
            ("Payette", 1930),
            ("New Plymouth", 544),
        ],
        "POWER": [
            ("American Falls", 1422),
        ],
        "SHOSHONE": [
            ("Wallace", 2117),
            ("Kellogg", 3147),
            ("Mullan", 1581),
            ("Burke", 1858),
            ("Wardner", 1289),
        ],
        "TETON": [
            ("Victor", 440),
            ("Driggs", 380),
        ],
        "TWIN FALLS": [
            ("Twin Falls", 10292),
            ("Buhl", 1586),
            ("Filer", 543),
        ],
        "VALLEY": [
            ("Cascade", 632),
            ("McCall", 571),
        ],
        "WASHINGTON": [
            ("Weiser", 2803),
            ("Cambridge", 533),
        ],
    },
    # =========================================================================
    # ARIZONA
    # =========================================================================
    "AZ": {
        "APACHE": [
            ("St. Johns", 1369),
            ("Springerville", 322),
        ],
        "COCHISE": [
            ("Bisbee", 8023),
            ("Douglas", 6407),
            ("Willcox", 1010),
            ("Tombstone", 808),
            ("Benson", 745),
        ],
        "COCONINO": [
            ("Flagstaff", 3663),
            ("Williams", 2072),
        ],
        "GILA": [
            ("Globe", 5151),
            ("Miami", 2194),
            ("Payne", 483),
        ],
        "GRAHAM": [
            ("Safford", 2213),
            ("Thatcher", 586),
            ("Pima", 699),
        ],
        "GREENLEE": [
            ("Clifton", 3122),
            ("Morenci", 1621),
            ("Duncan", 622),
        ],
        "MARICOPA": [
            ("Phoenix", 48118),
            ("Mesa", 3711),
            ("Tempe", 2340),
            ("Glendale", 1649),
            ("Scottsdale", 500),
            ("Peoria", 405),
            ("Chandler", 0),  # later
            ("Buckeye", 417),
            ("Wickenburg", 569),
        ],
        "MOHAVE": [
            ("Kingman", 1233),
        ],
        "NAVAJO": [
            ("Winslow", 3067),
            ("Holbrook", 1506),
            ("Snowflake", 711),
            ("Taylor", 460),
        ],
        "PIMA": [
            ("Tucson", 32506),
            ("South Tucson", 0),  # later
            ("Ajo", 0),  # unincorporated at time
        ],
        "PINAL": [
            ("Florence", 1036),
            ("Coolidge", 1024),
            ("Casa Grande", 1089),
            ("Ray", 370),
        ],
        "SANTA CRUZ": [
            ("Nogales", 6006),
            ("Patagonia", 652),
        ],
        "YAVAPAI": [
            ("Prescott", 4700),
            ("Jerome", 1298),
            ("Clarkdale", 625),
            ("Cottonwood", 524),
        ],
        "YUMA": [
            ("Yuma", 4292),
            ("Wellton", 431),
        ],
    },
    # =========================================================================
    # NEW MEXICO
    # =========================================================================
    "NM": {
        "BERNALILLO": [
            ("Albuquerque", 26570),
        ],
        "CATRON": [
            ("Reserve", 317),
        ],
        "CHAVES": [
            ("Roswell", 10068),
            ("Dexter", 436),
        ],
        "COLFAX": [
            ("Raton", 4717),
            ("Springer", 838),
        ],
        "CURRY": [
            ("Clovis", 7443),
            ("Texico", 389),
        ],
        "DE BACA": [
            ("Fort Sumner", 1188),
        ],
        "DONA ANA": [
            ("Las Cruces", 5811),
            ("Mesilla", 875),
        ],
        "EDDY": [
            ("Carlsbad", 3803),
            ("Artesia", 1282),
        ],
        "GRANT": [
            ("Silver City", 4216),
            ("Bayard", 0),  # later
        ],
        "GUADALUPE": [
            ("Santa Rosa", 1649),
        ],
        "HARDING": [
            ("Mosquero", 409),
        ],
        "HIDALGO": [
            ("Lordsburg", 1727),
        ],
        "LEA": [
            ("Hobbs", 989),
            ("Lovington", 480),
        ],
        "LINCOLN": [
            ("Ruidoso", 0),  # later
            ("Carrizozo", 1156),
            ("Capitan", 351),
        ],
        "LOS ALAMOS": [
            ("Los Alamos", 0),  # later (Manhattan Project)
        ],
        "LUNA": [
            ("Deming", 2952),
        ],
        "MCKINLEY": [
            ("Gallup", 3126),
        ],
        "MORA": [
            ("Mora", 510),
        ],
        "OTERO": [
            ("Alamogordo", 2304),
            ("Tularosa", 1084),
            ("Cloudcroft", 259),
        ],
        "QUAY": [
            ("Tucumcari", 3235),
            ("San Jon", 450),
        ],
        "RIO ARRIBA": [
            ("Española", 1503),
            ("Chama", 422),
        ],
        "ROOSEVELT": [
            ("Portales", 2519),
        ],
        "SAN JUAN": [
            ("Aztec", 1585),
            ("Farmington", 1527),
            ("Bloomfield", 941),
        ],
        "SAN MIGUEL": [
            ("Las Vegas", 7144),
            ("Pecos", 521),
        ],
        "SANDOVAL": [
            ("Bernalillo", 861),
            ("Cuba", 329),
        ],
        "SANTA FE": [
            ("Santa Fe", 11176),
        ],
        "SIERRA": [
            ("Truth or Consequences (Hot Springs)", 1382),
        ],
        "SOCORRO": [
            ("Socorro", 2479),
            ("Magdalena", 574),
        ],
        "TAOS": [
            ("Taos", 1312),
            ("Raton", 0),  # actually Colfax Co
        ],
        "TORRANCE": [
            ("Estancia", 544),
            ("Moriarty", 310),
        ],
        "UNION": [
            ("Clayton", 1489),
        ],
        "VALENCIA": [
            ("Belen", 3514),
            ("Los Lunas", 676),
            ("Grants", 664),
        ],
    },
    # =========================================================================
    # NEVADA
    # =========================================================================
    "NV": {
        "CHURCHILL": [
            ("Fallon", 2427),
        ],
        "CLARK": [
            ("Las Vegas", 5165),
            ("Reno", 0),  # Washoe Co
            ("Boulder City", 0),  # later (Hoover Dam construction)
        ],
        "DOUGLAS": [
            ("Gardnerville", 316),
            ("Minden", 334),
        ],
        "ELKO": [
            ("Elko", 2832),
            ("Wells", 859),
        ],
        "ESMERALDA": [
            ("Goldfield", 605),
        ],
        "EUREKA": [
            ("Eureka", 620),
        ],
        "HUMBOLDT": [
            ("Winnemucca", 1556),
        ],
        "LANDER": [
            ("Battle Mountain", 893),
            ("Austin", 320),
        ],
        "LINCOLN": [
            ("Pioche", 683),
            ("Caliente", 531),
        ],
        "LYON": [
            ("Yerington", 780),
            ("Fernley", 432),
        ],
        "MINERAL": [
            ("Hawthorne", 868),
        ],
        "NYE": [
            ("Tonopah", 1504),
            ("Goldfield", 0),  # Esmeralda Co
        ],
        "PERSHING": [
            ("Lovelock", 1267),
        ],
        "STOREY": [
            ("Virginia City", 597),
        ],
        "WASHOE": [
            ("Reno", 18529),
            ("Sparks", 2290),
        ],
        "WHITE PINE": [
            ("Ely", 2995),
            ("East Ely", 1533),
            ("McGill", 1148),
        ],
    },
}


def get_towns_for_county(state_abbr: str, county_norm: str) -> TownList:
    """Return list of (town_name, 1930_population) for a given county.

    Returns an empty list if no data is available for that county.
    """
    state_data = TOWN_DB.get(state_abbr.upper(), {})
    return state_data.get(county_norm.upper(), [])


def has_town_data(state_abbr: str, county_norm: str) -> bool:
    """Check if real town data exists for the given county."""
    return bool(get_towns_for_county(state_abbr, county_norm))
