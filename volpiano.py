# import argparse
import json
import re

from lxml import etree

P_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
NS_MAP = {"p": P_NS}

INFILE = "D-MbsClm2766_Seite_010.xml"
OUTFILE = "D-MbsClm2766_Seite_010.json"

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

# f(c1, 4) => 9   == +5
# f(c2, 6) => 9   == +3
# f(c3, 8) => 9   == +1
# f(c4, 10) => 9  == -1

# f(f1, 4) => 5   == +1 
# f(f2, 6) => 5   == -1
# f(f3, 8) => 5	  == -3
# f(f4, 10) => 5  == -5

CLEFS = {
     "c1": 5,
     "c2": 3,
     "c3": 1, 
     "c4": -1, 
     "f1": 1, 
     "f2": -1,
     "f3": -3,
     "f4": -5
 }

# b-Vorzeichen: Ton (=Ton in Volpiano) : b-Vorzeichen in Volpiano
# B (=b): y 
# es‘(=e): w 
# b‘(=j): i 
# es‘‘(=m): x 
# b‘‘(=q): z

VOLP2BVOLP = {
    "b": "y",
    "e": "w",
    "j": "i", 
    "m": "x", 
    "q": "z"
}



# str -> str
def determine_clef(clef_str):
    if re.search(r"[/\[]", clef_str): #zusammengesetzter clef "c4/f2" oder "[c4]"
        clef_str = re.search(r"(c\d+|f\d+)", clef_str).group(0)
        return clef_str
    else:
        return clef_str


# str -> bool
def is_note_token(token_str):
    return re.match(r"^(l|z)(-2|-1|[1-6])", token_str) is not None


# (str, str) -> str
def token2volp(clef, token_str):
    if is_note_token(token_str):
        return NUM2VOLP[TOKEN2NUM[token_str] + CLEFS[clef]] 
    elif token_str == ",":
        return "-"
    elif token_str == "L":
        return "-3-"
    elif token_str.startswith("cu_"): # Kustos, in Transkribus: "cu_z2" => 'kleine Note' in Volpiano Großbuchstaben, davor 2 Abstände (lt. RK) (volp: "--A")
        cu_token_str = token_str.lstrip("cu_") 
        return "--" + NUM2VOLP[TOKEN2NUM[cu_token_str] + CLEFS[clef]].upper()
    elif token_str.startswith("b"): # b-Vorzeichen in Transkribus: "bz3" (oder "b_z3"?!)
        b_token_str = token_str.lstrip("b") 
        return VOLP2BVOLP[NUM2VOLP[TOKEN2NUM[b_token_str] + CLEFS[clef]]]
    elif token_str.startswith("n"): #Auflösungszeichen: Großbuchstaben von b-Vorzeichen in Volpiano (oder "n_"?!)
        n_token_str = token_str.lstrip("n")
        return VOLP2BVOLP[NUM2VOLP[TOKEN2NUM[n_token_str] + CLEFS[clef]]].upper()
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
    clef2_index = next((i for i, token in enumerate(remaining) if re.match(r"\[(c|f)\d\]", token)), None)
    if clef2_index is not None:
        remaining1 = remaining[:clef2_index]
        clef_str2 = remaining[clef2_index]
        remaining2 = remaining[clef2_index + 1:]
        clef2 = determine_clef(clef_str2)
        transformed = [token2volp(clef, token) for token in remaining1] + ["-"] + [token2volp(clef2, token) for token in remaining2]
    else:
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
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(volpiano_notations, f, indent=2)


if __name__ == "__main__":
    main()
