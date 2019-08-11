import contextlib
import os
import tempfile


@contextlib.contextmanager
def temporary_arcpy_env():
    tempdir = tempfile.gettempdir()
    tempfn = 'arcmap_envsettings.xml'
    fn = os.path.join(tempdir, tempfn)
    try:
        arcpy.SaveSettings(fn)
        yield fn
    finally:
        arcpy.LoadSettings(fn)


def search(values, field, dataset, workspace, pad="%{}%", sr=None, **kwargs):
    field = field.upper()
    with temporary_arcpy_env() as envfn:
        arcpy.env.workspace = workspace
        results = []
        for value in values:
            search_value = "'" + pad.format(value.upper()) + "'"
            with arcpy.da.SearchCursor(dataset, ['OBJECTID', 'SHAPE@', field], '"{}" LIKE {}'.format(field, search_value), sr) as cursor:
                for row in cursor:
                    if not row in results:
                        results.append(row)
    return {'rows': results, 'sr': sr}

def search_egis(values, field, dataset, **kwargs):
    return search(values, field, dataset, r'V:\GisTools\DatabaseConnections\10.2\EGIS_PRD - ENVGIS.sde', **kwargs)

def search_suburb(values, **kwargs):
    return search_egis(values, 'SUBURB', 'DCDB.Suburb', **kwargs)

def search_drillhole_name(values, **kwargs):
    return search_egis(values, 'NAME', 'WATER.Drillholes', **kwargs)

def search_drillhole_unitno(values, pad='{}', **kwargs):
    return search_egis(values, 'MAPNUM', 'WATER.Drillholes', pad=pad, **kwargs)

def search_drillhole_obsno(values, pad='{}', **kwargs):
    return search_egis(values, 'OBSNUMBER', 'WATER.Drillholes', pad=pad, **kwargs)

def sr_current():
    mxd = arcpy.mapping.MapDocument('CURRENT')
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    return df.spatialReference

def results_bounds(results, index=1):
    xmin = False
    xmax = False
    ymin = False
    ymax = False
    for row in results['rows']:
        x0, y0, x1, y1, x2, y2, x3, y3 = row[index].hullRectangle.split()
        x = [float(v) for v in [x0, x1, x2, x3]]
        y = [float(v) for v in [y0, y1, y2, y3]]
        x0 = min(x)
        x1 = max(x)
        y0 = min(y)
        y1 = max(y)
        # x0, y0, x1, y1 = row[1].bounds
        if xmin is False:
            xmin = x0
        if xmax is False:
            xmax = x1
        if ymin is False:
            ymin = y0
        if ymax is False:
            ymax = y1
        if x0 < xmin:
            xmin = x0
        if x1 > xmax:
            xmax = x1
        if y0 < ymin:
            ymin = y0
        if y1 > ymax:
            ymax = y1
    return xmin, xmax, ymin, ymax


def zoom_results_currentmap(results):
    mxd = arcpy.mapping.MapDocument('CURRENT')
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    return zoom_results(results, df)

def zoom_suburb(key, **kwargs):
    return zoom_results_currentmap(
        search_suburb([key], sr=sr_current(), **kwargs)
    )

def zoom_results(results, dataframe):
    x0, x1, y0, y1 = results_bounds(results)

    # to_sr = df.spatialReference
    # from_sr = results['sr']
    # min_pt = arcpy.Point()
    # min_pt.ptGeoms = []
    # min_pt.X = x0
    # min_pt.Y = y0
    # max_pt = arcpy.Point()
    # max_pt.ptGeoms = []
    # max_pt.X = x1
    # max_pt.Y = y1
    # ptGeoms = [
    #     arcpy.PointGeometry(min_pt, sr_from),
    #     arcpy.PointGeometry(max_pt, sr_from),
    # ]

    return zoom(dataframe, x0, x1, y0, y1)

def zoom(dataframe, x0, x1, y0, y1):
    new_extent = dataframe.extent
    new_extent.XMin = x0
    new_extent.XMax = x1
    new_extent.YMin = y0
    new_extent.YMax = y1
    dataframe.extent = new_extent
    
    # save environment settings to tempdir
    # http://resources.arcgis.com/en/help/main/10.2/index.html#/SaveSettings/03q300000047000000/
    
    # set workspace

    # get fields for dataset

    # use da.SearchCursor to find the oids

    # figure out the extent

    # see the oids and dataset are contained in a layer already in the current map

    # if they are, select the oids

    # and regardless, zoom to a reasonable extent around the selection/extent, whatever is possible.


# proxy functions for EGIS, suburb, well name.