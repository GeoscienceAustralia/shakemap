#!/usr/bin/env python

#stdlib imports
import os.path
import sys
from collections import OrderedDict

#third party
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time as time

#hack the path so that I can debug these functions if I need to
homedir = os.path.dirname(os.path.abspath(__file__)) #where is this script?
shakedir = os.path.abspath(os.path.join(homedir,'..'))
sys.path.insert(0,shakedir) #put this at the front of the system path, ignoring any installed mapio stuff

from shakemap.grind.distance import *
from shakemap.grind.vector import Vector
from shakemap.grind.fault import Fault
from shakemap.utils.timeutils import ShakeDateTime
from shakemap.grind.source import Source

from openquake.hazardlib.geo.geodetic import npoints_towards
from openquake.hazardlib.geo.mesh import Mesh
from openquake.hazardlib.geo.point import Point
from openquake.hazardlib.geo.utils import get_orthographic_projection


def test_chichi():
    # read in fault file
    f = 'test/data/0137A.POL'
    i0 = np.arange(0, 9*11*3, 11)
    i1 = i0 + 10
    cs = list(zip(i0, i1))
    df = pd.read_fwf(f, cs, skiprows = 2, nrows = 5, header = None)
    mat = df.as_matrix()
    ix = np.arange(0, 9*3, 3)
    iy = ix + 1
    iz = ix + 2
    x0 = mat[0, ix]
    x1 = mat[1, ix]
    x2 = mat[2, ix]
    x3 = mat[3, ix]
    y0 = mat[0, iy]
    y1 = mat[1, iy]
    y2 = mat[2, iy]
    y3 = mat[3, iy]
    # Depth, positive down
    z0 = np.abs(mat[0, iz])
    z1 = np.abs(mat[1, iz])
    z2 = np.abs(mat[2, iz])
    z3 = np.abs(mat[3, iz])
    epilat = 23.85
    epilon = 120.82
    proj = get_orthographic_projection(
        epilon-1, epilon+1, epilat+1, epilat-1)
    lon0,lat0 = proj(x0, y0, reverse = True)
    lon1,lat1 = proj(x1, y1, reverse = True)
    lon2,lat2 = proj(x2, y2, reverse = True)
    lon3,lat3 = proj(x3, y3, reverse = True)
    flt = Fault.fromVertices(
        lon0, lat0, z0, lon1, lat1, z1, lon2, lat2, z2, lon3, lat3, z3)
    # event information doesn't matter except hypocenter
    event = {'lat': 23.85,  'lon': 120.82, 'depth':8, 'mag': 7.62, 
             'id':'', 'locstring':'', 'type':'U', 
             'time':ShakeDateTime.utcfromtimestamp(int(time.time())), 
             'timezone':'UTC'}
    source = Source(event, flt)
    
    # Get NGA distances
    distfile = 'test/data/NGAW2_distances.csv'
    df = pd.read_csv(distfile)
    df2 = df.loc[df['EQID'] == 137]
    slat = df2['Station Latitude'].as_matrix()
    slon = df2['Station Longitude'].as_matrix()
    sdep = np.zeros(slat.shape)
    nga_repi = df2['EpiD (km)'].as_matrix()
    nga_rhypo = df2['HypD (km)'].as_matrix()
    nga_rrup = df2['ClstD (km)'].as_matrix()
    nga_rjb = df2['Joyner-Boore Dist. (km)'].as_matrix()
    nga_rx = df2['T'].as_matrix()
    nga_T = df2['T'].as_matrix()
    nga_U = df2['U'].as_matrix()
    test_ry = np.array([
        -49.25445446,  -76.26871272,  -37.1288192 ,  -53.47792996,
        -50.30711637,  -63.96322125,  -61.01988704,  -81.2001781 ,
        -76.00646939,  -74.39038054,  -92.23617124,  -90.66976945,
        -89.68551411, -102.98798328, -114.70036085,  -29.83636082,
        -28.50133134,  -27.86922916,  -36.00619214,  -44.68826209,
        -47.64580208,  -53.92619079,  -59.11962858,  -55.90584822,
        -55.00772025,  -48.81756715,  -59.27542007,  -62.13633659,
        -70.0673351 ,  -75.96977638,  -61.6959293 ,  -60.34564074,
        -81.49792285,  -78.75933138,  -80.80533738,  -85.24473008,
        -94.07519297,  -93.75010471,  -96.87089883, -100.06112271,
        -98.86980873,  -95.92330113, -107.44086722, -119.1065369 ,
       -120.60405905, -113.42995442, -115.94930662, -115.2398216 ,
       -107.37840927,  -49.25445446,  -48.78386688, -108.49133002,
        -88.03303353,  -44.66653428,  -81.04476548,  -38.26801619,
        -70.51178983,  -69.15679931,  -74.74562139,  -86.51133446,
        -27.62153029,  -48.33279375,  -30.0808298 , -113.98345018,
        -97.96609537,  -87.9863122 ,  -39.45970018,  -80.1387617 ,
        -42.27121388,  -82.05027834,  -81.55987067,  -81.55987067,
       -107.25255717,   67.62695516,   -3.27797047, -197.98554369,
         82.30996151,   18.42180605,  -22.88851072,  -35.75245916,
        -19.54788146,  -18.19780517,   19.85077702,   20.33310282,
         19.95448398,   20.55508903,   18.17428572,   17.87997374,
         16.97323804,   16.0025885 ,   13.88001846,   18.42180605,
         -3.27797047,   51.43098894,   28.97695533,  -53.20579538,
         38.7537468 ,   33.48878882,   26.25189111,   22.54251612,
         13.37141837,   -5.80928302,   -6.68056794,  -14.50860117,
        -15.23992093,  -27.63281952,  -11.66075049,  -36.94595337,
        -40.97168031,  -41.2814342 ,  -48.64456898,  -61.55777751,
        -11.15038984,  -17.16482959,   55.84202839,   36.78540588,
         21.18550074,   19.14658833,   19.22680282,    5.76327358,
        -47.45309937,  -44.33194991,  -55.15852372,   37.33066096,
         37.64135657,   14.31598698,    4.60495737,    6.87107021,
         18.42180605,  113.59285783,  109.06420877,  104.23416509,
         99.21599973,   95.25204545,   90.29487934,   86.26977557,
         95.28705209,   87.12907925,  101.40561896,   96.68858152,
         92.90287952,  100.36659012,   97.19448577,   92.8627461 ,
         85.01448355,   93.36767736,   96.90824009,   86.48002825,
         88.71037964,  106.17282325,  102.56142319,   97.60004093,
         99.61798574,   97.36337239,   94.22000798,   86.99488734,
         90.05981676,   90.51189502,  100.7166391 ,  100.31931988,
         67.62695516,   94.15062409,   87.77053675,  124.21806013,
         99.23108884,  101.48199452,   92.63771423,   78.88723272,
         72.7261356 ,   80.58682246,   73.30258213,   70.20783518,
         60.57963211,  -87.72265602, -148.10933308, -150.41334959,
       -144.12558375, -145.5625388 , -132.09479688, -135.12980144,
       -121.10883695, -143.75755221, -117.73616176, -115.28563276,
       -138.79652905, -143.10405603, -151.78419035, -159.75299736,
       -149.69457229, -175.20332448, -181.00970647, -188.86536942,
       -176.88178468, -194.20978527, -204.54944453, -161.04413103,
       -197.98554369,  -96.74089367, -133.49237232,  -84.71198922,
       -164.97719097, -202.48241157,  -74.54550169, -147.37402934,
       -144.64074441, -147.94282804, -122.80976842, -133.1671346 ,
       -136.3051809 , -113.93174768, -151.02125407, -146.5198829 ,
       -156.19720713, -126.06138725, -131.44422964, -197.62591198,
       -204.42320856, -149.84576063, -121.56474664, -130.99947339,
       -148.41767074, -145.28448367,  104.58903799,   82.1649906 ,
         67.69977397,   39.46989193,  -69.00949731, -133.49237232,
       -128.264754  ,  -84.71198922, -108.49133002,  119.86128724,
        122.73556155,  126.28254009,  125.12436373,  123.32498578,
        123.8337768 ,  121.39931427,  121.48412837,  122.03669249,
        122.59675818,  119.54338365,  120.33961222,  120.69581745,
        116.96928355,  117.6687724 ,  116.62277942,  115.39650689,
        112.60751523,  109.82643069,  108.2500678 ,  130.9143614 ,
        126.50049543,  112.76229057,  132.76840098,  107.27099883,
        128.16063464,  123.83157143,  120.46711628,  112.55756637,
        135.59953867,  136.66138116,  136.98573162,  134.04528777,
        116.27744752,  129.2794577 ,  119.13550981,  124.67196321,
        130.9728774 ,  130.9039439 ,  128.70028371,  130.04592892,
        140.21819548,  140.60370422,  113.37585901,  123.21523323,
        123.88149248,  128.56894995,  128.45186255,  118.74080853,
        126.71189149,  119.79833338,  130.00866791, -160.01242472,
         13.55424709,  110.26938756,   97.71987778,  110.93671325,
        108.71965725,  105.03432063,  106.36049687,   99.27569343,
        115.06168146,   77.00378531,   81.50139192,   92.15605815,
         79.94311644,   83.16892433,   52.23389149,   50.97110177,
         67.95167063,   63.43930833,   40.20494692,   43.22936492,
         47.21513635,   38.94380012,   53.85489136,   56.69935207,
         48.07036522,   64.46887891,   14.98020647,   17.35046801,
         16.15236633,   14.41062231,   19.99605739,   18.31076661,
         15.07058247,   12.34339267,   13.57621451,   14.72685201,
         22.04539325,   20.47982142,    9.66768974,    8.05139052,
         29.22924869,    3.75876894,    7.8610467 ,   29.20272495,
         15.19325822,   -2.38981899,    5.58349359,   -0.62239018,
         -4.38178769,  -11.43651893,  -20.07048519,  -16.0588668 ,
         82.30996151,   13.55424709,  104.49355303,  -11.29628168,
         82.1649906 ,   34.22207039,   38.08490923,  -10.15855131,
        111.0308369 ,   81.78397481,   73.56334665,   81.27164139,
         74.55979012,   16.08437955,   23.8203941 ,   24.68836209,
         28.73767914,   21.06714416,   19.44159522,    4.62135887,
          3.41771413,    5.051121  ,   -6.81834189,    6.40341853,
         -0.35693923,  -17.74409367,   -8.91759817,  -18.05278804,
          7.70695248,   -5.52733835,  -16.02924961,   -4.54310111,
        -22.84234773,   -1.71908199,   39.46989193,  -14.74007542,
         23.59992543,  -10.49966883,  -11.47733869,  -22.8200901 ,
         -9.72486483,   95.96997763, -115.36487081,  -52.88924268,
        -90.2275069 , -132.22657274, -100.52455976, -115.24052939,
       -113.84482359, -114.41088165, -114.63386688, -115.92829006,
       -117.52597227, -114.49770514, -114.46881502,  -76.26871272,
       -115.36487081, -160.01242472, -110.6429636 ,  -77.47722955,
        -80.24672646,  -85.90422427,  -94.92075147, -102.44309541,
       -106.23741455, -111.56110193, -115.13402727,  -48.64043046,
        -60.86151946,  -66.52137871, -110.04628212,  -75.27694696,
        -78.87041369,  -88.08700161,  -90.18844188,  -93.65776393,
        -92.58976279, -107.31364843, -115.04064471, -125.98500718,
        -75.9341032 ,  -39.45970018,  -14.74007542,  -23.16835763])
    test_ry0 = np.array([
          5.38783354,   32.4020918 ,    0.        ,    9.61130904,
          6.44049545,   20.09660033,   17.15326613,   37.33355718,
         32.13984847,   30.52375962,   48.36955032,   46.80314854,
         45.81889319,   59.12136236,   70.83373993,    0.        ,
          0.        ,    0.        ,    0.        ,    0.82164117,
          3.77918116,   10.05956987,   15.25300766,   12.0392273 ,
         11.14109933,    4.95094623,   15.40879915,   18.26971567,
         26.20071419,   32.10315546,   17.82930838,   16.47901983,
         37.63130193,   34.89271046,   36.93871646,   41.37810916,
         50.20857205,   49.88348379,   53.00427791,   56.19450179,
         55.00318781,   52.05668021,   63.5742463 ,   75.23991598,
         76.73743813,   69.5633335 ,   72.0826857 ,   71.37320068,
         63.51178836,    5.38783354,    4.91724596,   64.6247091 ,
         44.16641261,    0.79991336,   37.17814456,    0.        ,
         26.64516892,   25.2901784 ,   30.87900047,   42.64471355,
          0.        ,    4.46617283,    0.        ,   70.11682926,
         54.09947445,   44.11969128,    0.        ,   36.27214079,
          0.        ,   38.18365743,   37.69324975,   37.69324975,
         63.38593626,   31.95985109,    0.        ,  154.11892278,
         46.64285745,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,   15.76388487,    0.        ,    9.33917446,
          3.08664273,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    4.77794806,   17.69115659,
          0.        ,    0.        ,   20.17492433,    1.11830182,
          0.        ,    0.        ,    0.        ,    0.        ,
          3.58647845,    0.46532899,   11.2919028 ,    1.6635569 ,
          1.97425251,    0.        ,    0.        ,    0.        ,
          0.        ,   77.92575377,   73.39710471,   68.56706103,
         63.54889567,   59.58494138,   54.62777528,   50.6026715 ,
         59.61994802,   51.46197518,   65.7385149 ,   61.02147746,
         57.23577546,   64.69948606,   61.52738171,   57.19564204,
         49.34737949,   57.7005733 ,   61.24113602,   50.81292419,
         53.04327558,   70.50571919,   66.89431913,   61.93293686,
         63.95088168,   61.69626833,   58.55290391,   51.32778327,
         54.3927127 ,   54.84479095,   65.04953504,   64.65221582,
         31.95985109,   58.48352003,   52.10343269,   88.55095607,
         63.56398477,   65.81489046,   56.97061016,   43.22012866,
         37.05903154,   44.9197184 ,   37.63547806,   34.54073112,
         24.91252804,   43.85603511,  104.24271216,  106.54672867,
        100.25896283,  101.69591788,   88.22817597,   91.26318052,
         77.24221603,   99.89093129,   73.86954084,   71.41901185,
         94.92990813,   99.23743511,  107.91756944,  115.88637645,
        105.82795138,  131.33670356,  137.14308555,  144.9987485 ,
        133.01516376,  150.34316435,  160.68282361,  117.17751011,
        154.11892278,   52.87427275,   89.6257514 ,   40.8453683 ,
        121.11057005,  158.61579065,   30.67888078,  103.50740842,
        100.77412349,  104.07620713,   78.9431475 ,   89.30051368,
         92.43855998,   70.06512676,  107.15463315,  102.65326198,
        112.33058622,   82.19476634,   87.57760872,  153.75929106,
        160.55658764,  105.97913971,   77.69812572,   87.13285248,
        104.55104982,  101.41786275,   68.92193392,   46.49788654,
         32.0326699 ,    3.80278787,   25.14287639,   89.6257514 ,
         84.39813309,   40.8453683 ,   64.6247091 ,   84.19418317,
         87.06845748,   90.61543602,   89.45725966,   87.65788171,
         88.16667274,   85.73221021,   85.81702431,   86.36958842,
         86.92965411,   83.87627959,   84.67250815,   85.02871339,
         81.30217949,   82.00166833,   80.95567535,   79.72940282,
         76.94041117,   74.15932662,   72.58296373,   95.24725733,
         90.83339137,   77.0951865 ,   97.10129692,   71.60389476,
         92.49353057,   88.16446736,   84.80001222,   76.89046231,
         99.93243461,  100.9942771 ,  101.31862755,   98.37818371,
         80.61034346,   93.61235363,   83.46840575,   89.00485915,
         95.30577334,   95.23683984,   93.03317965,   94.37882485,
        104.55109142,  104.93660016,   77.70875494,   87.54812917,
         88.21438842,   92.90184589,   92.78475848,   83.07370447,
         91.04478743,   84.13122931,   94.34156384,  116.14580381,
          0.        ,   74.60228349,   62.05277372,   75.26960919,
         73.05255319,   69.36721657,   70.69339281,   63.60858937,
         79.3945774 ,   41.33668124,   45.83428785,   56.48895409,
         44.27601238,   47.50182027,   16.56678743,   15.30399771,
         32.28456656,   27.77220427,    4.53784286,    7.56226086,
         11.54803229,    3.27669605,   18.1877873 ,   21.032248  ,
         12.40326116,   28.80177485,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
         46.64285745,    0.        ,   68.82644897,    0.        ,
         46.49788654,    0.        ,    2.41780516,    0.        ,
         75.36373283,   46.11687074,   37.89624258,   45.60453732,
         38.89268605,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,    0.        ,    3.80278787,    0.        ,
          0.        ,    0.        ,    0.        ,    0.        ,
          0.        ,   60.30287357,   71.49824989,    9.02262176,
         46.36088598,   88.35995182,   56.65793884,   71.37390848,
         69.97820268,   70.54426073,   70.76724596,   72.06166914,
         73.65935135,   70.63108422,   70.6021941 ,   32.4020918 ,
         71.49824989,  116.14580381,   66.77634268,   33.61060864,
         36.38010555,   42.03760335,   51.05413055,   58.57647449,
         62.37079364,   67.69448101,   71.26740635,    4.77380954,
         16.99489854,   22.65475779,   66.1796612 ,   31.41032604,
         35.00379277,   44.22038069,   46.32182096,   49.79114301,
         48.72314188,   63.44702751,   71.1740238 ,   82.11838626,
         32.06748228,    0.        ,    0.        ,    0.        ])
    
    dist_types = ['repi', 'rhypo', 'rjb', 'rrup', 'rx', 'ry', 'ry0', 'U', 'T']
    dists = get_distance(dist_types, slat, slon, sdep, source)
    
    np.testing.assert_allclose(
        nga_repi, dists['repi'], rtol = 0, atol = 2)
    
    np.testing.assert_allclose(
        nga_rhypo, dists['rhypo'], rtol = 0, atol = 2)

    np.testing.assert_allclose(
        nga_rjb, dists['rjb'], rtol = 0, atol = 2)

    np.testing.assert_allclose(
        nga_rrup, dists['rrup'], rtol = 0, atol = 2)
    
    np.testing.assert_allclose(
        nga_rx, dists['rx'], rtol = 0, atol = 2)

    np.testing.assert_allclose(
        test_ry, dists['ry'], rtol = 0, atol = 2)

    np.testing.assert_allclose(
        test_ry0, dists['ry0'], rtol = 0, atol = 2)

    np.testing.assert_allclose(
        nga_U, dists['U'], rtol = 0, atol = 6)

    np.testing.assert_allclose(
        nga_T, dists['T'], rtol = 0, atol = 2)
