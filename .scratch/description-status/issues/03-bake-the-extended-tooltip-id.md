# 03: The install bakes the extended tooltip id

**What to build:** Reading an object's vanilla description text in game needs the extended tooltip
string id, which is the dat's name string id plus a fixed offset. The runtime attribute that looks
like that id is not it: for the Villager it reports a different number whose derived tooltip does
not exist, and for Gaia objects it reports nothing. So the ids are baked rather than derived at
runtime. A checked-in source module holds the name string id for every technology, unit and
building the seed can install, stamped with where the data came from the way the game-cost table is,
and a maintainer-run tool regenerates it by reading the game dat through aoe2kit. The technology
and unit row generators emit the extended tooltip id per installed row, and the game's
thirty-five-building table carries one per building. Nothing reads the ids yet.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A source module holds the ids and names its provenance; a tool beside the other maintainer
      tools regenerates it from the game dat and says how to run it the way they do
- [ ] Every decorated technology row and unit row carries the extended tooltip id, and a row the
      seed does not install carries none
- [ ] The ids the rows carry agree with the source module rather than being invented or computed
      from a runtime value
- [ ] The building table carries one id per building, from the same source
- [ ] The table loaders in the game accept the extra field, and the xs lints from the xs folder
      against the entry point
- [ ] Covered as the technology and unit catalogues already are: build the table, assert on the rows
- [ ] The pre-commit subset for the files touched passes, plus the technology and unit catalogue
      tests
