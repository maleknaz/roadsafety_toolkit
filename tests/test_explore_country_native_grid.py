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
        self.events = []
        self.column_config = SimpleNamespace(LinkColumn=lambda label: label)

    def subheader(self, text):
        self.headings.append(text)

    def markdown(self, text, **kwargs):
        self.headings.append(text)
        self.events.append(('markdown', text))

    def caption(self, text):
        self.captions.append(text)

    def container(self, **kwargs):
        return nullcontext()

    def columns(self, count, **kwargs):
        self.layout.append(count)
        return [nullcontext() for _ in range(count)]

    def button(self, label, **kwargs):
        self.buttons.append((label, kwargs))
        self.events.append(('button', label))
        clicked = kwargs.get('key') == self.click
        if clicked and kwargs.get('on_click'):
            kwargs['on_click'](*kwargs.get('args', ()))
        return clicked

    def dataframe(self, value, **kwargs):
        self.tables.append(value)
        self.events.append(('dataframe', value))

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
    # The callback updates session state; Streamlit handles the fragment rerun
    # automatically, so another explicit rerun should not reset scroll.
    assert fake.reruns == []

    fake.click = None
    fake.headings.clear()
    fake.tables.clear()
    ui._render_country_domain_grid(data, 'Estonia')
    assert '#### ' + selected in fake.headings

    ui._render_country_domain_grid(data, 'Sweden')
    assert fake.session_state['rs_evidence_domain_selected_Estonia'] == selected
    assert fake.session_state['rs_evidence_domain_selected_Sweden'] in data['domains']


def test_details_appear_immediately_after_selected_row_not_below_all_17(monkeypatch):
    ui, fake = load_ui(monkeypatch)
    data = evidence.load_data(str(ui.DATA))
    domains = data['domains']
    # Select a card in row 1. The detail table/callout must precede the
    # next row's first card rather than coming after the seventeenth card.
    fake.session_state['rs_evidence_domain_selected_Estonia'] = domains[1]
    ui._render_country_domain_grid(data, 'Estonia')
    detail_index = next(i for i, (typ, value) in enumerate(fake.events)
                        if typ == 'markdown' and value == '#### ' + domains[1])
    first_row_end = next(i for i, (typ, label) in enumerate(fake.events)
                         if typ == 'button' and label.startswith('04  ·'))
    second_row_start = next(i for i, (typ, label) in enumerate(fake.events)
                            if typ == 'button' and label.startswith('05  ·'))
    assert first_row_end < detail_index < second_row_start


def test_unlinked_domain_shows_explicit_evidence_gap_beneath_row(monkeypatch):
    ui, fake = load_ui(monkeypatch)
    data = evidence.load_data(str(ui.DATA))
    domain = next(d for d in data['domains']
                  if not any(evidence.url(r.get('source_url','')) for r in
                             evidence.country_context(data, 'Sweden')['institutional']
                             if r.get('domain') == d))
    fake.session_state['rs_evidence_domain_selected_Sweden'] = domain
    ui._render_country_domain_grid(data, 'Sweden')
    assert '#### ' + domain in fake.headings
    assert any('This is an evidence gap, not proof' in h for h in fake.headings)
    assert all('Membership' not in repr(row) for table in fake.tables for row in table)


def test_click_uses_callback_and_detail_is_visible_in_same_render(monkeypatch):
    ui, fake = load_ui(monkeypatch)
    data = evidence.load_data(str(ui.DATA))
    target = data['domains'][8]
    fake.click = 'rs_choose_domain_Sweden_8'
    ui._render_country_domain_grid(data, 'Sweden')
    assert fake.session_state['rs_evidence_domain_selected_Sweden'] == target
    assert '#### ' + target in fake.headings
    detail_pos = next(i for i, (typ, text) in enumerate(fake.events)
                      if typ == 'markdown' and text == '#### ' + target)
    fourth_row_start = next(i for i, (typ, text) in enumerate(fake.events)
                            if typ == 'button' and text.startswith('13  ·'))
    assert detail_pos < fourth_row_start
