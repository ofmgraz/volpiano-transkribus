from volpiano import determine_clef, volp


def test_simple():
    assert determine_clef("c2") == "c2"


def test_simple_2():
    assert determine_clef("c3") == "c3"


# def test_double():
#     assert determine_clef("c4/f2") == "c4"


def test_excel_example():
    assert volp("g4/c2 z2 , z2 , l2 , z2 l2 l2 z1 , l2 , z2 l3 z2 l2 z2 , z2 z3 z2 l3 z2 l2 z2 l2 L z2 , z3 l3 z3 l4 L l4 z4 , z2 z2 z3 z3 l3") == "1-l-l-k-lkkj-k-lmlkl-lnlmlklk-3-lnmno-3-op-jjllk"
