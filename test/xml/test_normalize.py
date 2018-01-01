from open990.xmlfiles import util
from open990.xmlfiles import normalize as N
from lxml import etree
from mockito import mock

def test_attribs_to_elements(when):
    original = mock()

    transformed = "transformed"
    when(N)._transform(original).thenReturn(transformed)

    expected = "stripped"
    when(N)._strip_whitespace(transformed).thenReturn(expected)

    actual = N._attribs_to_elements(original)
    assert expected == actual

def test_normalize(when):
    raw = "the original XML"

    cleaned = "removed namespace and interstitial whitespace"
    when(util).clean_xml(raw).thenReturn(cleaned)

    dom = mock()
    when(N)._as_xml(cleaned).thenReturn(dom)

    expected = "string containing normalized XML"
    when(N)._attribs_to_elements(dom).thenReturn(expected)

    actual = N.normalize(raw)
    assert expected == actual

####################
# Functional tests #
####################

def test_normalize_f():
    raw = """
    <element attribute="value" />
    """

    """
    Turns out XML tree comparison is really hard. But this is what we expect:
    
    <element>
        <attribute>value</attribute>
    </element>
    """

    # Verify manually
    actual = N.normalize(raw)
    assert actual is not None

    et = etree.fromstring(actual)

    assert etree._Element == et.__class__
    assert {}             == et.attrib
    assert "element"      == et.tag
    assert {"attribute"}  == set([c.tag for c in et])
    assert "value"        == et[0].text

def test_normalize_f_recursive():
    raw = """
    <outer>
        <inner attribute="value">
            <innermost />
        </inner>
    </outer>
    """

    """
    Expected:
    
    <outer>
        <inner>
            <innermost />
            <attribute>value</attribute>
        </inner>
    </outer>
    """

    # Verify manually
    actual = N.normalize(raw)
    assert actual is not None

    et = etree.fromstring(actual)
    assert et.text is None
    assert etree._Element == et.__class__
    assert {}             == et.attrib
    assert "outer"        == et.tag
    assert {"inner"}      == set([c.tag for c in et])

    inner = et[0]
    assert "inner" == inner.tag
    assert inner.text is None

    children = {}
    for c in inner:
        children[c.tag] = c.text

    assert children["innermost"] is None
    assert "value" == children["attribute"]

def test_normalize_f_text():
    raw = """
    <e attribute="value">text</e>
    """

    """
    Expected:
    
    <e>
     <attribute>value</attribute>
     text
    </e>
    """

    actual = N.normalize(raw)
    assert actual is not None

    et = etree.fromstring(actual)
    assert "e"           == et.tag
    assert "text"        == util.consolidate_text(et)
    assert {}            == et.attrib
    assert {"attribute"} == set([c.tag for c in et])
    assert "value"       ==et[0].text

def test_normalize_f_namespace():
    raw = """
    <outer xmlns="horrible">
        <inner />
    </outer>
    """

    """
    Expected:
    
    <outer>
        <inner />
    </outer>
    """

    actual = N.normalize(raw)
    assert actual is not None

    et = etree.fromstring(actual)

    assert et.text is None
    assert "outer"   == et.tag
    assert {}        == et.attrib
    assert {"inner"} == set([c.tag for c in et])