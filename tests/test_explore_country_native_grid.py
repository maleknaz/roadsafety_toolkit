"""Regression coverage for the country findings grid, previously 17 stacked accordions.

The test exercises Streamlit's emitted widget structure and selection state,
not merely the existence of an unused HTML template.
"""
from contextlib import nullcontext
from types import SimpleNamespace
import importlib
import sys

from institutional_toolkit import evidence


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}
        self.layout = []
        self.buttons = []
        self.tables = []
        self.reruns = []
        self.expander_calls = 0
        self.click = None
        self.headings = []
        self.captions = []
        self.column_config = SimpleNamespace(LinkColumn=lambda label: label)

    def subheader(self, text):
        self.headings.append(text)

    def markdown(self, text, **kwargs):
        self.headings.append(text)

    def caption(self, text):
        self.captions.append(text)

    def container(self, **kwargs):
        return nullcontext()

    def columns(self, count, **kwargs):
        self.layout.append(count)
        return [nullcontext() for _ in range(count)]

    def button(self, label, **kwargs):
        self.buttons.append((label, kwargs))
        return kwargs.get('key') == self.click

    def dataframe(self, value, **kwargs):
        self.tables.append(value)

    def rerun(self, **kwargs):
        self.reruns.append(kwargs)

    def expander(self, *args, **kwargs):
        self.expander_calls += 1
        raise AssertionError('Institutional domains must not be in vertical expanders')


def load_ui(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    sys.modules.pop('institutional_toolkit.ui', None)
    ui = importlib.import_module('institutional_toolkit.ui')
    return ui, fake


def test_country_institutional_information_uses_real_four_column_cards(monkeypatch):
    ui, fake = load_ui(monkeypatch)
    data = evidence.load_data(str(ui.DATA))
    ui._render_country_domain_grid(data, 'Estonia')

    assert len(data['domains']) == 17
    assert fake.layout == [4, 4, 4, 4, 4]
    assert len(fake.buttons) == 17
    assert fake.expander_calls == 0
    assert 'Institutional information' in fake.headings
    assert fake.tables
    assert all('Membership' not in repr(row) for table in fake.tables for row in table)
    assert sum('linked research' in caption.lower() for caption in fake.captions) >= 17


def test_click_changes_selected_domain_and_country_is_separate(monkeypatch):
    ui, fake = load_ui(monkeypatch)
    data = evidence.load_data(str(ui.DATA))
    selected = data['domains'][4]

    fake.click = 'rs_choose_domain_Estonia_4'
    ui._render_country_domain_grid(data, 'Estonia')
    assert fake.session_state['rs_evidence_domain_selected_Estonia'] == selected
    assert fake.reruns == [{'scope': 'fragment'}]

    fake.click = None
    fake.headings.clear()
    fake.tables.clear()
    ui._render_country_domain_grid(data, 'Estonia')
    assert '### ' + selected in fake.headings

    ui._render_country_domain_grid(data, 'Sweden')
    assert fake.session_state['rs_evidence_domain_selected_Estonia'] == selected
    assert fake.session_state['rs_evidence_domain_selected_Sweden'] in data['domains']
