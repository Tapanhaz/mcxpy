Experimental code to fetch data from mcx. **** Do not use this code to programmatically get data from mcx exchange. This code is uploaded
here only for educational purpose. **** . The uploader is not liable for any type of damage caused by or arising from the use of this code.

Installation:

mcxpy installer is available on PyPI:

pip install mcxpy

Functions:

Below Functions will return data in pandas dataframe.. Any of the functions accepts date/expiry as %d-%m-%Y / datetime.datetime / datetime.date 
1. mcx_bhavcopy(bhavdate) -> Returns bhacopy of the given bhavdate.
2. mcx_marketwatch() -> Returns marketwatch.
3. mcx_circulars(from_date, to_date)  -> By default returns circulars within 4 days.
4. mcx_topgainers() -> Returns top gainers.
5. mcx_toploosers() -> Returns top loosers.
6. mcx_mostactiveoptions() -> Returns most active options.
7. mcx_mostactivecontracts() -> Returns most active contracts.
8. mcx_optionchain(commodity, expiry) -> Returns option chain of the given commodity of the given expiry.
9. mcx_pcr(expirywise) -> Returns commoditywise pcr if expirywise is False. If not, returns pcr expiry wise.
10. mcx_expiry(commodity, expirytype) -> By default returns current expiry date of Crudeoil.
11. mcx_heatmap() -> Returns heatmap dataframe.  
