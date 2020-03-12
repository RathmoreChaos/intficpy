import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface
from intficpy.vocab import nounDict
from intficpy.actor import Actor
from intficpy.verb import (
    getVerb,
    lookVerb,
    setOnVerb,
    leadDirVerb,
    jumpOverVerb,
    giveVerb,
    examineVerb,
)
from intficpy.exceptions import ObjectMatchError


class TestParser(IFPTestCase):
    def test_verb_with_no_objects(self):
        self.game.turnMain("look")

        self.assertIs(self.game.lastTurn.verb, lookVerb)
        self.assertIsNone(self.game.lastTurn.dobj)
        self.assertIsNone(self.game.lastTurn.iobj)

    def test_verb_with_dobj_only(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)

        self.game.turnMain(f"get {dobj.name}")

        self.assertIs(self.game.lastTurn.verb, getVerb)
        self.assertIs(self.game.lastTurn.dobj, dobj)
        self.assertIsNone(self.game.lastTurn.iobj)

    def test_gets_correct_verb_with_dobj_and_direction_iobj(self):
        dobj = Actor(self._get_unique_noun())
        self.start_room.addThing(dobj)
        iobj = "east"
        self.start_room.east = self.start_room

        self.game.turnMain(f"lead {dobj.name} {iobj}")

        self.assertIs(self.game.lastTurn.verb, leadDirVerb)
        self.assertIs(self.game.lastTurn.dobj, dobj)
        self.assertEqual(self.game.lastTurn.iobj, [iobj])

    def test_gets_correct_verb_with_prepopsition_dobj_only(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)

        self.game.turnMain(f"jump over {dobj.name}")

        self.assertIs(self.game.lastTurn.verb, jumpOverVerb)
        self.assertIs(self.game.lastTurn.dobj, dobj)
        self.assertIsNone(self.game.lastTurn.iobj)

    def test_gets_correct_verb_with_preposition_dobj_and_iobj(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)
        iobj = Surface(self._get_unique_noun(), self.game)
        self.start_room.addThing(iobj)

        self.game.turnMain(f"set {dobj.name} on {iobj.name}")

        self.assertIs(self.game.lastTurn.verb, setOnVerb)
        self.assertIs(self.game.lastTurn.dobj, dobj)
        self.assertIs(self.game.lastTurn.iobj, iobj)


class TestGetGrammarObj(IFPTestCase):
    def test_gets_correct_objects_with_adjacent_dobj_iobj(self):
        dobj_item = Actor(self._get_unique_noun())
        self.start_room.addThing(dobj_item)
        iobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(iobj_item)

        self.game.turnMain(f"give {dobj_item.name} {iobj_item.name}")

        self.assertEqual(self.game.lastTurn.dobj, dobj_item)
        self.assertEqual(self.game.lastTurn.iobj, iobj_item)


class TestGetThing(IFPTestCase):
    def test_get_thing(self):
        noun = self._get_unique_noun()
        self.assertNotIn(
            noun,
            nounDict,
            f"This test needs the value of noun ({noun}) to be such that it does not "
            "initially exist in nounDict",
        )
        item1 = Thing(noun)
        self.start_room.addThing(item1)
        self.assertTrue(
            noun in nounDict, "Name was not added to nounDict after Thing creation"
        )

        self.game.turnMain(f"examine {noun}")
        self.assertIs(
            self.game.lastTurn.dobj, item1, "Failed to match item from unambiguous noun"
        )

        item2 = Thing(noun)
        self.start_room.addThing(item2)
        self.assertEqual(len(nounDict[noun]), 2)

        adj1 = "unique"
        adj2 = "special"
        self.assertNotEqual(
            adj1, adj2, "This test requires that adj1 and adj2 are not equal"
        )

        item1.setAdjectives([adj1])
        item2.setAdjectives([adj2])

        self.game.turnMain(f"examine {noun}")

        self.assertEqual(self.game.lastTurn.dobj, [noun])

        self.game.turnMain(f"examine {adj1} {noun}")
        self.assertIs(
            self.game.lastTurn.dobj,
            item1,
            "Noun adjective array should have been unambiguous, but failed to match "
            "Thing",
        )


if __name__ == "__main__":
    unittest.main()
