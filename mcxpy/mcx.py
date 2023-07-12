import requests
import pandas as pd
from datetime import datetime, date, timedelta
import re
from typing import Literal, Union, NewType, List
from functools import lru_cache

DateFormat = NewType(name="%d-%m-%Y", tp=str)
DateFormat_2 = NewType(name="%Y%m%d", tp=str)
DateFormat_3 = NewType(name="%d%b%Y", tp=str)

urls = {
    "base_url" : "https://www.mcxindia.com",
    "routes" : {
        "bhavcopy" : "/backpage.aspx/GetDateWiseBhavCopy",
        "marketwatch" : "/backpage.aspx/GetMarketWatch",
        "circulars" : "/backpage.aspx/GetCircularAdvanceSearch",
        "gainers" : "/backpage.aspx/GetGainer",
        "losers" : "/backpage.aspx/GetLosers",
        "activeoptions" : "/backpage.aspx/GetMostActiveOptionsContractsByValue",
        "activecontracts" : "/backpage.aspx/GetMostActiveContractByValueFilter",
        "heatmap" : "/backpage.aspx/GetHeatMap",
        "optionchain" : "/backpage.aspx/GetOptionChain",
        "pcr" : "/backpage.aspx/GetCommoditywisePutCallRatio",
        "pcr_expirywise" : "/backpage.aspx/GetExpirywisePutCallRatio",
        "icomdex_details" : "/backpage.aspx/GetMCXIComdexIndicesDetails",
        "icomdex_historical" : "/backpage.aspx/GetMCXIComdexIndicesHistory",
        "getquote" : "/BackPage.aspx/GetQuote",
        "optionquote" : "/BackPage.aspx/GetQuoteOption"
    },
}


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://www.mcxindia.com",
    "Referer": "https://www.mcxindia.com",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "^\"Not.A/Brand^\";v=^\"8^\", ^\"Chromium^\";v=^\"114^\", ^\"Google Chrome^\";v=^\"114^\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "^\"Windows^\"",
}



def format_date(dateobj: Union[DateFormat, datetime, date], 
                isExpiry=False
                ) -> Union[DateFormat_2, DateFormat_3]:
    
    if isinstance(dateobj, str):
        try:
            if isExpiry:
                dt = datetime.strptime(dateobj, "%d-%m-%Y")
                return dt.strftime("%d%b%Y").upper()
            dt = datetime.strptime(dateobj, "%d-%m-%Y")
            return dt.strftime("%Y%m%d")
        except ValueError as e:
            print(f"Format Date String Error :: {e}")
            return
    elif isinstance(dateobj, datetime) or isinstance(dateobj, date):
        if isExpiry:
            return dateobj.strftime("%d%b%Y").upper()
        return dateobj.strftime("%Y%m%d")
    else:
        print("Invalid input type. Expected str(dd-mm-yyyy), date or datetime.")

def convert_to_ist(timestamp_str: str) -> datetime:
    try:
        match_str = re.search(r'\((-?\d+)\)', timestamp_str)
        if match_str:
            timestamp_ms = int(match_str.group(1))

            if timestamp_ms <= 0:
                return None

            ist_datetime = datetime.utcfromtimestamp(timestamp_ms / 1000) + timedelta(hours=5, minutes=30)
            return ist_datetime
        return None
    except Exception as e:
        print(f"Error :: {e}")

@lru_cache(maxsize=None)
def get_session(url: str) -> requests.Session:
    s = requests.Session()
    s.headers.update(headers)
    res = s.get(url)
    return s

def fallback_fetch(base_url: str, url: str, data: dict=None, retry=1) -> dict:
    try:
        session = get_session(base_url)
        res = session.post(url=url, json=data)
        res.raise_for_status()
        if res.status_code == 200:
            res_data = res.json()
            return res_data
    except requests.exceptions.RequestException:
        if retry <= 3:
            get_session.cache_clear()
            fallback_fetch(base_url=base_url, url=url, data=data, retry=retry+1)
    except Exception as e:
        print(f"Error :: {e}")

def mcxfetch(config_key: Literal["bhavcopy","marketwatch","circulars","gainers","losers","activeoptions",
                                 "activecontracts","heatmap","optionchain","pcr", "pcr_expirywise",
                                 "icomdex_details", "icomdex_historical", "getquote", "optionquote"],
            data: dict=None) -> dict:
    try:
        base_url = urls['base_url']
        url = base_url + urls['routes'][config_key]
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            res_data = response.json()
            return res_data
    except requests.HTTPError:
        res = fallback_fetch(base_url=base_url, url=url, data=data)
        return res
    except Exception as e:
        print(f"Error :: {e}")

def mcx_bhavcopy(bhavdate: Union[DateFormat, datetime, date]) -> pd.DataFrame:    
    try:
        fdate = format_date(bhavdate)
        
        data = {
            "Date": fdate,
            "InstrumentName": "ALL"
        }

        res = mcxfetch(config_key='bhavcopy',data=data)
        df = pd.DataFrame(res["d"]["Data"])
        selected_columns = [
                    'DateDisplay', 'InstrumentName', 'Symbol', 'ExpiryDate', 'OptionType', 'StrikePrice',
                    'Open', 'High', 'Low', 'Close', 'PreviousClose', 'Volume', 'VolumeInThousands',
                    'Value', 'OpenInterest'
                ]
        df = df[selected_columns]
        df = df.rename(columns={
            'DateDisplay' : 'Date', 
            'InstrumentName' : 'Instrument Name', 
            'ExpiryDate' : 'Expiry Date', 
            'OptionType' : 'Option Type', 
            'StrikePrice' : 'Strike Price',
            'PreviousClose' : 'Previous Close', 
            'Volume' : 'Volume(Lots)', 
            'Value' : 'Value(Lacs)', 
            'OpenInterest' : 'Open Interest(Lots)'
        })
        df['Date'] = pd.to_datetime(df['Date'], format='mixed',dayfirst=True)
        df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], format='mixed',dayfirst=True)
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_marketwatch() -> pd.DataFrame:
    try:
        res = mcxfetch(config_key='marketwatch')
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['__type'])
        df = df.replace('-', '')
        df = df.rename(columns={
        'ProductCode': 'Product',
        'ExpiryDate': 'Expiry',
        'BuyQuantity': 'BuyQty',
        'SellQuantity': 'SellQty'
        })
        df['Expiry'] = pd.to_datetime(df['Expiry'], format='mixed',dayfirst=True)
        df['UnderlineContract'] = pd.to_datetime(df['UnderlineContract'], format='mixed', dayfirst=True)
        df['LTT'] = df['LTT'].apply(convert_to_ist)
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_circulars(from_date: Union[DateFormat, datetime, date] =(datetime.now()-timedelta(days=4)),
                  to_date: Union[DateFormat, datetime, date]=datetime.now()
                  ) -> pd.DataFrame:    
    try:
        date1 = format_date(from_date)
        date2 = format_date(to_date) 

        data = {
            'CircularType':'ALL',
            'CircularNo':'',
            'Title':'',
            'FromDate': date1,
            'ToDate': date2
            }

        res = mcxfetch(config_key='circulars', data=data)
        df= pd.DataFrame(res['d'])
        df = df.drop(columns=['__type', 'CircularDate','CircularMonth','CircularYear','CircularTypes', 'CircularNumber'])
        df['DisplayCircularDate'] = pd.to_datetime(df['DisplayCircularDate'], format='mixed', dayfirst=True)
        df['CompareDate'] = pd.to_datetime(df['CompareDate'], format="%Y%m%d", yearfirst=True)
        df = df.rename(columns={
            'DisplayCircularDate': 'Date'
            })
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_topgainers() -> pd.DataFrame:    
    try:
        res = mcxfetch(config_key='gainers')
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['ExtensionData', 'EngSymbol'])  
        df['LTT'] = df['LTT'].apply(convert_to_ist)
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], format='%d%b%Y', dayfirst=True)
        reorderd_columns = ['Symbol', 'LTT', 'ExpiryDate','PreviousClosed', 'LTP', 
                      'AbsoluteChange', 'PercentChange']
        df = df[reorderd_columns]
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_toploosers() -> pd.DataFrame:    
    try:
        res = mcxfetch(config_key='losers')
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['ExtensionData', 'EngSymbol'])  
        df['LTT'] = df['LTT'].apply(convert_to_ist)
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], format='%d%b%Y', dayfirst=True)
        reorderd_columns = ['Symbol', 'LTT', 'ExpiryDate','PreviousClosed', 'LTP', 
                      'AbsoluteChange', 'PercentChange']
        df = df[reorderd_columns]
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_mostactiveoptions() -> pd.DataFrame:    
    try:
        option_list = ['CE', 'PE']
        inst_list = ['OPTFUT', 'OPTCOM']

        res_list = []
        for opt in option_list:
            for inst in inst_list:
                data = {
                    'OptionType':opt,
                    'Product':'ALL',
                    'InstrumentType':inst
                    }
                res = mcxfetch(config_key="activeoptions", data=data)
                res_data = res["d"]["Data"]
                res_list.append(res_data)
        dfs = [pd.DataFrame(sublist) for sublist in res_list]
        df = pd.concat(dfs)
        df = df.drop(columns=['ExtensionData', 'EngSymbol'])
        df['LTT'] = df['LTT'].apply(convert_to_ist)  
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], format='mixed', dayfirst=True)
        reorderd_columns = ['Symbol', 'LTT', 'ExpiryDate', 'InstrumentType', 'OptionType', 'StrikePrice', 'LTP','OpenInterest', 
                      'Volume', 'PremiumValueInLacs','NotionalValueInLacs', 'ValueOfUnderlying']
        df = df[reorderd_columns]
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_mostactivecontracts() -> pd.DataFrame:
    try:
        data = {
            "InstrumentType": "ALL"
            }
        res = mcxfetch(config_key='activecontracts', data=data)
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['ExtensionData', 'EngSymbol'])
        df['Date'] = df['Date'].apply(convert_to_ist)
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], format='mixed', dayfirst=True)
        reorderd_columns = ['Symbol', 'Date', 'ExpiryDate', 'InstrumentName', 'OptionType', 'StrikePrice', 'LTP',
                            'PercentageChange','OpenInterest', 'Volume', 'Value','NotionalValue', 'PremiumValue',
                            'UnderlineValue', 'Unit']
        df = df[reorderd_columns]
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_heatmap() -> pd.DataFrame:    
    try:
        res = mcxfetch(config_key='heatmap')
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['__type'])
        df['Dttm'] = df['Dttm'].apply(convert_to_ist)
        df['ExpiryDate'] = pd.to_datetime(df['ExpiryDate'], format='mixed', dayfirst=True)
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_optionchain(commodity: Literal['COPPER', 'CRUDEOIL', 'GOLD', 'GOLDM', 'NATURALGAS', 
                                       'NICKEL', 'SILVER', 'SILVERM','ZINC'],
                    expiry: Union[DateFormat, datetime, date]
                    ) -> pd.DataFrame:
    try:
        exp_date = format_date(dateobj=expiry, isExpiry=True)
        data = {
            'Commodity': commodity,
            'Expiry': exp_date
            }
        res = mcxfetch(config_key='optionchain', data=data) 
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['ExtensionData'])
        df['LTT'] = df['LTT'].apply(convert_to_ist)
        df['CE_LTT'] = df['CE_LTT'].apply(convert_to_ist)
        df['PE_LTT'] = df['PE_LTT'].apply(convert_to_ist)
        df['Symbol'] = commodity
        df['Expiry'] = datetime.strptime(exp_date, "%d%b%Y")
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_pcr(expirywise: bool=False) -> pd.DataFrame:    
    try:
        if expirywise:
            res = mcxfetch(config_key='pcr_expirywise')
        else:
            res = mcxfetch(config_key='pcr')        
            
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['ExtensionData'])
        df['Date'] = df['Date'].apply(convert_to_ist)
        if expirywise:
            df['Expiry'] = pd.to_datetime(df['Expiry'], format="%d%b%Y", dayfirst=True, errors="coerce")
        reorderd_columns = ['Symbol', 'Date', 'Expiry', 'Ratio']
        df = df[reorderd_columns]
        return df
    except Exception as e:
        print(f"Error :: {e}")

'''
def mcx_expiry(commodity: Literal['COPPER', 'CRUDEOIL', 'GOLD', 'GOLDM', 'NATURALGAS', 
                                  'NICKEL', 'SILVER', 'SILVERM','ZINC']='CRUDEOIL',
                expirytype : Literal['current', 'next', 'far', 'all']='current'
                ) -> Union[datetime,List[datetime]]:
    try:
        exp_df = mcx_pcr(expirywise=True)
        com_df = exp_df[exp_df['Symbol'] == commodity]
        exp_list = sorted(com_df['Expiry'].unique().tolist())
        exp_list = [item.to_pydatetime() for item in exp_list]
        if expirytype == "current":
            return exp_list[0]
        elif expirytype == "next":
            return exp_list[1]
        elif expirytype == "far":
            return exp_list[2]
        elif expirytype == "all":
            return exp_list
        else:
            print("Please input correct parameters.")
    except Exception as e:
        print(f"Error :: {e}")
'''
def mcx_expiry(commodity: Literal["ALUMINI", "ALUMINIUM", "COPPER", "COTTONCNDY", "CRUDEOIL", "CRUDEOILM", "GOLD", "GOLDGUINEA",
                                    "GOLDM", "GOLDPETAL", "KAPAS", "LEAD", "LEADMINI", "MCXBULLDEX", "MCXENRGDEX", "MCXMETLDEX",
                                    "MENTHAOIL", "NATGASMINI", "NATURALGAS", "NICKEL", "SILVER", "SILVERM", "SILVERMIC", "ZINC",
                                    "ZINCMINI"]='CRUDEOIL',
                instrument: Literal["option", "future"]="option",
                expirytype: Literal['current', 'next', 'far', 'all']='current'
                ) -> Union[datetime,List[datetime]]:
    
    try:
        df = mcx_marketwatch()
        if instrument == "option":
            inst = "OPTFUT"
        elif instrument == "future":
            inst = "FUTCOM"
        exp_list = df.query(f"Symbol in ['{commodity}'] and InstrumentName in ['{inst}']")['Expiry'].unique()
        exp_dates = sorted([item.to_pydatetime() for item in exp_list])
        if expirytype == "current":
            return exp_dates[0]
        elif expirytype == "next":
            return exp_dates[1]
        elif expirytype == "far":
            return exp_dates[2]
        elif expirytype == "all":
            return exp_dates
        else:
            print("Please input correct parameters.")
    except Exception as e:
        print(f"Error :: {e}")

def mcx_icomdexindices(datatype: Literal["today", "historical"]="today",
                       start_date: Union[DateFormat, datetime, date]=None,
                       end_date: Union[DateFormat, datetime, date]=None
                       ) -> pd.DataFrame:    
    try:
        if datatype == "today":
            data = {
                "Instrument_Identifier": "0",
                "Lang" : "en"
                } 
            res = mcxfetch(config_key="icomdex_details", data=data)
        elif datatype == "historical":
            if start_date is not None and end_date is not None:
                stdt = format_date(dateobj=start_date)
                enddt = format_date(dateobj=end_date)
                data = {
                    "Index": "0", 
                    "StartDate": stdt, 
                    "EndDate": enddt, 
                    "Lang": "en"
                    }
                res = mcxfetch(config_key='icomdex_historical', data=data)
            else:
                print("Please enter start_date and end_date for historical data.")
                return            
        df = pd.DataFrame(res["d"]["Data"])
        df = df.drop(columns=['__type']) 
        return df
    except Exception as e:
        print(f"Error :: {e}")

def mcx_quote(commodity: Literal["ALUMINI", "ALUMINIUM", "COPPER", "COTTONCNDY", "CRUDEOIL", "CRUDEOILM", "GOLD", "GOLDGUINEA",
                                    "GOLDM", "GOLDPETAL", "KAPAS", "LEAD", "LEADMINI", "MCXBULLDEX", "MCXENRGDEX", "MCXMETLDEX",
                                    "MENTHAOIL", "NATGASMINI", "NATURALGAS", "NICKEL", "SILVER", "SILVERM", "SILVERMIC", "ZINC",
                                    "ZINCMINI"],
                instrument: Literal["option", "future"], 
                expiry: Union[DateFormat, datetime, date], 
                optiontype: Literal["CE", "PE"]= None,
                strikeprice: Union[str, int, float]= None,
                outputtype: Literal["quote", "bidask"]="quote" 
                ) -> pd.DataFrame:
    try:
        exp_date = format_date(dateobj=expiry, isExpiry=True)
        if instrument == "future":
            data = {
                "Commodity": commodity, 
                "Expiry": exp_date
                }
            res = mcxfetch(config_key="getquote", data=data)
        elif instrument == "option":

            data = {
                "Commodity": commodity,
                "Expiry": exp_date, 
                "OptionType": optiontype, 
                "StrikPrice": str(strikeprice)
            }
            res = mcxfetch(config_key="optionquote", data=data)
        if outputtype == "quote":
            df = pd.DataFrame(res['d']['Data']).drop('QuoteBid', axis=1)
            if instrument == "future":
                df = df.drop(columns=['__type', 'Productdesc', 'ParentName'])
                reorderd_columns = ["Symbol", "Category", "ExpiryDate", "PreviousClose", "Open", "High", "Low", "LTP", "TotalBuyQty", 
                                    "TotalsellQty", "Volume", "AveragePrice", "PercentChange", "AbsoluteChange","UnderlineValue", "OpenInterest", 
                                    "ChangeInOpenInterest", "LifeTimeHigh", "LifeTimeLow", "DailyVolatility", "PriceQuoteUnit", "TradingUnit",  "VaR"]
                df = df[reorderd_columns]
            elif instrument == "option":
                df = df.drop(columns=['ExtensionData', 'Productdesc', 'ParentName'])
                reorderd_columns = ["Symbol","InstrumentName", "Category", "ExpiryDate", "PreviousClose", "Open","High", 
                                    "Low", "LTP", "TotalBuyQty", "TotalsellQty", "Volume", "AveragePrice","PercentChange", 
                                    "AbsoluteChange", "UnderlineValue", "OptionType", "StrikePrice", "OpenInterest", 
                                    "ChangeInOpenInterest", "LifeTimeHigh", "LifeTimeLow", "DailyVolatility", 
                                    "PriceQuoteUnit", "TradingUnit", "VaR"]
                df = df[reorderd_columns]
            df["ExpiryDate"] = pd.to_datetime(df["ExpiryDate"], format="%d-%b-%Y", dayfirst=True, errors='coerce')
        elif outputtype == "bidask":
            df = pd.DataFrame(res['d']['Data'][0]['QuoteBid'])
            df.insert(0, "Symbol", commodity) 
            if instrument == "option":
                df = df.drop(columns=["ExtensionData"])       
        df.insert(0, "Timestamp",convert_to_ist(res['d']['Summary']['AsOn']))
        return df
    except Exception as e:
        print(f"Error :: {e}")