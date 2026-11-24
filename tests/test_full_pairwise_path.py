"""Regression for the production pairwise UI path, not only a standalone grid.

An earlier release rendered a grid and then raised NameError because the
export path referenced undefined `rows`. This test invokes the full function.
"""
from __future__ import annotations
from contextlib import nullcontext
from pathlib import Path
import importlib
import sys
import types

from institutional_toolkit import evidence

ROOT=Path(__file__).resolve().parents[1]


class Col:
    def metric(self,*a,**k): pass
    def write(self,*a,**k): pass
    def markdown(self,*a,**k): pass
    def caption(self,*a,**k): pass
    def __enter__(self): return self
    def __exit__(self,*_): return False


class Fake:
    def __init__(self):
        self.session_state={}
        self.downloads=[]
    def selectbox(self,label,choices,**kwargs):
        if label=='Select the comparison country':
            return 'Sweden' if 'Sweden' in choices else choices[0]
        return choices[0]
    def columns(self,n): return [Col() for _ in range(n)]
    def expander(self,*_,**__): return nullcontext()
    def button(self,*_,**__): return False
    def download_button(self,*a,**kw): self.downloads.append((a,kw))
    def __getattr__(self,name):
        if name in ('caption','write','markdown','subheader','divider','info','warning','error','metric'):
            return lambda *a,**k: None
        raise AttributeError(name)


def test_comparison_function_does_not_crash_after_grid(monkeypatch):
    fake_module=types.ModuleType('streamlit')
    fake=Fake()
    fake_module.session_state=fake.session_state
    monkeypatch.setitem(sys.modules,'streamlit',fake_module)
    sys.modules.pop('institutional_toolkit.ui',None)
    ui=importlib.import_module('institutional_toolkit.ui')
    monkeypatch.setattr(ui,'st',fake)
    selected=[]
    monkeypatch.setattr(ui,'_render_domain_grid',lambda rows,a,b: selected.append((rows,a,b)))
    d=evidence.load_data(str(ROOT/'data'))
    ui._pairwise(d,'Estonia')
    assert len(selected)==1
    assert len(selected[0][0])==17
    assert (selected[0][1],selected[0][2])==('Estonia','Sweden')
    assert any('Excel' in str(args)+str(kwargs) for args,kwargs in fake.downloads)


def test_country_domain_records_remain_separate():
    from institutional_toolkit.domain_views import country_view,comparison_view
    d=evidence.load_data(str(ROOT/'data'))
    for country in ('Estonia','Sweden','Canada','Afghanistan'):
        html=country_view(d,country)
        assert html.count('class="domain-card"')==17
        assert 'Membership' not in html
        assert country in html
    html=comparison_view(evidence.compare(d,'Estonia','Sweden'),'Estonia','Sweden')
    assert html.count('class="domain-card"')==17
    assert 'Open source' in html
    assert 'Transport Administration and Government Traffic Commission' in html
    assert 'Swedish Transport Administration' in html
