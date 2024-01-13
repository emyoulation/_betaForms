#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016       Tim G L Lyons
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# $Id:
#
#
"""
Display whether census records have been found for a person, their spouse(s)
and
children
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc, SimpleTable
from gramps.gui.plug.quick import QuickTable
from gramps.gen.const import GRAMPS_LOCALE as glocale
import form
from gramps.gen.utils.alive import probably_alive, probably_alive_range

_ = glocale.get_addon_translator(__file__).gettext


def process_person(database, sa, stab, person, census_list):
   if not person:
       return

   # Check for any existing census events for the person
   found_census = []
   for event_ref in person.get_event_ref_list():
       event = database.get_event_from_handle(event_ref.ref)
       if event:
           citation = form.get_form_citation(database, event)
           if citation:
               source_handle = citation.get_reference_handle()
               source = database.get_source_from_handle(source_handle)
               if source:
                   form_id = form.get_form_id(source)
                   found_census.append(form_id)

   # Process all the possible censuses
   census_result = ()
   for key in sorted(census_list):
       if key in found_census:
           census_result += ("✔", )
       else:
           (b, d, ex, rel) = probably_alive_range(person, database)
           if probably_alive(person, database, census_list[key]):
               # If the person would be less than 100, the record may be closed
               if probably_alive(person, database, max_age_prob_alive=100):
                   census_result += ("⛔", )
               else:
                   census_result += ("❓", )
           else:
               census_result += ("—", )

   # Construct the results line
   columns = (sa.name(person), sa.birth_date_obj(person),
              sa.death_date_obj(person)) + census_result
   stab.row(*columns)


def run(database, document, person):
   """
   Display whether census records have been found for a person, their
   spouse(s) and children
   """

   # Construct a dictionary of census IDs and date
   census_list = {}
   for handle in database.get_source_handles():
       source = database.get_source_from_handle(handle)
       form_id = form.get_form_id(source)
       if form_id in form.get_form_ids():
           form_type = form.get_form_type(form_id)
           if form_type == "Census":
               census_list[form_id] = form.get_form_date(form_id)

   sa = SimpleAccess(database)
   sd = SimpleDoc(document)
   sd.title(_("Census Check for %s") % sa.name(person))
   sd.paragraph("")
   stab = QuickTable(sa)

   columns = (_("Name"), _("Birth date"), _("Death date")) + \
       tuple(key for key in sorted(census_list))
   stab.columns(*columns)
   # stab.set_link_col(1)

   process_person(database, sa, stab, person, census_list)

   for family in sa.parent_in(person):
       father = sa.father(family)
       mother = sa.mother(family)
       if father.handle != person.handle:
           spouse = father
       else:
           spouse = mother
       process_person(database, sa, stab, spouse, census_list)
       for child in sa.children(spouse):
           process_person(database, sa, stab, child, census_list)

   stab.write(sd)
   sd.paragraph("")
