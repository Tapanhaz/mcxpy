import pandas as pd
from datetime import date, datetime
from typing import List, Literal, Union, NewType

DateFormat = NewType(name="%d-%m-%Y", tp=str)
DateFormat_2 = NewType(name="%Y%m%d", tp=str)
DateFormat_3 = NewType(name="%d%b%Y", tp=str)

def mcx_bhavcopy(bhavdate: Union[DateFormat, datetime, date]) -> pd.DataFrame: ...
def mcx_marketwatch() -> pd.DataFrame: ...
def mcx_circulars(from_date: Union[DateFormat, datetime, date] = ..., to_date: Union[DateFormat, datetime, date] = ...) -> pd.DataFrame: ...
def mcx_topgainers() -> pd.DataFrame: ...
def mcx_toploosers() -> pd.DataFrame: ...
def mcx_mostactiveoptions() -> pd.DataFrame: ...
def mcx_mostactivecontracts() -> pd.DataFrame: ...
def mcx_heatmap() -> pd.DataFrame: ...
def mcx_optionchain(commodity: Literal['COPPER', 'CRUDEOIL', 'GOLD', 'GOLDM', 'NATURALGAS', 'NICKEL', 'SILVER', 'SILVERM', 'ZINC'], expiry: Union[DateFormat, datetime, date]) -> pd.DataFrame: ...
def mcx_pcr(expirywise: bool = ...) -> pd.DataFrame: ...
def mcx_expiry(commodity: Literal['COPPER', 'CRUDEOIL', 'GOLD', 'GOLDM', 'NATURALGAS', 'NICKEL', 'SILVER', 'SILVERM', 'ZINC'] = ..., expirytype: Literal['current', 'next', 'far', 'all'] = ...) -> Union[datetime, List[datetime]]: ...
