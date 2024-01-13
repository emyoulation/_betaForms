#------------------------------------------------------------------------
#
# Register the report
#
#------------------------------------------------------------------------

register(QUICKREPORT,
        id    = 'censuscheckquickview',
        name  = _("Census Check"),
        description= _("Check whether any Census events are missing for"
                       " a person and some of their descendents"),
        version = '1.0.2',
        gramps_target_version = '5.1',
        status = STABLE,
        fname = 'censuscheckquickview.py',
        authors = ["Tim Lyons"],
        authors_email = ["hidden"],
        category = CATEGORY_QR_PERSON,
        runfunc = 'run',
 )
