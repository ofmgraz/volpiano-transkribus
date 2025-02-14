from volpiano import determine_clef, volp, token2volp


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