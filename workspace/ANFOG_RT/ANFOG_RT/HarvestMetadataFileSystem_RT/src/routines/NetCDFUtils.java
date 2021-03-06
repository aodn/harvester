package routines;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

import ucar.nc2.units.DateUnit;

/*
 * user specification: the function's comment should contain keys as follows: 1. write about the function's comment.but
 * it must be before the "{talendTypes}" key.
 * 
 * 2. {talendTypes} 's value must be talend Type, it is required . its value should be one of: String, char | Character,
 * long | Long, int | Integer, boolean | Boolean, byte | Byte, Date, double | Double, float | Float, Object, short |
 * Short
 * 
 * 3. {Category} define a category for the Function. it is required. its value is user-defined .
 * 
 * 4. {param} 's format is: {param} <type>[(<default value or closed list values>)] <name>[ : <comment>]
 * 
 * <type> 's value should be one of: string, int, list, double, object, boolean, long, char, date. <name>'s value is the
 * Function's parameter name. the {param} is optional. so if you the Function without the parameters. the {param} don't
 * added. you can have many parameters for the Function.
 * 
 * 5. {example} gives a example for the Function. it is optional.
 */
public class NetCDFUtils {
    /**
     * addDays: add days including fractional component to reference date.
     * 
     * 
     * {talendTypes} Date
     * 
     * {Category} NetCDF
     * 
     * {param} date(referenceDate) input: the reference date.
     * 
     * {param} double(addValue) days : days since the reference date including fractional component
     * 
     * {param} boolean(nearestSecond) nearestSecond : round to nearest second
     * 
     * {example} 
     * 
     * ->> addDays(referenceDate, new Double("19326.1830555648", false) returns date 30/11/2002 04:23:36 with reference 
     * date 1/1/1950 00:00:00 #
     */
    public static Date addDays(Date referenceDate, Double days, boolean nearestSecond) {
        if (days == null || days.isNaN()) return null;
        
        DateUnit netcdfDate;
        
        try {
            SimpleDateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            netcdfDate = new DateUnit(days + " days since " + dateFormatter.format(referenceDate));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

        Date result = netcdfDate.getDate();
        
        if (nearestSecond) {
            Calendar cal = Calendar.getInstance();
            cal.setTime(result);
            cal.add( Calendar.MILLISECOND, 500 );
            cal.set( Calendar.MILLISECOND, 0);
            result = cal.getTime();
        }
        
        return result;
    }
    
    /**
     * addDays: add days including fractional component to reference date.
     * 
     * 
     * {talendTypes} Date
     * 
     * {Category} NetCDF
     * 
     * {param} date(referenceDate) input: the reference date.
     * 
     * {param} double(addValue) days : days since the reference date including fractional component
     * 
     * {example} 
     * 
     * ->> addDays(referenceDate, new Double("19326.1830555648") returns date 30/11/2002 04:23:36 with reference 
     * date 1/1/1950 00:00:00 #
     */
    public static Date addDays(Date referenceDate, Double days) {
        return addDays(referenceDate, days, false);
    }
    
	
    /**
     * addDays: add days including fractional component to reference date.
     * 
     * 
     * {talendTypes} Date
     * 
     * {Category} NetCDF
     * 
     * {param} string(referenceDate) input: the reference date.
     * 
     * {param} string(format) input: format of the reference date (as per SimpleDateFormat).
     * 
     * {param} double(addValue) days : days since the reference date including fractional component
     * 
     * {param} boolean(nearestSecond) nearestSecond : round to nearest second
     * 
     * {example} 
     * 
     * ->> addDays("19500101000000", "yyyyMMddHHmmss", new Double("19326.1830555648", false) returns date 30/11/2002 04:23:36 #
     */
    public static Date addDays(String stringDate, String format, Double days, boolean nearestSecond) {
        if (stringDate == null || stringDate.equals("")) return null;
        
        return addDays(TalendDate.parseDate(format, stringDate), days, nearestSecond);
    }

    /**
     * addDays: add days including fractional component to reference date.
     * 
     * 
     * {talendTypes} Date
     * 
     * {Category} NetCDF
     * 
     * {param} string(referenceDate) input: the reference date.
     * 
     * {param} string(format) input: format of the reference date (as per SimpleDateFormat).
     * 
     * {param} double(addValue) days : days since the reference date including fractional component
     * 
     * {example} 
     * 
     * ->> addDays("19500101000000", "yyyyMMddHHmmss", new Double("19326.1830555648") returns date 30/11/2002 04:23:36 #
     */
    public static Date addDays(String stringDate, String format, Double days) {
        return addDays(stringDate, format, days, false);
    }
}
