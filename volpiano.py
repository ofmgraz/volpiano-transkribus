# import argparse
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
    "f4": -5,
}

# b-Vorzeichen: Ton (=Ton in Volpiano) : b-Vorzeichen in Volpiano
# B (=b): y
# es‘(=e): w
# b‘(=j): i
# es‘‘(=m): x
# b‘‘(=q): z

VOLP2BVOLP = {"b": "y", "e": "w", "j": "i", "m": "x", "q": "z"}


# str -> str
def determine_clef(clef_str):
    if re.search(
        r"[/\[]", clef_str
    ):  # zusammengesetzter clef "c4/f2" oder "[c4]"
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
    elif token_str.startswith(
        "cu_"
    ):  # Kustos, in Transkribus: "cu_z2" => 'kleine Note' in Volpiano Großbuchstaben, davor 2 Abstände (lt. RK) (volp: "--A")
        cu_token_str = token_str.lstrip("cu_")
        return "--" + NUM2VOLP[TOKEN2NUM[cu_token_str] + CLEFS[clef]].upper()
    elif token_str.startswith(
        "b"
    ):  # b-Vorzeichen in Transkribus: "bz3" 
        b_token_str = re.sub(r'^b_|^b', '', token_str)
        return VOLP2BVOLP[NUM2VOLP[TOKEN2NUM[b_token_str] + CLEFS[clef]]]
    elif token_str.startswith(
        "n"
    ):  # Auflösungszeichen: Großbuchstaben von b-Vorzeichen in Volpiano
        n_token_str = re.sub(r'^n_|^n', '', token_str)
        return VOLP2BVOLP[
            NUM2VOLP[TOKEN2NUM[n_token_str] + CLEFS[clef]]
        ].upper()
    else:
        return "-2-"


# str -> str
def volp(notation_str):
    # split input string on space
    # first token is clef
    # for remaining tokens:
    #  map from input numeric values to output numeric values by clef offset
    notation_str = re.sub(
        r"(l|z)(-2|-1|[1-6]),", r"\1\2 ,", notation_str
    )  # XXX
    tokens = notation_str.split(" ")
    clef_str = tokens[0]
    remaining = tokens[1:]
    clef = determine_clef(clef_str)
    clef2_index = next(
        (
            i
            for i, token in enumerate(remaining)
            if re.match(r"\[(c|f)\d\]", token)
        ),
        None,
    )
    if clef2_index is not None:
        remaining1 = remaining[:clef2_index]
        clef_str2 = remaining[clef2_index]
        remaining2 = remaining[clef2_index + 1 :]
        clef2 = determine_clef(clef_str2)
        transformed = (
            [token2volp(clef, token) for token in remaining1]
            + ["-"]
            + [token2volp(clef2, token) for token in remaining2]
        )
    else:
        transformed = [token2volp(clef, token) for token in remaining]
    return "".join(["1-", *transformed])


# s -> [(int, int), (int, int), (int, int), (int, int)]
# 836,147 1247,147 1247,301 836,301
def change_coords(coords_str):
    pairs = coords_str.split()
    coords = [tuple(int(x) for x in pair.split(",")) for pair in pairs]
    (x1, y1) = coords[0]
    (x2, y2) = coords[2]
    left = x1
    top = y1
    width = x2 - x1
    height = y2 - y1
    return [left, top, width, height]

def maketype(custom): 
    # "readingOrder {index:0;} structure {score:0.94; type:rubrik2;}" ==> rubrik2
    type = re.search(r"type:([^;]+);", custom).group(1)
    return type

def cleaned_rubrik_text(text): #rubrik 2 text bereinigen
    text = " <br> ".join(text)
    return text


def cleaned_text(text): # text bereinigen
    text = "".join(text)
    return text

# dic of region ->  
def process_regions(data):
    if data["type"] == "notation": 
        data["text"] = volp(cleaned_text(data["text"]))
    if data["type"] == "rubrik2": 
        data["text"] = cleaned_rubrik_text(data["text"])
    else: 
        data["text"] = cleaned_text(data["text"])
        return data
    return data

def get_regions(tree):
    regions = {}
    for region in tree.xpath("//p:TextRegion", namespaces=NS_MAP): 
        region_id = region.get("id")
        type = maketype(region.get("custom"))
        text = region.xpath("./p:TextLine/p:TextEquiv/p:Unicode/text()", namespaces=NS_MAP)
        coords = region.find("./p:Coords", namespaces=NS_MAP).get("points")
        #regions = {region_id: {"type": type, "text": text, "coords": coords}}
        regions[region_id] = {"type": type, "text": text, "coords": coords}
        regions[region_id] = process_regions(regions[region_id])
    return regions

def create_html_output(tree):
    regions = get_regions(tree)
    html = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>VOLPIANO</title>
    <style>
.volpiano {
  font-family: Volpiano;
  font-size: 4rem;
}

.container-grid {
    display: grid;                     
    grid-template-columns: auto 1fr;  
    gap: 20px;                        
    height: 100vh;                    
}

.image-section-grid {
    position: sticky;  
    top: 0;           
    height: 100vh;
    overflow: hidden;
    position: relative; 
}

.text-section-grid {
    overflow-y: auto;  
    padding: 20px;
    font-size: 3em;
}

p {
    margin-bottom: 10px;
    margin-top: 10px;
}

h1 {
    margin: 20px;
    font-size: 4em;
}

p.highlight {
  border: 5px solid black;
  padding: 3px;
}

.image-region {
  position: absolute;
  border: 5px solid transparent;
  pointer-events: auto;
  z-index: 10;
}

.image-region.highlight {
  border: 5px solid black;
}
""" 
    html += """</style>
  </head>
  <body>
    <h1>Name der Datei bzw. Seite: D-MbsClm2766_Seite_010</h1>
    <div class="container-grid">
        <div class="image-section-grid">
            <img src="images/D-MbsClm2766_Seite_010.jpg">
"""
    
    # Add image regions based on the coordinates from your data
    for region_id, data in regions.items():
        coords = change_coords(data["coords"])
        html += f"""<div class="image-region" id="region-{region_id}" data-target="paragraph-{region_id}" 
                    style="left: {coords[0]}px; top: {coords[1]}px; width: {coords[2]}px; height: {coords[3]}px;"></div>"""

    
    html += """
        </div>
        <div class="text-section-grid">
"""
    for region_id, data in regions.items(): 
        text = data["text"]
        # Add id and data-target to ALL paragraph types
        if data["type"] == "notation":
            html += f"""<p id="paragraph-{region_id}" data-target="region-{region_id}" data-region="{region_id}" class="volpiano">{text}</p>"""
        elif data["type"] == "rubrik2": 
            html += f"""<p id="paragraph-{region_id}" data-target="region-{region_id}" data-region="{region_id}" style="color:red;">{text}</p>"""
        elif data["type"] == "rubrik": 
            html += f"""<p id="paragraph-{region_id}" data-target="region-{region_id}" data-region="{region_id}" style="color:red;">{text}</p>"""
        elif data["type"] == "initiale_lombarde" or data["type"] == "initiale_cadelle":
            html += f"""<p id="paragraph-{region_id}" data-target="region-{region_id}" data-region="{region_id}"><b>{text}</b></p>"""
        else:
            html += f"""<p id="paragraph-{region_id}" data-target="region-{region_id}" class="paragraph">{text}</p>"""
    html += """</div>
    </div>
    
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        const paragraphs = document.querySelectorAll('p[data-target]');
        const imageRegions = document.querySelectorAll('.image-region');
        
        paragraphs.forEach(paragraph => {
          paragraph.addEventListener('mouseenter', function() {
            const targetId = this.getAttribute('data-target');
            this.classList.add('highlight');
            
            const region = document.getElementById(targetId);
            if (region) {
              region.classList.add('highlight');
            }
          });
          
          paragraph.addEventListener('mouseleave', function() {
            const targetId = this.getAttribute('data-target');
            this.classList.remove('highlight');
            
            const region = document.getElementById(targetId);
            if (region) {
              region.classList.remove('highlight');
            }
          });
        });
        
        imageRegions.forEach(region => {
          region.addEventListener('mouseenter', function() {
            const targetId = this.getAttribute('data-target');
            this.classList.add('highlight');
            
            const paragraph = document.getElementById(targetId);
            if (paragraph) {
              paragraph.classList.add('highlight');
            }
          });
          
          region.addEventListener('mouseleave', function() {
            const targetId = this.getAttribute('data-target');
            this.classList.remove('highlight');
            
            const paragraph = document.getElementById(targetId);
            if (paragraph) {
              paragraph.classList.remove('highlight');
            }
          });
        });
      });
    </script>
  </body>
  </html>"""
    return html


def main():
    tree = etree.parse(INFILE)
    html = create_html_output(tree)
    #print(html)
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html)


if __name__ == "__main__":
    main()
    