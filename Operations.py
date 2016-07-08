import numpy
import math
import Objects

def grab_x_ys(elution_ends, slope, intercept):
    ''' 
    Output two pairs of (x, y) coordinates for plotting a regression line
    elution_ends is the x-series (list)
    intrecept and slope are ints
    '''
    
    last_elution = elution_ends[len(elution_ends) - 1] 
    
    x1 = 0
    x2 = last_elution   
    y1 = intercept
    y2 = slope * last_elution + intercept
    
    return (x1, y1), (x2, y2)

def basic_run_calcs(rt_wght, gfact, elut_starts, elut_ends, elut_cpms):
    '''Given initial CATE data, return elution data as corrected for
    G Factor, normalized for root weight, and logged
    '''    
    elut_cpms_gfact = [x * gfact for x in elut_cpms]
    elut_cpms_gRFW = []
    elut_cpms_log = []

    for index, item in enumerate(elut_cpms_gfact):
        temp = item / rt_wght / (elut_ends[index] - elut_starts[index])
        elut_cpms_gRFW.append(temp)
        elut_cpms_log.append(math.log10(temp))
                
    return elut_cpms_gfact, elut_cpms_gRFW, elut_cpms_log

def linear_regression(x, y):
    ''' Linear regression of x and y series (lists)
    Returns r^2 and m (slope), b (intercept) of y=mx+b
    '''
    coeffs = numpy.polyfit(x, y, 1)
        
    # Conversion to "convenience class" in numpy for working with polynomials        
    p = numpy.poly1d(coeffs)     
    
    # Determining R^2 on the current data set, fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = numpy.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = numpy.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = numpy.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    r2 = ssreg/sstot
    slope = coeffs[0]
    intercept = coeffs[1]
    
    return r2, slope, intercept

def set_obj_phases(run, obj_num_pts):
    '''
    Use objective regression to determine 3 phases exchange in data
    Phase 3 is found by identifying where r2 decreases for 3 points in a row
    Phase 1 and 2 is found by identifying the paired series in the remaining 
        data that yields the highest combined r2s
    obj_num_pts allows the user to specificy how mmany points we will ignore at
        the end of the data series before we start comparing r2s
    Returns tuples outlining limits of each phase, m and b of phase 3, and 
        lists of initial intercepts(bs)/slopes(ms)/r2s
    '''
    elut_ends, elut_cpms_log = run.elut_ends, run.elut_cpms_log
    r2s = []
    ms = [] # y = mx+b
    bs = []

    # Storing all possible r2s/ms/bs
    for index in range(len(elut_cpms_log)-2, -1, -1):
        temp_x = elut_ends[index:]
        temp_y = elut_cpms_log[index:]
        temp_r2, temp_m, temp_b = linear_regression(temp_x, temp_y)
        r2s =[temp_r2] + r2s
        ms = [temp_m] + ms
        bs = [temp_b] + bs
        
    # Determining the index at which r2 drops three times in a row 
    # from obj_num_pts from the end of the series
    counter = 0
    for index in range(len(elut_ends) - 1 - obj_num_pts, -1, -1):    
        # print elut_ends[index], elut_cpms_log[index], r2s[index], counter
        if r2s[index-1] < r2s[index]:
            counter += 1
            if counter == 3:
                break
        else:
            counter = 0
    start_p3 = index + 3
    end_p3 = -1 # end indexs are going to be inclusive of last result in phase
    r2_p3 = r2s[start_p3]
    m_p3 = ms[start_p3]
    b_p3 = bs[start_p3]

    # print elut_ends[:start_p3_index], elut_cpms_log[index], r2s[index], counter
    # print r2s

    # Now we have to determine the p1/p2 combo that gives us the highest r2
    temp_x_p12 = elut_ends[:start_p3]
    temp_y_p12 = elut_cpms_log[:start_p3]
    highest_r2 = 0

    for index in range(1, len(temp_x_p12) - 2): #-2 bec. min. len(list) = 2
        temp_start_p2 = index + 1
        temp_x_p2 = temp_x_p12[temp_start_p2:]
        temp_y_p2 = temp_y_p12[temp_start_p2:]
        temp_x_p1 = temp_x_p12[:temp_start_p2]
        temp_y_p1 = temp_y_p12[:temp_start_p2]
        temp_r2_p2, temp_m_p2, temp_b_p2 = linear_regression(temp_x_p2, temp_y_p2)
        temp_r2_p1, temp_m_p1, temp_b_p1 = linear_regression(temp_x_p1, temp_y_p1)
        if temp_r2_p1 + temp_r2_p2 > highest_r2:
            # print temp_x_p1, temp_x_p2, temp_r2_p1, temp_r2_p2
            highest_r2 = temp_r2_p1 + temp_r2_p2
            start_p2, end_p2 = temp_start_p2, start_p3
            start_p1, end_p1 = 0, temp_start_p2
             # these values are stored but I don't think I will need them 
             # (are calcylated by more general algorithms)
             # UPDATE: I'm fairly certain that I am correct
            r2_p2, m_p2, b_p2 = temp_r2_p2, temp_m_p2, temp_b_p2
            r2_p1, m_p1, b_p1 = temp_r2_p1, temp_m_p1, temp_b_p1

    return (start_p3, end_p3), (start_p2, end_p2), (start_p1, end_p1)

def extract_phase3(indexs, x, y, SA, load_time):
    '''
    Extract and return paramters from regression analysis of phase 3.
    indexs are a 2 item tuple, x and y are numpy arrays of elut_ends and
    elut_cpms_log 
    '''
    start_p3 = indexs[0]
    end_p3 = indexs[1]
    x_p3 = x[start_p3:end_p3]
    y_p3 = y[start_p3:end_p3]

    r2, slope, intercept = linear_regression(x, y) # y=(M)x+(B)
    xy1, xy2 = grab_x_ys(x, slope, intercept)
    k = abs(slope * 2.303)
    t05 = 0.693/k
    r0 = 10 ** intercept
    efflux = 60 * (r0 / (SA * (1 - math.exp(-k * load_time))))

    return Objects.Phase(
        indexs, xy1, xy2, r2, slope, intercept, x_p3, y_p3, k, t05, r0, efflux)

def p1_curve_stripped(p1_x, p1_y, last_used_index, slope, intercept):
    '''
    Curve-strip p1 (in the same list) according to p2 data
    Note: p1 data coming in (log_efflux) has been corrected for p3 already
    
    INPUT:
    p1_x (x-series; list) - elution end points (min)
    p1_y (y-series; list) - normalized efflux data (log cpm/g RFW)
    slope, intercept (ints) - line parameters of p2 regression
        
    RETURNED:
    p12_x (x-series; list) - elution_ends limited to range of p1 and p2
    corrected_p12_y (y-series; list) - corrected (curve-stripped) efflux data
    '''
    # Calculating p1 data from extrapolation of p2 linear regression into p1

    # Container for p3 data in p1/2 range
    p2_extrapolated_raw = []
    
    for x1 in range (0, len(p1_x)):
        extrapolated_x = (slope * x1) + intercept
        p2_extrapolated_raw.append(extrapolated_x)    

def p12_curvestrippedof_p3(x_p12, y_p12, slope, intercept):
    '''
    Curve-strip p1 and p2 (in the same list) according to p3 data
    
    INPUT:
    x_p12 (x-series; list) - elution end points (min) for p12 data
    y_p12 (y-series; list) - logged efflux data for p12 data unstripped
    
    RETURNED:
    p12_x (x-series; list) - elution_ends limited to range of p1 and p2
    corrected_p12_y (y-series; list) - corrected (curve-stripped) efflux data
    '''
    
    # Calculating p3 data from extrapolation of p3 linear regression into p1/2

    # Calculating p3 data extrapolated into p1/2 range
    p3_extrapolated_raw = []
    
    for x in range (0, len(x_p12)):
        extrapolated_x = (slope*x_p12[x]) + intercept
        p3_extrapolated_raw.append(extrapolated_x)
        
    # Antilog extrapolated p3 data and p1/2 data, subtract them, and relog them
    
    # Containers for curve-stripped p1/2 data
    corrected_p12_x = []
    corrected_p12_y = []
    
    for value in range (0, len(y_p12)):
        antilog_orig = 10 ** y_p12[value]
        antilog_reg = 10 ** p3_extrapolated_raw[value]
        corrected_p12_x_raw = antilog_orig - antilog_reg
        if corrected_p12_x_raw > 0: # We can perform a log operation
            corrected_p12_y.append(math.log10 (corrected_p12_x_raw))
            corrected_p12_x.append(x_p12[value])
                
    return corrected_p12_x, corrected_p12_y

def p1_curvestrippedof_p23(x_p1_curvestrippedof_p3, y_p1_curvestrippedof_p3, slope, intercept):
    '''
    Curve-strip p1 according to p2/3 data
    
    INPUT:
    elution_ends (x-series; list) - elution end points (min)
    log_efflux (y-series; list) - normalized efflux data (log cpm/g RFW)
    last_used_index is the first right-most point used in the p3 regression
        - used as end index for p2 because [x:y] y IS NOT INCLUSIVE
    
    RETURNED:
    p12_x (x-series; list) - elution_ends limited to range of p1 and p2
    corrected_p12_y (y-series; list) - corrected (curve-stripped) efflux data
    '''
    
    # Calculating p3 data from extrapolation of p3 linear regression into p1/2

    p2_extrapolated_raw = []
        
    for x in range (0, len(x_p1_curvestrippedof_p3)):
        extrapolated_x = (slope*x_p1_curvestrippedof_p3[x]) + intercept
        p2_extrapolated_raw.append(extrapolated_x)
            
    # Antilog extrapolated p3 data and p1/2 data, subtract them, and relog them
    
    # Container for curve-stripped p1/2 data
    corrected_p1_x = []
    corrected_p1_y = []
    
    for value in range (0, len(y_p1_curvestrippedof_p3)):
        antilog_orig = 10 ** y_p1_curvestrippedof_p3 [value]
        antilog_reg = 10 ** p2_extrapolated_raw [value]
        corrected_p1_x_raw = antilog_orig - antilog_reg
        
        if corrected_p1_x_raw > 0: # We can perform a log operation
            corrected_p1_y.append(math.log10 (corrected_p1_x_raw))
            corrected_p1_x.append(x_p1_curvestrippedof_p3[value])

    return corrected_p1_x, corrected_p1_y
   
def determine_p1_xy(p12_elution_ends, p12_log_efflux):     
    ''' Figuring out x/y-series that yield strongest correlations 
    (regression lines) for phases 1 and 2
    
    INPUT:
    elution_ends (x-series; list) - elution end points (min) of p1 + p2
    log_efflux (y-series; list) - normalized efflux data (log cpm/g RFW) of
         of p1 + p2
    
    RETURNED:
    Ordered lists (best_x1, best_y1) contained x and y series of p1 that yields
       the highest R^2 taking into account combined R^2 of possilbe p1/p2
    '''
    
    # Initialize the index(s) for the first regressions
    demarcation_index = 2 # Start regression using 1st 2 pts vs rest of series
    current_high_r2 = 0 # Tracking highest summed R^2 from p1 and p2
    last_used_index = len(p12_elution_ends)
        
    while demarcation_index < last_used_index - 1: 
        # Correcting loop end (last_used_index - 1) 
        # as otherwise x2_current = x [demarcation_index:] is only 1 entry.
        # Last index in lists is not inclusive!
        # So we can use one var to track end and start indexs of p1/2 regression
        
        # Setting current series for p1 regression
        x1_current = p12_elution_ends[:demarcation_index]
        y1_current = p12_log_efflux[:demarcation_index]
        # Setting current series for p2 regression
        x2_current = p12_elution_ends[demarcation_index:]
        y2_current = p12_log_efflux[demarcation_index:]     
        
        # Doing the current set of regressions
        current_p1_regression = linear_regression(x1_current, y1_current)
        current_p2_regression = linear_regression(x2_current, y2_current)
    
        current_r2_p1 = current_p1_regression[0]        
        current_r2_p2 = current_p2_regression[0]        
        
        # Checking to see if our last R^2 is higher than highest R^2
        if current_r2_p1 + current_r2_p2 > current_high_r2:
            # If it is the new highest R^2 we store p1/2 regression parameters
            current_high_r2 = current_r2_p1 + current_r2_p2
    
            best_x1 = x1_current
            best_y1 = y1_current
            best_r2_1 = current_r2_p1
            best_slope_1 = current_p1_regression[1]
            best_intercept_1 = current_p1_regression[2]
            
            best_x2 = x2_current
            best_y2 = y2_current
            best_r2_2 = current_r2_p2
            best_slope_2 = current_p2_regression[1]
            best_intercept_2 = current_p2_regression[2]
        # Moving the index counter forward
        demarcation_index += 1
        
    return best_x1, best_y1
  
    
def obj_regression_p3(elution_ends, log_efflux, num_points_reg):     
    ''' Figuring out R^2 (correlation) and parameters of linear regression.
    Linear regression gives the data about the 3rd phase of exchange (p3)
    
    elutions_ends are teh times when elutions  CHANGED/REMOVED. 
    elution_starts are times when elutions ADDED.
    
    Line parameters for the linear regression are returned as well as the lists containing the regression
    parameters for ALL the regressions done in the objective regression
    
    In the lists, the first three entries are parameters from regressions that are 
    discarded (r2 was decreasing).
    
    Parameters of interest are at the 4th index of each list (List[3])
    
    INPUT:
    elution_ends (x-series; list) - elution end points (min)
    log_efflux (y-series; list) - normalized efflux data (log cpm/g RFW)
    
    RETURNED:
    Line parameters for the linear regression (x1, x2, y1, y2, r2, slope; ints)
    '''
    
    # Lists to store the values from the SERIES of regressions.
    # Values from the most recent regression are stored at index 0 of each list
    r2 = [] 
    slope = []
    intercept = []
    
    # Variable to track current start index for x+y series to be analyzed
    current_index = int(len(log_efflux) - num_points_reg -1)
    
    # Variable to track if regression should continue
    reg_dec = False
    
    while reg_dec == False: # R^2 has not decreased 3 consecutive times
        print r2
        x = elution_ends[current_index:]
        y = log_efflux[current_index:]
        
        current_regression = linear_regression(x, y)
        r2.insert(0, current_regression[0])
        slope.insert(0, current_regression[1])
        intercept.insert(0, current_regression[2])        
               
        # Checking to see if you are out of the third phase of exchange
        # (has R^2 decreased 3 consecutive times)
        if len (r2) <= 3:
            # Extending the x+y series of values included in the regression
            current_index -= 1
        elif r2[0] < r2[1] and r2[1] < r2[2] and r2[2] < r2[3]:
            reg_dec = True
        else:
            # Extending the x+y series of values included in the regression
            current_index -= 1
    
    # Write points for graphing equation of linear regression
    x1, x2, y1, y2 = grab_x_ys(elution_ends, intercept [3], slope[3])
    
    # current_index, r2, slope, and intercept are corrected considering
    # that the last 3 regressions done with decreasing R^2s
    return x1, x2, y1, y2, r2[3], slope [3], intercept [3], current_index + 3,\
           r2, slope, intercept

def subj_regression_p3(elution_ends, log_efflux, p3_start, p3_end): 
    ''' Doing a custom regression on a data set wherein
    the limits of the regression are known.
    
    p3_start and p3_end are INDEXS corresponding to the lists elution_ends
    and log_efflux
    
    Unlike obj_regression, returning variables r2, slope, intercept are not
    lists but single values
    '''
        
    x = elution_ends[p3_start: p3_end + 1] # last index is not inclusive!!
    y = log_efflux[p3_start: p3_end + 1]
    
    # Doing the regression and storing the parameters
    r2, slope, intercept = linear_regression (x, y)
    
    # Write points for graphing equation of linear regression
    x1, x2, y1, y2 = grab_x_ys (elution_ends, intercept, slope)
    
    return x1, x2, y1, y2, r2, slope, intercept
    
if __name__ == '__main__':
    y_series = [5.134446324653075, 4.532511080497156, 3.9647696512150836, 3.6692523925695686, 3.509950796085591, 3.3869391729764766, 3.287809993163619, 3.230048067964903, 3.169204739621747, 3.1203409378545346, 2.95145986473132, 2.8916143915841324, 2.8589559610792583, 2.8463057128814175, 2.8413779879066166, 2.7532261939625293, 2.750050822474359, 2.6735829597693206, 2.7024903224651338, 2.661606690643107, 2.5998423959455335, 2.57889496358432, 2.5921979525818397, 2.557187996704314, 2.529320391444595, 2.558194007072854, 2.4833719392530966, 2.5557756556810562, 2.4045248209763437, 2.4642132678099204]
    test = obj_regression_p3(x_series, y_series, 2)
    '''print test [7]
    print x_series [test [7]]
    print y_series [test [7]]'''
