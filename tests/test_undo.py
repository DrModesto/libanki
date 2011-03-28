# coding: utf-8

import time
from tests.shared import assertException, getEmptyDeck
from anki.stdmodels import BasicModel

def test_op():
    d = getEmptyDeck()
    # should have no undo by default
    assert not d.undoName()
    # let's adjust a study option
    assert d.qconf['repLim'] == 0
    d.save("studyopts")
    d.qconf['repLim'] = 10
    # it should be listed as undoable
    assert d.undoName() == "studyopts"
    # with about 5 minutes until it's clobbered
    assert time.time() - d._lastSave < 1
    # undoing should restore the old value
    d.undo()
    assert not d.undoName()
    assert d.qconf['repLim'] == 0
    # an (auto)save will clear the undo
    d.save("foo")
    assert d.undoName() == "foo"
    d.save()
    assert not d.undoName()
    # and a review will, too
    d.save("add")
    f = d.newFact()
    f['Front'] = u"one"
    d.addFact(f)
    d.reset()
    assert d.undoName() == "add"
    c = d.sched.getCard()
    d.sched.answerCard(c, 2)
    assert d.undoName() == "Review"

def test_review():
    d = getEmptyDeck()
    f = d.newFact()
    f['Front'] = u"one"
    d.addFact(f)
    d.reset()
    assert not d.undoName()
    # answer
    assert d.sched.counts() == (1, 0, 0)
    c = d.sched.getCard()
    assert c.queue == 0
    assert c.grade == 0
    d.sched.answerCard(c, 2)
    assert d.sched.counts() == (0, 1, 0)
    assert c.queue == 1
    assert c.grade == 1
    # undo
    assert d.undoName()
    d.undo()
    d.reset()
    assert d.sched.counts() == (1, 0, 0)
    c.load()
    assert c.queue == 0
    assert c.grade == 0
    assert not d.undoName()
    # we should be able to undo multiple answers too
    f['Front'] = u"two"
    d.addFact(f)
    d.reset()
    assert d.sched.counts() == (2, 0, 0)
    c = d.sched.getCard()
    d.sched.answerCard(c, 2)
    c = d.sched.getCard()
    d.sched.answerCard(c, 2)
    assert d.sched.counts() == (0, 2, 0)
    d.undo()
    d.reset()
    assert d.sched.counts() == (1, 1, 0)
    d.undo()
    d.reset()
    assert d.sched.counts() == (2, 0, 0)
    # performing a normal op will clear the review queue
    c = d.sched.getCard()
    d.sched.answerCard(c, 2)
    assert d.undoName() == "Review"
    d.save("foo")
    assert d.undoName() == "foo"
    d.undo()
    assert not d.undoName()

