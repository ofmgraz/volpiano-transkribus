import re

from lxml import etree

P_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
NS_MAP = {"p": P_NS}

INFILE = "D-MbsClm2766_Seite_010.xml"

# # c4 z1, z2 , z2
# f(c4, 10) => 9
# f(c4, 5) => 4
#
# f(c2, 7) => 10
# f(c2, 6) => 9
# f(c2, 10) => 13
# f(c2, 11) => 14
#
# f(c1, 5) => 10
# f(c1, 4) => 9
# f(c1, 8) => 13
# f(c1, 9) => 14
#
# # ???
# f(c1, 7) => 5
# f(c1, 6) => 4
# f(c1, 10) => 8
# f(c1, 11) => 9

VOLP2NUM = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7,
    "j": 8,
    "k": 9,
    "l": 10,
    "m": 11,
    "n": 12,
    "o": 13,
    "p": 14,
    "q": 15,
    "r": 16,
    "s": 17,
}
NUM2VOLP = {v: k for k, v in VOLP2NUM.items()}

TOKEN2NUM = {
    "l-2": 0,
    "z-2": 1,
    "l-1": 2,
    "z-1": 3,
    "l1": 4,
    "z1": 5,
    "l2": 6,
    "z2": 7,
    "l3": 8,
    "z3": 9,
    "l4": 10,
    "z4": 11,
    "l5": 12,
    "z5": 13,
    "l6": 14,
    "z6": 15,
}


# str -> str
def determine_clef(clef_str):
    return clef_str


# str -> bool
def is_note_token(token_str):
    return re.match(r"^(l|z)(-2|-1|[1-6])", token_str) is not None


# (str, str) -> str
def token2volp(clef, token_str):
    if is_note_token(token_str):
        return NUM2VOLP[TOKEN2NUM[token_str] + 3]
    elif token_str == ",":
        return "-"
    elif token_str == "L":
        return "-3-"
    else:
        return "-2-"


# str -> str
def volp(notation_str):
    # split input string on space
    # first token is clef
    # for remaining tokens:
    #  map from input numeric values to output numeric values by clef offset
    notation_str = re.sub(r"(l|z)(-2|-1|[1-6]),", r"\1\2 ,", notation_str) # XXX
    tokens = notation_str.split(" ")
    clef_str = tokens[0]
    remaining = tokens[1:]
    clef = determine_clef(clef_str)
    transformed = [token2volp(clef, token) for token in remaining]
    return "".join(["1-", *transformed])


def main():
    tree = etree.parse(INFILE)
    notations = {
        region.get("id"): (
            t.text
            if (
                t := region.find(
                    "p:TextLine/p:TextEquiv/p:Unicode", namespaces=NS_MAP
                )
            )
            is not None
            else None
        )
        for region in tree.xpath(
            "//p:TextRegion[contains(@custom, 'type:notation')]",
            namespaces=NS_MAP,
        )
    }
    volpiano_notations = {k: volp(v) for k, v in notations.items()}
    print(volpiano_notations)


if __name__ == "__main__":
    main()
