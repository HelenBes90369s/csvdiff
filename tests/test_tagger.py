import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.tagger import (
    TagError, TagOptions, TaggedChange, tag_diff, changes_with_tag
)


def _fc(field="name", old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key=("1",), kind="changed"):
    fc = _fc()
    return RowChange(
        key=key,
        kind=kind,
        old_row={"id": key[0], "name": "a"} if kind != "added" else {},
        new_row={"id": key[0], "name": "b"} if kind != "removed" else {},
        field_changes=[fc] if kind == "changed" else [],
    )


def make_result(added=(), removed=(), changed=()):
    return DiffResult(added=list(added), removed=list(removed), changed=list(changed))


def test_tag_options_empty_rules_raises():
    with pytest.raises(TagError):
        TagOptions(rules={})


def test_tag_options_blank_name_raises():
    with pytest.raises(TagError):
        TagOptions(rules={"  ": lambda c: True})


def test_tag_diff_none_result_raises():
    opts = TagOptions(rules={"x": lambda c: True})
    with pytest.raises(TagError):
        tag_diff(None, opts)


def test_tag_diff_none_options_raises():
    with pytest.raises(TagError):
        tag_diff(make_result(), None)


def test_tag_diff_empty_result_returns_empty():
    opts = TagOptions(rules={"x": lambda c: True})
    assert tag_diff(make_result(), opts) == []


def test_tag_diff_applies_matching_rule():
    c = _change(kind="added")
    opts = TagOptions(rules={"new": lambda ch: ch.kind == "added"})
    result = tag_diff(make_result(added=[c]), opts)
    assert len(result) == 1
    assert result[0].tags == ["new"]


def test_tag_diff_no_match_uses_default():
    c = _change(kind="changed")
    opts = TagOptions(rules={"new": lambda ch: ch.kind == "added"}, default="other")
    result = tag_diff(make_result(changed=[c]), opts)
    assert result[0].tags == ["other"]


def test_tag_diff_no_match_no_default_empty_tags():
    c = _change(kind="changed")
    opts = TagOptions(rules={"new": lambda ch: ch.kind == "added"})
    result = tag_diff(make_result(changed=[c]), opts)
    assert result[0].tags == []


def test_tag_diff_multiple_rules_can_match():
    c = _change(kind="added")
    opts = TagOptions(rules={
        "new": lambda ch: ch.kind == "added",
        "all": lambda ch: True,
    })
    result = tag_diff(make_result(added=[c]), opts)
    assert set(result[0].tags) == {"new", "all"}


def test_changes_with_tag_filters_correctly():
    c1 = _change(key=("1",), kind="added")
    c2 = _change(key=("2",), kind="removed")
    opts = TagOptions(rules={"new": lambda ch: ch.kind == "added"})
    tagged = tag_diff(make_result(added=[c1], removed=[c2]), opts)
    found = changes_with_tag(tagged, "new")
    assert len(found) == 1
    assert found[0].key == ("1",)
