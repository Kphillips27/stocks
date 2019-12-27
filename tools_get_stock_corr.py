import os, sys
import datetime as dt
try:
    import bs4 as bs
except:
    os.system('pip install BeautifulSoup')
    import ba4 as bs
try:
    import matplotlib.pyplot as plt
except:
    os.system('pip install matplotlib')
    import matplotlib.pyplot as plt
try:
    import numpy as np
except:
    os.system('pip install numpy')
    import numpy as np
try:
    import pandas as pd
except:
    os.system('pip install pandas')
    import pandas as pd
try:
    import pandas_datareader.data as web
except:
    os.system('pip install pandas-datareader')
    import pandas_datareader.data as web
try:
    import pickle
except:
    os.system('pip install pickle')
    import pickle
try:
    import requests
except:
    os.system('pip install requests')
    import requests
'''From the Sentdex series on Matplotlib for Finance. This script
scrapes Wiki for stock abbreviations and returns list of abbrv. The
current DataReader documentation states yahoo! no longer works, but 
as of 2019.06.23, it's working for this script and we are pulling 
stock prices from yahoo.
'''
#---------------------------------------#
# Variables
#---------------------------------------#
in_file = 'in_file'                            # Read Wiki data into this file
provider = 'yahoo' 
currPath = os.getcwd()                  # Directory you are in NOW
savePath = 'askew'                      # We will be creating this new sub-directory
myPath = (currPath + '/' + savePath)    # The full path of the new sub-dir
stock = ""
stock = ""
#########################################
class corr():
#########################################
    def __init__(self, stock):
        self.stock = stock
        self.dict  = {}
        if len(stock) == 0:
            print("tools_get_stock_corr needs stock passed to it. Aborting with no action taken.")
            sys.exit(0)
    def run(self, stock):
        if not os.path.exists(myPath):      # The directory you are in NOW
            os.makedirs(myPath)             # create a new dir below the dir your are in NOW
            os.chdir(myPath)   
        get_data_from_yahoo(False) #Set to true if first time run of want to refresh
        compile_data()
        mystocks = visualize_data(stock)
        return mystocks
#---------------------------------------#
def moving_average(values, window):
#---------------------------------------#
    weights  = np.repeat(1.0, window) / window   #Numpy repeat - repeats items in array - "window" times
    smas = np.convolve(values, weights, 'valid') #Numpy convolve - returns the discrete, linear convolution of 2 seq.
    #https://stackoverflow.com/questions/20036663/understanding-numpys-convolve
    return smas
#---------------------------------------#
def save_sp500_stocks():
#---------------------------------------#

    resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'wikitable sortable'}) #Wiki only has 1 table.
    stocks = [] 
    stocks.append("TSLA")
    stocks.append("JCP")                                   #Allocate list to save results
    stocks.append('MANH')                          # Add missing stock

    for row in table.findAll('tr')[1:]:            #Wiki data starts w/2nd row
        stock = row.findAll('td')[0].text        #Wiki data starts 1st col
        stock = str(stock).replace('\n', '')
        stocks.append(stock)
    stocks.sort()
    with open("sp500stocks.pickle", "wb") as in_file:    #Pickle saves results as reuable object
        pickle.dump(stocks, in_file)                     #Save results from above to Pickle.
    
    #print(stocks)

    return(stocks)

#save_sp500_stocks()

#---------------------------------------#
def get_data_from_yahoo(reload_sp500 = True):
#---------------------------------------#
    os.chdir(myPath) 
    if reload_sp500:
        stocks = save_sp500_stocks()
    else:
        with open("sp500stocks.pickle", 'rb') as in_file:
            stocks = pickle.load(in_file)

    # if not os.path.exists(myPath):      # The directory you are in NOW
    #     os.makedirs(myPath)             # create a new dir below the dir your are in NOW
    # os.chdir(myPath)                    # move into the newly created sub-dir

    # if not os.path.exists(savePath):
    #     os.makedirs(savePath)

    start = ( dt.datetime.now() - dt.timedelta(days = 365) )       # Format is year, month, day
    end = dt.datetime.today()           # format of today() = [yyyy, mm, dd] - list of integers

    for stock in stocks:
        saveFile=('{}'.format(stock) + '.csv')    # The RESUlTS we are saving on a daily basis
        if os.path.exists(saveFile): #If results (stock.csv) exists, chk creation time.
            print('Already have {}'.format(stock), end = ' ') 
            st = os.stat(saveFile)
            if dt.date.fromtimestamp(st.st_mtime) != dt.date.today():
                try:
                    print(" but updating data to bring current to today:" , end)
                    df = web.DataReader(stock, provider, start, end)
                    df['MA10'] = df['Adj_Close'].rolling(10).mean()
                    df['MA30'] = df['Adj_Close'].rolling(30).mean()
                    df.to_csv('{}.csv'.format(stock))
                except:
                    print("Issue with updating ", stock, "skipping data extract")
            else:
                print(" and is current as of today:" , end)
        else:
            try:
                df = web.DataReader(stock, provider, start, end)
                df['MA10'] = df['Adj_Close'].rolling(10).mean()
                df['MA30'] = df['Adj_Close'].rolling(30).mean()
                df.to_csv('{}.csv'.format(stock))
            except:
                print("Issue with new file:", stock, "skipping data extract")
           
def compile_data():
    os.chdir(myPath)
    with open("sp500stocks.pickle", "rb") as in_file:
        stocks = pickle.load(in_file)
    main_df = pd.DataFrame()
    for count, stock in enumerate(stocks):
        try:
            df = pd.read_csv('{}.csv'.format(stock))

            df.set_index('Date', inplace = True)
            df.rename(columns = {'Adj_Close': stock}, inplace = True)
            df.drop(['Open', 'High','Low','Close', 'Volume', 'MA10', 'MA30'], axis = 1, inplace = True)
        except:
            print("Issue with enumerating stock:", stock, "skipping...")

        if main_df.empty:
            try:
                main_df = df
            except:
                print("main_df empty and issues with current df, skipping")
        else:
            try:
                main_df = main_df.join(df, how = 'outer')
            except:
                print("main_df join issues, skipping current df.")

    #print(main_df.sample(n=10))
    main_df.to_csv('sp500_joined_closes.csv')

def visualize_data(stock):
    print("Entering visualize_data with stock", stock)
    os.chdir(myPath)
    df  = pd.read_csv('sp500_joined_closes.csv')

    df_corr = df.corr()
    df1 = pd.DataFrame(columns = df_corr.columns)
    df1  = df_corr[[stock]]
    df1.reset_index()
    df1.set_index(df1.axes[0])
    #df1.set_index(df['Date'], inplace = True)
   
    #df1.set_index(['Date'])
    print("df1.axes[0] =", df1.axes[0])
    print("df1.axes[1] = ", df1.axes[1])
    # mask = np.zeros_like(df.corr())
    # triangle_indices = np.triu_indices_from(mask)
    # mask[triangle_indices] = True
    # print(mask)

    #data = df_corr.values
    data = df1.values
    dict = {}
    counter = 0
    for datum in data:
        if datum > .80 and datum < 1:
            print("tools_get_stock_corr -->datum:", datum, "counter:", counter, "column:", (df1.axes[0][counter]))
            dict[(df1.axes[0][counter])] = float(datum)
        counter += 1
    print("tools_get_stock_corr returning -->", dict)
    return dict


    

#########################################
# M A I N   L O G I C
#########################################
if __name__ == "__main__":
    a = corr('TSLA')
    a.run('TSLA')