import xml.etree.ElementTree as ET
import importlib.util
spec = importlib.util.spec_from_file_location('pc', 'portfolio-classifier.py')
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)
from pc import PortfolioPerformanceFile


def test_no_industry_tag_in_classified_fixture():
    tree = ET.parse('test/Simple_classified.xml')
    root = tree.getroot()
    securities = root.findall('.//securities/security')
    # ensure no security element has an Industry child (Industry is stored internally)
    for sec in securities:
        ind = sec.find('Industry')
        assert ind is None, f"Security {sec.find('name').text} unexpectedly has Industry tag"


def test_holdings_has_industry_attribute():
    # Creating a holdings report should have an 'industry' attribute (no network calls)
    from pc import Security, SecurityHoldingReport
    s = Security(name='Test', ISIN='XY0000000000', secid='', UUID='u', isRetired='false', note=None)
    assert hasattr(s, 'holdings')
    sr = SecurityHoldingReport()
    assert hasattr(sr, 'industry')
    assert isinstance(sr.industry, str)


def test_absence_of_industry_does_not_break_get_security(tmp_path):
    sample = '''<client>
  <securities>
    <security>
      <uuid>test-uuid</uuid>
      <name>Test Security</name>
      <currencyCode>EUR</currencyCode>
      <isin>XY0000000000</isin>
      <tickerSymbol>TS</tickerSymbol>
      <feed>PP</feed>
      <isRetired>false</isRetired>
    </security>
  </securities>
</client>'''
    p = tmp_path / "tmp.xml"
    p.write_text(sample)
    pp = PortfolioPerformanceFile(str(p))
    sec = pp.get_security('.//securities/security')
    assert sec is not None


def test_holding_taxonomy_present():
    # Ensure that the 'Holding' taxonomy exists and has expected keys (no network)
    assert 'Holding' in pc.taxonomies
    t = pc.taxonomies['Holding']
    assert 'url' in t and 'jsonpath' in t and 'percent' in t


def test_industry_taxonomy_present():
    # Ensure that the 'Industry' taxonomy exists and has expected keys (no network)
    assert 'Industry' in pc.taxonomies
    t = pc.taxonomies['Industry']
    assert 'url' in t and ('jsonpath' in t or 'jsonpath-stocks' in t)

