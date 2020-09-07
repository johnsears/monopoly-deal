from enum import Enum

HOUSE = 'House'
HOTEL = 'Hotel'

class Card():
    def __init__(self, index, value):
        self.index = index
        self.value = value


class Cashable:
    pass


class CashCard(Card, Cashable):
    def __repr__(self):
        return f'<CashCard (${self.value})>'


class ActionCard(Card, Cashable):
    def __init__(self, index, value, name, description):
        super().__init__(index, value)
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<ActionCard: {self.name} (${self.value})>'


class PropertyCard(Card):
    def __init__(self, index, value, name, color, rent, buildable):
        super().__init__(index, value)
        self.name = name
        self.color = color
        self.rent = rent
        self.buildable = buildable

    def __repr__(self):
        return f'<PropertyCard: {self.name} (${self.value})>'


class RentCard(Card):
    def __init__(self, index, value, color, wild):
        super().__init__(index, value)
        self.color = color  # Set
        self.wild = wild  # Boolean - Targeting

    def __repr__(self):
        return f'<RentCard: {self.color}>'


class Color(Enum):
    RED = "red"
    DBLUE = "darkblue"
    LBLUE = "lightblue"
    PURPLE = "purple"
    GREEN = "green"
    ORANGE = "orange"
    YELLOW = "yellow"
    BROWN = "brown"
    RR = "railroad"
    UTIL = "utility"
    ALL = "all"

    def __repr__(self):
        return self.value

deck = {
    1: PropertyCard(1, 3, HOUSE, {Color.ALL}, [], False),
    2: PropertyCard(2, 3, HOUSE, {Color.ALL}, [], False),
    3: PropertyCard(3, 3, HOUSE, {Color.ALL}, [], False),
    4: PropertyCard(4, 4, HOTEL, {Color.ALL}, [], False),
    5: PropertyCard(5, 4, HOTEL, {Color.ALL}, [], False),
    6: PropertyCard(6, 4, HOTEL, {Color.ALL}, [], False),
    7: ActionCard(7, 2, "It's my birthday!", "All players give you $2M as a gift."),
    8: ActionCard(8, 2, "It's my birthday!", "All players give you $2M as a gift."),
    9: ActionCard(9, 2, "It's my birthday!", "All players give you $2M as a gift."),
    10: ActionCard(10, 1, "Double the Rent", "Needs to be played with a rent card."),
    11: ActionCard(11, 1, "Double the Rent", "Needs to be played with a rent card."),
    12: ActionCard(12, 5, "Deal Breaker", "Steal a complete set from any player (includes any buildings)"),
    13: ActionCard(13, 5, "Deal Breaker", "Steal a complete set from any player (includes any buildings)"),
    14: ActionCard(14, 4, "Just Say No!", "Use any time when an action card is played against you."),
    15: ActionCard(15, 4, "Just Say No!", "Use any time when an action card is played against you."),
    16: ActionCard(16, 4, "Just Say No!", "Use any time when an action card is played against you."),
    17: ActionCard(17, 3, "Debt Collector", "Force any player to pay you $5M"),
    18: ActionCard(18, 3, "Debt Collector", "Force any player to pay you $5M"),
    19: ActionCard(19, 3, "Debt Collector", "Force any player to pay you $5M"),
    20: ActionCard(20, 3, "Sly Deal", "Steal a property from a player of your choice (cannot be a part of a full set)!"),
    21: ActionCard(21, 3, "Sly Deal", "Steal a property from a player of your choice (cannot be a part of a full set)!"),
    22: ActionCard(22, 3, "Sly Deal", "Steal a property from a player of your choice (cannot be a part of a full set)!"),
    23: ActionCard(23, 3, "Forced Deal", "Swap any property with another player (cannot be part of a full set)!"),
    24: ActionCard(24, 3, "Forced Deal", "Swap any property with another player (cannot be part of a full set)!"),
    25: ActionCard(25, 3, "Forced Deal", "Swap any property with another player (cannot be part of a full set)!"),
    26: ActionCard(26, 3, "Forced Deal", "Swap any property with another player (cannot be part of a full set)!"),
    27: ActionCard(27, 1, "Pass Go", "Draw two extra cards!"),
    28: ActionCard(28, 1, "Pass Go", "Draw two extra cards!"),
    29: ActionCard(29, 1, "Pass Go", "Draw two extra cards!"),
    30: ActionCard(30, 1, "Pass Go", "Draw two extra cards!"),
    31: ActionCard(31, 1, "Pass Go", "Draw two extra cards!"),
    32: ActionCard(32, 1, "Pass Go", "Draw two extra cards!"),
    33: ActionCard(33, 1, "Pass Go", "Draw two extra cards!"),
    34: ActionCard(34, 1, "Pass Go", "Draw two extra cards!"),
    35: ActionCard(35, 1, "Pass Go", "Draw two extra cards!"),
    36: ActionCard(36, 1, "Pass Go", "Draw two extra cards!"),
    37: PropertyCard(37, 2, "Electric Company", {Color.UTIL}, [1, 2], True),
    38: PropertyCard(38, 2, "Waterworks", {Color.UTIL}, [1, 2], True),
    39: PropertyCard(39, 2, "Pennsylvania Railroad", {Color.RR}, [1, 2, 3, 4], True),
    40: PropertyCard(40, 2, "Reading Railroad", {Color.RR}, [1, 2, 3, 4], True),
    41: PropertyCard(41, 2, "B. & O. Railroad", {Color.RR}, [1, 2, 3, 4], True),
    42: PropertyCard(42, 2, "Short Line Railroad", {Color.RR}, [1, 2, 3, 4], True),
    43: PropertyCard(43, 1, "Baltic Avenue", {Color.BROWN}, [1, 2], True),
    44: PropertyCard(44, 1, "Mediterranean Avenue", {Color.BROWN}, [1, 2], True),
    45: PropertyCard(45, 1, "Oriental Avenue",    {Color.LBLUE}, [1, 2, 3], True),
    46: PropertyCard(46, 1, "Connecticut Avenue", {Color.LBLUE}, [1, 2, 3], True),
    47: PropertyCard(47, 1, "Vermont Avenue",    {Color.LBLUE}, [1, 2, 3], True),
    48: PropertyCard(48, 2, "States Avenue",     {Color.PURPLE}, [1, 2, 4], True),
    49: PropertyCard(49, 2, "Virginia Avenue",   {Color.PURPLE}, [1, 2, 4], True),
    50: PropertyCard(50, 2, "St. Charles Place", {Color.PURPLE}, [1, 2, 4], True),
    51: PropertyCard(51, 2, "St. James Place",   {Color.ORANGE}, [1, 3, 5], True),
    52: PropertyCard(52, 2, "Tennessee Avenue",  {Color.ORANGE}, [1, 3, 5], True),
    53: PropertyCard(53, 2, "New York Avenue",   {Color.ORANGE}, [1, 3, 5], True),
    54: PropertyCard(54, 3, "Indiana Avenue",    {Color.RED}, [2, 3, 6], True),
    55: PropertyCard(55, 3, "Illinois Avenue",   {Color.RED}, [2, 3, 6], True),
    56: PropertyCard(56, 3, "Kentucky Avenue",   {Color.RED}, [2, 3, 6], True),
    57: PropertyCard(57, 3, "Atlantic Avenue",   {Color.YELLOW}, [2, 4, 6], True),
    58: PropertyCard(58, 3, "Marvin Gardens",    {Color.YELLOW}, [2, 4, 6], True),
    59: PropertyCard(59, 3, "Ventnor Avenue",    {Color.YELLOW}, [2, 4, 6], True),
    60: PropertyCard(60, 4, "Pennsylvania Avenue", {Color.GREEN}, [2, 4, 7], True),
    61: PropertyCard(61, 4, "Pacific Avenue", {Color.GREEN}, [2, 4, 7], True),
    62: PropertyCard(62, 4, "North Carolina Avenue", {Color.GREEN}, [2, 4, 7], True),
    63: PropertyCard(63, 4, "Park Place", {Color.DBLUE}, [3, 8], True),
    64: PropertyCard(64, 4, "Boardwalk", {Color.DBLUE}, [3, 8], True),
    65: PropertyCard(65, 0, "Wild", {Color.ALL, Color.ALL}, [], True),
    66: PropertyCard(66, 0, "Wild", {Color.ALL, Color.ALL}, [], True),
    67: PropertyCard(67, 4, "Wild", {Color.RR, Color.LBLUE}, [], True),
    68: PropertyCard(68, 2, "Wild", {Color.RR, Color.UTIL}, [], True),
    69: PropertyCard(69, 4, "Wild", {Color.RR, Color.GREEN}, [], True),
    70: PropertyCard(70, 4, "Wild", {Color.GREEN, Color.DBLUE}, [], True),
    71: PropertyCard(71, 3, "Wild", {Color.YELLOW, Color.RED}, [], True),
    72: PropertyCard(72, 3, "Wild", {Color.YELLOW, Color.RED}, [], True),
    73: PropertyCard(73, 1, "Wild", {Color.LBLUE, Color.BROWN}, [], True),
    74: PropertyCard(74, 2, "Wild", {Color.PURPLE, Color.ORANGE}, [], True),
    75: PropertyCard(75, 2, "Wild", {Color.PURPLE, Color.ORANGE}, [], True),
    76: RentCard(76, 1, {Color.BROWN, Color.LBLUE}, False),
    77: RentCard(77, 1, {Color.BROWN, Color.LBLUE}, False),
    78: RentCard(78, 1, {Color.RED, Color.YELLOW}, False),
    79: RentCard(79, 1, {Color.RED, Color.YELLOW}, False),
    80: RentCard(80, 1, {Color.GREEN, Color.DBLUE}, False),
    81: RentCard(81, 1, {Color.GREEN, Color.DBLUE}, False),
    82: RentCard(82, 1, {Color.RR, Color.UTIL}, False),
    83: RentCard(83, 1, {Color.RR, Color.UTIL}, False),
    84: RentCard(84, 1, {Color.PURPLE, Color.ORANGE}, False),
    85: RentCard(85, 1, {Color.PURPLE, Color.ORANGE}, False),
    86: RentCard(86, 3, {Color.ALL}, True),
    87: RentCard(87, 3, {Color.ALL}, True),
    88: RentCard(88, 3, {Color.ALL}, True),
    89: CashCard(89, 1),
    90: CashCard(90, 1),
    91: CashCard(91, 1),
    92: CashCard(92, 1),
    93: CashCard(93, 1),
    94: CashCard(94, 1),
    95: CashCard(95, 2),
    96: CashCard(96, 2),
    97: CashCard(97, 2),
    98: CashCard(98, 2),
    99: CashCard(99, 2),
    100: CashCard(100, 3),
    101: CashCard(101, 3),
    102: CashCard(102, 3),
    103: CashCard(103, 4),
    104: CashCard(104, 4),
    105: CashCard(105, 4),
    106: CashCard(106, 5),
    107: CashCard(107, 5),
    108: CashCard(108, 10)
}

property_set_rents = {
    Color.UTIL: [1, 2],
    Color.RR: [1, 2, 3, 4],
    Color.BROWN: [1, 2],
    Color.LBLUE: [1, 2, 3],
    Color.PURPLE: [1, 2, 4],
    Color.ORANGE: [1, 3, 5],
    Color.RED: [2, 3, 6],
    Color.YELLOW: [2, 4, 6],
    Color.GREEN: [2, 4, 7],
    Color.DBLUE: [3, 8]
}