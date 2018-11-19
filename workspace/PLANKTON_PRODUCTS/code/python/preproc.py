#! /usr/bin/env python

"""Pre-process a CPR/NRS plankton product file to prepare for harvesting."""

import os
import re
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd

FILENAME_PATTERN = re.compile(r"(cpr|nrs)_(phyto|zoop)_(htg|genus|species|raw|copes|noncopes)(.*).csv")

TIME_COLS = ('sampledateutc',)
DOUBLE_COLS = ('latitude', 'longitude')
REAL_TYPES = (np.float16, np.float32, np.float64)
INT_TYPES = (np.int16, np.int32, np.int64)

METADATA_COLS = ('route', 'latitude', 'longitude', 'sampledateutc', 'year', 'month', 'day', 'time_24hr')

VALID_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")

RENAME_STRINGS = [
    (r"(\d+) +- +(\d+)", "\\1-\\2"),  # remove spaces from size range e.g "30 - 50" => "30-50"
    (" " + chr(318), "u"),  # replace Greek letter "mu" with "u" and remove space before it
    (r" */ *",  "_or_"),  # "/" means "or"
    (r" *<= *", "_le_"),  # less than or equal to
    (r" *< *",  "_lt_"),  # less than
    (r" *> *",  "_gt_"),  # greater than
    (r"[()]", ""),  # strings to delete
    (r" ", "_"),  # space to underscore
]
RENAME_PATTERNS = [(re.compile(p), r) for p, r in RENAME_STRINGS]

HEADER = """
  <changeSet author="talend" id="{name}">
    <sql>
      CREATE TABLE {name} (
        id bigserial PRIMARY KEY,"""

FOOTER = """        geom geometry(Geometry,4326) CHECK (st_isvalid(geom))
      );

      CREATE INDEX {name}_gist_idx ON {name} USING GIST (geom);
    </sql>
  </changeSet>
"""


def db_type(df, col):
    """Return the the correct type for a column in the database representing the given column in a DataFrame.

    :param df: pandas DataFrame
    :param col: column name
    :returns: column type to use in database
    :rtype: str
    """
    if col.lower() in TIME_COLS:
        return 'timestamp without time zone'
    if col.lower() in DOUBLE_COLS:
        return 'double precision'
    dtype = df[col].dtype
    if dtype in REAL_TYPES:
        return 'real'
    if dtype in INT_TYPES:
        return 'integer'
    return 'text'


def rename_column(colname):
    """Rename a column so that it is a valid XML element name (required for use in a WFS).
    The rules are (https://protect-au.mimecast.com/s/DbMCCq7BJXt9Rg6QuZUDb3?domain=w3schools.com):
     * Element names are case-sensitive
     * Element names must start with a letter or underscore
     * Element names cannot start with the letters xml (or XML, or Xml, etc)
     * Element names can contain letters, digits, hyphens, underscores, and periods
     * Element names cannot contain spaces
    """
    newname = colname

    for pattern, repl in RENAME_PATTERNS:
        newname = pattern.sub(repl, newname)

    return newname


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No input file provided!")
        exit(1)

    infile = sys.argv[1]
    name_match = FILENAME_PATTERN.match(os.path.basename(infile))
    if not name_match:
        raise ValueError("File name '{name}' doesn't match expected pattern!".format(name=os.path.basename(infile)))
    outfile = name_match.expand("\\1_\\2_\\3.csv")
    table_name = name_match.expand("\\1_\\2_\\3_map")
    df = pd.read_csv(infile)
    df = df.iloc[:20]

    all_columns = []
    renamed_columns = OrderedDict()
    warning_columns = []

    print(HEADER.format(name=table_name))

    for col in df.columns:
        if "unnamed" in col.lower():  # Remove and skip "unnamed" columns
            df.drop(columns=col, inplace=True)
            continue

        if col.lower() in METADATA_COLS:
            notnull = " NOT NULL"
        else:
            notnull = ""
            df[col] = df[col].astype(np.float64)  # all data columns should be floats

        ctype = db_type(df, col)
        cname = rename_column(col)
        all_columns.append(cname)

        print('        "{cname}" {ctype}{notnull},'.format(cname=cname, ctype=ctype, notnull=notnull))

        if cname != col:
            renamed_columns[col] = cname
            continue

        if not VALID_NAME_PATTERN.match(col):
            warning_columns.append(col)

    print(FOOTER.format(name=table_name))

    # for colname, newname in renamed_columns.items():
    #     print("{:40} => {}".format(colname, newname))

    if warning_columns:
        print("WARNING! Weird named columns not renamed: {warning_columns}".format(warning_columns=warning_columns))

    # print("\nCSV Header:")
    # print(*all_columns, sep=',')

    # write template csv with updated column names and types
    df.rename(columns=renamed_columns, inplace=True)
    df.to_csv(outfile, index=False)
