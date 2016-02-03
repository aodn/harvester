"
WITH std_agg AS ( 
       SELECT string_agg(value, ', ') AS standard_names
       FROM variable_attribute 
       WHERE file_id = " + context.fileId + " AND 
             name='standard_name' AND
             value !~ 'flag$'
     ), var_agg AS (
       SELECT string_agg(name, ', ') AS variables
       FROM variable
       WHERE file_id = " + context.fileId + " AND
             name !~ '_quality_control$'
     )
UPDATE file_metadata m
  SET
    feature_type = getglobalattribute(f.id, 'featureType'),
    file_version = substring(f.url, '_FV0([012])'),
    toolbox_version = getglobalattribute(f.id, 'toolbox_version'),
    compliance_checker_version = getglobalattribute(f.id, 'compliance_checker_version'),
    compliance_checker_last_updated = getglobalattributeastimestamp(f.id, 'compliance_checker_last_updated'),
    compliance_checks_passed = 
        substring(getglobalattribute(f.id, 'history'), 'passed compliance checks: ([^(]*) \\('),
    site_code = getglobalattribute(f.id, 'site_code'),
    platform_code = getglobalattribute(f.id, 'platform_code'),
    deployment_code = getglobalattribute(f.id, 'deployment_code'),
    instrument = getglobalattribute(f.id, 'instrument'),
    instrument_serial_number = getglobalattribute(f.id, 'instrument_serial_number'),
    instrument_nominal_depth = getglobalattribute(f.id, 'instrument_nominal_depth'),
    geospatial_vertical_min = getglobalattributeasdouble(f.id, 'geospatial_vertical_min'),
    geospatial_vertical_max = getglobalattributeasdouble(f.id, 'geospatial_vertical_max'),
    date_created = getglobalattributeastimestamp(f.id, 'date_created'),
    time_coverage_start = getglobalattributeastimestamp(f.id, 'time_coverage_start'),
    time_coverage_end = getglobalattributeastimestamp(f.id, 'time_coverage_end'),
    time_deployment_start = getglobalattributeastimestamp(f.id, 'time_deployment_start'),
    time_deployment_end = getglobalattributeastimestamp(f.id, 'time_deployment_end'),
    geom = st_geomfromtext('POINT(' || longitude::text || ' ' || latitude::text || ')', 4326),
    data_category = substring(f.url, '/(Temperature|CTD_timeseries|CTD_profiles|Biogeochem_timeseries|Biogeochem_profiles|Velocity|Wave|CO2|Meteorology)'),
    variables = v.variables,
    standard_names = s.standard_names,
    realtime = (f.url ~ 'realtime|REAL_TIME'),
    deleted = false
  FROM indexed_file f, std_agg s, var_agg v
  WHERE m.file_id = f.id AND f.id = " + context.fileId
