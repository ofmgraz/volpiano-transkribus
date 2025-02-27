from volpiano import determine_clef, volp, token2volp, maketype, process_regions, cleaned_text, cleaned_rubrik_text, change_coords


def test_simple():
    assert determine_clef("c2") == "c2"
    assert determine_clef("c3") == "c3"


def test_simple_2():
    assert determine_clef("g4/c2") == "c2"
    assert determine_clef("c4/f2") in ("c4", "f2")
    assert determine_clef("[c4]") == "c4"


def test_token2volp():
    assert token2volp("f2", "cu_z2") == "--G"
    assert token2volp("c3", "cu_z2") == "--J"


def test_excel_example():
    assert volp("g4/c2 z2 , z2 , l2 , z2 l2 l2 z1 , l2 , z2 l3 z2 l2 z2 , z2 z3 z2 l3 z2 l2 z2 l2 L z2 , z3 l3 z3 l4 L l4 z4 , z2 z2 z3 z3 l3") == "1-l-l-k-lkkj-k-lmlkl-lnlmlklk-3-l-nmno-3-op-llnnm"


def test_b2volp(): 
    assert volp("c4 l3 , l3 bz3 , z2 cu_z2") == "1-h-hi-g--G"
    assert volp("c4 l3 , l3 bz3 nz3 , z2 cu_z2") == "1-h-hiI-g--G"

def test_2clefs():
    assert volp("c4 l3 , [c2] z3 l3") == "1-h--nm"

def test_maketype():
    assert maketype("readingOrder {{index:0;}} structure {{score:0.94; type:rubrik2;}}") == "rubrik2"
    assert maketype("readingOrder {{index:1;}} structure {{score:0.87; type:initiale_fleuro_lombarde;}}") == "initiale_fleuro_lombarde"

def test_cleaned_text(): 
    assert cleaned_text(['c4 z1, z2 , z2']) == "c4 z1, z2 , z2"

def test_cleaned_rubrik_text(): 
    text = ['Dominica prima In adventu', 'domini ad vesperas super Ps. An.']
    text2 = 'Dominica prima In adventu <br> domini ad vesperas super Ps. An.'
    assert cleaned_rubrik_text(text) == text2

def test_process_regions():
    data = {'type': 'rubrik2', 'text': ['Dominica prima In adventu', 'domini ad vesperas super Ps. An.'], 'coords': '836,147 1247,147 1247,301 836,301'}
    data2 = {'type': 'notation', 'text': ['c4 z1, z2 , z2'], 'coords': '646,154 839,154 839,238 646,238'}
    result = {'type': 'rubrik2', 'text': 'Dominica prima In adventu <br> domini ad vesperas super Ps. An.', 'coords': '836,147 1247,147 1247,301 836,301'}
    result2 = {'type': 'notation', 'text': '1-e-g-g', 'coords': '646,154 839,154 839,238 646,238'}
    assert process_regions(data) == result
    assert process_regions(data2) == result2

def test_change_coords():
    assert change_coords('836,147 1247,147 1247,301 836,301') == [836, 147, 411, 154]