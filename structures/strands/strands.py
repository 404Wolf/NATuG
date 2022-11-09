import logging
from collections import namedtuple
from contextlib import suppress
from itertools import islice
from math import dist
from typing import List, NamedTuple

import settings
from structures.misc import Profile
from structures.points import NEMid
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class Strands:
    def __init__(self, strands: List[Strand], profile: Profile) -> None:
        """
        Initialize an instance of Strands.

        Args:
            strands: A list of strands to create a Strands object from.
            profile: The settings profile to use for computations.
        """
        assert [isinstance(strand, Strand) for strand in strands]
        self.strands = strands

        assert isinstance(profile, Profile)
        self.profile = profile

        self.previous_strands = {}

    def recolor(self):
        for strand in self.strands:
            if strand.interdomain:
                illegal_colors = []

                for potentially_touching in self.strands:
                    if strand.touching(potentially_touching):
                        illegal_colors.append(potentially_touching.color)

                for color in settings.colors["strands"]["colors"]:
                    if color not in illegal_colors:
                        strand.color = color
                        break
            else:
                if strand.up_strand:
                    strand.color = settings.colors["strands"]["greys"][1]
                elif strand.down_strand:
                    strand.color = settings.colors["strands"]["greys"][0]
                else:
                    raise ValueError(
                        "Strand should all be up/down if it is single-domain."
                    )

    def add_junction(self, NEMid1: NEMid, NEMid2: NEMid) -> None:
        """
        Add a cross-strand junction where NEMid1 and NEMid2 overlap.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.
        """
        if dist(NEMid1.position(), NEMid2.position()) > settings.junction_threshold:
            raise ValueError(
                "NEMids are not close enough to create a junction.",
                NEMid1.position(),
                NEMid2.position(),
            )

        # ensure that NEMid1 is the lefter NEMid
        if NEMid1.x_coord > NEMid2.x_coord:
            NEMid1, NEMid2 = NEMid2, NEMid1

        # save the old strand references
        old_strands = (NEMid1.strand, NEMid2.strand)

        # flag the new NEMids as junctions
        NEMid1.junction, NEMid2.junction = True, True
        NEMid1.juncmate, NEMid2.juncmate = NEMid2, NEMid1

        new_strands = [Strand([]), Strand([])]

        if NEMid1.strand is NEMid2.strand:
            # create shorthand for strand since they are the same
            strand = NEMid1.strand # == NEMid2.strand

            # remove the old strands
            # note that NEMid1.strand IS NEMid2.strand
            self.strands.remove(strand)

            if NEMid2.index < NEMid1.index:
                # crawl from the index of the right NEMid to the index of the left NEMid
                new_strands[0].items.extend(
                    islice(strand.items, NEMid2.index, NEMid1.index + 1)
                )

                # crawl from the beginning of the strand to the index of the right NEMid
                new_strands[1].items.extend(
                    islice(strand.items, 0, NEMid2.index + 1)
                )
                # crawl from the index of the left NEMid to the end of the strand
                new_strands[1].items.extend(
                    islice(strand.items, NEMid1.index, None)
                )
            elif NEMid1.index < NEMid2.index:
                # crawl from the index of the left NEMid to the index of the right NEMid
                new_strands[0].items.extend(
                    islice(strand.items, NEMid1.index, NEMid2.index + 1)
                )

                # crawl from the beginning of the strand to the index of the left NEMid
                new_strands[1].items.extend(
                    islice(strand.items, 0, NEMid1.index + 1)
                )
                # crawl from the index of the right NEMid to the end of the strand
                new_strands[1].items.extend(
                    islice(strand.items, NEMid2.index, None)
                )

            logger.info("Created same-strand junction.")

        elif NEMid1.strand is not NEMid2.strand:
            # remove the old strands
            self.strands.remove(NEMid1.strand)
            self.strands.remove(NEMid2.strand)

            if NEMid1.strand.closed and NEMid2.strand.closed:
                raise NotImplementedError

                new_strands[0].items.extend(
                    islice(NEMid1.strand.items, 0, NEMid1.index)
                )
                new_strands[0].items.extend(NEMid2.strand.items)
                new_strands[0].items.extend(
                    islice(NEMid1.strand.items, NEMid1.index, None)
                )

            elif (not NEMid1.strand.closed) and (not NEMid2.strand.closed):
                # crawl from beginning of NEMid#1's strand to the junction site
                new_strands[0].items.extend(
                    islice(NEMid1.strand.items, 0, NEMid1.index + 1)
                )
                # crawl from the junction site on NEMid#2's strand to the end of the strand
                new_strands[0].items.extend(
                    islice(NEMid2.strand.items, NEMid2.index + 1, None)
                )

                # crawl from the beginning of NEMid#2's strand to the junction site
                new_strands[1].items.extend(
                    islice(NEMid2.strand.items, 0, NEMid2.index + 1)
                )
                # crawl from the junction on NEMid #1's strand to the end of the strand
                new_strands[1].items.extend(
                    islice(NEMid1.strand.items, NEMid1.index + 1, None)
                )

            logger.info("Created same-strand junction.")

        # assign the new strand to each NEMid
        # (updates NEMid.strand for all NEMids moved)
        for new_strand in new_strands:
            new_strand.assign_strands()

        # if the new strand of NEMid#1 or NEMid#2 doesn't leave its domain
        # then mark NEMid1 as not-a-junction
        for NEMid_ in (NEMid1, NEMid2):
            if not NEMid_.strand.interdomain:
                NEMid_.junction = False

        for old_strand, new_strand in zip(old_strands, new_strands):
            # if the strand isn't empty then remove the old one and add the new one
            if not new_strand.empty:
                self.strands.append(new_strand)
                # ValueError = already was removed
                with suppress(ValueError):
                    self.strands.remove(old_strand)

        self.recolor()

    @property
    def size(self) -> NamedTuple("Size", width=float, height=float):
        """
        Obtain the size of all strands when laid out.

        Returns:
            tuple(width, height)
        """
        x_coords: List[float] = []
        z_coords: List[float] = []

        for strand in self.strands:
            strand: Strand
            for NEMid_ in strand.items:
                NEMid_: NEMid
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

        return namedtuple("Size", "width height")(
            max(x_coords) - min(x_coords), max(z_coords) - min(z_coords)
        )
