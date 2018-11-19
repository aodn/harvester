UPDATE cpr_phyto_htg_mat m
  SET geom = st_geomfromtext('POINT(' || \"Longitude\"::text || ' ' || \"Latitude\"::text || ')', 4326) ;
