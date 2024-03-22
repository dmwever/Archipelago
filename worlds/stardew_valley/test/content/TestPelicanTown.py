from . import SVContentPackTestBase
from ...strings.fish_names import Fish
from ...strings.villager_names import NPC


class TestPelicanTown(SVContentPackTestBase):

    def test_all_pelican_town_villagers_are_included(self):
        self.assertIn(NPC.alex, self.content.villagers)
        self.assertIn(NPC.elliott, self.content.villagers)
        self.assertIn(NPC.harvey, self.content.villagers)
        self.assertIn(NPC.sam, self.content.villagers)
        self.assertIn(NPC.sebastian, self.content.villagers)
        self.assertIn(NPC.shane, self.content.villagers)
        self.assertIn(NPC.abigail, self.content.villagers)
        self.assertIn(NPC.emily, self.content.villagers)
        self.assertIn(NPC.haley, self.content.villagers)
        self.assertIn(NPC.leah, self.content.villagers)
        self.assertIn(NPC.maru, self.content.villagers)
        self.assertIn(NPC.penny, self.content.villagers)
        self.assertIn(NPC.caroline, self.content.villagers)
        self.assertIn(NPC.clint, self.content.villagers)
        self.assertIn(NPC.demetrius, self.content.villagers)
        self.assertIn(NPC.dwarf, self.content.villagers)
        self.assertIn(NPC.evelyn, self.content.villagers)
        self.assertIn(NPC.george, self.content.villagers)
        self.assertIn(NPC.gus, self.content.villagers)
        self.assertIn(NPC.jas, self.content.villagers)
        self.assertIn(NPC.jodi, self.content.villagers)
        self.assertIn(NPC.kent, self.content.villagers)
        self.assertIn(NPC.krobus, self.content.villagers)
        self.assertIn(NPC.lewis, self.content.villagers)
        self.assertIn(NPC.linus, self.content.villagers)
        self.assertIn(NPC.marnie, self.content.villagers)
        self.assertIn(NPC.pam, self.content.villagers)
        self.assertIn(NPC.pierre, self.content.villagers)
        self.assertIn(NPC.robin, self.content.villagers)
        self.assertIn(NPC.sandy, self.content.villagers)
        self.assertIn(NPC.vincent, self.content.villagers)
        self.assertIn(NPC.willy, self.content.villagers)
        self.assertIn(NPC.wizard, self.content.villagers)

        self.assertEqual(33, len(self.content.villagers))

    def test_all_pelican_town_fishes_are_included(self):
        fish_names = self.content.fishes.keys()

        self.assertIn(Fish.albacore, fish_names)
        self.assertIn(Fish.anchovy, fish_names)
        self.assertIn(Fish.bream, fish_names)
        self.assertIn(Fish.bullhead, fish_names)
        self.assertIn(Fish.carp, fish_names)
        self.assertIn(Fish.catfish, fish_names)
        self.assertIn(Fish.chub, fish_names)
        self.assertIn(Fish.dorado, fish_names)
        self.assertIn(Fish.eel, fish_names)
        self.assertIn(Fish.flounder, fish_names)
        self.assertIn(Fish.ghostfish, fish_names)
        self.assertIn(Fish.goby, fish_names)
        self.assertIn(Fish.halibut, fish_names)
        self.assertIn(Fish.herring, fish_names)
        self.assertIn(Fish.ice_pip, fish_names)
        self.assertIn(Fish.largemouth_bass, fish_names)
        self.assertIn(Fish.lava_eel, fish_names)
        self.assertIn(Fish.lingcod, fish_names)
        self.assertIn(Fish.midnight_carp, fish_names)
        self.assertIn(Fish.octopus, fish_names)
        self.assertIn(Fish.perch, fish_names)
        self.assertIn(Fish.pike, fish_names)
        self.assertIn(Fish.pufferfish, fish_names)
        self.assertIn(Fish.rainbow_trout, fish_names)
        self.assertIn(Fish.red_mullet, fish_names)
        self.assertIn(Fish.red_snapper, fish_names)
        self.assertIn(Fish.salmon, fish_names)
        self.assertIn(Fish.sandfish, fish_names)
        self.assertIn(Fish.sardine, fish_names)
        self.assertIn(Fish.scorpion_carp, fish_names)
        self.assertIn(Fish.sea_cucumber, fish_names)
        self.assertIn(Fish.shad, fish_names)
        self.assertIn(Fish.slimejack, fish_names)
        self.assertIn(Fish.smallmouth_bass, fish_names)
        self.assertIn(Fish.squid, fish_names)
        self.assertIn(Fish.stonefish, fish_names)
        self.assertIn(Fish.sturgeon, fish_names)
        self.assertIn(Fish.sunfish, fish_names)
        self.assertIn(Fish.super_cucumber, fish_names)
        self.assertIn(Fish.tiger_trout, fish_names)
        self.assertIn(Fish.tilapia, fish_names)
        self.assertIn(Fish.tuna, fish_names)
        self.assertIn(Fish.void_salmon, fish_names)
        self.assertIn(Fish.walleye, fish_names)
        self.assertIn(Fish.woodskip, fish_names)
        self.assertIn(Fish.blob_fish, fish_names)
        self.assertIn(Fish.midnight_squid, fish_names)
        self.assertIn(Fish.spook_fish, fish_names)
        self.assertIn(Fish.angler, fish_names)
        self.assertIn(Fish.crimsonfish, fish_names)
        self.assertIn(Fish.glacierfish, fish_names)
        self.assertIn(Fish.legend, fish_names)
        self.assertIn(Fish.mutant_carp, fish_names)
        self.assertIn(Fish.clam, fish_names)
        self.assertIn(Fish.cockle, fish_names)
        self.assertIn(Fish.crab, fish_names)
        self.assertIn(Fish.crayfish, fish_names)
        self.assertIn(Fish.lobster, fish_names)
        self.assertIn(Fish.mussel, fish_names)
        self.assertIn(Fish.oyster, fish_names)
        self.assertIn(Fish.periwinkle, fish_names)
        self.assertIn(Fish.shrimp, fish_names)
        self.assertIn(Fish.snail, fish_names)

        self.assertEqual(62, len(self.content.fishes))
