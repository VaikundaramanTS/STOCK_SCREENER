def Main():
    from flask import Flask, render_template, request
    from Symbols import Symbols
    from periods import periods
    import pandas as pd
    from pandas_datareader.data import DataReader
    import matplotlib.pyplot as plt
    import datetime as dlt
    import yfinance as yfn
    import io
    import base64
    from Symbols import Symbols
    
    
    app = Flask(__name__)
    
    
    #First page code that receives conditions
    @app.route('/')
    def selection_app():
        while True:
            symbol = request.args.get('Symbol Selector', False)
            period = request.args.get('periods', 'max')
            benchmark_condition = request.args.get('benchmark', 'y')
        
            #inputs from prev work
            ticker = symbol
            period = period
            benchmark_condition = str(benchmark_condition)
        
            #check condition and going to page 2
            if symbol and period and benchmark_condition:
                #Getting the company ticker
                
                ticker = ticker + '.NS'
                ticker_obj = yfn.Ticker(ticker)
                
                DATA = ticker_obj.history(period="max")
                
                
                #Important infos and ratios
                info = ticker_obj.info
        
                Business_info = info["longBusinessSummary"]
                Sector = info["sector"]
                website = info["website"]
                long_name = info["longName"]
                book_value = info["bookValue"]
                PB_ratio = info["priceToBook"]
                beta = info["beta"]
                mar_cap = info["marketCap"]
                fif2_high = info["fiftyTwoWeekHigh"]
                fif2_low = info["fiftyTwoWeekLow"]
                debtToEquity = info["debtToEquity"]
                returnOnEquity = info["returnOnEquity"]
                forwardEps = info["forwardEps"]
                pegratio = info["pegRatio"]
                forwardPE = info["forwardPE"]
                trailingPE = info.get("trailingPE", None)
                fiveYearAvgDividendYield = info["fiveYearAvgDividendYield"]
                recommendationKey = info["recommendationKey"]
        
                #Recommandation card color
                if recommendationKey.lower() == 'buy':
                    rec_color = 'green'
                elif recommendationKey.lower() == 'sell':
                    rec_color = 'red'
                else:
                    rec_color = 'rgb(147, 147, 147)'
                
                
                #Setting the starting point of the 1st Graph
                if period == '1M':
                    start = -22
                elif period == '6M':
                    start = -132
                elif period == "1yr":
                    start = -250
                elif period == '5yr':
                    start = -1250
                elif period == 'YTD':
                    start = -len(DATA.loc['2022':, "Close"])
                else:
                    start = 0
        
                #Ensuring the index didn't cross the bounds
                if -start > DATA.Close.count():
                    start = -DATA.Close.count()
        
        
                if DATA['Close'].iloc[start] > DATA['Close'].iloc[-1]:
                    color = 'red'
                else:
                    color = 'green'
        
                
                #Company name
                company_name = long_name
        
        
                #200DMA and 50DMA
                DMA200_start = DATA['Close'].iloc[start:].index[0]-dlt.timedelta(days = 300)
                if DMA200_start < DATA.Close.index[0]:
                    DMA200_start = DATA.Close.index[0]
                else:
                    DMA200_start = pd.Timestamp(DMA200_start.year, DMA200_start.month, DMA200_start.day)
                DMA50_start = DATA['Close'].iloc[start:].index[0]-dlt.timedelta(days = 80)
                if DMA50_start < DATA.Close.index[0]:
                    DMA50_start = DATA.Close.index[0]
                else:
                    DMA50_start = pd.Timestamp(DMA50_start.year, DMA50_start.month, DMA50_start.day)
                DMA200 = DATA['Close'].loc[DMA200_start:].rolling(window=200).mean()
                DMA50 = DATA['Close'].loc[DMA50_start:].rolling(window=50).mean()
        
        
                #Benchmark Nifty
                
                benchmark = DataReader("^NSEI", 'yahoo', start=DATA.iloc[start:].index[0], end=dlt.datetime.now())
                if start != 0:
                    first = benchmark.Close.loc[DATA['Close'].iloc[start:].index[0]]
                    benchmark['Close'] = benchmark.Close.div(first).mul(DATA.Close.iloc[start])
        
                if DATA.Close.index[0] <= pd.Timestamp(2007, 9, 17) and start == 0:
                    first = benchmark.Close.iloc[0]
                    benchmark['Close'] = benchmark.Close.div(first).mul(DATA.Close.loc["2007-09-17"])
        
        
                #Balance sheet
                balance_sheet = ticker_obj.balance_sheet
                balance_sheet = balance_sheet.to_html(justify='center')
                balance_sheet = balance_sheet.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
                quarterly_balance_sheet = ticker_obj.quarterly_balance_sheet
                quarterly_balance_sheet = quarterly_balance_sheet.to_html()
                quarterly_balance_sheet = quarterly_balance_sheet.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
        
        
                #Cash Flow
                cash_flow = ticker_obj.cashflow
                cash_flow = cash_flow.to_html()
                cash_flow = cash_flow.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
                quarterly_cash_flow = ticker_obj.quarterly_cashflow
                quarterly_cash_flow = quarterly_cash_flow.to_html()
                quarterly_cash_flow = quarterly_cash_flow.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
        
        
                #P&L statements  
                P_and_L = ticker_obj.earnings
                P_and_L = P_and_L.to_html()
                P_and_L = P_and_L.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
                quarterly_P_and_L = ticker_obj.quarterly_earnings
                quarterly_P_and_L = quarterly_P_and_L.to_html()
                quarterly_P_and_L = quarterly_P_and_L.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
        
        
                #Quarterly Finance
                Quarterly_Finance = ticker_obj.quarterly_financials
                Quarterly_Finance = Quarterly_Finance.to_html()
                Quarterly_Finance = Quarterly_Finance.replace('<table border=\"1\" class=\"dataframe\">','<table class=\"table table-dark table-hover\">')
                
        
                #max graph colour
                if DATA.Close.iloc[0] > DATA.Close.iloc[-1]:
                    max_color = 'red'
                else:
                    max_color = 'green'
        
        
                #Plotting the graph using DataFrame.plot mtd
                DATA['Close'].plot(kind='line', color = max_color, title = ticker[:-3], linestyle = '-', label = ticker[:-3], figsize=(10, 5))
        
                #Text and style graph2
                plt.text(DATA.index[-1] + pd.Timedelta(days = 10) , DATA.Close.iloc[-1]+10, str("{:.3f}".format(DATA.Close.iloc[-1])), backgroundcolor = max_color)
                plt.text(DATA.index[0] - pd.Timedelta(days = 5), DATA.Close.iloc[0]-5, str("{:.3f}".format(DATA.Close.iloc[0])), backgroundcolor = max_color)
                plt.ylabel('Price in INR')
                plt.grid(True, color = 'black')
                plt.legend()
        
                #Saving and encoding graph2
                tmpfile2 = io.BytesIO()
                plt.savefig(tmpfile2, format='png')
                encoded2 = base64.b64encode(tmpfile2.getvalue()).decode('utf-8')
                
                #Using the twinx of pyplot to plot the graphs in same page
                fig, ax = plt.subplots(figsize = (15, 8))
                exact_returns = DATA['Close'].iloc[-1]-DATA['Close'].iloc[start]
                percent_returns = (exact_returns/DATA['Close'].iloc[start])*100
        
                #Title
                if exact_returns > 0:
                    sub = "{:.3f}% (+{:.3f}) (increased)".format(percent_returns, exact_returns)
                else:
                    sub = "{:.3f}% ({:.3f}) (decreased)".format(percent_returns, exact_returns)
                plt.suptitle(sub, color = color, fontsize= 15)
                plt.title("{} (Current price: {:.4f})".format(ticker[:-3], DATA.Close.iloc[-1]), fontsize = 30, color = color)
        
                #twinx()
                ax2 = ax.twinx()
        
                #200DMA and 50DMA plotting
                ax2.plot(DMA200.loc[DATA.iloc[start:].index[0]:].index, DMA200.loc[DATA.iloc[start:].index[0]:], color = 'orange', label="200-DMA", linestyle = ":", linewidth = 2)
                ax2.plot(DMA50.loc[DATA.iloc[start:].index[0]:].index, DMA50.loc[DATA.iloc[start:].index[0]:], color = 'blue', label="50-DMA", linestyle = ":", linewidth = 2)
                if benchmark_condition == 'y':
                    ax2.plot(benchmark.index, benchmark.Close, color = 'pink', alpha=0.5, label = "NIFTY 50 INDEX", linewidth = 2)
                
        
                #Plots of volume and price
                
                ax2.plot(DATA.iloc[start:].index, DATA['Close'].iloc[start:], color = color, linewidth = 2)
                plt.grid(True, which='major', axis='both', color='white')
                ax.bar(DATA.iloc[start:].index, DATA['Volume'].iloc[start:].div(1000), alpha = 0.3, label = "Volume")
                plt.grid(True, which='major', axis='both', color='white')
                plt.style.use('dark_background')
                ax2.set_ylabel("Price in INR", color ="white")
                ax.set_ylabel("Volume in thousands", color='white')
                ax.set_facecolor('black')
        
                #Restricting the values in x_axis
                ax2.xaxis.set_major_locator(plt.MaxNLocator(10))
                ax2.yaxis.set_major_locator(plt.MaxNLocator(10))
                ax.yaxis.set_major_locator(plt.MaxNLocator(10))
                ax2.tick_params(axis='both', colors='white')
                ax.tick_params(axis='both', colors='white')
        
                #Plot style 
                plt.legend()
                plt.tight_layout()
                if start == 0:
                    plt.text(DATA.index[-1] + pd.Timedelta(days = 10) , DATA.Close.iloc[-1]+10, str("{:.3f}".format(DATA.Close.iloc[-1])), backgroundcolor = color)
                else:
                    plt.text(DATA.index[-1] + pd.Timedelta(days = -start/30) , DATA.Close.iloc[-1]+10, str("{:.3f}".format(DATA.Close.iloc[-1])), backgroundcolor = color)
                
        
                #Saving encoding graph 1    
                tmpfile = io.BytesIO()
                plt.savefig(tmpfile, format='png')
                encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
        
                img_file1 = '<img class="img-fluid" src=\'data:image/png;base64,{}\'>\n\n\n'.format(encoded)
                img_file2 = '<img class="img-fluid" src=\'data:image/png;base64,{}\'>\n\n\n'.format(encoded2) 
        
                #Opening and Reading template
                with open("templates\\Readtemplate.html", "r") as html:
                    html = html.read()
        
                #Writing on test file to run
                with open("templates\\test.html", "w") as f:
                    f.write(html.format(ticker[:-3], company_name, website, ticker[:-3], img_file1, fif2_high, fif2_low, 
                    Business_info, book_value, PB_ratio, mar_cap, Sector, beta, debtToEquity, returnOnEquity, forwardEps, pegratio, forwardPE, trailingPE, fiveYearAvgDividendYield, rec_color, recommendationKey,
                    img_file2, balance_sheet, quarterly_balance_sheet, cash_flow, quarterly_cash_flow, P_and_L, quarterly_P_and_L, Quarterly_Finance))
        
                #return template
                return render_template("test.html")
        
            #return 1st page
            return render_template("First.html", Symbols = Symbols, periods = periods)
            
    
    if __name__ == "__main__":
        app.run()
        
Main()
